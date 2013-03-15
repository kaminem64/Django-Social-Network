from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.core.context_processors import csrf
from django.template import RequestContext
import os
from django.contrib.auth.models import User, Group
from solutioner.users.models import User as User_info
from solutioner.users.models import NotificationSettings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from rbac.models import RBACRole, RBACOperation, RBACPermission, RBACGenericPermission, RBACGenericPermissionManager
from solutioner.events.models import Event
from solutioner.comments.models import Comment
from solutioner.solutions.models import Solution, Vote
from django.db.models import Q
from solutioner.comments.views import get_comment_by_id
from django.utils import simplejson
from django.template.defaultfilters import striptags, timesince
from django.contrib.auth.decorators import login_required



not_sd = {'owner_own__is_suspended': False, 'owner_own__is_deleted': False, 'object_own__is_suspended': False, 'object_own__is_deleted': False, 'operator_own__is_suspended': False, 'operator_own__is_deleted': False, 'operation_result_own__is_suspended': False, 'operation_result_own__is_deleted': False}
  
def check_event_perm(request, owner, model, operation, operator_user, event):
  try:
    permission = RBACGenericPermission.objects.get_user_permission(owner=owner, model=model, operation=operation, operator_user=operator_user, use_cache=True)
  except:
    permission = False
  if permission or event.operator == request.user:
    return True
  else:
    return False

def get_user_info(user):
  return {'username': '%s'%user.username, 'first_name': '%s'%user.first_name, 'last_name': '%s'%user.last_name}


def event_dict_f(event):
  return {'id': event.id,'owner': get_user_info(event.owner), 'object': '%s'%event.object, 'object_ct_name': '%s'%event.object_ct.name, 'object_id': '%s'%event.object_id, 'operator': get_user_info(event.operator), 'operation': '%s'%event.operation, 'operation_result_id': '%s'%event.operation_result_id}


def events_list_maker(request, events, JSON=False):
  from solutioner.users.views import graphs_user
  operators_info = {}
  events_list = []
  for event in events:
    event_dict = {'datetime_since': timesince(event.datetime) }
    event_dict['datetime'] = '%s'%event.datetime if JSON else event.datetime
    try:
      event_dict['graphs_user_info'] = operators_info[event.operator]
    except:
      operators_info[event.operator] = graphs_user(request=request, user=event.operator, JSON=False)
      event_dict['graphs_user_info'] = operators_info[event.operator]
    if event.operation_result_ct == ContentType.objects.get_for_model(Comment) and event.operation.name == 'post_desk':
      permission = check_event_perm(request, owner=event.owner, model=event.object, operation='view_desk', operator_user=request.user, event=event)
      if permission:
        event_dict.update(event_dict_f(event))
        if JSON:
          comment = get_comment_by_id(request, id_exact=event.operation_result_id, operation='view_desk', JSON='JSON_ready')
        else:
          comment = get_comment_by_id(request, id_exact=event.operation_result_id, operation='view_desk', JSON=False)
        event_dict['comment'] = comment
        event_dict['type'] = 'comment'
      else:
        event_dict = {}

    elif event.operation_result_ct == ContentType.objects.get_for_model(Comment) and event.object_ct == ContentType.objects.get_for_model(Solution) and event.operation.name == 'add_comment':
      #permission = check_event_perm(request, owner=event.owner, model=event.operation_result, operation='view_comment', operator_user=request.user, event=event)
      if True: #permission
        event_dict.update(event_dict_f(event))
        if JSON:
          comment = get_comment_by_id(request, id_exact=event.operation_result_id, operation='view_comment', JSON='JSON_ready')
        else:
          comment = get_comment_by_id(request, id_exact=event.operation_result_id, operation='view_comment', JSON=False)
        event_dict['comment'] = comment
        event_dict['type'] = 'commented_on_solution'
      else:
        event_dict = {}

    elif event.operation_result_ct == ContentType.objects.get_for_model(Solution) and event.operation.name == 'add_solution':
      #permission = check_event_perm()
      if True: #permission
        event_dict.update(event_dict_f(event))
        from solutioner.users.views import graphs_solution_plus_user
        solution = graphs_solution_plus_user(request, event.operation_result_id, JSON='JSON_ready', safe=True)
        event_dict['type'] = 'add_solution'
        event_dict['solution'] = solution
    elif event.operation_result_ct == ContentType.objects.get_for_model(Solution) and event.operation.name == 'edit_solution':
      #permission = check_event_perm()
      if True: #permission
        event_dict.update(event_dict_f(event))
        event_dict['type'] = 'edit_solution'
    elif event.operation_result_ct == ContentType.objects.get_for_model(User) and event.operation.name == 'register':
      #permission = check_event_perm()
      if True: #permission
        event_dict.update(event_dict_f(event))
        event_dict['type'] = 'register'
    elif event.operation_result_ct == ContentType.objects.get_for_model(User) and event.operation.name == 'edit_profile':
      #permission = check_event_perm()
      if True: #permission
        event_dict.update(event_dict_f(event))
        event_dict['type'] = 'edit_profile'
    elif event.operation_result_ct == ContentType.objects.get_for_model(Vote) and event.operation.name == 'vote_solution':
      #permission = check_event_perm()
      if True: #permission
        event_dict.update(event_dict_f(event))
        event_dict['type'] = 'vote_solution'
    events_list.append(event_dict)
    last_event = event.id
  try:
    last_event = last_event
  except:
    last_event = 1
  return events_list, last_event


