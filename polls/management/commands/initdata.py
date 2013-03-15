from django.core.management.base import BaseCommand, CommandError
from solutioner.polls.init_data import init_data

class Command(BaseCommand):
  def handle(self, *args, **options):
    try:
      
      self.stdout.write('%s\n' % init_data() )
    except:
      raise CommandError('Error')

