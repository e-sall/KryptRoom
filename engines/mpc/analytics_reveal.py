"""The sole M3 reconstruction boundary; deny before any transfer to a PYU."""
from analytics_contract import PARTIES, metric_reveal, output_id, validate_policy


class RevealService:
    def __init__(self, policy, parties, reconstruct, scalarize):
        self.policy = policy
        self.parties = parties
        self._reconstruct = reconstruct
        self._scalarize = scalarize

    def metadata(self, producer):
        validate_policy(self.policy)
        if not self.policy.authorizes("ciphertext-metadata", PARTIES):
            raise PermissionError("Ciphertext metadata is not authorized")
        return self._reconstruct(producer())

    def authorize(self, spec, name):
        validate_policy(self.policy)
        metric = next((m for m in spec["metrics"] if metric_reveal(m) == name), None)
        if (name not in spec["requestedReveals"] or metric is None
                or not self.policy.authorizes(name, PARTIES)):
            raise PermissionError("Analytics scalar reveal is not authorized")
        return output_id(metric)

    def scalar(self, spec, name, load_secret):
        artifact_id = self.authorize(spec, name)
        # Authorization precedes loading, SPU->PYU transfer and reconstruction.
        return self._scalar_from_artifact(artifact_id, load_secret)

    def authorize_named(self, requested_reveals, name, artifact_by_reveal):
        """Authorize a committed non-M3 scalar without adding a reveal boundary."""
        validate_policy(self.policy)
        if (name not in requested_reveals or name not in artifact_by_reveal
                or not self.policy.authorizes(name, PARTIES)):
            raise PermissionError("Named scalar reveal is not authorized")
        return artifact_by_reveal[name]

    def named_scalar(self, requested_reveals, name, artifact_by_reveal, load_secret):
        artifact_id = self.authorize_named(requested_reveals, name, artifact_by_reveal)
        # Authorization precedes loading, SPU->PYU transfer and reconstruction.
        return self._scalar_from_artifact(artifact_id, load_secret)

    def _scalar_from_artifact(self, artifact_id, load_secret):
        secret = load_secret(artifact_id)
        values = self._reconstruct([secret.to(self.parties[p]) for p in PARTIES])
        scalars = [self._scalarize(v) for v in values]
        if len(scalars) != 2 or scalars[0] != scalars[1]:
            raise RuntimeError("Participants disagree on the authorized scalar")
        return scalars[0]


def production_service(policy, parties):
    # No other M3 module imports SecretFlow's reveal function.
    import numpy as np
    import secretflow as sf
    return RevealService(policy, parties, sf.reveal, lambda v: np.asarray(v).item())