def notification_list_maker(events,request=None, JSON=False, cur_user=None):
  operators_info = {}
  events_list = []
  for event in events:
    event_dict = {}
    from solutioner.users.views import graphs_user
    try:
      event_dict['graphs_user_info'] = operators_info[event.operator]
    except:
      operators_info[event.operator] = graphs_user(request=request, user=event.operator, JSON=False, cur_user=cur_user)
      event_dict['graphs_user_info'] = operators_info[event.operator]
    if event.operation_result_ct == ContentType.objects.get_for_model(Comment) and event.operation.name == 'post_desk':
      #permission = check_event_perm(request, owner=event.owner, model=event.object, operation='view_desk', operator_user=request.user, event=event)
      if True:
        event_dict.update(event_dict_f(event))
        event_dict['type'] = 'commented_on_desk'
        event_dict['datetime'] = '%s'%event.datetime if JSON else event.datetime
      else:
        event_dict = {}

    elif event.operation_result_ct == ContentType.objects.get_for_model(Comment) and event.object_ct == ContentType.objects.get_for_model(Solution) and event.operation.name == 'add_comment':
      #permission = check_event_perm(request, owner=event.owner, model=event.operation_result, operation='view_comment', operator_user=request.user, event=event)
      if True: #permission
        event_dict.update(event_dict_f(event))
        event_dict['type'] = 'commented_on_solution'
        event_dict['datetime'] = '%s'%event.datetime if JSON else event.datetime
      else:
        event_dict = {}

    elif event.operation_result_ct == ContentType.objects.get_for_model(Solution) and event.operation.name == 'add_solution':
      #permission = check_event_perm()
      if True: #permission
        event_dict.update(event_dict_f(event))
        event_dict['type'] = 'add_solution'
        event_dict['datetime'] = '%s'%event.datetime if JSON else event.datetime
    elif event.operation_result_ct == ContentType.objects.get_for_model(Solution) and event.operation.name == 'edit_solution':
      #permission = check_event_perm()
      if True: #permission
        event_dict.update(event_dict_f(event))
        event_dict['type'] = 'edit_solution'
        event_dict['datetime'] = '%s'%event.datetime if JSON else event.datetime
    elif event.operation_result_ct == ContentType.objects.get_for_model(User) and event.operation.name == 'register':
      #permission = check_event_perm()
      if True: #permission
        event_dict.update(event_dict_f(event))
        event_dict['type'] = 'register'
        event_dict['datetime'] = '%s'%event.datetime if JSON else event.datetime
    elif event.operation_result_ct == ContentType.objects.get_for_model(User) and event.operation.name == 'edit_profile':
      #permission = check_event_perm()
      if True: #permission
        event_dict.update(event_dict_f(event))
        event_dict['type'] = 'edit_profile'
        event_dict['datetime'] = '%s'%event.datetime if JSON else event.datetime
    elif event.operation_result_ct == ContentType.objects.get_for_model(Vote) and event.operation.name == 'vote_solution':
      #permission = check_event_perm()
      if True: #permission
        event_dict.update(event_dict_f(event))
        event_dict['type'] = 'vote_solution'
        event_dict['datetime'] = '%s'%event.datetime if JSON else event.datetime
    events_list.append(event_dict)
    
  return events_list


