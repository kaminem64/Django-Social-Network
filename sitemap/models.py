from django.contrib.sitemaps import Sitemap
from solutioner.solutions.models import Solution

class SolutionSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Solution.objects.filter(is_deleted=0)

    def lastmod(self, obj):
        return obj.datetime_added
