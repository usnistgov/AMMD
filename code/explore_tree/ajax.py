""" Ajax calls for the exploration tree

"""
import json
from django.http.response import HttpResponse
from django.shortcuts import render
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from explore_tree.api.models import Navigation
from explore_tree.api.navigation.operations import retrieve_navigation_filters, get_navigation_node_for_document
from mgi.models import XMLdata
from utils.json_parser.processview import processview, processviewdocidlist, process_cross_query
from parser import query


def load_view(request):
    """

    :param request:
    :return:
    """
    # nav_id parameter is mandatory, if it doesn't exist we delete other parameters to raise and error
    if "nav_id" not in request.POST:
        request.POST = {}

    if "node_id" in request.POST and "doc_id" in request.POST:
        return __load_leaf_view(request)
    elif "node_id" in request.POST:
        return __load_branch_view(request)
    elif "ref_node_id" in request.POST and "doc_id" in request.POST:
        return __load_link_view(request)
    else:
        error = {
            "message": "Request is malformed."
        }

        return HttpResponse(json.dumps(error), status=HTTP_400_BAD_REQUEST)


def __load_leaf_view(request):
    """ Load view for a leaf

    Parameters:
        -   request:

    Returns:
    """
    # Retrieve the view annotation
    xml_document = XMLdata.get(request.POST["doc_id"])
    navigation_node = Navigation.objects.get(pk=request.POST["node_id"])

    # Display XML file if "projection_view" annotation is not configured
    if "projection_view" not in navigation_node.options:
        # TODO transform the XML into a data table
        return HttpResponse(json.dumps({}), HTTP_200_OK)

    projection_views = json.loads(navigation_node.options["projection_view"])

    view_data = {
        "header": xml_document.get("title"),
        "type": "leaf",
        "views": []
    }

    # Send the annotation to the processor and collect the data
    for projection_view in projection_views:
        result_data = {
            "title": projection_view["title"],
            "data": None
        }

        # FIXME better handling of x-
        if "query" in projection_view.keys():
            result_data["data"] = process_cross_query(request.POST["nav_id"], request.POST["doc_id"],
                                                      projection_view["query"], projection_view["data"])
        else:
            result_data["data"] = processview(request.POST["nav_id"], request.POST["doc_id"], projection_view["data"])

        view_data["views"].append(result_data)

    return render(request, "explore_tree/components/view.html", view_data)


def __load_branch_view(request):
    """ Load view for a branch

    :param request:
    :return:
    """
    # Retrieve the view annotation
    navigation_node = Navigation.objects.get(pk=request.POST["node_id"])
    filters = retrieve_navigation_filters(navigation_node)

    # FIXME modified query part to execute query directly
    documents = []
    query_documents = query.execute_query(filters, '{"_id": 1}')

    for query_doc in query_documents:
        documents.append(query_doc["_id"])

    # Display XML file if "projection_view" annotation is not configured
    if "view" not in navigation_node.options:
        error = {
            "message": "'cql:view' annotation does not exist for this branch."
        }

        return HttpResponse(json.dumps(error), HTTP_400_BAD_REQUEST)

    branch_views = json.loads(navigation_node.options["view"])

    name = navigation_node.name.split('#')[1] if '#' in navigation_node.name else navigation_node.name
    view_data = {
        "header": name,
        "type": "branch",
        "views": []
    }

    for branch_view in branch_views:
        result_data = {
            "title": branch_view["title"],
            "data": processviewdocidlist(request.POST["nav_id"], documents, branch_view["data"])
        }

        view_data["views"].append(result_data)

    return render(request, "explore_tree/components/view.html", view_data)


def __load_link_view(request):
    # retrieve document id
    # retrieve the projection content
    ref_node_id = request.POST["ref_node_id"]
    reference_node = get_navigation_node_for_document(ref_node_id, request.POST["doc_id"])

    xml_document = XMLdata.get(request.POST["doc_id"])

    if "projection_view" in reference_node.options and reference_node.options["projection_view"] is not None:
        projection_views = json.loads(reference_node.options["projection_view"])

        view_data = {
            "header": xml_document.get("title"),
            "type": "leaf",
            "views": []
        }

        # Send the annotation to the processor and collect the data
        for projection_view in projection_views:
            result_data = {
                "title": projection_view["title"],
                "data": None
            }

            # FIXME better handling of x-queries
            if "query" in projection_view.keys():
                result_data["data"] = process_cross_query(request.POST["nav_id"], request.POST["doc_id"],
                                                          projection_view["query"], projection_view["data"])
            else:
                result_data["data"] = processview(request.POST["nav_id"], request.POST["doc_id"],
                                                  projection_view["data"])

            view_data["views"].append(result_data)

        html_data = render(request, "explore_tree/components/view.html", view_data)
        doc_id = str(reference_node.pk) + "." + str(xml_document["_id"])

        # return render(request, "explore_tree/components/view.html", view_data)
        return HttpResponse(json.dumps({"html": html_data.content, "doc_id": doc_id}), status=HTTP_200_OK)
    else:
        return HttpResponse(json.dumps({}), HTTP_200_OK)
