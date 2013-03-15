from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404
from solutioner.comments.models import Comment
from solutioner.comments.forms import AddComment
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from solutioner.users.models import Ownership
from solutioner.events.models import Event
from django.utils import simplejson
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from solutioner.users.models import Ownership
from solutioner.rbac.models import RBACRole, RBACOperation, RBACGenericPermission, get_user_roles
from django.contrib.auth.models import User
from solutioner.solutions.models import Solution
from django.template.defaultfilters import striptags, timesince


def ajax_login_required(view_func):
  def wrap(request, *args, **kwargs):
    if request.user.is_authenticated():
      return view_func(request, *args, **kwargs)
    json = simplejson.dumps({ 'not_authenticated': True })
    return HttpResponse(json, mimetype='application/json')
  wrap.__doc__ = view_func.__doc__
  wrap.__dict__ = view_func.__dict__
  return wrap

@login_required(login_url='/login/')
def add_comment(request, object_inst, operation='add_comment', JSON=True):
  if request.method =='POST':
    form = AddComment(request.POST)
    if form.is_valid():
      posted = form.cleaned_data
      new_comment = Comment.objects.create_comment(request=request, operator=request.user, object_inst=object_inst, message=posted['message'], operation=operation )
      uncomplete = False
      return uncomplete

  else:
    form = AddComment()
  return form

@ajax_login_required
def rm_comment(request):
  try:
    redirectTo = re.search(r'http://[-.\w\d]+/(.+)', request.META['HTTP_REFERER']).group(1)
    redirectTo = '/'+redirectTo
  except:
    redirectTo = '/'
  try:
    JSON = request.GET['JSON']
  except:
    JSON = False
  error = 'error'
  try:
    if request.method =='POST':
      toRM = int(request.POST['toRM'])
      toRM_comment = Comment.objects.get(id=toRM)
      comment_ownership = Ownership.objects.get_ownership(toRM_comment)
      #--delete-pemission-check-------------------------------------------
      if (comment_ownership.owner_id, comment_ownership.owner_ct ) == (request.user.id, ContentType.objects.get_for_model(request.user) ):
        toRM_comment.is_deleted = 1
        toRM_comment.save()
        comment_ownership.is_deleted = 1
        comment_ownership.save()
  except:
    pass
  if JSON:
    return HttpResponse(simplejson.dumps({'status':'done', 'redirectTo': redirectTo}, sort_keys=True, indent=4), content_type = 'application/json')
  else:
    return HttpResponseRedirect(redirectTo)
  
  
def get_comment_by_id(request, id_exact, operation='view_comment', JSON=True):
  from solutioner.users.views import graphs_user
  operator_user = request.user
  try:
    comment = Comment.objects.get(id__exact = id_exact)
    graphs_user_info = graphs_user(request, comment.operator.username, JSON=False)
    comment_datetime = '%s'%comment.datetime if JSON else comment.datetime
    message_dict = {'not_allowed': False, 'id': comment.id, 'message': comment.message, 'datetime': comment_datetime, 'graphs_user_info': graphs_user_info}
  except:
    comment = None
    message_dict = {'not_allowed': True}
  if JSON == 'JSON_ready':
    return message_dict
  elif JSON:
    return HttpResponse(simplejson.dumps(message_dict, sort_keys=True, indent=4), content_type = 'application/json')
  else:
    return message_dict



def get_comment_by_id_perm(request, id_exact, operation='view_comment', JSON=True):
  from solutioner.users.views import graphs_user
  operator_user = request.user
  try:
    comment = Comment.objects.get(id__exact = id_exact)
    try:
      permission = RBACGenericPermission.objects.get_user_permission(comment.owner, comment.owner, operation, operator_user)
    except:
      permission = False
    if not (permission or comment.operator == request.user):
      comment = None
      message_dict = {'not_allowed': True}
    else:
      graphs_user_info = graphs_user(request, comment.operator.username, JSON=False)
      comment_datetime = '%s'%comment.datetime if JSON else comment.datetime
      message_dict = {'not_allowed': False, 'id': comment.id, 'message': comment.message, 'datetime': comment_datetime, 'graphs_user_info': graphs_user_info}
  except:
    comment = None
    message_dict = {'not_allowed': True}
  if JSON:
    return HttpResponse(simplejson.dumps(message_dict, sort_keys=True, indent=4), content_type = 'application/json')
  else:
    return message_dict

def get_comment(request, owner, model, object_inst, operation, order_by='datetime', last_id=False, first_ever_comment=False, limit=5, JSON=False, **kwargs):
  from solutioner.users.views import graphs_user
  filter_dict = {'is_deleted': False, 'owner_id': owner.id, 'owner_ct': ContentType.objects.get_for_model(owner), 'object_ct': ContentType.objects.get_for_model(object_inst), 'object_id': object_inst.id }
  for key in kwargs:
    if kwargs[key]:
      filter_dict[key] = kwargs[key]
  operator_user = request.user
  try:
    permission = RBACGenericPermission.objects.get_user_permission(owner, model, operation, operator_user)
  except:
    permission = False
  if not permission:
    filter_dict['operator_id'] = request.user.id
  if last_id:
    filter_dict['id__lt'] = last_id
  else:
    try:
      filter_dict['id__lt'] = Comment.objects.filter(**filter_dict).order_by(order_by)[:1][0].id + 1
    except:
      filter_dict['id__lt'] = 0
  if first_ever_comment:
    try:
      first_ever_comment = Comment.objects.filter(**filter_dict).order_by('datetime')[:1][0].id
    except:
      first_ever_comment = 0
  comments =  Comment.objects.filter(**filter_dict).order_by(order_by)[:limit]
        
  comments_list = []
  for comment in comments:
    last_comment = comment.id
    graphs_user_info = graphs_user(request, comment.operator.username, JSON=False)
    comment_datetime = '%s'%comment.datetime if JSON else comment.datetime
    message_dict = {'id': comment.id, 'message': comment.message, 'datetime': comment_datetime, 'datetime_since': timesince(comment.datetime), 'graphs_user_info': graphs_user_info}
    comments_list.append(message_dict)
    comments= {'last_comment': last_comment, 'first_ever_comment': first_ever_comment, 'comments_list': comments_list }
  if JSON:
    return HttpResponse(simplejson.dumps(comments, sort_keys=True, indent=4), content_type = 'application/json')
  else:
    return comments_list


def solution_comments(request, solution_no):
  try:
    last_comment = int(request.POST['last_comment'])
  except:
    last_comment = False
  try:
    comments_limit = int(request.POST['comments_limit'])
  except:
    events_limit = 5
  try:
    first_ever_comment = int(request.POST['first_ever_comment'])
    first_ever_comment = False
  except:
    first_ever_comment = True
  model = Solution
  object_inst = Solution.objects.get(id=solution_no)
  owner = object_inst.owner
  operation = 'view_comment'
  return get_comment(request, owner, model, object_inst, operation, order_by='-datetime', last_id=last_comment, limit=events_limit, first_ever_comment=first_ever_comment, JSON=True)
  

def desk_comments(request, user_username):
  owner = User.objects.get(username=user_username)
  model = User
  object_inst = owner
  operation = 'view_desk'
  return get_comment(request, owner, model, object_inst, operation, order_by='-datetime', from_no=0, limit=5, JSON=True)







