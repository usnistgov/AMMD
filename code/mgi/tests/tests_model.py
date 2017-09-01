################################################################################
#
# File Name: tests_models.py
# Application: mgi
# Description:
#
# Author: Xavier SCHMITT
#         xavier.schmitt@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################
from testing.models import RegressionTest
from mgi.models import Template, TemplateVersion, Type, TypeVersion, XMLdata, FormData, delete_template_and_version, delete_type_and_version, delete_template, delete_type

class tests_model(RegressionTest):

    def test_delete_template_and_version(self):
        template = self.createTemplate()
        delete_template_and_version(str(template.id))
        self.assertEquals(len(Template.objects()), 0)
        self.assertEquals(len(TemplateVersion.objects()), 0)

    def test_delete_type_and_version(self):
        self.assertEquals(len(Type.objects()), 0)
        self.assertEquals(len(TypeVersion.objects()), 0)
        type = self.createType()
        delete_type_and_version(str(type.id))
        self.assertEquals(len(Type.objects()), 0)
        self.assertEquals(len(TypeVersion.objects()), 0)

    def test_delete_template_no_dependencies(self):
        template = self.createTemplate()
        delete_template(str(template.id))
        self.assertEquals(len(Template.objects()), 0)
        self.assertEquals(len(TemplateVersion.objects()), 0)

    def test_delete_template_with_dependencies(self):
        template = self.createTemplate()
        XMLdata(schemaID=str(template.id), title='testRecord', xml='<test>test xmldata</test>').save()
        FormData(template=str(template.id), name='testFormData', xml_data='testest', user=str(1)).save()
        listDependencies = delete_template(str(template.id))
        self.assertEquals(len(Template.objects()), 1)
        self.assertEquals(len(TemplateVersion.objects()), 1)
        self.assertEquals(listDependencies, 'testFormData, testRecord')

    def test_delete_type_no_dependencies(self):
        type = self.createType()
        delete_type(str(type.id))
        self.assertEquals(len(Type.objects()), 0)
        self.assertEquals(len(TypeVersion.objects()), 0)

    def test_delete_type_with_dependencies(self):
        type = self.createType()
        Type(title='testType', filename='filename', content='content', hash='hash', dependencies=[str(type.id)]).save()
        Template(title='testTemplate', filename='filename', content='content', hash='hash', dependencies=[str(type.id)]).save()
        listDependencies = delete_type(str(type.id))
        self.assertEquals(len(Type.objects()), 2)
        self.assertEquals(len(TypeVersion.objects()), 1)
        self.assertEquals(listDependencies, 'testType, testTemplate')




