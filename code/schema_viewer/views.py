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
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from mgi.models import Template


@ensure_csrf_cookie
def xsd_viewer(request):
    xsd_files = Template.objects.all()
    return render(request, "schema_viewer_wrapper.html", {"templates": xsd_files})


def tabbed_viewer(request):
    return render(request, "schema_viewer_wrapper_2.html", {"schema": {"id": request.GET["sid"],
                                                                       "name": request.GET["sname"]}})


# def oxygen_viewer(request):
#     return render(request, "schema_viewer/oxygen/"+request.GET["name"]+".html")
