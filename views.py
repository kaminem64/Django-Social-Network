from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.core.context_processors import csrf
from django.template import RequestContext
import os
from django.contrib.auth.models import User, Group
from solutioner.users.models import User as User_info

from rbac.models import RBACRole, RBACOperation, RBACPermission, RBACGenericPermission, RBACGenericPermissionManager
from solutioner.events.models import Event
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from solutioner.events.views import get_home_events

def home(request):
  from solutioner.solutions.views import most_recent_sols, most_pop_sols
  from solutioner.users.forms import RegisterForm, LoginForm
  form_login = LoginForm()
  form_reg = RegisterForm(prefix='0')
  from solutioner.solutions.views import add_solution
  from solutioner.comments.views import add_comment
  form_add_solution = add_solution(request, JSON=False)
  form_add_comment = add_comment(request, object_inst=request.user, operation='post_desk', JSON=False)
  if request.user.is_authenticated():
    last_event, firstever_event = get_home_events(request, JSON=False)
  else:
    last_event, firstever_event = 1, 1

  return render_to_response('home.html', {'last_event': last_event, 'firstever_event': firstever_event, 'form_reg': form_reg, 'form_login': form_login, 'form_add_solution': form_add_solution, 'form_add_comment': form_add_comment, 'latestsols': most_recent_sols(), 'mostpops': most_pop_sols()}, context_instance=RequestContext(request))

def users_are_friends(user, target_user):
  if user == target_user:
    return True
  else:
    return False

def users_are_coworkers(user, target_user):
    return True

def get_user_roles(user, target_user):
    roles = []
    if users_are_friends(user, target_user):
        roles.append(RBACRole.objects.get(name='friends'))
    if users_are_coworkers(user, target_user):
        roles.append(RBACRole.objects.get(name='public'))
    return roles

def developers(request):
  return render_to_response('developers.html', {'title': 'Developers'}, context_instance=RequestContext(request))

def licenses(request):
  return render_to_response('licenses.html', {'title': 'Copyright Policy'}, context_instance=RequestContext(request))

def terms_of_service(request):
  return render_to_response('terms_of_service.html', {'title': 'Terms of Service'}, context_instance=RequestContext(request))

def privacy_policy(request):
  return render_to_response('privacy_policy.html', {'title': 'Privacy Policy'}, context_instance=RequestContext(request))    

def about_us(request):
  return render_to_response('about_us.html', {'title': 'About Us'}, context_instance=RequestContext(request))




