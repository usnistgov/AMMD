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

from ajax import load_view
from views import exploration_tree

urlpatterns = patterns(
    '',
    url(r'^$', exploration_tree, name='exploration_tree'),
    url(r'^load_view$', load_view, name='load_view'),
)
