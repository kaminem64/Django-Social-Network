from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from solutioner.users.models import User as User_info
from solutioner.users.models import NotificationSettings
from solutioner.scores.models import Score as User_score
from solutioner.solutions.models import Solution
from rbac.models import RBACRole, RBACOperation, RBACGenericPermission
from django.conf import settings
from solutioner import captcha
import re

class LoginForm(forms.Form):
  username = forms.CharField(label="Username or Email", max_length=50, error_messages ={'required': 'Required'})
  username.widget.attrs = {'class': 'general_input','title': 'Username or Email'}
  password = forms.CharField(label="Password", widget=forms.PasswordInput, max_length=50, error_messages ={'required': 'Required'})
  password.widget.attrs = {'class': 'general_input','title': 'Password'}
  
class ChangePasswordForm(forms.Form):
  def __init__(self, *args, **kwargs):
    self.request = kwargs.pop('request', None)
    super(ChangePasswordForm, self).__init__(*args, **kwargs)

  oldpassword = forms.CharField(label="Password", widget=forms.PasswordInput, max_length=50, error_messages ={'required': 'Required'})
  newpassword = forms.CharField(label="New Password", widget=forms.PasswordInput, max_length=50, error_messages ={'required': 'Required'})
  cnewpassword = forms.CharField(label="Re-New Password", widget=forms.PasswordInput, max_length=50, error_messages ={'required': 'Required'})

  def clean_oldpassword(self):
    oldpassword = self.cleaned_data['oldpassword']
    if not auth.authenticate(username=self.request.user.username, password=oldpassword):
      raise forms.ValidationError("Wrong password!")
    return oldpassword
    
  def clean_cnewpassword(self):
    newpassword = self.cleaned_data.get("newpassword", "")
    cnewpassword = self.cleaned_data["cnewpassword"]
    if newpassword != cnewpassword:
      raise forms.ValidationError("Passwords doesn't match")
    if len(cnewpassword)< 8:
      raise forms.ValidationError("Password must have atleast 8 characters")
    return cnewpassword
    
  def save(self, request):
    user = User.objects.get(username=request.user)
    user.set_password(self.cleaned_data['cnewpassword'])
    user.save()
    return user


class RegisterCaptchaForm(forms.Form):
  def __init__(self, *args, **kwargs):
    self.request = kwargs.pop('request', None)
    super(RegisterCaptchaForm, self).__init__(*args, **kwargs)
  recaptcha_challenge = forms.CharField(label="recaptcha_challenge", widget=forms.HiddenInput, required=False)
  recaptcha_response = forms.CharField(label="recaptcha_response", widget=forms.HiddenInput, required=False)
  recaptcha_meta = forms.CharField(label="recaptcha_meta", widget=forms.HiddenInput, required=False)
  terms_check = forms.BooleanField(required=True, error_messages ={'required': 'You must agree to Terms before you can use the Service'})
  
  
  def clean(self):
    cleaned_data = self.cleaned_data
    try:
      self.recaptcha_challenge = self.request.POST['recaptcha_challenge_field']
      self.recaptcha_response = self.request.POST['recaptcha_response_field']
      self.recaptcha_meta = self.request.META['REMOTE_ADDR']
    except:
      x = None
    captcha_check = captcha.submit(self.recaptcha_challenge, self.recaptcha_response, settings.RECAPTCHA_PRIVATE_KEY, self.recaptcha_meta)
    captcha_check = not captcha_check.is_valid
    if captcha_check:
      raise forms.ValidationError(self.recaptcha_challenge)
    return cleaned_data

