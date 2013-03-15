from django import forms
from solutioner.comments.models import Comment


class AddComment(forms.Form):

  message = forms.CharField(widget=forms.Textarea, max_length=1000, required=True, error_messages={'required': '*'})
  message.widget.attrs = {'class': 'post_desk'}
  
  class Meta:
    model = Comment
