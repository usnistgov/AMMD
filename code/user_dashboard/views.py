################################################################################
#
# File Name: views.py
# Application: dashboard
# Description:
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Xavier SCHMITT
#         xavier.schmitt@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from django.contrib.auth.decorators import login_required
from django.conf import settings

from mgi.common import SCHEMA_NAMESPACE
from mgi.settings import BLOB_HOSTER, BLOB_HOSTER_URI, BLOB_HOSTER_USER, BLOB_HOSTER_PSWD, MDCS_URI
from utils.BLOBHoster.BLOBHosterFactory import BLOBHosterFactory
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.template import RequestContext, loader
from django.shortcuts import redirect
from mgi.models import Template, FormData, XMLdata, Type, Module
from admin_mdcs.forms import EditProfileForm, UserForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate
import lxml.etree as etree
from io import BytesIO
from mgi import common
import os
import xmltodict
from bson.objectid import ObjectId
import json
from password_policies.views import PasswordChangeFormView
from django.utils import timezone
from django.core.urlresolvers import reverse
from utils.DateTimeDecoder import DateTimeEncoder

################################################################################
#
# Function Name: my_profile(request)
# Inputs:        request -
# Outputs:       My Profile Page
# Exceptions:    None
# Description:   Page that allows to look at user's profile information
#
################################################################################
@login_required(login_url='/login')
def my_profile(request):
    template = loader.get_template('dashboard/my_profile.html')
    context = RequestContext(request, {
        '': '',
    })
    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: my_profile_edit(request)
# Inputs:        request -
# Outputs:       Edit My Profile Page
# Exceptions:    None
# Description:   Page that allows to edit a profile
#
################################################################################
@login_required(login_url='/login')
def my_profile_edit(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=request.user.id)
            if request.POST['username'] != user.username:
                try:
                    user = User.objects.get(username=request.POST['username'])
                    message = "A user with the same username already exists."
                    return render(request, 'my_profile_edit.html', {'form':form, 'action_result':message})
                except:
                    user.username = request.POST['username']

            user.first_name = request.POST['firstname']
            user.last_name = request.POST['lastname']
            user.email = request.POST['email']
            user.save()
            messages.add_message(request, messages.INFO, 'Profile information edited with success.')
            return redirect('/dashboard/my-profile')
    else:
        user = User.objects.get(id=request.user.id)
        data = {'firstname':user.first_name,
                'lastname':user.last_name,
                'username':user.username,
                'email':user.email}
        form = EditProfileForm(data)

    return render(request, 'dashboard/my_profile_edit.html', {'form': form})

################################################################################
#
# Function Name: dashboard_records(request)
# Inputs:        request -
# Outputs:       Dashboard - Records
# Exceptions:    None
# Description:   Dashboard - Records
#
################################################################################
@login_required(login_url='/login')
def dashboard_records(request):
    template = loader.get_template('dashboard/my_dashboard_my_records.html')
    query = {}
    # ispublished = request.GET.get('ispublished', None)
    #If ispublished not None, check if we want publish or unpublish records
    # if ispublished:
    #     ispublished = ispublished == 'true'
    #     query['ispublished'] = ispublished
    query['iduser'] = str(request.user.id)
    userXmlData = sorted(XMLdata.find(query), key=lambda data: data['lastmodificationdate'], reverse=True)
    #Add user_form for change owner
    user_form = UserForm(request.user)
    context = RequestContext(request, {'XMLdatas': userXmlData,
                                       # 'ispublished': ispublished,
                                       'user_form': user_form
    })
    #If the user is an admin, we get records for other users
    if request.user.is_staff:
        #Get user name for admin
        usernames = dict((str(x.id), x.username) for x in User.objects.all())
        query['iduser'] = {"$ne": str(request.user.id)}
        otherUsersXmlData = sorted(XMLdata.find(query), key=lambda data: data['lastmodificationdate'], reverse=True)
        context.update({'OtherUsersXMLdatas': otherUsersXmlData, 'usernames': usernames})

    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: dashboard_my_forms(request)
