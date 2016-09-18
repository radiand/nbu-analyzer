# -*- coding: utf-8 -*-


def nested_set(dict_, keys, value):
    """
    Sets value for a nested key in dict.
    :param dict_: (dict) to be set
    :param keys: (list) of (str) as nested keys
    :param value: value to be set in nested key in dict_
    """
    for key in keys[:-1]:
        dict_ = dict_.setdefault(key, {})
    dict_[keys[-1]] = value


def count_dict(dict_):
    occurs = 0
    for keydate in dict_:
        occurs += dict_[keydate]
    return occurs
