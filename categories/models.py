from django.db import models

class Category(models.Model):
  name = models.CharField(max_length=10000)
  related_to = models.CharField(blank=True, max_length=10000)
  
  def __unicode__(self):
    return self.name
