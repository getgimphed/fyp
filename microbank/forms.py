import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from microbank.models import Client
from material import Layout, Row, Column, Fieldset, Span2, Span3, Span4, Span5, Span6, Span10

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    layout = Layout('username', 'email',
                    Row('password', 'password_confirm'),
                    Fieldset('Pesonal details',
                             Row('first_name', 'last_name')))
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )

class ApplyForLoanForm(forms.Form):
    address = forms.CharField(max_length=255, required=True, help_text='H no 9, Jodhpur...')
    mobile = forms.CharField(max_length=11, required=True, help_text='xxxxx xxxx.')
    singleOrGroup = forms.IntegerField(help_text='Want to take Loan Single (0) or in Group (1)?')

    layout = Layout('address', 'mobile','singleOrGroup')
    class Meta:
        fields = ('address', 'mobile', 'singleOrGroup',)
