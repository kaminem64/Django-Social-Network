from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import datetime
from solutioner.users.models import Ownership
from solutioner.events.models import Event
from solutioner.rbac.models import RBACRole, RBACOperation, RBACGenericPermission, get_user_roles
from django.contrib.auth.models import User



class CommentManager(models.Manager):
  def create_comment(self, request, operator, object_inst, message, operation):
    owner_ct, owner_id = Ownership.objects.get_ownership_ct_id(object_inst)

    object_own = Ownership.objects.get_ownership(object_inst)
    owner_own = Ownership.objects.get_ownership(object_own.owner)

    object_ct = ContentType.objects.get_for_model(object_inst)
    object_id = object_inst.id

    operator_ct = ContentType.objects.get_for_model(operator)
    operator_id = operator.id

    operator_own = Ownership.objects.get_ownership(operator)

    comment = Comment.objects.create(owner_ct=owner_ct, owner_id=owner_id, owner_own=owner_own, object_ct=object_ct, object_id=object_id, object_own=object_own, operator_ct=operator_ct, operator_id=operator_id, operator_own=operator_own, message=message)

    ownership = Ownership.objects.create_ownership(request.user, comment)
    comment.ownership = ownership
    comment.save()
    
    Event.objects.create_event(operator=request.user, object_inst=object_inst, operation=operation, operation_result=comment)
    
    return comment



class Comment(models.Model):
  ownership = models.ForeignKey(Ownership, blank=True, null=True, default=None, related_name='comment_ownership')

  owner_ct = models.ForeignKey(ContentType, related_name='comment_owner')
  owner_id = models.PositiveIntegerField()
  owner_own = models.ForeignKey(Ownership, related_name='comment_owner_own')

  object_ct = models.ForeignKey(ContentType, related_name='comment_object')
  object_id = models.PositiveIntegerField()
  object_own = models.ForeignKey(Ownership, related_name='comment_object_own')

  operator_ct = models.ForeignKey(ContentType, related_name='comment_operator')
  operator_id = models.PositiveIntegerField()
  operator_own = models.ForeignKey(Ownership, related_name='comment_operator_own')

  message = models.CharField(max_length=1000)

  datetime = models.DateTimeField(default=datetime.datetime.now)
  is_suspended = models.BooleanField(default=False)
  is_deleted = models.BooleanField(default=False)
  
  owner = generic.GenericForeignKey('owner_ct', 'owner_id')
  object = generic.GenericForeignKey('object_ct', 'object_id')
  operator = generic.GenericForeignKey('operator_ct', 'operator_id')

  objects = CommentManager()

  def __unicode__(self):
    return '%s | %s | %s | %s | %s' % (self.owner, self.object, self.operator, self.message, self.datetime)

