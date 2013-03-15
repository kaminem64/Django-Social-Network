from django.core.management.base import BaseCommand, CommandError
from solutioner.solutions.views import sync_user_score

class Command(BaseCommand):
  def handle(self, *args, **options):
    try:
      status = sync_user_score()
      self.stdout.write('%s\n' % status)
    except:
      raise CommandError('Error')

