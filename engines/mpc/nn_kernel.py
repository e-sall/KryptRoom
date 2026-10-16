"""The fixed M4 JAX neural network, trained and evaluated entirely on SPU."""
import jax
import jax.numpy as jnp


def _normalized(mask, left, right, training_spec):
    mask_fp = jnp.reshape(mask.astype(jnp.float32), (-1, 1))
    x = jnp.reshape(
        left[:, :, training_spec["feature"]["column"]].astype(jnp.float32), (-1, 1)
    ) / jnp.float32(training_spec["feature"]["divideBy"])
    y = jnp.reshape(
        right[:, :, training_spec["label"]["column"]].astype(jnp.float32), (-1, 1)
    ) / jnp.float32(training_spec["label"]["divideBy"])
    return mask_fp, x, y


def _forward(params, x):
    w1, b1, w2, b2 = params
    hidden = jnp.matmul(x, w1) + b1
    activated = hidden * hidden
    return jnp.matmul(activated, w2) + b2


def _masked_mse(params, x, y, mask):
    error = _forward(params, x) - y
    # The denominator remains the secret mask count. Public cardinality is used
    # only by the pre-runtime contract to reject an empty cohort.
    return jnp.sum(mask * error * error) / jnp.sum(mask)


def training_kernel_for(training_spec, initial_values):
    """Capture only public, commitment-bound initialization and hyperparameters."""
    learning_rate = training_spec["learningRate"]
    steps = training_spec["steps"]

    def train(mask, left, right):
        mask_fp, x, y = _normalized(mask, left, right, training_spec)
        params = (
            jnp.reshape(jnp.asarray(initial_values[0], dtype=jnp.float32), (1, 2)),
            jnp.reshape(jnp.asarray(initial_values[1], dtype=jnp.float32), (2,)),
            jnp.reshape(jnp.asarray(initial_values[2], dtype=jnp.float32), (2, 1)),
            jnp.reshape(jnp.asarray(initial_values[3], dtype=jnp.float32), (1,)),
        )
        for _ in range(steps):
            gradients = jax.grad(_masked_mse)(params, x, y, mask_fp)
            params = tuple(
                value - jnp.float32(learning_rate) * gradient
                for value, gradient in zip(params, gradients, strict=True)
            )
        return params

    return train


def evaluation_kernel_for(evaluation_spec):
    def evaluate(mask, left, right, w1, b1, w2, b2):
        mask_fp, x, y = _normalized(mask, left, right, evaluation_spec)
        value = _masked_mse((w1, b1, w2, b2), x, y, mask_fp)
        return jnp.reshape(value, (1,))

    return evaluate
