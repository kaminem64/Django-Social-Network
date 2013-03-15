from django.contrib import auth
from django.http import HttpResponseRedirect
from solutioner.users.forms import *
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from django import forms
from django.conf import settings
from solutioner import captcha
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
import re
from solutioner.users.models import User as User_info
from solutioner.users.models import NotificationSettings
from solutioner.scores.models import Score as User_score
from django.contrib.auth.models import User
from solutioner.solutions.models import Solution, Vote
from django.utils import simplejson
from solutioner.users.models import ExternalUser
from solutioner.categories.models import Category
from solutioner.rbac.models import RBACRole, RBACOperation, RBACGenericPermission, get_user_roles
from solutioner.solutions.forms import AddSolution
from solutioner.users.models import Source
from solutioner.tags.models import Tag
from solutioner.ajax.templates import render_block_to_string
from django.template import loader, Context
from django.contrib.contenttypes.models import ContentType
from solutioner.users.models import Ownership
from solutioner.events.models import Event
from solutioner.comments.models import Comment
from solutioner.comments.views import add_comment, get_comment
from solutioner.events.views import get_profile_events
from django.db.models import Q
import random


def follow_suggest(request):
  random_t = random.random()
  suggest = None
  following_count = User_info.objects.get(user=request.user).following.all().count()
  f_list = range(0, following_count)
  done = False
  
  if random_t > 0.5:
    while not done:
      if f_list:
        rand = random.choice(f_list)
        following = User_info.objects.get(user=request.user).following.all()[rand]
        suggest_count = User_info.objects.get(user=following).following.all().count()
        suggest_list = range(0, suggest_count)
        suggested = False
        while not suggested:
          if suggest_list:
            s_rand = random.choice(suggest_list)
            suggest = User_info.objects.get(user=following).following.all()[s_rand]
            if suggest != request.user and not (User_info.objects.get(user=request.user).following.filter(username=suggest.username)):
              suggested = True
              done = True
            else:
              suggest = None
              suggest_list.remove(s_rand)
          else:
            f_list.remove(rand)
            suggested = True
      else:
        done = True
    if not suggest:
      followers_count = request.user.users_usersfollowing.all().count()
      followers_list = range(0, followers_count)
      suggested = False
      while not suggested:
        if followers_list:
          rand = random.choice(followers_list)
          suggest = suggest = User.objects.get(username=request.user.users_usersfollowing.all()[rand])
          
          if suggest != request.user and not (User_info.objects.get(user=request.user).following.filter(username=suggest)):
            suggested = True
          else:
            suggest = None
            followers_list.remove(rand)
        else:
          suggested = True
  else:
    followers_count = request.user.users_usersfollowing.all().count()
    followers_list = range(0, followers_count)
    suggested = False
    while not suggested:
      if followers_list:
        rand = random.choice(followers_list)
        suggest = User.objects.get(username=request.user.users_usersfollowing.all()[rand])
        
        if suggest != request.user and not (User_info.objects.get(user=request.user).following.filter(username=suggest)):
          suggested = True
        else:
          suggest = None
          followers_list.remove(rand)
      else:
        suggested = True
    if not suggest:
      while not done:
        if f_list:
          rand = random.choice(f_list)
          following = User_info.objects.get(user=request.user).following.all()[rand]
          suggest_count = User_info.objects.get(user=following).following.all().count()
          suggest_list = range(0, suggest_count)
          suggested = False
          while not suggested:
            if suggest_list:
              s_rand = random.choice(suggest_list)
              suggest = User_info.objects.get(user=following).following.all()[s_rand]
              if suggest != request.user and not (User_info.objects.get(user=request.user).following.filter(username=suggest.username)):
                suggested = True
                done = True
              else:
                suggest = None
                suggest_list.remove(s_rand)
            else:
              f_list.remove(rand)
              suggested = True
        else:
          done = True
  if suggest:
    from solutioner.users.views import graphs_user
    suggest = graphs_user(request, user=suggest, JSON=False)
        
  return HttpResponse(simplejson.dumps({'suggest': suggest}, sort_keys=True, indent=4), content_type = 'application/json')














