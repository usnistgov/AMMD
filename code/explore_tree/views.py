"""
#
# File Name: views.py
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
#
################################################################################
"""
import json
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.template import loader
from django.template.context import RequestContext
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_405_METHOD_NOT_ALLOWED
from api.navigation.views import navigation_post
from explore_tree.api.models import Navigation
from explore_tree.parser.renderer import render_navigation
from api.query_ontology.views import get_ontology


@ensure_csrf_cookie
def exploration_tree(request):
    """

    :param request:
    :return:
    """
    if request.method != "GET":
        return HttpResponse({}, status=HTTP_405_METHOD_NOT_ALLOWED)

    # A request
    if "nav_id" not in request.GET:
        active_ontologies = get_ontology(status=1)
        active_ontologies_nb = len(active_ontologies)

        # Error cases handling the possibility of having more than one ontology active
        if active_ontologies_nb > 1:
            error = {
                "message": "More than one active ontology found."
            }

            return HttpResponse(json.dumps(error), status=HTTP_500_INTERNAL_SERVER_ERROR)
        elif active_ontologies_nb == 0:
            error = {
                "message": "No active ontologies found."
            }

            return HttpResponse(json.dumps(error), status=HTTP_404_NOT_FOUND)

        active_ontology = active_ontologies[0]

        # Parsing the content of the ontology
        # FIXME navigation trees are never cleaned up
        navigation = navigation_post(active_ontology.content)

        request_path = "%s?%s=%s" % (request.path, "nav_id", navigation.pk)
        return redirect(request_path)
    else:
        try:
            navigation = Navigation.objects.get(pk=request.GET["nav_id"])
            html_tree = render_navigation(navigation)
        except Exception as exc:
            print exc  # FIXME use logger
            return HttpResponseBadRequest('An error occurred during the generation of the navigation tree.')

        template = loader.get_template('explore_tree_wrapper.html')
        context = RequestContext(request, {
            'ajax': {  # FIXME this is not useful anymore (?)
                'load_view': reverse('load_view')
            },
            'navigation_tree': html_tree,
        })

        return HttpResponse(template.render(context))
