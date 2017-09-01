################################################################################
#
# File Name: models.py
# Application: explore_tree/ontology
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
import operator
from datetime import datetime
from mongoengine.queryset.visitor import Q
from ..models import QueryOntology, TemplateVersion


def create_ontology(name, content):
    """ Create a new ontology of queries

    :param name:
    :param content:
    :return:
    """
    try:
        query_ontology = QueryOntology(
            name=name,
            content=content,
            last_modif=datetime.now()
        )

        query_ontology.save()
        return query_ontology.pk
    except Exception as exc:
        return -1


def edit_ontology_status(ontology_id, status):
    try:
        status = int(status)
    except ValueError:
        return -1

    current_ontology = get_ontology(ontology_id)

    if status == 1:  # If we activate an ontology, we deactivate all the other ones
        active_ontologies = get_ontology(status=1)

        for active_ontology in active_ontologies:
            active_ontology.update(set__status=0)

    current_ontology.update(set__status=status)

    return 0


def edit_ontology_name(ontology_id, name):
    query_ontology = QueryOntology.objects.get(pk=ontology_id)
    query_ontology.update(set__name=name)
    query_ontology.update(set__last_modif=datetime.now())

    query_ontology.reload()


def edit_ontology_template(ontology_id, template_version_id):
    query_ontology = QueryOntology.objects.get(pk=ontology_id)
    query_ontology.update(set__template_version=TemplateVersion.objects.get(pk=template_version_id))
    query_ontology.update(set__last_modif=datetime.now())

    query_ontology.reload()


def get_ontology(ontology_id=None, status=None):
    """ Get an ontology of queries

    :param ontology_id:
    :param status:
    :return:
    """
    query = {}

    if ontology_id is not None:
        query["pk"] = ontology_id

    if status is not None:
        query["status"] = status

    query_list = {Q(**({key: value})) for key, value in query.iteritems()}

    if len(query_list) == 0:
        return QueryOntology.objects.all()

    return QueryOntology.objects(reduce(operator.and_, query_list)).all()


def ontology_delete(ontology_id):
    """

    :param ontology_id:
    :return:
    """
    ontology = QueryOntology.objects.get(pk=ontology_id)
    ontology.delete()