class RegisterForm(forms.Form):
  username = forms.CharField(label="Username", max_length=50, error_messages ={'required': 'Required'})
  username.widget.attrs = {'class': 'general_input','title': 'Username'}
  
  password = forms.CharField(label="Password", widget=forms.PasswordInput, max_length=50, error_messages ={'required': 'Required'})
  password.widget.attrs = {'class': 'general_input','title': 'Password'}
  
  cpassword = forms.CharField(label="Re-Password", widget=forms.PasswordInput, max_length=50, error_messages ={'required': 'Required'})
  cpassword.widget.attrs = {'class': 'general_input','title': 'Re-Password'}
  
  emailaddress = forms.EmailField(label="Email Address", max_length=75, required=True, error_messages ={'required': 'Required'})
  emailaddress.widget.attrs = {'class': 'general_input','title': 'Email Address'}
  
  firstname = forms.CharField(label="First Name", max_length=20, required=True, error_messages ={'required': 'Required'})
  firstname.widget.attrs = {'class': 'general_input','title': 'First Name'}
  
  lastname = forms.CharField(label="Last Name", max_length=40, required=True, error_messages ={'required': 'Required'})
  lastname.widget.attrs = {'class': 'general_input','title': 'Last Name'}
  
  class Meta:
    model = User
    fields = ("username",)

  def clean_username(self):
    username = self.cleaned_data.get("username", "")
    try:
      username.decode()
      if not re.match("^[A-Za-z0-9_.]+$", username):
        raise
    except:
      raise forms.ValidationError("a to z letters, underscore, and dot are allowed for username")
    if username[0] == '.' or username[0] == '_' or username[-1] == '.' or username[-1] == '_':
      raise forms.ValidationError("first and last character of username cann't be dot or underscore")
    dup_user = User.objects.filter(username=username).count()
    if dup_user:
      raise forms.ValidationError("The entered username is taken, please try another username.")
    return username
    
  def clean_cpassword(self):
    password = self.cleaned_data.get("password", "")
    cpassword = self.cleaned_data["cpassword"]
    if password != cpassword:
      raise forms.ValidationError("Passwords doesn't match")
    if len(cpassword)< 8:
      raise forms.ValidationError("Password must have atleast 8 characters")
    return cpassword
    
  def clean_emailaddress(self):
    emailaddress = self.cleaned_data.get("emailaddress", "")
    dup_emailaddress = User.objects.filter(email=emailaddress).count()
    if dup_emailaddress:
      raise forms.ValidationError("There's already one Solutioner account associated with this email address.")
    return emailaddress

  def save(self):
    user = User.objects.create_user(username=self.cleaned_data['username'], password=self.cleaned_data['password'], email=self.cleaned_data['emailaddress'])
    user.first_name = self.cleaned_data['firstname']
    user.last_name = self.cleaned_data['lastname']
    user.save()
    User_info.objects.create(user=user)
    User_score.objects.create(user=user)
    
    profilepicture_perm_role=RBACRole.objects.get(name='public')
    emailaddress_perm_role=RBACRole.objects.get(name='public')
    website_perm_role=RBACRole.objects.get(name='public')
    location_perm_role=RBACRole.objects.get(name='public')
    birthdate_perm_role=RBACRole.objects.get(name='public')
    view_desk_perm_role=RBACRole.objects.get(name='liker')
    post_desk_perm_role=RBACRole.objects.get(name='liker')
    add_comment_solution_perm_role=RBACRole.objects.get(name='liker')
    add_comment_solution_perm_role=RBACRole.objects.get(name='public')
    RBACGenericPermission.objects.create_permission(user, User, 'display_profilepicture', [RBACRole.objects.get(name=profilepicture_perm_role)])
    RBACGenericPermission.objects.create_permission(user, User, 'display_emailaddress', [RBACRole.objects.get(name=emailaddress_perm_role)])
    RBACGenericPermission.objects.create_permission(user, User_info, 'display_website', [RBACRole.objects.get(name=website_perm_role)])
    RBACGenericPermission.objects.create_permission(user, User_info, 'display_location', [RBACRole.objects.get(name=location_perm_role)])
    RBACGenericPermission.objects.create_permission(user, User_info, 'display_birthdate', [RBACRole.objects.get(name=birthdate_perm_role)])
    RBACGenericPermission.objects.create_permission(user, User, 'view_desk', [RBACRole.objects.get(name=view_desk_perm_role)])
    RBACGenericPermission.objects.create_permission(user, User, 'post_desk', [RBACRole.objects.get(name=post_desk_perm_role)])
    RBACGenericPermission.objects.create_permission(user, Solution, 'add_comment', [RBACRole.objects.get(name=add_comment_solution_perm_role)])
    RBACGenericPermission.objects.create_permission(user, Solution, 'view_comment', [RBACRole.objects.get(name=add_comment_solution_perm_role)])
    return user

