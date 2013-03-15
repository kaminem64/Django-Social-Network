from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.contrib.auth.models import User
from django.db.models import Q
from django.template import RequestContext


def friend_finder(request):
  q = unicode(request.GET['search'])
  tags_found1 = User.objects.filter(Q(first_name__istartswith=q) | Q(last_name__istartswith=q)).values('username','first_name','last_name').order_by('?')[:4]
  tags_found2 = []
  tags_count = tags_found1.count()
  if tags_count < 4:
    r = 4 - tags_count
    tags_found2 = User.objects.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q)).exclude(Q(first_name__istartswith=q) | Q(last_name__istartswith=q)).values('username','first_name','last_name').order_by('?')[:r]
  tags_found = list(tags_found1) + list(tags_found2)
  jjson = simplejson.dumps(tags_found)
  return HttpResponse(jjson, mimetype='application/json')

def search_page(request):
  try:
    search_target = request.GET['search_target']
    if search_target != 'users' and search_target != 'solutions':
      search_target = 'users'
  except:
    search_target = 'users'
  return render_to_response('search.html', {'search_target': search_target}, context_instance=RequestContext(request))
