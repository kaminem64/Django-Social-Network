# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from solutioner.views import *
from solutioner.users.views import *
from solutioner.solutions.views import *
from solutioner.tags.views import *
from solutioner.categories.views import *
#from solutioner.comments.views import *
import os
from django.conf import settings
from django.shortcuts import render_to_response
from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()
from solutioner.sitemap.models import *
from solutioner.support.views import *
from solutioner.comments.views import *
from solutioner.events.views import *
from solutioner.widgets.views import *
from django.utils import simplejson
from solutioner.search.views import *


def alexa_confirm(request):
  return render_to_response('o0vyQVHfO3qLHSIFLr79SDqNZIo.html')
  
def robots_txt(request):
  return render_to_response('robots.txt', mimetype="text/plain")

sitemaps = {
    'solutions': SolutionSitemap,
}
urlpatterns = patterns('django.contrib.sitemaps.views',
    (r'^sitemap\.xml$', 'index', {'sitemaps': sitemaps}),
    (r'^sitemap-(?P<section>.+)\.xml$', 'sitemap', {'sitemaps': sitemaps}),
)


from sorl.thumbnail import get_thumbnail
from django.http import HttpResponse
def thumbnailer(request,wsize, hsize, url):
  size = unicode(wsize)+'x'+unicode(hsize)
  im = get_thumbnail(url, size, crop='center', quality=100)
  return HttpResponse(im.read(), mimetype="image/jpeg")




from solutioner.tags.models import Tag

def jauto(request):
  q = unicode(request.GET['search'])
  tags_found1 = Tag.objects.filter(name__istartswith=q).order_by('-used_no', 'name')[:4]
  tags_found2 = []
  tags_count = tags_found1.count()
  if tags_count < 4:
    r = 4 - tags_count
    tags_found2 = Tag.objects.filter(name__icontains=q).exclude(name__istartswith=q).order_by('-used_no', 'name')[:r]
  tags_found = list(tags_found1) + list(tags_found2)
  jjson = simplejson.dumps(map(unicode, tags_found))
  return HttpResponse(jjson, mimetype='application/json')



from django.conf.urls.defaults import *
from django.contrib.auth.views import password_reset
from solutioner.users.views import RegisterWizard
from solutioner.users.forms import RegisterForm, RegisterCaptchaForm

urlpatterns += patterns('',
  url(r'^admin/', include(admin.site.urls)),
  #url(r'^comments/', include('django.contrib.comments.urls')),
  url(r'^$', home),
  url(r'^login/$', login),
  url(r'^logout/$', logout),
  url(r'^register/$', RegisterWizard.as_view([RegisterForm, RegisterCaptchaForm] )),
  #url(r'^register/$', register_testver),
  #url(r'^addcomment/$', add_comment),
  url(r'^solutions/add/$', add_solution),
  url(r'^profile/([.\w\d]+)/info/$', profile_info),
  url(r'^profile/edit/$', edit_profile),
  url(r'^profile/edit/password/change/$', change_password),
  url(r'^profile/edit/privacy/settings/$', privacy_settings),
  url(r'^profile/edit/notifications/settings/$', notifications_settings),
  url(r'^profile/([.\w\d]+)/solutions/$', profile_solutions),
  url(r'^profile/([.\w\d]+)/$', profile_desk),
  url(r'^profile/([.\w\d]+)/desk/$', profile_desk),
  url(r'^profile/([.\w\d]+)/scores/$', profile_scores),
  url(r'^profile/([.\w\d]+)/votes/$', profile_votes),
  url(r'^profile/([.\w\d]+)/follow/$', profile_follow),
  url(r'^graphs/([.\w\d]+)/desk_comments/$', desk_comments),
  url(r'^graphs/comments/(\d+)/$', get_comment_by_id),
  url(r'^graphs/comments/(\d+)/([.\w\d]+)/$', get_comment_by_id),
  url(r'^solutions/view/(\d+)/$', view_solution),
  url(r'^solutions/edit/(\d+)/$', edit_solution), 
  url(r'^ajax/solutions/vote/(\d+)/$', ajax_sol_vote),
  url(r'^graphs/solution/(\d+)/$', graphs_solution),
  url(r'^graphs/user/([.\w\d]+)/$', graphs_user),
  url(r'^solutions/view/$', solutionList),
  #url(r'^search/$', include('haystack.urls')),
  url(r'^search/$', search_page),
  url(r'^tags/(.+)/$', tags_view),
  url(r'^tags/$', tags),
  url(r'^categories/$', categories),
  url(r'^categories/(.+)/$', categories_view),
  url(r'^o0vyQVHfO3qLHSIFLr79SDqNZIo.html/$', alexa_confirm),
  url(r'^robots.txt/$', robots_txt),
  url(r'^graphs/([.\w\d]+)/solutions/$', graphs_user_solutions),
  url(r'^rm_solution/$', rm_solution),
  url(r'^rm_comment/$', rm_comment),
  url(r'^thumbs/(\d+)x(\d+)/(.+)$', thumbnailer),
  url(r'^follow/$', user_follow),
  url(r'^ajax/follow/$', user_follow),
  url(r'^ajax/jauto/$', jauto),
  url(r'^profile/edit/password/reset/$', password_reset, {'post_reset_redirect': '/'}),
  url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', {'post_reset_redirect': '/logout/' }),
  url(r'^developers/$', developers),
  url(r'^licenses/$', licenses),
  url(r'^termsofservice/$', terms_of_service),
  url(r'^privacypolicy/$', privacy_policy),
  url(r'^aboutus/$', about_us),
  url(r'^contactus/$', support_contactus),
  url(r'^ajax/notifications/$', notifications),
  url(r'^ajax/last_checked/$', last_checked),
  url(r'^notifications/$', notifications_page),
  url(r'^graphs/home_events/$', get_home_events),
  url(r'^graphs/([.\w\d]+)/profile_events/$', get_profile_events),
  url(r'^solutions/fork/$', fork_solution),
  url(r'^ajax/follow_suggest/$', follow_suggest),
  url(r'^ajax/friend_finder/$', friend_finder),
  url(r'^ajax/solutions/(\d+)/view/comments/$', solution_comments),

  

  

)


