from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import datetime
from solutioner.users.models import Ownership
from solutioner.rbac.models import RBACOperation





class EventManager(models.Manager):
  def create_event(self, operator, object_inst, operation, operation_result):
    owner_ct, owner_id = Ownership.objects.get_ownership_ct_id(object_inst)
    
    object_own = Ownership.objects.get_ownership(object_inst)
    owner_own = Ownership.objects.get_ownership(object_own.owner)

    object_ct = ContentType.objects.get_for_model(object_inst)
    object_id = object_inst.id
    
    operator_ct = ContentType.objects.get_for_model(operator)
    operator_id = operator.id
    operator_own = Ownership.objects.get_ownership(operator)
    
    operation = RBACOperation.objects.get(name=operation)
    operation_result_ct = ContentType.objects.get_for_model(operation_result)
    operation_result_id = operation_result.id
    operation_result_own = Ownership.objects.get_ownership(operation_result)
    
    event = Event.objects.create(owner_ct=owner_ct, owner_id=owner_id, owner_own=owner_own, object_ct=object_ct, object_id=object_id, object_own=object_own, operator_ct=operator_ct, operator_id=operator_id, operator_own=operator_own, operation=operation, operation_result_ct=operation_result_ct, operation_result_id=operation_result_id, operation_result_own=operation_result_own)
    from solutioner.events.views import notification_email
    notification_email(owner_ct=owner_ct, owner_id=owner_id, object_ct=object_ct, object_id=object_id, operator_ct=operator_ct, operator_id=operator_id, operation=operation, operation_result_ct=operation_result_ct, operation_result_id=operation_result_id)
    return event


class Event(models.Model):
  owner_ct = models.ForeignKey(ContentType, related_name='event_owner')
  owner_id = models.PositiveIntegerField()
  owner_own = models.ForeignKey(Ownership, related_name='event_owner_own')

  object_ct = models.ForeignKey(ContentType, related_name='event_object')
  object_id = models.PositiveIntegerField()
  object_own = models.ForeignKey(Ownership, related_name='event_object_own')
  
  operator_ct = models.ForeignKey(ContentType, related_name='event_operator')
  operator_id = models.PositiveIntegerField()
  operator_own = models.ForeignKey(Ownership, related_name='event_operator_own')
  
  operation = models.ForeignKey(RBACOperation)
  operation_result_ct = models.ForeignKey(ContentType, related_name='event_operation_result')
  operation_result_id = models.PositiveIntegerField()
  operation_result_own = models.ForeignKey(Ownership, related_name='operator_operation_result_own')

  datetime = models.DateTimeField(default=datetime.datetime.now)
  
  owner = generic.GenericForeignKey('owner_ct', 'owner_id')
  object = generic.GenericForeignKey('object_ct', 'object_id')
  operator = generic.GenericForeignKey('operator_ct', 'operator_id')
  operation_result = generic.GenericForeignKey('operation_result_ct', 'operation_result_id')

  objects = EventManager()

  class Meta:
    unique_together = ('owner_ct', 'owner_id', 'object_ct', 'object_id', 'operator_ct', 'operator_id', 'operation', 'operation_result_ct', 'operation_result_id', 'datetime')
   
  def __unicode__(self):
    return '%s | %s | %s | %s | %s | %s' % (self.owner, self.object, self.operator, self.operation, self.operation_result, self.datetime)

