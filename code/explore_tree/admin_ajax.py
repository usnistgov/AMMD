"""

"""
import json
from time import time
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http.request import QueryDict
from django.http.response import HttpResponse
from os.path import join, exists, splitext
from os import mkdir
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_405_METHOD_NOT_ALLOWED, HTTP_200_OK, \
    HTTP_500_INTERNAL_SERVER_ERROR
from api.query_ontology.views import create_ontology, edit_ontology_name
from explore_tree.api.query_ontology.views import edit_ontology_status, ontology_delete
from utils import randomizer


@staff_member_required
def admin_upload_owl(request):
    uploaded_file = request.FILES["files[]"]

    if splitext(uploaded_file.name)[1] != ".owl":
        error = {
            "message": "Wrong file type"
        }

        return HttpResponse(json.dumps(error), status=HTTP_400_BAD_REQUEST)

    # Creating temp folder if it doesn't exist
    temp_folder = join(settings.SITE_ROOT, "tmp")
    if not exists(temp_folder):
        mkdir(temp_folder)

    # Writing file to the server
    uploaded_file_path = join(temp_folder, uploaded_file.name)

    with open(uploaded_file_path, "wb") as uploaded_file_pointer:
        for chunk in uploaded_file.chunks():
            uploaded_file_pointer.write(chunk)

    with open(uploaded_file_path, "r") as uploaded_file_pointer:
        ontology_content = ''.join(uploaded_file_pointer.readlines())

    # Renaming the file to avoid name collision
    timestamp = str(int(time() * 1000))
    uploaded_file_name = splitext(uploaded_file.name)[0]

    ontology_name = "_".join([uploaded_file_name, randomizer.generate_string(6, True, False, True), timestamp])

    ontology_id = create_ontology(ontology_name + ".owl", ontology_content)

    if ontology_id == -1:  # An exception happened while creating the ontology
        error = {
            "message": "Impossible to save file in DB"
        }

        return HttpResponse(json.dumps(error), status=HTTP_500_INTERNAL_SERVER_ERROR)

    ontology_data = {
        "_id": str(ontology_id),
        "name": ontology_name
    }

    return HttpResponse(json.dumps(ontology_data), status=HTTP_200_OK, content_type="application/json")


@staff_member_required
def admin_query_ontology(request):
    """ Ajax requests for ontology management

    :param request:
    :return:
    """
    try:
        exit_code = 0

        if request.method == "GET":  # Retrieve an existing ontology
            query_onto_id = request.GET["id"]

        elif request.method == "POST":  # Create / Edit an ontology
            query_onto_id = request.POST["id"]

            if "name" in request.POST:
                edit_ontology_name(query_onto_id, request.POST["name"] + ".owl")
            elif "status" in request.POST:
                exit_code = edit_ontology_status(query_onto_id, request.POST["status"])

        elif request.method == "DELETE":  # Delete an ontology
            query = QueryDict(request.body)
            query_onto_id = query["id"]

            ontology_delete(query_onto_id)
        else:
            return HttpResponse(status=HTTP_405_METHOD_NOT_ALLOWED)

        if exit_code != 0:
            return HttpResponse(status=HTTP_400_BAD_REQUEST)

        return HttpResponse(status=HTTP_200_OK)
    except Exception as exc:
        error_message = {
            "message": exc.message
        }

        return HttpResponse(json.dumps(error_message), status=HTTP_400_BAD_REQUEST)