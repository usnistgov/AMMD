################################################################################
#
# File Name: urls.py
# Application: mgi
# Purpose:
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from django.conf.urls import patterns, url

import views
import ajax

urlpatterns = patterns(
    '',
    url(r'^$', views.xsd_viewer, name='xsd_viewer'),
    url(r'^tabbed$', views.tabbed_viewer, name='tabbed_viewer'),
    url(r'^oxygen', views.oxygen_viewer, name='oxygen_viewer'),

    url(r'^render_schema$', ajax.render_schema, name='xsd_viewer_render_schema'),
    url(r'^download_schema', ajax.download_schema, name='xsd_viewer_download_schema'),

    url(r'^sandbox', views.sandbox_viewer, name='sandbox')
)
