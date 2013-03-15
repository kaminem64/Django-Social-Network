from django import forms
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from solutioner.categories.models import Category
from lxml.html import fromstring
from lxml import etree
from lxml.html.clean import Cleaner
import lxml
from lxml.html import clean

def clean_html(html):
  html = lxml.html.fromstring(html)
  #clean.defs.safe_attrs=frozenset(['href','src'])
  cleaner = clean.Cleaner(allow_tags=['h1','h2','h3','h4','h5','h6','p','div','span','pre','code','img','a','br'], safe_attrs_only=True, 
remove_unknown_tags=False)
  cleaned = cleaner.clean_html(html)
  return lxml.html.tostring(cleaned)


class AddSolution(forms.Form):
  def __init__(self, *args, **kwargs):
    super(AddSolution, self).__init__(*args, **kwargs)
    self.fields['problem_desc'].label = "Problem Description (optional)"

  problem = forms.CharField(max_length=200, error_messages={'required': '*'})
  problem.widget.attrs = {'class': 'problem_input'}
  problem_desc = forms.CharField(widget=forms.Textarea, required=False)
  problem_desc.widget.attrs = {'class': 'problem_desc_textarea'}
  category =  forms.ModelChoiceField(queryset=Category.objects.all(),initial='1', error_messages={'required': '*'})
  #category.widget.attrs = {'class': 'uiselectmenu'}
  solution = forms.CharField(widget=forms.Textarea, error_messages={'required': '*'})
  solution.widget.attrs = {'class': 'solution_textarea'}
  tags = forms.CharField(required=False, max_length = 10000, widget=forms.HiddenInput)
  
  def clean_title (self):
    title = self.cleaned_data['title']
    if len(title) > 200:
      raise forms.ValidationError("Title can't have more than 10000 characters")
    return title
 
  def clean_problem_desc (self):
    problem_desc = self.cleaned_data['problem_desc']
    if problem_desc == '<br>':
      problem_desc = ''
    if problem_desc:
      try:
        return clean_html(problem_desc)
      except:
        raise forms.ValidationError("*")
    else:
      return problem_desc
  
  def clean_solution (self):
    solution = self.cleaned_data['solution']
    if solution == '<br>':
      solution = ''
      raise forms.ValidationError("*")
    if solution:
      return clean_html(solution)
    else:
      return solution
