"""
# File Name: query.py
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
"""
import json
from mgi.models import XMLdata
from utils.xml_utils.projection import get_projection


def _is_advanced_filter(str_filter):
    """ Helper able to determine if a filter is advanced or not

    :param str_filter:
    :return:
    """
    try:
        json_filter = json.loads(str_filter)

        expected_keys = {"documents", "query"}
        return len(expected_keys.difference(json_filter.keys())) == 0
    except Exception as exc:
        return False


def execute_query(templateID, filters=list(), projection=None):

    """
    :param filters:
    :param projection:
    :return:
    """
    # query = {
    #     "$and": []
    # }

    results_id = {xml_data["_id"] for xml_data in XMLdata.executeFullTextQuery("", [templateID])}

    results = []

    # Parsing filters if present
    for _filter in filters:
        if _is_advanced_filter(_filter):
            json_filter = json.loads(_filter)
            # Get matching document
            #   list possible values of the right hand side
            #   match resulted documents
            documents_field = json_filter["documents"].values()[0]

            values = get_filter_values(documents_field)
            matching_documents = get_matching_document(templateID, json_filter["documents"].keys()[0], values, json_filter["query"])

            # Extract correct documents
            filter_result = []

            for doc in matching_documents:
                doc_cross_query = {json_filter["documents"].values()[0]: get_projection(doc)}
                filter_result += XMLdata.executeQueryFullResult(doc_cross_query, json.loads(projection))
        else:
            filter_result = XMLdata.executeQueryFullResult(json.loads(_filter), json.loads(projection))

        filter_id = {document["_id"] for document in filter_result}
        results_id = results_id.intersection(filter_id)

        results = [doc for doc in filter_result if doc["_id"] in results_id]


    return results


def get_filter_values(field):
    """ Get matching values in MongoDB for a given field

    :param field:
    :return:
    """
    query = {field: {"$exists": True}}
    projection = {field: 1}

    documents = XMLdata.executeQueryFullResult(query, projection)
    return {get_projection(doc) for doc in documents}


def get_matching_document(templateId, field, values, query):
    """

    :param field:
    :param values:
    :param query:
    :return:
    """
    document_set = []
    document_projection = {field: 1}

    for value in values:
        tmp_query = [
            json.dumps(query),
            json.dumps({field: value})
        ]

        document_set += execute_query(templateId, tmp_query, json.dumps(document_projection))

    return document_set
