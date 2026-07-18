
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


class TypeKeywords():
    """
    Class for having a single definition of special keyword constants
    for types in one place.
    """

    # Number keywords
    DOUBLE = "double"
    FLOAT = "float"
    INT = "int"
    INTEGER = "integer"

    # XXX Future number-type keywords
    LONG = "long"
    SHORT = "short"
    BYTE = "byte"

    # Other type keywords
    BOOLEAN = "boolean"
    STRING = "string"
    LIST = "list"
    TUPLE = "tuple"
    DICTIONARY = "dict"
    VOID = "void"

    # Common spec keywords
    CHOICE = "choice"
    TYPE = "type"