# Inputs:        request -
# Outputs:       Review forms page
# Exceptions:    None
# Description:   Page that allows to review user forms
#
################################################################################
@login_required(login_url='/login')
def dashboard_my_forms(request):
    template = loader.get_template('dashboard/my_dashboard_my_forms.html')
    # xml_data_id False if document not curated
    forms = FormData.objects(user=str(request.user.id), xml_data_id__exists=False,
                                 xml_data__exists=True).order_by('template')
    detailed_forms = []
    for form in forms:
        detailed_forms.append({'form': form, 'template_name': Template.objects().get(pk=form.template).title,
                               'user': form.user})
    user_form = UserForm(request.user)
    context = RequestContext(request, {'forms': detailed_forms,
                                       'user_form': user_form
    })
    #If the user is an admin, we get forms for other users
    if request.user.is_staff:
        #Get user name for admin
        usernames = dict((str(x.id), x.username) for x in User.objects.all())
        other_users_detailed_forms = []
        otherUsersForms = FormData.objects(user__ne=str(request.user.id), xml_data_id__exists=False,
                                                       xml_data__exists=True).order_by('template')
        for form in otherUsersForms:
            other_users_detailed_forms.append({'form': form,
                                               'template_name': Template.objects().get(pk=form.template).title,
                                               'user': form.user})
        context.update({'otherUsersForms': other_users_detailed_forms, 'usernames': usernames})

    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: dashboard_templates(request)
# Inputs:        request -
# Outputs:       Dashboard - Templates
# Exceptions:    None
# Description:   Dashboard - Templates
#
################################################################################
@login_required(login_url='/login')
def dashboard_templates(request):
    template = loader.get_template('dashboard/my_dashboard_my_templates_types.html')
    objects = Template.objects(user=str(request.user.id))
    context = RequestContext(request, {
                'objects': objects,
                'objectType': "Template"
            })
    #If the user is an admin, we get templates for other users
    if request.user.is_staff:
        #Get user name for admin
        usernames = dict((str(x.id), x.username) for x in User.objects.all())
        otherUsersObjects = Template.objects(user__not__in={str(request.user.id), None})
        context.update({'otherUsersObjects': otherUsersObjects, 'usernames': usernames})

    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: dashboard_types(request)
# Inputs:        request -
# Outputs:       Dashboard - Types
# Exceptions:    None
# Description:   Dashboard - Types
#
################################################################################
@login_required(login_url='/login')
def dashboard_types(request):
    template = loader.get_template('dashboard/my_dashboard_my_templates_types.html')
    objects = Type.objects(user=str(request.user.id))
    context = RequestContext(request, {
                'objects': objects,
                'objectType': "Type"
            })
    #If the user is an admin, we get templates for other users
    if request.user.is_staff:
        #Get user name for admin
        usernames = dict((str(x.id), x.username) for x in User.objects.all())
        otherUsersObjects = Type.objects(user__not__in={str(request.user.id), None})
        context.update({'otherUsersObjects': otherUsersObjects, 'usernames': usernames})

    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: dashboard_modules(request)
# Inputs:        request -
# Outputs:       User Request Page
# Exceptions:    None
# Description:   Page that allows to add modules to a template or a type
#
################################################################################
@login_required(login_url='/login')
def dashboard_modules(request):
    template = loader.get_template('dashboard/my_dashboard_modules.html')

    object_id = request.GET.get('id', None)
    object_type = request.GET.get('type', None)

    if object_id is not None:
        try:
            if object_type == 'Template':
                db_object = Template.objects.get(pk=object_id)
            elif object_type == 'Type':
                db_object = Type.objects.get(pk=object_id)
            else:
                raise AttributeError('Type parameter unrecognized')

            xslt_path = os.path.join(settings.SITE_ROOT, 'static', 'resources', 'xsl', 'xsd2html4modules.xsl')
            xslt = etree.parse(xslt_path)
            transform = etree.XSLT(xslt)

            dom = etree.parse(BytesIO(db_object.content.encode('utf-8')))
            annotations = dom.findall(".//{http://www.w3.org/2001/XMLSchema}annotation")
            for annotation in annotations:
                annotation.getparent().remove(annotation)
            newdom = transform(dom)
            xsd_tree = str(newdom)

            request.session['moduleTemplateID'] = object_id
            request.session['moduleTemplateContent'] = db_object.content

            namespaces = common.get_namespaces(BytesIO(str(db_object.content)))
            for prefix, url in namespaces.iteritems():
                if url == SCHEMA_NAMESPACE:
                    request.session['moduleDefaultPrefix'] = prefix
                    break

            context = RequestContext(request, {
                'xsdTree': xsd_tree,
                'modules': Module.objects,
                'object_type': object_type
            })

            return HttpResponse(template.render(context))
        except:
            return redirect('/')
    else:
        return redirect('/')


