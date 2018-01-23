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
import os #
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
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.core.cache import caches
from django.contrib.sessions.models import Session
from mgi.models import XMLdata, Template, TemplateVersion ##
#from django.template import RequestContext, loader ##
#from mgi.models import template_list_current ##

#from os.path import join#
#from os import listdir#
#import requests#
#import json#
#import sys#
#from pymongo import MongoClient#

navigation_cache = caches['navigation']
html_tree_cache  = caches['html_tree']
nav_id_cache     = caches['nav_id']
tmpl_cache       = caches['tmpls']

@cache_page(600 * 15)
#@cache_page(60 * 1)
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

        nav_key = str(active_ontology.pk)
        if ( nav_key not in navigation_cache ):
            navigation = navigation_post(active_ontology.content)
            navigation_cache.set(nav_key, navigation)
        else:
            navigation = navigation_cache.get(nav_key)

        request_path = "%s?%s=%s" % (request.path, "nav_id", navigation.pk)
        return redirect(request_path)
    else:
        active_ontologies = get_ontology(status=1)
        active_ontologies_nb = len(active_ontologies)
        # FIXME -> more than one active is bad

        try:
            navigation=None
            n_key = request.GET["nav_id"]
            if ( n_key in nav_id_cache ):
                navigation = nav_id_cache.get(n_key)
            else:
                navigation = Navigation.objects.get(pk=request.GET["nav_id"])
                nav_id_cache.set(n_key, navigation)

            html_tree=None
            if ( n_key in html_tree_cache ):
                html_tree = html_tree_cache.get(n_key)
            else:
                tpl_version = active_ontologies[0].template_version
                html_tree = render_navigation(navigation, tpl_version.current)
                html_tree_cache.set(n_key, html_tree)

        except Exception as exc:
            print exc  # FIXME use logger
            return HttpResponseBadRequest('An error occurred during the generation of the navigation tree.')

        template=None
        t_key='explore_tree_wrapper.html'
        if( t_key in tmpl_cache ):
            template = tmpl_cache.get(t_key)
        else:
            template = loader.get_template('explore_tree_wrapper.html')
            tmpl_cache.set(t_key, template)

        context = RequestContext(request, {
            'ajax': {  # FIXME this is not useful anymore (?)
                'load_view': reverse('load_view')
            },
            'navigation_tree': html_tree,
        })
        #print context
        #print html_tree
        #print type(html_tree)
        return HttpResponse(template.render(context))
