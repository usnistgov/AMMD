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
import os

from lxml import etree
from django.http.response import HttpResponse
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_405_METHOD_NOT_ALLOWED

from curate.views import curate_enter_data_downloadxsd
from mgi.common import LXML_SCHEMA_NAMESPACE
from mgi.models import Template


def render_schema(request):
    if request.method != "POST":
        return HttpResponse(status=HTTP_405_METHOD_NOT_ALLOWED)

    if "xsd_id" not in request.POST:
        return HttpResponse(status=HTTP_400_BAD_REQUEST)

    xsd_id = request.POST["xsd_id"]
    xsd_file = Template.objects.get(pk=xsd_id)
    xsd_tree = etree.fromstring(str(xsd_file.content.encode("utf-8")))

    annotations = xsd_tree.findall(".//{}annotation".format(LXML_SCHEMA_NAMESPACE))
    for annotation in annotations:
        annotation.getparent().remove(annotation)

    script_location = os.path.dirname(__file__)
    xslt_file = os.path.join(script_location, 'static', 'schema_viewer', 'xsl', 'xsd2html.xsl')
    # with open(xslt_file, "r") as xslt_fp:
    #     xslt_content = xslt_fp.read()
    #
    # xslt_tree = etree.fromstring(xslt_content)
    xslt_tree = etree.parse(xslt_file)
    xslt_transformation = etree.XSLT(xslt_tree)

    xsd_xslt_tree = xslt_transformation(xsd_tree)
    xsd_xslt_html = str(xsd_xslt_tree)

    return HttpResponse(xsd_xslt_html, status=HTTP_200_OK)


def download_schema(request):
    """

    :param request:
    :return:
    """
    # FIXME this function needs to be updated when the core is done.
    if request.method != "GET":
        return HttpResponse(status=HTTP_405_METHOD_NOT_ALLOWED)

    if "schema_id" not in request.GET:
        return HttpResponse(status=HTTP_400_BAD_REQUEST)

    request.session['currentTemplateID'] = request.GET["schema_id"]

    response = curate_enter_data_downloadxsd(request)

    del request.session['currentTemplateID']
    return response
