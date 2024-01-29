# Program Author: Qingxu Fu, CASIA

from collections import namedtuple


def convert(dictionary):
    return namedtuple('GenericDict', dictionary.keys())(**dictionary)
