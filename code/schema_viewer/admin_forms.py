from django.forms import Form, FileField, RadioSelect, CharField, BooleanField
from schema_viewer.forms import FormDefaultTemplate


class FormUnzip(FormDefaultTemplate):
    """
    Form to associate <oxygen> zip file with a template
    """

    # Zip file to be associated with the schema
    zip_file = FileField(label='Oxygen zip file', required=True, allow_empty_file=False)

    def set_default(self, widget="select", empty_label=True):
        super(FormUnzip, self).set_default(widget=widget, empty_label=empty_label)


class FormManageVisibilityDefault(Form):
    """
    Form to set the attributes for the templates use by the schema viewer as default and visible
    """

    # linked schema
    schema_name = CharField(label="Schema name")

    # Visible attribute
    is_visible = BooleanField(label="Is visible",
                              initial=True,
                              widget=RadioSelect(
                                  choices=[
                                      (True, 'Is visible'),
                                      (False, 'Is not visible')
                                  ],
                                  attrs={
                                      'class': "class_visible"
                                  }
                              ),
                              required=False
                              )

    # Default attribute
    is_default = BooleanField(label="Is default",
                              initial=False,
                              widget=RadioSelect(
                                  choices=[
                                      (True, 'Is default'),
                                      (False, 'Is not default')
                                  ],
                                  attrs={
                                      'class': "class_default"
                                  }
                              ),
                              required=False
                              )