################################################################################
#
# Function Name: dashboard_files(request)
# Inputs:        request -
# Outputs:       Dashboard - Files
# Exceptions:    None
# Description:   Dashboard - Files
#
################################################################################
@login_required(login_url='/login')
def dashboard_files(request):
    template = loader.get_template('dashboard/my_dashboard_my_files.html')
    bh_factory = BLOBHosterFactory(BLOB_HOSTER, BLOB_HOSTER_URI, BLOB_HOSTER_USER, BLOB_HOSTER_PSWD, MDCS_URI)
    blob_hoster = bh_factory.createBLOBHoster()
    files = getListFiles(blob_hoster.find("metadata.iduser", str(request.user.id)))
    context = RequestContext(request, {
                'files': files,
                'url': MDCS_URI
    })
    #If the user is an admin, we get templates for other users
    if request.user.is_staff:
        #Get user name for admin
        usernames = dict((str(x.id), x.username) for x in User.objects.all())
        otherUsersFiles = getListFiles(blob_hoster.find("metadata.iduser", { '$ne': str(request.user.id) }))
        context.update({'otherUsersFiles': otherUsersFiles, 'usernames': usernames})

    return HttpResponse(template.render(context))


def getListFiles(listBlob):
    files = []
    for grid in listBlob:
        item = {'name': grid.name,
                'id': str(grid._id),
                'uploadDate': grid.upload_date,
                'user': grid.metadata['iduser']
                }
        files.append(item)
    return files


################################################################################
#
# Function Name: dashboard_detail_record
# Inputs:        request -
# Outputs:       Detail of a record
# Exceptions:    None
# Description:   Page that allows to see detail record from a selected record
#
################################################################################
@login_required(login_url='/login')
def dashboard_detail_record(request):
    template = loader.get_template('dashboard/my_dashboard_detail_record.html')
    record_id = request.GET['id']
    record_type = request.GET['type']

    if record_type == 'form':
        form_data = FormData.objects.get(pk=ObjectId(record_id))
        xml_string = form_data.xml_data.encode(encoding='UTF-8')
        title = form_data.name
        schema_id = form_data.template
    elif record_type == 'record':
        xml_string = XMLdata.get(record_id)
        title = xml_string['title']
        schema_id = xml_string['schema']
        xml_string = XMLdata.unparse(xml_string['content']).encode('utf-8')
    else:
        raise Exception("Unknow record type: " + str(record_type))

    xslt_path = os.path.join(settings.SITE_ROOT, 'static', 'resources', 'xsl', 'xml2html.xsl')
    xslt = etree.parse(xslt_path)
    transform = etree.XSLT(xslt)

    dom = ''

    # Check if a custom detailed result XSLT has to be used
    try:
        if xml_string != "":
            dom = etree.fromstring(xml_string)
            schema = Template.objects.get(pk=schema_id)

            if schema.ResultXsltDetailed:
                short_xslt = etree.parse(BytesIO(schema.ResultXsltDetailed.content.encode('utf-8')))
                short_transform = etree.XSLT(short_xslt)
                newdom = short_transform(dom)
            else:
                newdom = transform(dom)
        else:
            newdom = 'No data has been saved to this form yet.'
    except Exception as e:
        # We use the default one
        newdom = transform(dom)

    result = str(newdom)
    context = RequestContext(request, {
        'XMLHolder': result,
        'title': title,
        'type': record_type
    })

    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: change_owner_record(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Change the record owner
#
################################################################################
def change_owner_record(request):
    if 'recordID' in request.POST and 'userID' in request.POST:
        xml_data_id = request.POST['recordID']
        user_id = request.POST['userID']
        try:
            XMLdata.update_user(xml_data_id, user=user_id)
            messages.add_message(request, messages.INFO, 'Record Owner changed with success.')
        except Exception, e:
            return HttpResponseServerError({"Something wrong occurred during the change of owner."}, status=500)
    else:
        return HttpResponseBadRequest({"Bad entries. Please check the parameters."})

    return HttpResponse(json.dumps({}), content_type='application/javascript')

class UserDashboardPasswordChangeFormView(PasswordChangeFormView):
    def form_valid(self, form):
        messages.success(self.request, "Password changed with success.")
        return super(UserDashboardPasswordChangeFormView, self).form_valid(form)

    def get_success_url(self):
        """
Returns a query string field with a previous URL if available (Mimicing
the login view. Used on forced password changes, to know which URL the
user was requesting before the password change.)
If not returns the :attr:`~PasswordChangeFormView.success_url` attribute
if set, otherwise the URL to the :class:`PasswordChangeDoneView`.
"""
        checked = '_password_policies_last_checked'
        last = '_password_policies_last_changed'
        required = '_password_policies_change_required'
        now = json.dumps(timezone.now(), cls=DateTimeEncoder)
        self.request.session[checked] = now
        self.request.session[last] = now
        self.request.session[required] = False
        redirect_to = self.request.POST.get(self.redirect_field_name, '')
        if redirect_to:
            url = redirect_to
        elif self.success_url:
            url = self.success_url
        else:
            url = reverse('password_change_done')
        return url
