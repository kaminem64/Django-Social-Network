from django.db import models
from django.contrib.auth.models import User as authUser
from solutioner.solutions.models import Solution
from solutioner.users.models import ExternalUser

class Score(models.Model):
  user = models.ForeignKey(authUser, blank=True, null=True, default=None, related_name='score_user')
  external_user = models.ForeignKey(ExternalUser, blank=True, null=True, default=None, related_name='score_externalusers')
  votes_count = models.BigIntegerField(blank=True, null=True, default=0)
  voted = models.BigIntegerField(blank=True, null=True, default=0)
  voted_count = models.BigIntegerField(blank=True, null=True, default=0)
  views_count = models.BigIntegerField(blank=True, null=True, default=0)
  viewed_count = models.BigIntegerField(blank=True, null=True, default=0)
  solutions_count = models.BigIntegerField(blank=True, null=True, default=0)

  def __unicode__(self):
    return '%s'%(self.user)
