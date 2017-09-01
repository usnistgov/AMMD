"""
# File Name: models.py
# Application: explore_tree
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
"""
from mongoengine import Document, StringField, DictField, ListField, IntField
from mongoengine.fields import DateTimeField


class QueryOntology(Document):
    """ Ontology of queries to generate the navigation tree
    """
    name = StringField(required=True, unique=True)
    status = IntField(default=0, required=True)  # 0: Uploaded; 1: Active; 2: Blank; -1: Deleted
    last_modif = DateTimeField(required=False)
    content = StringField(required=True)


class Navigation(Document):
    """ Data structure to handle the navigation tree
    """
    name = StringField(required=False)
    parent = StringField(required=False)
    children = ListField(required=False)
    options = DictField(required=False)
