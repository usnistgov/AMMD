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
from io import BytesIO
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from bson import ObjectId
from lxml import etree

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader

from curate.forms import NewForm
from mgi.models import Template, FormData
from mgi.settings import SITE_ROOT
from os import path, listdir
from django.contrib.messages import add_message, WARNING

from schema_viewer.forms import FormDefaultTemplate
from schema_viewer.models import FormDataSandbox
from utils.XSDParser.parser import delete_branch_from_db


@ensure_csrf_cookie
def xsd_viewer(request):
    form = FormDefaultTemplate()
    form.set_default(empty_label=False)
    return render(request, "schema_viewer_wrapper.html", locals())


def tabbed_viewer(request):
    return render(request, "schema_viewer_wrapper_2.html", {"schema": {"id": request.GET["sid"],
                                                                       "name": request.GET["name"]}})


def oxygen_viewer(request):
    template_name = request.GET.get("name", None)
    #file_name = "wrap_" + template_name + ".html"
    file_name = template_name + ".html"

    if file_name in listdir(path.join(SITE_ROOT, 'schema_viewer', 'templates', 'schema_viewer', 'oxygen')):
        return render(request, "schema_viewer/oxygen/" + file_name)
    else:
        message = "The oxygen documentation file associated to the request template is not available. " \
                  "Please contact your administrator for further information."
        add_message(request, WARNING, message)
        return redirect(reverse("xsd_viewer"),  locals())


def sandbox_viewer(request):
    user = request.user.id
    request.session['curate_edit'] = False

    template_id = request.GET.get("id", None)
    if template_id is None:
        message = "The template doesn't exist anymore."
        add_message(request, WARNING, message)
        return redirect(reverse("xsd_viewer"), locals())
    request.session['currentTemplateID'] = template_id
    request.session.modified = True
    request.session['xmlDocTree'] = etree.tostring(
        etree.parse(
            BytesIO(
                Template.objects.get(pk=template_id).content.encode('utf-8')
            )
        )
    )

    list_names = FormData.objects.values_list("name")

    form_name = "form_sandbox" + str(ObjectId())
    while form_name in list_names:
        form_name = "form_sandbox" + str(ObjectId())
    new_form = NewForm(request.POST)
    form_data = FormData(user=str(user), template=template_id, name=form_name)
    form_data.save()
    form_data_sb = FormDataSandbox()
    form_data_sb.form_data = form_data
    form_data_sb.save()
    request.session['curateFormData'] = str(form_data.id)

    context = {
        'edit': True,
        'sandbox': True,
        'curate_form': ['new'],
        'document_name': [form_name]
    }

    if 'form_id' in request.session:
        del request.session['form_id']

    template = loader.get_template('curate/curate_enter_data.html')
    return HttpResponse(template.render(context))
