# -*- coding: utf-8 -*-
from django.contrib import auth
from django.http import HttpResponseRedirect
from solutioner.users.forms import *
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, Http404
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


VIEWER = 0.1
CRITIC = 1
AUTHOR = 5
AUTHOR_USEFUL = 1
AUTHOR_VIEWED = 0.1
def graphs_user(request=None, user_username=None, external=False, JSON=True, cur_user=None, user=None, score=False, solutionvote=False, gender=False, email=False, website=False, location=False, birthdate=False):
  graphs_user_info = {}
  graphs_user_info['is_page_owner'] = False
  if not user:
    user = get_object_or_404(User,username = user_username)
  if not cur_user:
    cur_user = request.user


  user_profile, c = User_info.objects.get_or_create(user=user)

  image = 'profiles/pictures/pna.jpg'
  if user == cur_user:
    graphs_user_info['is_page_owner'] = True
  if RBACGenericPermission.objects.get_user_permission(user, User_info, 'display_profilepicture', cur_user):
    if user_profile.image:
      image = user_profile.image
  if gender:
    if RBACGenericPermission.objects.get_user_permission(user, User_info, 'display_gender', cur_user):
      graphs_user_info['gender'] = user_profile.get_gender_display()
  if email:
    if RBACGenericPermission.objects.get_user_permission(user, User, 'display_emailaddress', cur_user):
      graphs_user_info['email'] = user.email
  if website:
    if RBACGenericPermission.objects.get_user_permission(user, User_info, 'display_website', cur_user):
      graphs_user_info['website'] = user_profile.website
  if location:
    if RBACGenericPermission.objects.get_user_permission(user, User_info, 'display_location', cur_user):
      graphs_user_info['location'] = user_profile.get_location_display()
  if birthdate:
    if RBACGenericPermission.objects.get_user_permission(user, User_info, 'display_birthdate', cur_user):
      graphs_user_info['birthdate'] = user_profile.birthdate if not JSON else '%s'%user_profile.birthdate

  graphs_user_info['id'] = user.id
  graphs_user_info['username'] = user.username
  graphs_user_info['first_name'] = user.first_name
  graphs_user_info['last_name'] = user.last_name
  graphs_user_info['profile_pic'] = '%s'%image
  
  graphs_user_info['is_followed'] = is_followed(request=request, owner=user, cur_user=cur_user)
  
  if score:
    user_score = User_score.objects.get(user=user)
    viewer_score = int(user_score.views_count)*VIEWER
    critic_score = int(user_score.votes_count)*CRITIC
    if user_score.voted_count:
      author_critic = float(user_score.voted)/int(user_score.voted_count)
    else:
      author_critic = 0
    author_score = int(user_score.solutions_count)*AUTHOR + (author_critic/100)*AUTHOR_USEFUL + int(user_score.viewed_count)*AUTHOR_VIEWED
    total_voted_count = int(user_score.voted_count)
    accept_rate = author_critic
    total_score = viewer_score + critic_score + author_score
    level = 0
    if total_score > 0:
      while (2**level-1) <= total_score:
        level = level + 1
      level = level - 1
    else:
      level = 1
    main_attr_dict = {'Developer': author_score, 'Critic': critic_score, 'Viewer': viewer_score}
    main_attr = max(main_attr_dict, key=main_attr_dict.get)
    
    graphs_user_info['viewer_score'] = round(viewer_score,1)
    graphs_user_info['critic_score'] = round(critic_score,1)
    graphs_user_info['develop_score'] = round(author_score,1)
    graphs_user_info['total_score'] = round(total_score,1)
    graphs_user_info['main_attr'] = main_attr
    graphs_user_info['level'] = level
    graphs_user_info['accept_rate'] = int(accept_rate)
    graphs_user_info['viewed_count'] = user_score.viewed_count
    graphs_user_info['solutions_count'] = user_score.solutions_count
    graphs_user_info['total_voted_count'] = total_voted_count

  if solutionvote:
    solutionvote = []
    for vote in Vote.objects.filter(is_deleted=False, user=user).order_by('-vote'):
      solutionvote.append({'id':vote.solution.id, 'problem':vote.solution.problem, 'vote': vote.vote})
    graphs_user_info['voted_solutions'] = solutionvote
    graphs_user_info['voted_solutions_count'] = len(graphs_user_info['voted_solutions'])


  if JSON==True:
    return HttpResponse(simplejson.dumps(graphs_user_info, sort_keys=True, indent=4), content_type = 'application/json')
  else:
    return graphs_user_info

  """elif external:
    user = ExternalUser.objects.get(id = user_id)
    user_score = User_score.objects.get(external_user=user)
    total_voted_count = int(user_score.useful_voted_count) + int(user_score.unuseful_voted_count)
    if total_voted_count != 0:
      accept_rate = ((int(user_score.useful_voted_count) - int(user_score.unuseful_voted_count))/float(total_voted_count))*100
    else:
      accept_rate = 0

    graphs_user_info = {'username': user.username, 'profile_pic': user.image, 'url': user.url, 'total_voted_count': total_voted_count, 'accept_rate': int(accept_rate),'viewed_count': user_score.viewed_count, 'solutions_count': user_score.solutions_count}"""




