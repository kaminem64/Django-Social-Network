from django.shortcuts import render_to_response
from solutioner.support.models import Message
from solutioner.support.forms import *
from django.http import HttpResponseRedirect
from django.template import RequestContext


def support_contactus(request):
  redirectTo = '/contactus/'
  if request.method =='POST':
    if request.user.is_authenticated():
      form = SupportMessageUsers(request.POST)
      if form.is_valid():
        posted = form.cleaned_data
        new_message = Message.objects.create(user=request.user, subject=posted['subject'], message=posted['message'])
        return render_to_response("contactus.html", {'title': 'Contact Us', 'done': True }, context_instance=RequestContext(request))
      else:
        return render_to_response("contactus.html", {'title': 'Contact Us', 'form': form }, context_instance=RequestContext(request))
    else:
      form = SupportMessage(request.POST)
      if form.is_valid():
        posted = form.cleaned_data
        new_message = Message.objects.create(fullname=posted['fullname'], email=posted['email'], subject=posted['subject'], message=posted['message'])
        return render_to_response("contactus.html", {'title': 'Contact Us', 'done': True }, context_instance=RequestContext(request))
      else:
        return render_to_response("contactus.html", {'title': 'Contact Us', 'form': form }, context_instance=RequestContext(request))

    return HttpResponseRedirect(redirectTo)
  else:
    if request.user.is_authenticated():
      form = SupportMessageUsers()
    else:
      form = SupportMessage()
    return render_to_response("contactus.html", {'title': 'Contact Us', 'form': form }, context_instance=RequestContext(request))

