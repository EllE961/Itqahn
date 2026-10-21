"""Build the README figure from the files in this repo.

Run from the repo root:  python scripts/make_figures.py
Writes docs/assets/hero.png. Needs only matplotlib.
"""
import hashlib
import re
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import MultipleLocator, StrMethodFormatter

BG, PANEL = "#0d0c0b", "#131211"
INK, INK2, INK3 = "#ede7de", "#aaa299", "#7a736c"
GRID = "#24221f"
EMBER, TEMPER, PURPLE, GREEN = "#d95926", "#3987e5", "#9085e9", "#199e70"
SERIES = [EMBER, TEMPER, PURPLE, GREEN, "#e8b44c", "#c0509c"]
HEAT = LinearSegmentedColormap.from_list("heat", ["#141110", "#2a1410", "#4b170c", "#7a1f0a", "#ad320c",
                                                  "#d9520f", "#f07a1e", "#f9a63b", "#fccf6b", "#fff0c2"])
plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": PANEL, "savefig.facecolor": BG,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "axes.titlecolor": INK, "axes.titleweight": "semibold",
    "axes.titlesize": 12.5, "axes.titlelocation": "left", "axes.titlepad": 12, "axes.labelsize": 10,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.8, "grid.linestyle": "-",
    "xtick.color": INK3, "ytick.color": INK3, "xtick.labelsize": 9, "ytick.labelsize": 9,
    "xtick.major.size": 0, "ytick.major.size": 0, "xtick.major.pad": 6, "ytick.major.pad": 6,
    "axes.axisbelow": True, "font.family": ["Segoe UI", "DejaVu Sans"], "lines.linewidth": 2,
    "lines.solid_capstyle": "round", "legend.frameon": False, "legend.fontsize": 9.5, "legend.labelcolor": INK2,
    "figure.dpi": 110, "savefig.dpi": 200,
})

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "assets"


def section_label(folder):
    # "07-integrations" -> "07 integrations"
    num, _, rest = folder.partition("-")
    return f"{num} {rest.replace('-', ' ')}"


def doc_lines_per_section():
    counts = {}
    for section in sorted(p for p in (ROOT / "docs").iterdir() if p.is_dir() and p.name[:2].isdigit()):
        total = 0
        for md in section.rglob("*.md"):
            with md.open(encoding="utf-8") as fh:
                total += sum(1 for _ in fh)
        counts[section.name] = total
    return counts


def agent_specs_per_department():
    """Split each department into specs that share the common body template and specs written on their own.

    Two specs share the template when their body is identical after removing the role name
    and the one-line Purpose paragraph.
    """
    bodies = {}
    for spec in sorted((ROOT / "agents").glob("*/*.md")):
        text = spec.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
        if not m:
            continue
        name = re.search(r"^name:\s*(\S+)", m.group(1), re.M).group(1)
        body = m.group(2).replace(name, "NAME")
        body = re.sub(r"## Purpose\n.*?\n\n", "", body, flags=re.S)
        bodies[spec] = hashlib.md5(body.encode("utf-8")).hexdigest()

    template_hash, _ = Counter(bodies.values()).most_common(1)[0]
    split = defaultdict(lambda: [0, 0])  # dept -> [shared template, individual]
    for spec, h in bodies.items():
        split[spec.parent.name][0 if h == template_hash else 1] += 1
    return dict(sorted(split.items()))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    docs = doc_lines_per_section()
    agents = agent_specs_per_department()
    n_docs = sum(1 for _ in (ROOT / "docs").rglob("*.md"))
    n_specs = sum(a + b for a, b in agents.values())
    n_shared = sum(a for a, _ in agents.values())

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.6), gridspec_kw={"width_ratios": [1, 1.1], "wspace": 0.42})

    # Left: lines of Markdown per docs section
    labels = [section_label(k) for k in docs][::-1]
    values = list(docs.values())[::-1]
    bars = ax1.barh(labels, values, color=TEMPER, height=0.62)
    for b, v in zip(bars, values):
        ax1.text(v + max(values) * 0.015, b.get_y() + b.get_height() / 2, f"{v:,}",
                 va="center", ha="left", color=INK2, fontsize=8.5)
    ax1.set_title(f"Lines of Markdown per docs section ({n_docs} docs, {sum(values):,} lines)")
    ax1.set_xlim(0, max(values) * 1.16)
    ax1.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    ax1.grid(axis="y", visible=False)
    ax1.grid(axis="x", visible=True)
    ax1.tick_params(axis="y", labelcolor=INK2)

    # Right: agent specs per department, split by template vs individually written
    depts = [section_label(k) for k in agents][::-1]
    shared = [agents[k][0] for k in agents][::-1]
    own = [agents[k][1] for k in agents][::-1]
    ax2.barh(depts, shared, color="#3a3632", height=0.62, label=f"shared body template ({n_shared})")
    ax2.barh(depts, own, left=shared, color=EMBER, height=0.62,
             label=f"written individually ({n_specs - n_shared})")
    for y, (s, o) in enumerate(zip(shared, own)):
        ax2.text(s + o + 0.15, y, str(s + o), va="center", ha="left", color=INK2, fontsize=8.5)
    ax2.set_title(f"Agent role specs per department ({n_specs} specs)")
    ax2.set_xlim(0, max(s + o for s, o in zip(shared, own)) + 1.6)
    ax2.xaxis.set_major_locator(MultipleLocator(2))
    ax2.grid(axis="y", visible=False)
    ax2.grid(axis="x", visible=True)
    ax2.tick_params(axis="y", labelcolor=INK2)
    ax2.legend(loc="upper right", bbox_to_anchor=(1.0, -0.07), ncol=2, handlelength=1.2)

    fig.text(0.012, -0.07,
             "Counted from docs/**/*.md and agents/*/*.md. A spec counts as shared template when its body matches "
             "the most common one after removing the role name and the one-line purpose.",
             color=INK3, fontsize=8.5, ha="left", va="top")
    path = OUT / "hero.png"
    fig.savefig(path, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    print(f"wrote {path.relative_to(ROOT)}  docs={n_docs} lines={sum(values)} specs={n_specs} shared={n_shared}")


if __name__ == "__main__":
    main()