GENDER_CHOICES = (
  ('N', '-'),
  ('M', 'Male'),
  ('F', 'Female'),
)
from solutioner.users.country_field import COUNTRIES2 as LOCATION_CHOICES


class EditProfileForm(forms.Form):
  profilepicture = forms.ImageField(label="Profile Picture", required=False, error_messages ={'invalid_image': 'Only images files are allowed'})
  firstname = forms.CharField(label="First Name", max_length=20, required=True, error_messages ={'required': 'Required'})
  firstname.widget.attrs = {'class': 'perm_charfield'}
  lastname = forms.CharField(label="Last Name", max_length=40, required=True, error_messages ={'required': 'Required'})
  lastname.widget.attrs = {'class': 'perm_charfield'}
  gender = forms.CharField(max_length=1, widget=forms.Select(choices=GENDER_CHOICES))
  gender.widget.attrs = {'class': 'uiselectmenu'}
  emailaddress = forms.EmailField(label="Email Address", max_length=75, required=True, error_messages ={'required': 'Required'})
  emailaddress.widget.attrs = {'class': 'perm_charfield'}
  website = forms.CharField(label="Website", max_length=100, required=False)
  website.widget.attrs = {'class': 'perm_charfield'}
  location = forms.CharField(max_length=3, widget=forms.Select(choices=LOCATION_CHOICES))
  location.widget.attrs = {'class': 'uiselectmenu perm_charfield'}
  birthdate = forms.CharField(label="Birth Date", max_length=10, required=False)
  birthdate.widget.attrs = {'class': 'perm_charfield'}
  profilepicture_perm =  forms.ModelChoiceField(queryset=RBACRole.objects.all(),initial='1', error_messages={'required': '*'})
  profilepicture_perm.widget.attrs = {'class': 'uiselectmenu'}
  gender_perm =  forms.ModelChoiceField(queryset=RBACRole.objects.all(),initial='1', error_messages={'required': '*'})
  gender_perm.widget.attrs = {'class': 'uiselectmenu'}
  emailaddress_perm =  forms.ModelChoiceField(queryset=RBACRole.objects.all(),initial='1', error_messages={'required': '*'})
  emailaddress_perm.widget.attrs = {'class': 'uiselectmenu'}
  website_perm =  forms.ModelChoiceField(queryset=RBACRole.objects.all(),initial='1', error_messages={'required': '*'})
  website_perm.widget.attrs = {'class': 'uiselectmenu'}
  location_perm =  forms.ModelChoiceField(queryset=RBACRole.objects.all(),initial='1', error_messages={'required': '*'})
  location_perm.widget.attrs = {'class': 'uiselectmenu'}
  birthdate_perm =  forms.ModelChoiceField(queryset=RBACRole.objects.all(),initial='1', error_messages={'required': '*'})
  birthdate_perm.widget.attrs = {'class': 'uiselectmenu'}

  def clean_profilepicture(self):
    image = self.cleaned_data['profilepicture']
    if image:
      if image._size > 1024*1024:
        raise forms.ValidationError("Too large (>1mb)")
      return image
  
  def save(self, request):
    user = User.objects.get(username=request.user)
    user.first_name = self.cleaned_data['firstname']
    user.last_name = self.cleaned_data['lastname']
    user.email = self.cleaned_data['emailaddress']

    profilepicture_perm_role=RBACRole.objects.get(name=unicode(self.cleaned_data['profilepicture_perm']))
    gender_perm_role=RBACRole.objects.get(name=unicode(self.cleaned_data['gender_perm']))
    emailaddress_perm_role=RBACRole.objects.get(name=unicode(self.cleaned_data['emailaddress_perm']))
    website_perm_role=RBACRole.objects.get(name=unicode(self.cleaned_data['website_perm']))
    location_perm_role=RBACRole.objects.get(name=unicode(self.cleaned_data['location_perm']))
    birthdate_perm_role=RBACRole.objects.get(name=unicode(self.cleaned_data['birthdate_perm']))
    
    RBACGenericPermission.objects.create_permission(user, User_info, 'display_profilepicture', [RBACRole.objects.get(name=profilepicture_perm_role)])
    RBACGenericPermission.objects.create_permission(user, User_info, 'display_gender', [RBACRole.objects.get(name=gender_perm_role)])
    RBACGenericPermission.objects.create_permission(user, User, 'display_emailaddress', [RBACRole.objects.get(name=emailaddress_perm_role)])
    RBACGenericPermission.objects.create_permission(user, User_info, 'display_website', [RBACRole.objects.get(name=website_perm_role)])
    RBACGenericPermission.objects.create_permission(user, User_info, 'display_location', [RBACRole.objects.get(name=location_perm_role)])
    RBACGenericPermission.objects.create_permission(user, User_info, 'display_birthdate', [RBACRole.objects.get(name=birthdate_perm_role)])

    user.save()
    user_info = User_info.objects.get(user=request.user)
    user_info.gender = self.cleaned_data['gender']
    user_info.website = self.cleaned_data['website']
    user_info.location = self.cleaned_data['location']
    if self.cleaned_data['profilepicture']:
      user_info.image = self.cleaned_data['profilepicture']
    if self.cleaned_data['birthdate'] != '':
      user_info.birthdate = self.cleaned_data['birthdate']
    user_info.save()
    return user
  
  
  
