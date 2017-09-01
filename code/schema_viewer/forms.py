from mongoengine import DoesNotExist

from mgi.models import Template
from schema_viewer.models import TemplateSchemaViewer
from django.forms import Form, Select, RadioSelect, ModelChoiceField


class FormDefaultTemplate(Form):
    """
    Form to get all the visible templates, with as first choice, the default template if it exists.
    """

    # Schema showed in the form,
    schema = ModelChoiceField(
        label='Schema',
        required=True,
        queryset=Template.objects.all(),
    )

    def set_default(self, widget="select", empty_label=True):
        """
        Populate the form with the visible template, and set the default one if it exists.

        :param widget: name of the widget used to represent the form (default: select):
            _"select": Select
            _"radio": RadioSelect

        :param empty_label: True is an empty label has to be created, False else. (default: True)
        """

        # Set the widget
        if widget == "radio":
            self.fields["schema"].widget = RadioSelect()
        else:
            self.fields["schema"].widget = Select()

        # Populate the form with all the visible templates
        not_visible_templates_id = TemplateSchemaViewer.get_id_not_visible_template()
        self.fields["schema"].queryset = Template.objects.filter(pk__nin=not_visible_templates_id)

        # Create an empty label is needed
        if empty_label:
            self.fields["schema"].empty_label = None
        else:
            self.fields["schema"].empty_label = 'Schema...'

        # Set the default template if it exists
        try:
            self.initial['schema'] = TemplateSchemaViewer.objects.get(is_default=True).template
        except DoesNotExist:
            pass