from solutioner.templatetags.templatetags.sanitize import sanitize


def graphs_solution(request, real_solution_id, JSON=True, safe=False):
  #Check premissions
    needed_solution = Solution.objects.get(id=real_solution_id)
    graphs_solution_info_add = {}
    try:  
      tags = []
      for tag in needed_solution.tags.all():
        tags.append(tag.name)
    except:
      pass
    
    owner = needed_solution.owner
    is_external = False
    licenses = {}
    for license in needed_solution.source.licenses.all():
      licenses[license.license] = license.license_url
    source = { 'source': '%s'%needed_solution.source.source,  'image': '%s'%needed_solution.source.image,  'url': '%s'%needed_solution.source.url, 'licenses': licenses}
    try:
      vote = Vote.objects.get(is_deleted=False, solution=needed_solution, user=request.user)
      sol_user_accept_rate = int(vote.vote)
      sol_user_is_voted = True
    except:
      sol_user_accept_rate = 0
      sol_user_is_voted = False

    try:
      sol_votes_count = needed_solution.votes_count
      sol_votes = needed_solution.votes_sum
      sol_accept_rate = float(sol_votes)/int(sol_votes_count)
    except:
      sol_accept_rate = 0
      sol_votes_count = 0

    from django.template.defaultfilters import striptags, timesince
    from solutioner.templatetags.templatetags.truncatechars import truncatechars
    problem = striptags(needed_solution.problem) if safe else sanitize(needed_solution.problem)
    problem_desc = sanitize(truncatechars(striptags(needed_solution.problem_desc),300)) if safe else sanitize(needed_solution.problem_desc)
    solution = sanitize(truncatechars(striptags(needed_solution.solution),300)) if safe else sanitize(needed_solution.solution)
    datetime_added_since = timesince(needed_solution.datetime_added)
    
    graphs_solution_info = {'id': needed_solution.id, 'is_external': is_external, 'tags': tags, 'problem': '%s'%problem, 'problem_desc': '%s'%problem_desc, 'solution': '%s'%solution, 'datetime_added': '%s'%needed_solution.datetime_added, 'datetime_added_since': '%s'%datetime_added_since, 'viewed': '%s'%needed_solution.viewed,  'source': source, 'category': '%s'%needed_solution.category.name, 'sol_accept_rate': int(sol_accept_rate),'sol_user_accept_rate': int(sol_user_accept_rate), 'sol_user_is_voted': sol_user_is_voted,  'sol_votes_count': sol_votes_count}
    graphs_solution_info.update(graphs_solution_info_add)
    if JSON == True:
      return HttpResponse(simplejson.dumps(graphs_solution_info, sort_keys=True, indent=4), content_type = 'application/json')
    elif JSON == 'JSON_ready':
      return graphs_solution_info
    else:
      graphs_solution_info['datetime_added'] = needed_solution.datetime_added
      return graphs_solution_info

