from django.db import models
from django.contrib.auth.models import User
import datetime


class Message(models.Model):
  user = models.ForeignKey(User, blank=True, null=True, default=None)
  fullname = models.CharField(max_length=100, blank=True, null=True, default=None)
  email = models.CharField(max_length=75, blank=True, null=True, default=None)
  subject = models.CharField(max_length=200, blank=True, null=True, default=None)
  message = models.TextField()
  datetime_added = models.DateTimeField(default=datetime.datetime.now)
  is_deleted = models.BooleanField(default=False)

