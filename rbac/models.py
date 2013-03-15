from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ObjectDoesNotExist
from solutioner.users.models import User as User_info
from django.core.cache import cache


def _get_permission(queryset_model, filters, roles):
  try:
    permission = queryset_model.objects.get(**filters)
  # If permission does not exist, authorization is not allowed
  except ObjectDoesNotExist:
    return False
  else:
    perm_roles = permission.roles.all()
    return True if filter(lambda x: x in perm_roles, roles) else False

def is_liker(owner, operator_user):
  if owner in User_info.objects.get(user=operator_user).following.all():
    return True
  else:
    return False
  return False

def get_user_roles(owner, operator_user):
  roles = []
  roles.append(RBACRole.objects.get(name='public'))
  if operator_user.is_authenticated():
    if is_liker(owner, operator_user):
      roles.append(RBACRole.objects.get(name='followers'))
    if owner == operator_user:
      roles.append(RBACRole.objects.get(name='followers'))
      roles.append(RBACRole.objects.get(name='myself'))
  return roles

class RBACPermissionManager(models.Manager):

  def _get_filters(self, owner, model_inst, operation):
    owner_ct = ContentType.objects.get_for_model(owner)
    model_ct = ContentType.objects.get_for_model(model_inst)
    filters = {'owner_ct': owner_ct, 'owner_id': owner.id,
           'object_ct': model_ct, 'object_id': model_inst.id,
           'operation': operation}
    return filters

  def get_permission(self, owner, model, operation, roles):
    filters = self._get_filters(owner, model, operation)
    queryset_model = RBACPermission
    return _get_permission(queryset_model, filters, roles)

  def create_permission(self, owner, model_inst, operation, roles):
    filters = self._get_filters(owner, model_inst, operation)
    permission, c = RBACPermission.objects.get_or_create(**filters)
    permission.roles.clear()
    for role in roles:
      permission.roles.add(role)
    return permission


class RBACGenericPermissionManager(models.Manager):

  def get_user_roles(self, owner, operator_user, use_cache=False):
    cached_roles = cache.get('%s-%s'%(owner.username, operator_user.username)) if use_cache else False
    if cached_roles:
      return cached_roles
    else:
      roles = []
      roles.append(RBACRole.objects.get(name='public'))
      if operator_user.is_authenticated():
        if is_liker(owner, operator_user):
          roles.append(RBACRole.objects.get(name='followers'))
        if owner == operator_user:
          roles.append(RBACRole.objects.get(name='followers'))
          roles.append(RBACRole.objects.get(name='myself'))
      if use_cache:
        cache.set( '%s-%s'%(owner.username, operator_user.username), roles, 3)
      return roles

  def _get_filters(self, owner, model, operation):
    owner_ct = ContentType.objects.get_for_model(owner)
    model_ct = ContentType.objects.get_for_model(model)
    filters = {'owner_ct': owner_ct, 'owner_id': owner.id,
           'content_type': model_ct, 'operation': operation}
    return filters

  def get_permission_setting(self, owner, model, operation):
    operation = RBACOperation.objects.get(name=operation)
    try:
      filters = self._get_filters(owner, model, operation)
      permission = RBACGenericPermission.objects.get(**filters)
      return permission.roles.all()[0]
    except:
      return '1'
    
  def get_permission(self, owner, model, operation, roles):
    operation = RBACOperation.objects.get(name=operation)
    filters = self._get_filters(owner, model, operation)
    queryset_model = RBACGenericPermission
    return _get_permission(queryset_model, filters, roles)

  def get_user_permission(self, owner, model, operation, operator_user, use_cache=False):
    return self.get_permission(owner, model, operation, self.get_user_roles(owner, operator_user, use_cache=use_cache))
  
  def create_permission(self, owner, model, operation, roles):
    operation = RBACOperation.objects.get(name=operation)
    filters = self._get_filters(owner, model, operation)
    permission, c = RBACGenericPermission.objects.get_or_create(**filters)
    permission.roles.clear()
    for role in roles:
      permission.roles.add(role)
    return permission


class RBACOperation(models.Model):
  name = models.CharField(max_length=30, unique=True)
  desc = models.CharField(max_length=150, blank=True)

  def __unicode__(self):
    return '%s' % self.name


class RBACRole(models.Model):
  name = models.CharField(max_length=30, unique=True)
  desc = models.CharField(max_length=150, blank=True)

  def __unicode__(self):
    return '%s' % self.name


class RBACPermission(models.Model):
  owner_ct = models.ForeignKey(ContentType, related_name='permission_owner')
  owner_id = models.PositiveIntegerField()
  object_ct = models.ForeignKey(ContentType, related_name='permission_object')
  object_id = models.PositiveIntegerField()
  operation = models.ForeignKey(RBACOperation)
  roles = models.ManyToManyField(RBACRole, related_name='permissions')

  owner = generic.GenericForeignKey('owner_ct', 'owner_id')
  object = generic.GenericForeignKey('object_ct', 'object_id')

  objects = RBACPermissionManager()

  class Meta:
    unique_together = ('owner_ct', 'owner_id', 'object_ct', 'object_id', 'operation')
   
  def __unicode__(self):
    return '%s | %s | %s' % (self.owner, self.object, self.operation)


class RBACGenericPermission(models.Model):
  owner_ct = models.ForeignKey(ContentType, related_name='generic_permission_owner')
  owner_id = models.PositiveIntegerField()
  content_type = models.ForeignKey(ContentType, related_name='generic_permission_model')
  operation = models.ForeignKey(RBACOperation)
  roles = models.ManyToManyField(RBACRole, related_name='generic_permissions')

  owner = generic.GenericForeignKey('owner_ct', 'owner_id')

  objects = RBACGenericPermissionManager()

  class Meta:
    unique_together = ('owner_ct', 'owner_id', 'content_type', 'operation')
  
  def __unicode__(self):
    return '%s | %s | %s' % (self.owner, self.content_type, self.operation)