def graphs_solution_plus_user(request, real_solution_id, JSON=True, safe=False):
  owner = Solution.objects.get(id=real_solution_id).owner
  sol_JSON = 'JSON_ready' if JSON else False
  graphs_solution_info = graphs_solution(request, real_solution_id, sol_JSON, safe)
  graphs_user_info = graphs_user(request, owner.username, external=False, JSON=False)
  graphs_solution_info['graphs_user_info'] = graphs_user_info
  if JSON == True:
    return HttpResponse(simplejson.dumps(graphs_solution_info, sort_keys=True, indent=4), content_type = 'application/json')
  elif JSON == 'JSON_ready':
    return graphs_solution_info
  else:
    graphs_solution_info['datetime_added'] = needed_solution.datetime_added
    return graphs_solution_info
  
  

def graphs_user_solutions(request, user_username, JSON=True, include_user=False, from_no=0, solutions_from_limit=2, order='-datetime_added'):
  try:
    first_sol = request.GET['last_sol']
  except:
    first_sol = False
  try:
    solutions_from_limit = request.GET['solutions_from_limit']
  except:
    pass
  user = get_object_or_404(User,username = user_username)
  owner_ct=ContentType.objects.get_for_model(user)
  owner_id=user.id
  solutions_from = {}
  try:
    firstever_sol = Solution.objects.filter(owner_ct=owner_ct, owner_id=owner_id, is_deleted=False).order_by('datetime_added')[0].id
  except:
    firstever_sol = 'None'
  if solutions_from_limit == 'all' or solutions_from_limit == False:
    needed_solutions = Solution.objects.filter(owner_ct=owner_ct, owner_id=owner_id, is_deleted=False).order_by(order)
  else:
    if first_sol:
      needed_solutions = Solution.objects.filter(owner_ct=owner_ct, owner_id=owner_id, is_deleted=False, id__lt=first_sol).order_by(order)[from_no:solutions_from_limit]
    else:
      needed_solutions = Solution.objects.filter(owner_ct=owner_ct, owner_id=owner_id, is_deleted=False).order_by(order)[from_no:solutions_from_limit]
        
  if include_user:
    graphs_user_info = graphs_user(request, user.username, external=False, JSON=False)
    user_solutions = {'graphs_user_info': graphs_user_info, 'solutions': [] }
  else:
    user_solutions = {'solutions': [] }
  if JSON:
    if needed_solutions:
      for needed_solution in needed_solutions:
        graphs_user_info = graphs_user(request, user_username, external=False, JSON=False)
        user_solutions['solutions'].append(graphs_solution(request, needed_solution.id, JSON='JSON_ready', safe=True))
        last_sol = needed_solution.id
      user_solutions['last_sol'] = last_sol
      user_solutions['firstever_sol'] = firstever_sol
      return HttpResponse(simplejson.dumps(user_solutions, sort_keys=True, indent=4), content_type = 'application/json')
    else:
      return HttpResponse(simplejson.dumps({'last_sol':'None', 'firstever_sol': firstever_sol}, sort_keys=True, indent=4), content_type = 'application/json')
  else:
    if needed_solutions:
      for needed_solution in needed_solutions:
        user_solutions['solutions'].append(graphs_solution(request, needed_solution.id, JSON='False', safe=True))
        last_sol = needed_solution.id
      user_solutions['last_sol'] = last_sol
      user_solutions['firstever_sol'] = firstever_sol
    else:
      user_solutions['last_sol'] = 'None'
      user_solutions['firstever_sol'] = firstever_sol
    return user_solutions

def graphs_categories(request, JSON=True):
  allcategories = Category.objects.all()
  if JSON:
    return HttpResponse(simplejson.dumps(allcategories, sort_keys=True, indent=4), content_type = 'application/json')
  else:
    return allcategories
    
