from django.shortcuts import render_to_response
from django.template import RequestContext
from solutioner.categories.models import Category
from solutioner.solutions.models import Solution
from solutioner.solutions.views import per_page_creator

def categories_view(request, category):
  output_dict = per_page_creator(request, Solution.objects.filter(category=Category.objects.get(name=category)), table_type='solution')
  output_dict_add = {'category': category}
  output_dict.update(output_dict_add)
  return render_to_response("categories_view.html", output_dict, context_instance=RequestContext(request))
  
def categories(request):
  output_dict = per_page_creator(request, Category.objects, order='name')
  return render_to_response("categories.html", output_dict, context_instance=RequestContext(request))
