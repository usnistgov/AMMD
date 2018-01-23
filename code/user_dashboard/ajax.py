################################################################################
#
# File Name: ajax.py
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
from mgi.settings import BLOB_HOSTER, BLOB_HOSTER_URI, BLOB_HOSTER_USER, BLOB_HOSTER_PSWD, MDCS_URI
from utils.BLOBHoster.BLOBHosterFactory import BLOBHosterFactory
from django.http import HttpResponse
from mgi.models import Template, XMLdata, Type, delete_template, delete_type
from django.contrib import messages
import lxml.etree as etree
from io import BytesIO
import json
from mgi.common import send_mail_to_managers
import os
from django.utils.importlib import import_module
settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)
MDCS_URI = settings.MDCS_URI


################################################################################
#
# Function Name: edit_information(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Edit information of an object (template or type)
#
################################################################################
@login_required(login_url='/login')
def edit_information(request):
    object_id = request.POST['objectID']
    object_type = request.POST['objectType']
    new_name = request.POST['newName']
    new_filename = request.POST['newFilename']

    if object_type == "Template":
        object = Template.objects.get(pk=object_id)
        testFilenameObjects = Template.objects(filename=new_filename.strip())
        testNameObjects = Template.objects(title=new_name.strip())
    else:
        object = Type.objects.get(pk=object_id)
        testFilenameObjects = Type.objects(filename=new_filename.strip())
        testNameObjects = Type.objects(title=new_name.strip())

    if len(testNameObjects) == 1: # 0 is ok, more than 1 can't happen
            #check that the type with the same filename is the current one
        if testNameObjects[0].id != object.id:
            response_dict = {'name': 'True'}
            return HttpResponse(json.dumps(response_dict), content_type='application/javascript')

    if len(testFilenameObjects) == 1: # 0 is ok, more than 1 can't happen
            #check that the type with the same filename is the current one
        if testFilenameObjects[0].id != object.id:
            response_dict = {'filename': 'True'}
            return HttpResponse(json.dumps(response_dict), content_type='application/javascript')

    object.title = new_name.strip()
    object.filename = new_filename.strip()
    object.save()

    return HttpResponse(json.dumps({}), content_type='application/javascript')

################################################################################
#
# Function Name: delete_object(request)
# Inputs:        request -
# Outputs:       JSON data
# Exceptions:    None
# Description:   Delete an object (template or type).
#
################################################################################
@login_required(login_url='/login')
def delete_object(request):
    print 'BEGIN def delete_object(request)'
    object_id = request.POST['objectID']
    object_type = request.POST['objectType']

    listObject = ''
    if object_type == "Template":
        listObject = delete_template(object_id)

    elif object_type == "Type":
        listObject = delete_type(object_id)

    else:
        url = request.POST['url']
        bh_factory = BLOBHosterFactory(BLOB_HOSTER, BLOB_HOSTER_URI, BLOB_HOSTER_USER, BLOB_HOSTER_PSWD, MDCS_URI)
        blob_hoster = bh_factory.createBLOBHoster()
        blob_hoster.delete(url+"/rest/blob?id="+object_id)
        messages.add_message(request, messages.INFO, 'File deleted with success.')
        print 'END def delete_object(request)'
        return HttpResponse(json.dumps({}), content_type='application/javascript')

    if listObject is not None and listObject != '':
        response_dict = {object_type: listObject}
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    else:
        messages.add_message(request, messages.INFO, object_type+' deleted with success.')

    print 'END def delete_object(request)'
    return HttpResponse(json.dumps({}), content_type='application/javascript')

################################################################################
#
# Function Name: dashboard_toXML(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Page that display XML
#
################################################################################
@login_required(login_url='/login')
def dashboard_toXML(request):
    xmlString = request.POST['xml']

    xsltPath = os.path.join(settings.SITE_ROOT, 'static', 'resources', 'xsl', 'xsd2html.xsl')
    xslt = etree.parse(xsltPath)
    transform = etree.XSLT(xslt)
    xmlTree = ""
    if (xmlString != ""):

        dom = etree.parse(BytesIO(xmlString.encode('utf-8')))
        annotations = dom.findall(".//{http://www.w3.org/2001/XMLSchema}annotation")
        for annotation in annotations:
            annotation.getparent().remove(annotation)
        newdom = transform(dom)
        xmlTree = str(newdom)

    response_dict = {'XMLHolder': xmlTree}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
#
# Function Name: delete_result(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Delete an XML document from the database
#
################################################################################
def delete_result(request):
    result_id = request.GET['result_id']

    try:
        XMLdata.delete(result_id)
    except:
        # XML can't be found
        pass

    return HttpResponse(json.dumps({}), content_type='application/javascript')

################################################################################
#
# Function Name: update_publish(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Publish and update the publish date of an XMLdata
#
################################################################################
def update_publish(request):
    XMLdata.update_publish(request.GET['result_id'])
    resource = XMLdata.get(request.GET['result_id'])

    # Send mail to the user and the admin
    context = {'URI': MDCS_URI,
               'title': resource['title'],
               'publicationdate': resource['publicationdate'],
               'user': request.user.username}

    send_mail_to_managers(subject='Resource Published',
                                pathToTemplate='dashboard/email/resource_published.html',
                                context=context)
    return HttpResponse(json.dumps({}), content_type='application/javascript')

################################################################################
#
# Function Name: update_unpublish(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Unpublish an XMLdata
#
################################################################################
def update_unpublish(request):
    XMLdata.update_unpublish(request.GET['result_id'])
    return HttpResponse(json.dumps({}), content_type='application/javascript')

################################################################################
#
# Function Name: show_people_records(request) // dashboard_otherusers_records
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Display other users records
#
################################################################################
def ddashboard_otherusers_records(request):
    json_content = ''
    return HttpResponse(json_content, HTTP_200_OK)

def dasshboard_otherusers_records(request):
    template = loader.get_template('dashboard/my_dashboard_my_records.html')
    query = {}

    query['iduser'] = str(request.user.id)
    userXmlData = sorted(XMLdata.find(query), key=lambda data: data['lastmodificationdate'], reverse=True)

    templates_used = sorted(Template.find(query), key=lambda data: data['content'], reverse=True)
    user_form = UserForm(request.user)

    otherUsers = User.objects.all()
    idotherUsers = User.objects.only('_id')
    otherUXMLdatas = [] # sorted(XMLdata.find(query), key=lambda data: data['lastmodificationdate'], reverse=True)

    otherUXMLd =[]
    context = RequestContext(request, {'XMLdatas': userXmlData,
                                       # 'ispublished': ispublished,
                                       'user_form': user_form,
                                       'Templates': templates_used,
                                       'OtherUXMLdatas': otherUXMLdatas,
                                       'OtherUsers': otherUsers,
                                       'IdotherUsers':idotherUsers,
                                       'OtherUXMLd' : otherUXMLd
    })
    #If the user is an admin, we get records for other users
    if request.user.is_staff:
        #Get user name for admin
        usernames = dict((str(x.id), x.username) for x in User.objects.all())
        query['iduser'] = {"$ne": str(request.user.id)}
        otherUsersXmlData = sorted(XMLdata.find(query), key=lambda data: data['lastmodificationdate'], reverse=True)
        context.update({'OtherUsersXMLdatas': otherUsersXmlData, 'usernames': usernames})
    print "{{{{{{-}}}}}"
    print otherUsersXmlData
    print type(otherUsersXmlData)
    return HttpResponse(template.render(context))