def login(request):
  if request.user.is_authenticated():
    return HttpResponseRedirect('/profile/'+request.user.username)
  if request.method == 'POST':
    form = LoginForm(request.POST)
    redirectTo = request.POST.get('next', '/')
    if form.is_valid():
      username = request.POST.get('username', '')
      password = request.POST.get('password', '')
      if '@' in username:
        username = User.objects.get(email=username).username
      user = auth.authenticate(username=username, password=password)
      if user is not None and user.is_active:
        auth.login(request, user)
        if redirectTo == '/' or 'reset' in redirectTo:
          redirectTo = '/profile/'+request.user.username
        return HttpResponseRedirect(redirectTo)
      else:
        return render_to_response("login.html", {'form': form, 'next': redirectTo, 'login_error': True}, context_instance=RequestContext(request))
  else:
    form = LoginForm()
  try:
    redirectTo = request.GET['next']
  except:
    try:
      redirectTo = re.search(r'http://[-.\w\d]+/(.+)', request.META['HTTP_REFERER']).group(1)
      if redirectTo:
        redirectTo = '/'+redirectTo
      else:
        redirectTo = '/'
    except:
      redirectTo = '/'
  return render_to_response("login.html", {'form': form, 'next': redirectTo, 'login_error': request.GET.get('login_error', '')}, context_instance=RequestContext(request))




def logout(request):
  try:
    redirectTo = re.search(r'http://[-.\w\d]+/(.+)', request.META['HTTP_REFERER']).group(1)
    redirectTo = '/'+redirectTo
  except:
    redirectTo = '/'
  if request.user.is_authenticated():
    auth.logout(request)
    return HttpResponseRedirect(redirectTo)
  else:
    return HttpResponseRedirect("/login/")


def register(request):
  html_captcha = captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)
  if request.method == 'POST':
    check_captcha = captcha.submit(request.POST['recaptcha_challenge_field'], request.POST['recaptcha_response_field'], settings.RECAPTCHA_PRIVATE_KEY, request.META['REMOTE_ADDR'])
    form = RegisterForm(request.POST)
    redirectTo = request.POST.get('redirectTo', '/')
    if form.is_valid():
      if check_captcha.is_valid is False:
        return render_to_response("register.html", {'form': form, 'redirectTo': redirectTo, 'html_captcha': html_captcha, 'recaptchaError': 'True'}, context_instance=RequestContext(request))
      else:
        form.save()
        return HttpResponseRedirect("/login/?redirectTo="+redirectTo)
  else:
    form = RegisterForm()
  try:
    redirectTo = re.search(r'http://[-.\w\d]+/(.+)', request.META['HTTP_REFERER']).group(1)
    redirectTo = '/'+redirectTo
  except:
    redirectTo = '/'
  return render_to_response("register.html", {'form': form, 'redirectTo': redirectTo, 'html_captcha': html_captcha, }, context_instance=RequestContext(request))

def is_followed(owner_username=None, cur_user=None, owner=None, request=None,):
  if not cur_user:
    cur_user = request.user
  if not owner:
    owner = User.objects.get(username=owner_username)
  roles = get_user_roles(owner, cur_user)
  if RBACRole.objects.get(name='myself') not in roles:
    result = RBACRole.objects.get(name='followers') in roles
  else:
    result = 'owner'
  return result

def user_follow(request):
  try:
    redirectTo = re.search(r'http://[-.\w\d]+/(.+)', request.META['HTTP_REFERER']).group(1)
    redirectTo = '/'+redirectTo
  except:
    redirectTo = '/'
  try:
    tofollow_user = request.POST['toFOLLOW']
  except:
    raise Http404 
  try:
    JSON = True if request.POST['JSON'] == 'True' else False
    JSON_response = False
  except:
    JSON = False
  followed = is_followed(request=request, owner_username=tofollow_user)
  to_follow_user = User.objects.get(username=tofollow_user)
  if request.method == 'POST':
    if not followed:
      User_info.objects.get(user=request.user).following.add(to_follow_user)
      JSON_response = 'added'
      Event.objects.create_event(operator=request.user, object_inst=to_follow_user, operation='follow', operation_result=to_follow_user)
    elif followed and followed != 'owner':
      User_info.objects.get(user=request.user).following.remove(User.objects.get(username=tofollow_user))
      JSON_response = 'removed'
  return  HttpResponse(simplejson.dumps({'status': JSON_response}, sort_keys=True, indent=4), content_type = 'application/json') if JSON else HttpResponseRedirect(redirectTo)

