"""Exactly four scalar reductions, executed by SPU on the persisted join grid."""
import jax.numpy as jnp


def kernel_for(metrics):
    # Public specification is captured before tracing; there is no secret branching.
    def compute(mask, left, right):
        count = jnp.sum(mask, dtype=jnp.int32)
        mask_fp = mask.astype(jnp.float32)
        count_fp = count.astype(jnp.float32)
        features = {"lab-a-features": left, "lab-b-features": right}

        def feature(selector):
            return features[selector["artifact"]][:, :, selector["column"]].astype(jnp.float32)

        outputs = []
        for metric in metrics:
            op = metric["op"]
            if op == "COUNT":
                value = count
            elif op in ("SUM", "MEAN"):
                value = jnp.sum(mask_fp * feature(metric["input"]))
                if op == "MEAN":
                    value = value / count_fp
            elif op == "CROSS_MEAN":
                value = jnp.sum(mask_fp * feature(metric["left"]) * feature(metric["right"])) / count_fp
            else:
                raise ValueError("Unsupported analytics metric")
            outputs.append(jnp.reshape(value, (1,)))
        return tuple(outputs)
    return compute
