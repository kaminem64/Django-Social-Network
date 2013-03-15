import datetime
from haystack.indexes import *
from haystack import site
from solutioner.solutions.models import Solution


class SolutionIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    datetime_added = DateTimeField(model_attr='datetime_added')

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return Solution.objects.filter(datetime_added__lte=datetime.datetime.now())


site.register(Solution, SolutionIndex)
