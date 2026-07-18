
# Copyright (C) 2020-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
#
# This software is a trade secret, and contains proprietary and confidential
# materials of Cognizant Digital Business Evolutionary AI.
# Cognizant Digital Business prohibits the use, transmission, copying,
# distribution, or modification of this software outside of the
# Cognizant Digital Business EAI organization.
#
# END COPYRIGHT
from pyleafai.toolkit.data.math.type_keywords import TypeKeywords


class DoubleToNumber():
    """
    Class for casting between floats and various supported types.

    Overall, there is less of a call for this in Python than in Java, however
    I'd like to keep both language implementation somewhat similar, and there
    is a desire to keep number primitive type information supported by the
    JSON spec format all in one place.
    """

    def __init__(self, type_class=None, type_example=None):
        """
        Constructor.

        :param type_class: a type keyword indicating what class is to be
                converted to in cast_to_type().
        :param type_example: an example object whose type is to be sampled.
                That type will be used for the conversions in cast_to_type()
        """

        self._type_class = type_class
        if type_class is None:

            # Default is double -> double
            self._type_class = TypeKeywords.DOUBLE
            if type_example is not None and \
                    isinstance(type_example, int):

                self._type_class = TypeKeywords.INT

    def cast_to_type(self, value):

        double_value = float(value)
        if self.is_instance(TypeKeywords.DOUBLE):
            return_value = double_value
        elif self.is_instance(TypeKeywords.FLOAT):
            return_value = double_value
        elif self.is_instance(TypeKeywords.INT):
            return_value = int(double_value)
        elif self.is_instance(TypeKeywords.INTEGER):
            return_value = int(double_value)
        elif self.is_instance(TypeKeywords.LONG):
            return_value = int(double_value)
        elif self.is_instance(TypeKeywords.SHORT):
            return_value = int(double_value)
        elif self.is_instance(TypeKeywords.BYTE):
            return_value = int(double_value)
        else:
            raise ValueError(f"Don't know how to convert double to Type {self._type_class}")
        return return_value

    def is_instance(self, data_class):

        data_class_lower = str(data_class).lower()
        return self._type_class == data_class_lower
