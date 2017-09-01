################################################################################
#
# File Name: views.py
# Application: explore_tree/parser
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
from collections import OrderedDict
from lxml import etree

OWL_NAMESPACE = "{http://www.w3.org/2002/07/owl#}"
RDFS_NAMESPACE = "{http://www.w3.org/2000/01/rdf-schema#}"
RDF_NAMESPACE = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"

CQL_NAMESPACE = "{http://siam.nist.gov/Database-Navigation-Ontology#cql:}"  # FIXME replace hard coded elements


def parse_ontology(ontology):
    owl_tree = etree.fromstring(ontology)
    nav_tree = generate_classes(owl_tree)
    return nav_tree


def generate_classes(owl_tree):
    """
    Parse OWL Classes
    :param owl_tree:
    :return:
    """
    classes = OrderedDict()
    owl_classes = owl_tree.findall("{}Class".format(OWL_NAMESPACE))

    # get the annotations of the ontology
    annotations = []
    owl_annotations = owl_tree.findall("{}AnnotationProperty".format(OWL_NAMESPACE))
    for owl_annotation in owl_annotations:
        annotation = owl_annotation.attrib['{}about'.format(RDF_NAMESPACE)]
        try:
            annotation_name = annotation.split(':')[-1]
        except Exception as exc:
            annotation_name = annotation

        annotations.append(annotation_name)

    for owl_class in owl_classes:
        owl_subclasses = owl_class.findall("{}subClassOf".format(RDFS_NAMESPACE))
        # Top level if not subclass of other class
        if len(owl_subclasses) == 0:
            owl_class_name = owl_class.attrib['{}about'.format(RDF_NAMESPACE)]

            classes[owl_class_name] = {
                "annotations": get_class_annotations(owl_class, annotations),
                "children": generate_subclasses(owl_tree, owl_class_name, annotations)
            }

    return classes


def generate_subclasses(owl_tree, base_class_name, annotations):
    """
    Parse OWL Subclasses
    :param owl_tree:
    :param base_class_name:
    :param annotations:
    :return:
    """
    subclasses = OrderedDict()
    owl_classes = owl_tree.findall("{}Class".format(OWL_NAMESPACE))

    for owl_class in owl_classes:
        owl_subclasses = owl_class.findall("{}subClassOf".format(RDFS_NAMESPACE))

        # Test if subclass of other class
        if len(owl_subclasses) > 0:
            for owl_subclass in owl_subclasses:
                resource_name = owl_subclass.attrib['{}resource'.format(RDF_NAMESPACE)]

                if resource_name == base_class_name:
                    class_name = owl_class.attrib['{}about'.format(RDF_NAMESPACE)]

                    subclasses[class_name] = {
                        "annotations": get_class_annotations(owl_class, annotations),
                        'children': generate_subclasses(owl_tree, class_name, annotations)
                    }

                    break

    return subclasses


def get_class_annotations(owl_class, annotations):
    """ Return annotations found in the class

    :param owl_class: owl class to look in
    :param annotations: list of annotations to look for
    :return:
    """
    # Get annotations of the class
    class_annotations = {}

    for annotation in annotations:
        class_annotation = owl_class.find("{0}{1}".format(CQL_NAMESPACE, annotation))

        if class_annotation is not None:
            class_annotations[annotation] = class_annotation.text

    return class_annotations