def get_home_events(request, JSON=True, last_no=0):
  following = User_info.objects.get(user=request.user).following.all().values_list('id', flat=True)
  if JSON:
    try:
      last_event = int(request.POST['last_event'])
    except:
      last_event = 1
    try:
      events_limit = int(request.POST['events_limit'])
    except:
      events_limit = 5
    events = Event.objects.select_related().filter(Q(owner_id__in=following) | Q(owner_id=request.user.id), id__lt=last_event, **not_sd).order_by('-datetime')[:events_limit]
    events_list, last_event = events_list_maker(request, events, JSON=True)
    return HttpResponse(simplejson.dumps({'events':  events_list, 'last_event': last_event}, sort_keys=True, indent=4), content_type = 'application/json')
  else:
    events = Event.objects.filter(Q(owner_id__in=following) | Q(owner_id=request.user.id), **not_sd).order_by('-datetime')[:1]
    firstever_event = events.reverse()[0].id
    last_event = events[0].id + 1
    return last_event , firstever_event


def get_profile_events(request, user_username, JSON=True, last_no=0):
  try:
    last_event = int(request.POST['last_event'])
  except:
    last_event = 1
  try:
    events_limit = int(request.POST['events_limit'])
  except:
    events_limit = 5
  if not JSON:
    events_limit = 1
    last_event = Event.objects.all().count()+1
  firstever_event = 1
  user = User.objects.get(username=user_username)
  try:
    permission = RBACGenericPermission.objects.get_user_permission(owner=user, model=user, operation='view_desk', operator_user=request.user)
  except:
    permission = False
  if permission:
    events = Event.objects.filter(Q(operator_ct=ContentType.objects.get_for_model(user) ,operator_id=user.id) | Q(object_ct=ContentType.objects.get_for_model(user) ,object_id=user.id), id__lt=last_event, **not_sd).order_by('-datetime')[:events_limit]
    firstever_event = events.reverse()[0].id
  else:
    try:
      events = Event.objects.filter(id__lt=last_event, object_ct=ContentType.objects.get_for_model(user) ,object_id=user.id, operator_ct=ContentType.objects.get_for_model(request.user) ,operator_id=request.user.id, **not_sd).order_by('-datetime')[:events_limit]
      firstever_event = events.reverse()[0].id
    except:
      events = False

  if JSON:
    if events:
      events_list, last_event = events_list_maker(request, events, JSON=True)
    else:
      events_list, last_event = False, False
    return HttpResponse(simplejson.dumps({'events':  events_list, 'last_event': last_event}, sort_keys=True, indent=4), content_type = 'application/json')
  else:
    if events:
      firstever_event = events.reverse()[0].id
      last_event = events[0].id + 1
    else:
      last_event = None
    return last_event, firstever_event


