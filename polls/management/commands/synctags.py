from django.core.management.base import BaseCommand, CommandError
from solutioner.solutions.views import sync_tag_used_no

class Command(BaseCommand):
  def handle(self, *args, **options):
    try:
      used_no = sync_tag_used_no()
      self.stdout.write('Successfully done. %s tag_no been updated.\n' % used_no)
    except:
      raise CommandError('Error')

