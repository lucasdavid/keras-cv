import tensorflow as tf
from tensorflow import keras

from keras_cv.utils import preprocessing


class RandomShear(tf.keras.__internal__.layers.BaseImageAugmentationLayer):
    """Randomly shears an image.

    Args:
        x: float, 2 element tuple, or `None`.  For each augmented image a value is sampled
            from the provided range.  If a float is passed, the range is interpreted as
            `(0, x)`.  If `None` is passed, no shear occurs on the X axis.  Defaults to
            `None`.
        y: float, 2 element tuple, or `None`.  For each augmented image a value is sampled
            from the provided range.  If a float is passed, the range is interpreted as
            `(0, x)`.  If `None` is passed, no shear occurs on the Y axis.  Defaults to
            `None`.
        interpolation: interpolation method used in the `ImageProjectiveTransformV3` op.
             Supported values can be found in the `ImageProjectiveTransformV3`
             documentation.  Defaults to `"bilinear"`.
        fill_mode: fill_mode in the `ImageProjectiveTransformV3` op.
             Supported values can be found in the `ImageProjectiveTransformV3`
             documentation.  Defaults to `"reflect"`.
        fill_value: fill_value in the `ImageProjectiveTransformV3` op.
             Supported values can be found in the `ImageProjectiveTransformV3`
             documentation.  Defaults to `0.0`. 
    """

    def __init__(
        self,
        x=None,
        y=None,
        interpolation="bilinear",
        fill_mode="reflect",
        fill_value=0.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if isinstance(x, float):
            x = (0, x)
        if isinstance(y, float):
            y = (0, y)
        self.x = x
        self.y = y
        self.interpolation = interpolation

    def get_random_tranformation(self):
        x = self._get_shear_amount(self.x)
        y = self._get_shear_amount(self.y)
        return (x, y)

    def _get_shear_amount(self, constraint):
        if constraint is None:
            return None

        negate = self._random_generator.random_uniform((), 0, 1, dtype=tf.float32) > 0.5
        negate = tf.cond(negate, lambda: -1.0, lambda: 1.0)

        return negate * self._random_generator.random_uniform(
            (), constraint[0], constraint[1]
        )

    def augment_image(self, image, transformation=None):
        image = tf.expand_dims(image, axis=0)

        x, y = transformation

        if x is not None:
            transform_x = RandomShear._format_transform(
                [1.0, x, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]
            )
            image = preprocessing.transform(
                images=image,
                transforms=transform_x,
                interpolation=self.interpolation,
                fill_mode=self.fill_mode,
                fill_value=self.fill_value,
                interpolation=self.interpolation,
            )

        if y is not None:
            transform_y = RandomShear._format_transform(
                [1.0, 0.0, 0.0, y, 1.0, 0.0, 0.0, 0.0]
            )
            image = preprocessing.transform(
                images=image,
                transforms=transform_y,
                interpolation=self.interpolation,
                fill_mode=self.fill_mode,
                fill_value=self.fill_value,
                interpolation=self.interpolation,
            )

        return tf.squeeze(image, axis=0)

    @staticmethod
    def _format_transform(transform):
        transform = tf.convert_to_tensor(transform, dtype=tf.float32)
        return transform[None]
