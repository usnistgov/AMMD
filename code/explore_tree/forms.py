from django import forms
from mgi.models import TemplateVersion


class ModelChoiceInput(forms.Form):
    """ Form to open an existing form
    """
    values = forms.ModelChoiceField(label='Select associated template',
                                    required=True,
                                    queryset=TemplateVersion.objects.all())

