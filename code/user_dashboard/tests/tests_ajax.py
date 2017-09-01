################################################################################
#
# File Name: tests_ajax.py
# Application: dashboard
# Description:
#
# Author: Xavier SCHMITT
#         xavier.schmitt@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from testing.models import RegressionTest
from mgi.models import Template, Type, XMLdata, TemplateVersion, TypeVersion, Status
import json

class tests_user_dashboard_ajax(RegressionTest):

    def test_edit_information_template(self):
        template = self.createTemplate()
        url='/dashboard/edit_information'
        data = {'objectID': template.id, 'objectType': 'Template', 'newName': ' othername', 'newFilename': 'otherfilename '}
        r = self.doRequestPostAdminClientLogged(url=url, data=data)
        modifiedTemplate = Template.objects.get(pk=template.id)
        self.assertEquals('otherfilename', modifiedTemplate.filename)
        self.assertEquals('othername', modifiedTemplate.title)

    def test_edit_information_type(self):
        type = self.createType()
        url='/dashboard/edit_information'
        data = {'objectID': type.id, 'objectType': 'Type', 'newName': 'othername ', 'newFilename': ' otherfilename'}
        r = self.doRequestPostAdminClientLogged(url=url, data=data)
        modifiedType = Type.objects.get(pk=type.id)
        self.assertEquals('otherfilename', modifiedType.filename)
        self.assertEquals('othername', modifiedType.title)

    def test_edit_information_template_same_name(self):
        self.createTemplate(title='othername')
        template = self.createTemplate()
        url = '/dashboard/edit_information'
        data = {'objectID': template.id, 'objectType': 'Template', 'newName': ' othername', 'newFilename': 'otherfilename '}
        r = self.doRequestPostAdminClientLogged(url=url, data=data)
        modifiedTemplate = Template.objects.get(pk=template.id)
        self.assertNotEquals('otherfilename', modifiedTemplate.filename)
        self.assertNotEquals('othername', modifiedTemplate.title)
        self.assertEquals('test', modifiedTemplate.filename)
        self.assertEquals('test', modifiedTemplate.title)
        result = json.loads(r.content)
        self.assertEquals('True', result.get('name'))

    def test_edit_information_type_same_filename(self):
        self.createType(filename='otherfilename')
        type = self.createType()
        url = '/dashboard/edit_information'
        data = {'objectID': type.id, 'objectType': 'Type', 'newName': 'othername ', 'newFilename': ' otherfilename'}
        r = self.doRequestPostAdminClientLogged(url=url, data=data)
        modifiedType = Type.objects.get(pk=type.id)
        self.assertNotEquals('otherfilename', modifiedType.filename)
        self.assertNotEquals('othername', modifiedType.title)
        self.assertEquals('test', modifiedType.filename)
        self.assertEquals('test', modifiedType.title)
        result = json.loads(r.content)
        self.assertEquals('True', result.get('filename'))

    def test_delete_result(self):
        id = self.createXMLData()
        self.assertIsNotNone(XMLdata.get(id))
        self.assertEquals(Status.ACTIVE, XMLdata.get(id)['status'])
        url = '/dashboard/delete_result'
        data = {'result_id': str(id)}
        r = self.doRequestGetAdminClientLogged(url=url, data=data)
        self.assertIsNotNone(XMLdata.get(id))
        self.assertEquals(Status.DELETED, XMLdata.get(id)['status'])

    def test_update_publish(self):
        id = self.createXMLData()
        self.assertEquals(False, XMLdata.get(id)['ispublished'])
        url = '/dashboard/update_publish'
        data = {'result_id': str(id)}
        r = self.doRequestGetAdminClientLogged(url=url, data=data)
        self.assertEquals(True, XMLdata.get(id)['ispublished'])

    def test_update_unpublish(self):
        id = self.createXMLData(ispublished=True)
        self.assertEquals(True, XMLdata.get(id)['ispublished'])
        url = '/dashboard/update_unpublish'
        data = {'result_id': str(id)}
        r = self.doRequestGetAdminClientLogged(url=url, data=data)
        self.assertEquals(False, XMLdata.get(id)['ispublished'])

    def test_delete_object_template(self):
        template = self.createTemplate()
        url = '/dashboard/delete_object'
        data = {'objectID': template.id, 'objectType': 'Template'}
        r = self.doRequestPostAdminClientLogged(url=url, data=data)
        self.assertEquals(0, len(Template.objects()))
        self.assertEquals(0, len(TemplateVersion.objects()))

    def test_delete_object_type(self):
        type = self.createType()
        url = '/dashboard/delete_object'
        data = {'objectID': type.id, 'objectType': 'Type'}
        r = self.doRequestPostAdminClientLogged(url=url, data=data)
        self.assertEquals(0, len(Type.objects()))
        self.assertEquals(0, len(TypeVersion.objects()))

    def test_delete_object_template_with_dependencie(self):
        self.assertEquals(0, len(Template.objects()))
        template = self.createTemplate()
        self.assertEquals(1, len(Template.objects()))
        self.createXMLData(schemaID=template.id)
        url = '/dashboard/delete_object'
        data = {'objectID': template.id, 'objectType': 'Template'}
        r = self.doRequestPostAdminClientLogged(url=url, data=data)
        self.assertEquals(1, len(Template.objects()))
        self.assertEquals(1, len(TemplateVersion.objects()))

    def test_delete_object_type_with_dependencie(self):
        type = self.createType()
        otherType = self.createType()
        otherType.dependencies = [str(type.id)]
        otherType.save()
        url = '/dashboard/delete_object'
        data = {'objectID': type.id, 'objectType': 'Type'}
        r = self.doRequestPostAdminClientLogged(url=url, data=data)
        self.assertIsNotNone(Type.objects(pk=type.id).get())


