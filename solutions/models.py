from django.db import models
from django.contrib.auth.models import User as authUser
from solutioner.categories.models import Category
import datetime
from solutioner.users.models import ExternalUser, Ownership
from solutioner.tags.models import Tag
from solutioner.users.models import Source
from solutioner.events.models import Event
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class ExternalUrl(models.Model):
  url = models.CharField(max_length=200)
  
  def __unicode__(self):
    return '%s'%(self.url)


class SolutionManager(models.Manager):
  def create_solution(self, owner_inst, source, category, problem, problem_desc, solution, is_published=True):
    owner_ct, owner_id = Ownership.objects.get_ownership_ct_id(owner_inst)
    owner_own = Ownership.objects.get_ownership(owner_inst)
    
    solution = Solution.objects.create(owner_ct=owner_ct, owner_id=owner_id, owner_own=owner_own, source=source, category=category, problem=problem, problem_desc=problem_desc, solution=solution, is_published=is_published)
    ownership = Ownership.objects.create_ownership(owner_inst, solution)
    solution.ownership = ownership
    solution.save()
    Event.objects.create_event(operator=owner_inst, object_inst=owner_inst, operation='add_solution', operation_result=solution)
    return solution
  

class Solution(models.Model):
  ownership = models.ForeignKey(Ownership, blank=True, null=True, default=None, related_name='solution_ownership')
  owner_ct = models.ForeignKey(ContentType, related_name='solution_owner')
  owner_id = models.PositiveIntegerField()
  owner_own = models.ForeignKey(Ownership, related_name='solution_owner_own')
  source = models.ForeignKey(Source)
  category =  models.ForeignKey(Category)
  problem = models.CharField(max_length=200)
  problem_desc = models.TextField()
  solution = models.TextField()
  tags = models.ManyToManyField(Tag, related_name='solution_tags')
  votes_sum = models.BigIntegerField(blank=True, null=True, default=0)
  votes_count = models.BigIntegerField(blank=True, null=True, default=0)
  viewed = models.BigIntegerField(blank=True, null=True, default=0)
  datetime_added = models.DateTimeField(default=datetime.datetime.now)
  is_published = models.BooleanField(default=True)
  is_suspended = models.BooleanField(default=False)
  is_deleted = models.BooleanField(default=False)
  
  owner = generic.GenericForeignKey('owner_ct', 'owner_id')

  site = models.ForeignKey(Site,default=1)
  objects = models.Manager()
  on_site = CurrentSiteManager()

  objects = SolutionManager()

  def get_absolute_url(self):
    return "/solutions/view/%i/" % self.id
  
  def __unicode__(self):
    return '%s, %s'%(self.id, self.problem)
    

class VoteManager(models.Manager):
  def get_or_create_vote(self,solution, solution_owner, user):
    c = False
    try:
      vote = Vote.objects.get(solution=solution, solution_owner=solution_owner, user=user)
      if vote.is_deleted:
        c = True
        vote.is_deleted = False
        vote.save()
        event = Event.objects.create_event(operator=user, object_inst=solution, operation='vote_solution', operation_result=vote)
    except:
      c = True
      vote = Vote.objects.create(solution=solution, solution_owner=solution_owner, user=user)
      ownership, d = Ownership.objects.get_or_create_ownership(solution_owner, vote) #FIXME user or solution_owner?
      vote.ownership = ownership
      vote.save()
      event = Event.objects.create_event(operator=user, object_inst=solution, operation='vote_solution', operation_result=vote)
      
    return vote, c


class Vote(models.Model):
  ownership = models.ForeignKey(Ownership, blank=True, null=True, default=None, related_name='vote_ownership')
  solution = models.ForeignKey(Solution, related_name='votes_solutions_voted')
  user = models.ForeignKey(authUser, related_name='votes_vote_owner')
  solution_owner = models.ForeignKey(authUser, related_name='votes_solution_owner')
  vote = models.IntegerField(default=0)
  datetime = models.DateTimeField(default=datetime.datetime.now)
  is_suspended = models.BooleanField(default=False)
  is_deleted = models.BooleanField(default=False)

  objects = VoteManager()
  
  
  
