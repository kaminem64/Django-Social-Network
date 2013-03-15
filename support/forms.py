from django import forms
from solutioner.support.models import Message


class SupportMessage(forms.Form):

  fullname = forms.CharField(label="Full Name", max_length=100, required=True, error_messages ={'required': '*'})
  fullname.widget.attrs = {'class': 'general_input input100','title': 'Full Name'}

  emailaddress = forms.EmailField(label="Email Address", max_length=75, required=True, error_messages ={'required': '*'})
  emailaddress.widget.attrs = {'class': 'general_input input100','title': 'Email Address'}

  subject = forms.CharField(label="Subject", max_length=100, required=True, error_messages ={'required': '*'})
  subject.widget.attrs = {'class': 'general_input input100','title': 'Subject'}

  message = forms.CharField(widget=forms.Textarea, required=True, error_messages={'required': '*'})
  message.widget.attrs = {'class': 'general_input support_message'}
  
  class Meta:
    model = Message


class SupportMessageUsers(forms.Form):

  subject = forms.CharField(label="Subject", max_length=100, required=True, error_messages ={'required': '*'})
  subject.widget.attrs = {'class': 'general_input input100','title': 'Subject'}

  message = forms.CharField(widget=forms.Textarea, required=True, error_messages={'required': '*'})
  message.widget.attrs = {'class': 'general_input support_message'}
  
  class Meta:
    model = Message
