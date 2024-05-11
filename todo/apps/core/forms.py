from django import forms

from todo.apps.core import models


class ReportForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields['theme'].required = True

    class Meta:
        model = models.Report
        fields = ('theme', 'content')
        widgets = {}