def last_checked(request):
  try:
    new_last_checked_id = int(request.POST['last_checked_id'])
  except:
    new_last_checked_id = 0
  user_info = User_info.objects.get(user=request.user)
  last_checked_id = user_info.last_checked_id
  if new_last_checked_id > last_checked_id:
    user_info.last_checked_id = new_last_checked_id
    user_info.save()
  return HttpResponse(simplejson.dumps({'status': True}, sort_keys=True, indent=4), content_type = 'application/json')


def notifications(request):
  user = request.user
  try:
    count = request.POST['count']
  except:
    count = False
  try:
    user_info = User_info.objects.get(user=request.user)
    last_checked_id = user_info.last_checked_id
  except:
    last_checked_id = 0
  if count:
    notifications_count = Event.objects.filter(id__gt=last_checked_id, owner_ct=ContentType.objects.get_for_model(user) ,owner_id=user.id, **not_sd).exclude(operator_ct=ContentType.objects.get_for_model(request.user) ,operator_id=request.user.id).order_by('-datetime').count()
    return HttpResponse(simplejson.dumps({'count': notifications_count}, sort_keys=True, indent=4), content_type = 'application/json')
  else:
    notifications_queryset = Event.objects.filter(id__gt=last_checked_id, owner_ct=ContentType.objects.get_for_model(user) ,owner_id=user.id, **not_sd).exclude(operator_ct=ContentType.objects.get_for_model(request.user) ,operator_id=request.user.id).order_by('-datetime')
    try:
      last = notifications_queryset[0].id
    except:
      last = 0
    notifications_list = notification_list_maker(request, notifications_queryset, JSON=True)
    return HttpResponse(simplejson.dumps({'notifications_list': notifications_list, 'last': last}, sort_keys=True, indent=4), content_type = 'application/json')
  
@login_required(login_url='/login/')
def notifications_page(request):
  user = request.user
  try:
    user_info = User_info.objects.get(user=request.user)
    last_checked_id = user_info.last_checked_id
  except:
    last_checked_id = 0
  notifications_queryset = Event.objects.filter(id__gt=last_checked_id-51, owner_ct=ContentType.objects.get_for_model(user) ,owner_id=user.id, **not_sd).exclude(operator_ct=ContentType.objects.get_for_model(request.user) ,operator_id=request.user.id).order_by('-datetime')
  try:
    last = notifications_queryset[0].id
  except:
    last = 0
  notifications_list = notification_list_maker(request=request, events=notifications_queryset, JSON=False)
  return render_to_response("notifications.html", {'notifications_list': notifications_list, 'last': last}, context_instance=RequestContext(request))


from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context

def notification_email(owner_ct, owner_id, object_ct, object_id, operator_ct, operator_id, operation, operation_result_ct, operation_result_id):
  notifications_queryset = Event.objects.filter(owner_ct=owner_ct, owner_id=owner_id, object_ct=object_ct, object_id=object_id, operator_ct=operator_ct, operator_id=operator_id, operation=operation, operation_result_ct=operation_result_ct, operation_result_id=operation_result_id, **not_sd)
  notifications_list = notification_list_maker(notifications_queryset, JSON=False, cur_user=owner_ct.get_object_for_this_type(id=owner_id))
  
  if not (owner_ct == operator_ct and owner_id == operator_id):
    owner = owner_ct.get_object_for_this_type(id=owner_id)
    email = owner.email
    notif_settings, c = NotificationSettings.objects.get_or_create(user=owner)
    notif_settings_dict = {'commented_on_desk':notif_settings.comment_on_desk , 'commented_on_solution':notif_settings.comment_on_solution}
    try:
      type_of_notif = notifications_list[0]['type']
    except:
      type_of_notif = False
    if type_of_notif:
      if notif_settings_dict.get(type_of_notif, False):
        html = get_template('notif_email.html')

        d = Context({ 'event': notifications_list[0] })

        subject, from_email, to = 'Solutioner', 'notifications@solutioner.net', email
        html_content = html.render(d)
        msg = EmailMessage(subject, html_content, from_email, [to])
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send(fail_silently=False)


