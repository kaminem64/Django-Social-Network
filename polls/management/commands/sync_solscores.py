from django.core.management.base import BaseCommand, CommandError
from solutioner.solutions.views import sync_sol_score

class Command(BaseCommand):
  def handle(self, *args, **options):
    try:
      status = sync_sol_score()
      self.stdout.write('%s\n' % status)
    except:
      raise CommandError('Error')