class PrivacySettings(forms.Form):
  view_desk_perm =  forms.ModelChoiceField(queryset=RBACRole.objects.all(),initial='1', error_messages={'required': '*'})
  view_desk_perm.widget.attrs = {'class': 'uiselectmenu'}
  post_desk_perm =  forms.ModelChoiceField(queryset=RBACRole.objects.all(),initial='1', error_messages={'required': '*'})
  post_desk_perm.widget.attrs = {'class': 'uiselectmenu'}
  add_comment_solution_perm =  forms.ModelChoiceField(queryset=RBACRole.objects.all(),initial='1', error_messages={'required': '*'})
  add_comment_solution_perm.widget.attrs = {'class': 'uiselectmenu'}
  view_comment_solution_perm =  forms.ModelChoiceField(queryset=RBACRole.objects.all(),initial='1', error_messages={'required': '*'})
  view_comment_solution_perm.widget.attrs = {'class': 'uiselectmenu'}

  def save(self, request):
    user = User.objects.get(username=request.user)

    view_desk_perm_role=RBACRole.objects.get(name=unicode(self.cleaned_data['view_desk_perm']))
    post_desk_perm_role=RBACRole.objects.get(name=unicode(self.cleaned_data['post_desk_perm']))
    add_comment_solution_perm_role=RBACRole.objects.get(name=unicode(self.cleaned_data['add_comment_solution_perm']))
    view_comment_solution_perm_role=RBACRole.objects.get(name=unicode(self.cleaned_data['view_comment_solution_perm']))

    RBACGenericPermission.objects.create_permission(user, User, 'view_desk', [RBACRole.objects.get(name=view_desk_perm_role)])
    RBACGenericPermission.objects.create_permission(user, User, 'post_desk', [RBACRole.objects.get(name=post_desk_perm_role)])
    RBACGenericPermission.objects.create_permission(user, Solution, 'add_comment', [RBACRole.objects.get(name=add_comment_solution_perm_role)])
    RBACGenericPermission.objects.create_permission(user, Solution, 'view_comment', [RBACRole.objects.get(name=view_comment_solution_perm_role)])

    return True
  
class NotificationSettingsForm(forms.Form):
  comment_on_desk =  forms.BooleanField(required=False)
  comment_on_solution = forms.BooleanField(required=False)


  def save(self, request):
    user = User.objects.get(username=request.user)

    notif_settings, c = NotificationSettings.objects.get_or_create(user=user)
    
    notif_settings.comment_on_desk=self.cleaned_data['comment_on_desk']
    notif_settings.comment_on_solution=self.cleaned_data['comment_on_solution']
    notif_settings.save()

    return notif_settings


