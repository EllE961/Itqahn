# Kyverno Policies

These policies are applied at the Kubernetes admission layer.

They enforce:
- image signing requirements (when available),
- disallow privileged pods,
- require resource requests/limits,
- require TTL labels for ephemeral environments.

Note: Tune these to your cluster and security model.
