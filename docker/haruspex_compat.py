import runpy
import sys
import tensorflow as tf

# Enable TensorFlow 1-style execution.
tf.compat.v1.disable_v2_behavior()

# Restore legacy top-level names used by the original Haruspex code.
legacy_names = (
    "app",
    "train",
    "estimator",
    "ConfigProto",
    "Session",
    "random_uniform",
    "case",
    "to_int32",
    "to_float",
    "global_variables_initializer",
    "local_variables_initializer",
)

for name in legacy_names:
    if not hasattr(tf, name) and hasattr(tf.compat.v1, name):
        setattr(tf, name, getattr(tf.compat.v1, name))

# Restore legacy layers if available in this TensorFlow build.
if not hasattr(tf, "layers") and hasattr(tf.compat.v1, "layers"):
    tf.layers = tf.compat.v1.layers

# Preserve the original CLI arguments and the original script.
sys.argv = [
    "/opt/hpx/hpx_unet_190116.py",
    *sys.argv[1:],
]


# Restore numpy_input_fn if the TF 1.x compatibility API provides it.
legacy_estimator = tf.compat.v1.estimator

if not hasattr(tf.estimator, "inputs") and hasattr(legacy_estimator, "inputs"):
    tf.estimator.inputs = legacy_estimator.inputs


runpy.run_path(
    "/opt/hpx/hpx_unet_190116.py",
    run_name="__main__",
)
