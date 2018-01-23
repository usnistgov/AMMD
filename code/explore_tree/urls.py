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
from ajax import download_xml
from ajax import download_corrolated_xml
#from ajax import cache_all_docs #
#from ajax import cache_docs#

urlpatterns = patterns(
    '',
    url(r'^$', exploration_tree, name='exploration_tree'),
    url(r'^load_view$', load_view, name='load_view'),
    url(r'^download_xml', download_xml, name='download_xml'),
    url(r'^download_corrolated_xml', download_corrolated_xml, name='download_corrolated_xml'),
    #url(r'^cache_all_docs$', cache_all_docs, name='cache_all_docs'),
    #url(r'^cache_docs$', cache_docs, name='cache_docs'),
)
