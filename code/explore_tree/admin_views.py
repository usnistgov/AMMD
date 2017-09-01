"""

"""
from cStringIO import StringIO
from itertools import chain

from django.contrib.admin.views.decorators import staff_member_required
from django.core.servers.basehttp import FileWrapper

from django.http.response import HttpResponse
from django.shortcuts import render
from rest_framework.status import HTTP_405_METHOD_NOT_ALLOWED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from api.query_ontology.views import get_ontology


@staff_member_required
def admin_exploration_tree(request):
    """

    :param request:
    :return:
    """
    context = {
        "owl_available_list": list(chain(get_ontology(status=1), get_ontology(status=0))),
        "owl_deleted_list": get_ontology(status=-1)
    }

    return render(request, "admin/explore_tree_wrapper.html", context)


def __build_attachment(ontology_list):
    if len(ontology_list) != 1:
        return HttpResponse({}, status=HTTP_404_NOT_FOUND)

    ontology = ontology_list[0]
    ontology_content = ontology.content

    ontology_content_obj = StringIO(ontology_content.encode('utf-8'))

    # MIME type specs: https://www.w3.org/TR/owl-ref/#MIMEType
    response = HttpResponse(FileWrapper(ontology_content_obj), content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename=' + ontology.name
    return response


@staff_member_required
def admin_download_owl(request):
    if request.method != "GET":
        return HttpResponse({}, status=HTTP_405_METHOD_NOT_ALLOWED)

    if "owl_id" not in request.GET:
        ontology_list = get_ontology(status=2)
    else:
        ontology_list = get_ontology(ontology_id=request.GET["owl_id"])

    return __build_attachment(ontology_list)