def user_following_graph(request, owner, JSON=True, from_no=0, limit=False):
  if limit:
    following = User_info.objects.get(user=User.objects.get(username=owner)).following.all().order_by('?')[:limit]
  else:
    following = User_info.objects.get(user=User.objects.get(username=owner)).following.all().order_by('?')
  user_following_graph = {}
  for follow in following:
    user_info = User_info.objects.get(user=follow)
    if user_info.image:
      image = user_info.image
    else:
      image = 'profiles/pictures/pna.jpg'
    user_following_graph[follow.username] = {'first_name': follow.first_name, 'last_name': follow.last_name, 'profile_pic': image}
  return user_following_graph

def user_followers_graph(request, owner, JSON=True, from_no=0, limit=False):
  if limit:
    followers=User.objects.get(username=owner).users_usersfollowing.all().order_by('?')[:limit]
  else:
    followers=User.objects.get(username=owner).users_usersfollowing.all().order_by('?')
  user_followers_graph = {}
  for follower in followers:
    follower_user = User.objects.get(username=follower)
    user_info = User_info.objects.get(user=follower_user)
    if user_info.image:
      image = user_info.image
    else:
      image = 'profiles/pictures/pna.jpg'
    user_followers_graph[follower_user.username] = {'first_name': follower_user.first_name, 'last_name': follower_user.last_name, 'profile_pic': image}
  return user_followers_graph
  
#profile
#-------------------------------------------------------------------------------------------
def profile_desk(request, user_username):
  try:
    redirectTo = re.search(r'http://[-.\w\d]+/(.+)', request.META['HTTP_REFERER']).group(1)
    redirectTo = '/'+redirectTo
  except:
    redirectTo = '/'
  user = User.objects.get(username=user_username)
  post_desk = False
  if RBACGenericPermission.objects.get_user_permission(user, User, 'post_desk', request.user):
    post_desk = True
  if post_desk: #if permissions passed then POST vars come to account
    form = add_comment(request, object_inst=user, operation='post_desk', JSON=False)
    if not form: #DONE!
      return HttpResponseRedirect(redirectTo)
  else:
    form = None
  from solutioner.solutions.views import add_solution
  form_add_solution = add_solution(request, JSON=False)
  last_event, firstever_event = get_profile_events(request, user_username=user_username, JSON=False)
  graphs_user_info = graphs_user(request, user_username=user_username, JSON=False)
  return render_to_response("profile_desk.html", {'title': 'Desk', 'graphs_user_info': graphs_user_info, 'form': form, 'form_add_solution': form_add_solution, 'post_desk': post_desk, 'last_event': last_event, 'firstever_event': firstever_event, 'user_following_limited_graph': user_following_graph(request, user_username, limit=5), 'user_followers_limited_graph': user_followers_graph(request, user_username, limit=5) }, context_instance=RequestContext(request))

def profile_info(request, user_username):
  graphs_user_info = graphs_user(request=request, user_username=user_username,  JSON=False, solutionvote=False, gender=True, email=True, website=True, location=True, birthdate=True)
  return render_to_response("profile_info.html", {'title': 'Info', 'graphs_user_info': graphs_user_info, 'user_following_limited_graph': user_following_graph(request, user_username, limit=5), 'user_followers_limited_graph': user_followers_graph(request, user_username, limit=5)}, context_instance=RequestContext(request))

