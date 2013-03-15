from django.shortcuts import render_to_response
from django.template import RequestContext
from solutioner.tags.models import Tag
from solutioner.solutions.views import per_page_creator

def tags_view(request, tag):
  output_dict = per_page_creator(request, Tag.objects.get(name=tag).solution_tags.filter(is_deleted=False), 'solution')
  output_dict_add = {'tag': tag}
  output_dict.update(output_dict_add)
  return render_to_response("tags_view.html", output_dict, context_instance=RequestContext(request))


def tags(request):
  output_dict = per_page_creator(request, Tag.objects, order='-used_no', default_per_no=25)
  return render_to_response("tags.html", output_dict, context_instance=RequestContext(request))

