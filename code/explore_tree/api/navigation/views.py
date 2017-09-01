################################################################################
#
# File Name: models.py
# Application: explore_tree/navigation
# Purpose:
#
# Author:
#         Philippe Dessauw
#         philippe.dessauw@nist.gov
#
#         Guillaume Sousa Amaral
#         guillaume.sousa@nist.gov
#
#         Sharief Youssef
#         sharief.youssef@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################
from ..models import Navigation
from explore_tree.parser.parser import parse_ontology


def navigation_get(navigation_id):
    """
    Get a navigation tree
    :param navigation_id:
    :return:
    """
    return Navigation.objects().get(pk=navigation_id)


def navigation_post(owl_content):
    """

    :param owl_content:
    :return:
    """
    parsed_ontology = parse_ontology(owl_content)
    return _create_navigation(parsed_ontology)


def _create_navigation(tree):
    """
    Create navigation from the root element
    :param tree:
    :return:
    """
    # create navigation
    navigation = Navigation().save()

    # generate children
    children = _create_navigation_branches(tree, str(navigation.id))

    # update children
    navigation.children = children
    navigation.save()

    return navigation


def _create_navigation_branches(tree, parent):
    """
    Create navigation branches
    :param tree:
    :param parent:
    :return:
    """
    children_ids = []

    for name, values in tree.iteritems():
        # create navigation
        navigation = Navigation(
            name=name,
            parent=parent
        ).save()

        # generate children
        children = _create_navigation_branches(values['children'], str(navigation.id))

        # update navigation
        navigation.options = values['annotations']
        navigation.children = children
        navigation.save()

        # add the navigation to the list
        children_ids.append(str(navigation.id))

    return children_ids