def profile_solutions(request, user_username):
  try:
    redirectTo = re.search(r'http://[-.\w\d]+/(.+)', request.META['HTTP_REFERER']).group(1)
    redirectTo = '/'+redirectTo
  except:
    redirectTo = '/'
  from solutioner.solutions.views import add_solution
  form = add_solution(request, JSON=False)
  if not form: #DONE!
    return HttpResponseRedirect(redirectTo)
  categories_info = graphs_categories(request, JSON=False)
  user = get_object_or_404(User,username = user_username)
  owner_ct=ContentType.objects.get_for_model(user)
  owner_id=user.id
  try:
    last_sol = Solution.objects.filter(owner_ct=owner_ct, owner_id=owner_id, is_deleted=False).order_by('-datetime_added')[0].id + 1
  except:
    last_sol = 0
  try:
    firstever_sol = Solution.objects.filter(owner_ct=owner_ct, owner_id=owner_id, is_deleted=False).order_by('datetime_added')[0].id
  except:
    firstever_sol = 0
  
  graphs_user_solutions_ins = graphs_user_solutions(request, user_username, JSON=False)
  graphs_user_info = graphs_user(request, user_username=user_username, JSON=False) 
  inf, c = User_info.objects.get_or_create(user=User.objects.get(username=user_username))
  return render_to_response("profile_solutions.html", {'title': 'Solutions', 'graphs_user_info': graphs_user_info, 'last_sol': last_sol, 'firstever_sol': firstever_sol, 'categories_info': categories_info, 'form': form, 'inf': inf, 'user_following_limited_graph': user_following_graph(request, user_username, limit=5), 'user_followers_limited_graph': user_followers_graph(request, user_username, limit=5) }, context_instance=RequestContext(request))

def profile_scores(request, user_username):
  graphs_user_info = graphs_user(request=request, user_username=user_username, JSON=False, score=True)
  return render_to_response("profile_scores.html", {'title': 'Scores', 'graphs_user_info': graphs_user_info, 'user_following_limited_graph': user_following_graph(request, user_username, limit=5), 'user_followers_limited_graph': user_followers_graph(request, user_username, limit=5)}, context_instance=RequestContext(request))

def profile_votes(request, user_username):
  graphs_user_info = graphs_user(request, user_username=user_username, JSON=False, solutionvote=True)
  return render_to_response("profile_votes.html", {'title': 'Votes', 'graphs_user_info': graphs_user_info, 'user_following_limited_graph': user_following_graph(request, user_username, limit=5), 'user_followers_limited_graph': user_followers_graph(request, user_username, limit=5)}, context_instance=RequestContext(request))

def profile_follow(request, user_username):
  graphs_user_info = graphs_user(request, user_username=user_username, JSON=False)
  return render_to_response("profile_follow.html", {'title': 'Following Followers', 'graphs_user_info': graphs_user_info, 'user_following_graph': user_following_graph(request, user_username), 'user_followers_graph': user_followers_graph(request, user_username)}, context_instance=RequestContext(request))
#-------------------------------------------------------------------------------------------
@login_required(login_url='/login/')
def edit_solution(request, solution_id):
  redirectTo = '/solutions/view/%s/'%solution_id
  solution = Solution.objects.get(id=solution_id)
  try:
    forked = True if request.GET['forked'] == 'True' else False
  except:
    forked = False
    
  if request.user == solution.owner:
    if request.method == 'POST':
      form = AddSolution(request.POST)
      if form.is_valid():
        posted = form.cleaned_data
        edited_solution = Solution.objects.filter(id=solution_id).update(**{'category': Category.objects.get(name=unicode(posted['category'])), 'problem': posted['problem'], 'problem_desc': posted['problem_desc'], 'solution': posted['solution']})
        Event.objects.create_event(operator=request.user, object_inst=request.user, operation='edit_solution', operation_result=Solution.objects.get(id=solution_id))
        former_tags = [unicode(tag) for tag in solution.tags.all()]
        if posted['tags']:
          tags=posted['tags']
          tags = re.findall(r'\S+', tags.replace(',',' '))
          solution.tags.clear()
          tag_list = []
          for tag in tags:
            tag = tag.strip()
            tag = tag[:50]
            tag = tag.lower()
            try:
              selected_tag = Tag.objects.get(name=tag)
              solution.tags.add(selected_tag)
              if not tag in former_tags:
                selected_tag.used_no = int(selected_tag.used_no) + 1
                selected_tag.save()
            except:
              new_tag = Tag(name=tag, used_no=1)
              new_tag.save()
              solution.tags.add(new_tag)
          for former_tag in former_tags:
            if not former_tag in tags:
              selected_tag = Tag.objects.get(name=former_tag)
              selected_tag.used_no = int(selected_tag.used_no) - 1
              selected_tag.save()
        else:
          solution.tags.clear()
          for former_tag in former_tags:
            selected_tag = Tag.objects.get(name=former_tag)
            selected_tag.used_no = int(selected_tag.used_no) - 1
            selected_tag.save()
          
      return HttpResponseRedirect(redirectTo)
    else:
      form = AddSolution(initial={'problem': solution.problem, 'problem_desc': solution.problem_desc, 'solution': solution.solution, 'category': solution.category, 'tags': ','.join( [unicode(tag) for tag in solution.tags.all()] )   })
      if not form:
        return HttpResponseRedirect(redirectTo)
      return render_to_response("edit_solutions.html", {'title': 'Edit Solution', 'solution_id': solution_id, 'form': form, 'forked': forked }, context_instance=RequestContext(request))
  else:
    return HttpResponseRedirect(redirectTo)
  
  
  
