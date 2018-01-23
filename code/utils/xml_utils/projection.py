"""
"""
from mgi.exceptions import MDCSError


def get_projection(document):
    """ Get the value returned by the projection

    :param document:
    :return:
    """
    if len(document) == 1:  # If only one key, _id (by default from mongo)
        return document['_id']
    elif len(document) == 2:  # If 2 keys, get the the one that is not _id
        keys = document.keys()
        for key in keys:
            if key != '_id':
                return get_projection_value(document[key])

    raise MDCSError('Unable to get a value for the projection.')


def get_projection_value(document):
    """
    Go recursively down the dict to get the value
    :param document:
    :return:
    """
    value = document[document.keys()[0]]
    if isinstance(value, dict):
        return get_projection_value(value)
    else:
        return value
