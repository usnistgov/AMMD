################################################################################
#
# File Name: tests.py
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
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from django.test.testcases import TestCase
from os.path import join
from explore_tree.parser.parser import parse_ontology
from explore_tree.parser.renderer import render_tree
from mgi.settings import BASE_DIR
import json


RESOURCES_PATH = join(BASE_DIR, 'explore_tree', 'parser', 'tests', 'data')


class ParseOntologyTestSuite(TestCase):
    """
    """

    def setUp(self):
        pass

    def test_parse_ontology_1(self):
        owl_path = join(RESOURCES_PATH, 'am1.owl')

        with open(owl_path) as owl_file:
            owl_content = owl_file.read()
            nav_tree = parse_ontology(owl_content)
            print json.dumps(nav_tree, indent=4)
            nav_tree_html = render_tree(nav_tree)
            with open(join(RESOURCES_PATH, 'result_tree.html'), 'w') as html_tree:
                html_tree.write(nav_tree_html)
