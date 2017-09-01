from datetime import datetime

from mongoengine import ReferenceField, BooleanField, Document, CASCADE, DateTimeField

from mgi.models import Template, FormData


class TemplateSchemaViewer(Document):
    """
    Collection to represent, all the attributes related to a template used by the schema viewer.

    Template: The selected template.
    is_default: True if the template is the default one.
    is_visible: True if the template has to be shown in the different forms.
    """
    template = ReferenceField(Template, required=True, reverse_delete_rule=CASCADE)
    is_default = BooleanField(default=False, required=True)
    is_visible = BooleanField(default=True, required=True)

    @staticmethod
    def get_id_not_visible_template():
        """
        Get all the visible template IDs.

        :return: List of visible template IDs.
        """
        not_visible_templates_id = list()
        not_visible_templates = list(TemplateSchemaViewer.objects.filter(is_visible=False).values_list('template'))

        for not_visible_template in not_visible_templates:
            not_visible_templates_id.append(str(not_visible_template.id))

        return not_visible_templates_id


class FormDataSandbox(Document):
    form_data = ReferenceField(FormData, reverse_delete_rule=CASCADE)
    timestamp = DateTimeField(default=datetime.now)
