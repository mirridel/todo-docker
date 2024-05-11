from allauth.account.forms import SignupForm
from django import forms

from todo.apps.custom_account import models


class StaffForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['phone_number'].required = True

    class Meta:
        model = models.User
        fields = ['first_name', 'last_name', 'phone_number']
        widgets = {'phone_number': forms.TextInput(attrs={'type': 'tel'}), }


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=200, label='Имя', widget=forms.TextInput(attrs={'placeholder': 'Имя'}))
    last_name = forms.CharField(max_length=200, label='Фамилия', widget=forms.TextInput(attrs={'placeholder': 'Фамилия'}))
    phone_number = forms.CharField(max_length=12, label='Телефон', widget=forms.TextInput(attrs={'placeholder': 'Телефон'}))

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.phone_number = self.cleaned_data['first_name']
        user.phone_number = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        user.save()
        return user
