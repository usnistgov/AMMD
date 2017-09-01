"""
# File Name: admin.py
# Application: explore_tree
# Purpose:
#
# Author: Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov

        Philippe DESSAUW
        philippe.dessauw@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
"""
from django.contrib import admin
from django.conf.urls import url, patterns

import admin_views
import admin_ajax


admin_urls = patterns(
    '',

    # Views
    url(r'^explore_tree$', admin_views.admin_exploration_tree, name='admin_exploration_tree'),
    url(r'^explore_tree/download_owl$', admin_views.admin_download_owl, name='admin_download_owl'),

    # AJAX
    url(r'^explore_tree/upload_owl', admin_ajax.admin_upload_owl, name='admin_upload_owl'),
    url(r'^explore_tree/query_ontology', admin_ajax.admin_query_ontology, name='admin_query_ontology'),
)

urls = admin.site.get_urls()
admin.site.get_urls = lambda: admin_urls + urls