@login_required(login_url='/login/')
def handle_uploaded_file(request):
  f = request.FILES['profilepicture']
  name = request.user.id
  try:
    filetype = f.name.split('.')[-1]
  except:
    filetype = 'jpg'
  destination = open('%s/%s.%s'%('/home/kambiz/www/media/profiles/pictures', name, filetype), 'wb+')
  for chunk in f.chunks():
    destination.write(chunk)
  destination.close()
  user_profile = User_info.objects.get(user=request.user.id)
  user_profile.image = '%s.%s'%(name, filetype)
  user_profile.save()


@login_required(login_url='/login/')
def edit_profile(request):
  saved = False
  if request.method == 'POST':
    form = EditProfileForm(request.POST, request.FILES)
    if form.is_valid():
      form.save(request=request)
      Event.objects.create_event(operator=request.user, object_inst=request.user, operation='edit_profile', operation_result=request.user)
      saved = True
  
  user = User.objects.get(id=request.user.id)
  user_info, c = User_info.objects.get_or_create(user=request.user)
  form = EditProfileForm(initial={
  'firstname': user.first_name,
  'lastname': user.last_name,
  'gender': user_info.gender,
  'emailaddress': request.user.email,
  'website': user_info.website,
  'location': user_info.location,
  'birthdate': user_info.birthdate,
  'profilepicture_perm': RBACGenericPermission.objects.get_permission_setting(request.user, User_info, 'display_profilepicture'),
  'gender_perm': RBACGenericPermission.objects.get_permission_setting(request.user, User_info, 'display_gender'),
  'emailaddress_perm': RBACGenericPermission.objects.get_permission_setting(request.user, User, 'display_emailaddress'),
  'website_perm': RBACGenericPermission.objects.get_permission_setting(request.user, User_info, 'display_website'),
  'location_perm': RBACGenericPermission.objects.get_permission_setting(request.user, User_info, 'display_location'),
  'birthdate_perm': RBACGenericPermission.objects.get_permission_setting(request.user, User_info, 'display_birthdate'),
  })
  graphs_user_info = graphs_user(request, user_username=request.user.username, JSON=False)
  return render_to_response("edit_profile.html", {'form': form, 'saved': saved, 'graphs_user_info': graphs_user_info}, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def privacy_settings(request):
  saved = False
  if request.method == 'POST':
    form = PrivacySettings(request.POST)
    if form.is_valid():
      form.save(request=request)
      saved = True
      
  form = PrivacySettings(initial={
  'view_desk_perm': RBACGenericPermission.objects.get_permission_setting(request.user, User, 'view_desk'),
  'post_desk_perm': RBACGenericPermission.objects.get_permission_setting(request.user, User, 'post_desk'),
  'add_comment_solution_perm': RBACGenericPermission.objects.get_permission_setting(request.user, Solution, 'add_comment'),
  'view_comment_solution_perm': RBACGenericPermission.objects.get_permission_setting(request.user, Solution, 'view_comment'),
  })
  graphs_user_info = graphs_user(request, user_username=request.user.username, JSON=False)
  return render_to_response("privacy_settings.html", {'form': form, 'saved': saved, 'graphs_user_info': graphs_user_info}, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def notifications_settings(request):
  saved = False
  if request.method == 'POST':
    form = NotificationSettingsForm(request.POST)
    if form.is_valid():
      form.save(request=request)
      saved = True
  notif_settings, c = NotificationSettings.objects.get_or_create(user=request.user)    
  form = NotificationSettingsForm(initial={
  'comment_on_desk': notif_settings.comment_on_desk,
  'comment_on_solution': notif_settings.comment_on_solution,
  })
  graphs_user_info = graphs_user(request, user_username=request.user.username, JSON=False)
  return render_to_response("notifications_settings.html", {'form': form, 'saved': saved, 'graphs_user_info': graphs_user_info}, context_instance=RequestContext(request))


@login_required(login_url='/login/')
def change_password(request):
  if request.method == 'POST':
    form = ChangePasswordForm(request.POST, request.FILES,request=request)
    if form.is_valid():
      form.save(request=request)
      return HttpResponseRedirect('/profile/'+unicode(request.user.username))
  else:
    form = ChangePasswordForm(request=request,initial={'username': request.user})
  return render_to_response("change_password.html", {'form': form}, context_instance=RequestContext(request))
  

from solutioner.users.forms import RegisterForm, RegisterCaptchaForm
from solutioner.formwizard.views import *

class RegisterWizard(SessionWizardView):
  def get(self, request, *args, **kwargs):
    if request.user.is_authenticated():
      return HttpResponseRedirect('/profile/'+request.user.username)
    return super(RegisterWizard, self).get(self.request, *args, **kwargs)

  def post(self, *args, **kwargs):
    if self.request.user.is_authenticated():
      request = self.request
      return HttpResponseRedirect('/profile/'+request.user.username)
    return super(RegisterWizard, self).post(*args, **kwargs)

  def get_template_names(self):
    template_name = super(RegisterWizard, self).get_template_names()
    return 'register_%s.html'% self.steps.current
  def get_context_data(self, form, **kwargs):
    context = super(RegisterWizard, self).get_context_data(form, **kwargs)
    if self.steps.current == '1':
      html_captcha = captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)
      context.update({'html_captcha': html_captcha})
    return context
  def get_form_kwargs(self, step):
    kwargs = {}
    if step == '1':
      kwargs = {'request': self.request}
    return kwargs
    
  def done(self, form_list, **kwargs):
    request = self.request
    register = self.get_cleaned_data_for_step('0')

    user = User.objects.create_user(username=register['username'], password=register['password'], email=register['emailaddress'])
    user.first_name = register['firstname']
    user.last_name = register['lastname']
    user.save()
    User_info.objects.create(user=user)
    User_score.objects.create(user=user)
    
    profilepicture_perm_role=RBACRole.objects.get(name='public')
    emailaddress_perm_role=RBACRole.objects.get(name='public')
    website_perm_role=RBACRole.objects.get(name='public')
    location_perm_role=RBACRole.objects.get(name='public')
    birthdate_perm_role=RBACRole.objects.get(name='public')
    view_desk_perm_role=RBACRole.objects.get(name='followers')
    post_desk_perm_role=RBACRole.objects.get(name='followers')
    add_comment_solution_perm_role=RBACRole.objects.get(name='followers')
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

    Ownership.objects.create_ownership(user, user)
    Event.objects.create_event(operator=user, object_inst=user, operation='register', operation_result=user)
      
    user = auth.authenticate(username=register['username'], password=register['password'])
    if user is not None and user.is_active:
      auth.login(request, user)
    return render_to_response("done.html", {'register': register}, context_instance=RequestContext(request))





