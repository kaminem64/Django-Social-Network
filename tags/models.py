from django.db import models

class Tag(models.Model):
  name = models.CharField(blank=False, max_length=50)
  used_no = models.BigIntegerField(blank=True, null=True, default=0)
  is_suspended = models.BooleanField(default=False)
  is_deleted = models.BooleanField(default=False)
  
  def __unicode__(self):
    return '%s'%(self.name)
