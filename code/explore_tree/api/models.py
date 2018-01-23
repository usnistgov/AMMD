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
from mongoengine import Document, StringField, DictField, ListField, IntField, ReferenceField
from mongoengine.fields import DateTimeField
from mgi.models import TemplateVersion
from itertools import chain#
from collections import deque#
import xml.etree.ElementTree as ET#
from xml.etree.ElementTree import XMLParser#

from django.utils.importlib import import_module
import os
from pymongo import MongoClient#, TEXT, DESCENDING, errors
from bson.objectid import ObjectId

settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)
MONGODB_URI = settings.MONGODB_URI
MGI_DB = settings.MGI_DB

class QueryOntology(Document):
    """ Ontology of queries to generate the navigation tree
    """
    name = StringField(required=True, unique=True)
    status = IntField(default=0, required=True)  # 0: Uploaded; 1: Active; 2: Blank; -1: Deleted
    last_modif = DateTimeField(required=False)
    content = StringField(required=True)
    template_version = ReferenceField(TemplateVersion, required=False)


class Navigation(Document):
    """ Data structure to handle the navigation tree
    """
    name = StringField(required=False)
    parent = StringField(required=False)
    children = ListField(required=False)
    options = DictField(required=False)
    @staticmethod
    def get_name(postID):#,name):
        nav = Navigation.objects().get(pk=postID)
        return nav.name
    #@register.filter
    def get_id(name):#,name):
        client = MongoClient(MONGODB_URI)
        db = client[MGI_DB]

        navigation = Navigation.objects
        return navigation

    #Append all children of parent to the nodes list.
    def appendAllChildrenToList(nodes, parent, getChildChildren):
        childrens = parent.children
        if (childrens != None):
            childrens2 = childrens
            while (childrens2):#.hasMoreElements()) {
                node = childrens[0]#.nextElement();
                nodes.append(node)
                if (getChildChildren):
                    appendAllChildrenToList(nodes, node, getChildChildren)
                childrens2.remove[node]

    #Return a list of all nodes found in the tree.
    def getAllNodes(tree):
        nodes = []
        #root = Navigation.objects.get(pk=tree)
        #root = tree
        nodes.append(tree)#root)
        appendAllChildrenToList(nodes, tree, "True")#root, true);
        return nodes

    #Return a list of all nodes that are child, grand-child, etc...
    def getAllNodes_2(node):
        return getAllNodes_3(node, "True")

    def getAllNodes_3(node, getChildChildren):##getChildChildren= boolean
        nodes = []
        appendAllChildrenToList(nodes, node, getChildChildren)
        return nodes


class MaxDepth:                     # The target object of the parser
    maxDepth = 0
    depth = 0
    def start(self, tag, attrib):   # Called for each opening tag.
        self.depth += 1
        if self.depth > self.maxDepth:
            self.maxDepth = self.depth
    def end(self, tag):             # Called for each closing tag.
        self.depth -= 1
    def data(self, data):
        pass            # We do not need to do anything with data.
    def close(self):    # Called when all data has been parsed.
        return self.maxDepth

class MyParser:                     # The target object of the parser
    tree = None
    node_stack = []

    def start(self, tag, attrib): # Called for each opening tag.
        new_node = [tag, []]
        if not self.tree:
            # Si c'est la racine
            self.tree = new_node
            self.node_stack.append(new_node)
        else:
            # Si c'est un fils
            parent_tag, parent_child_list = self.node_stack[-1]
            # Append mode : Respecte la definition d'un node suivante : [tag, [liste_des_nodes_fils]]
            # Extend mode : Moins de listes mais necessite un unpacking precis
            #parent_child_list.append(new_node)
            parent_child_list.extend(new_node)
            self.node_stack.append(new_node)

    def end(self, tag): # Called for each closing tag.
        # On remote d'un cran dans la pile
        self.node_stack.pop()
        pass
    def data(self, data):
        pass
    def close(self):    # Called when all data has been parsed.
        return self.tree

class Node(object):
    def __init__(self, data):
        self.data = data
        self.children = []

    def add_child(self, obj):
        self.children.append(obj)

    def get_child(self, data):
        for child in self.children:
            if data == child.data:
                return child
        return None

    def set_texts(self,listeoftexts):
        i=0
        for child in self.getiterator():
            if child.getchildren():
                pass
            else:
                child.text = listoftexts[i]
                i +=1
