from django.contrib.auth.models import User
from django.db import models
from stdimage import StdImageField


# Create your models here.


class StaffGroup(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)
    isDeleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'a) User Group List'


class StaffUser(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    photo = StdImageField(upload_to='photo/img', blank=True, variations={
        'large': (600, 400),
        'thumbnail': (50, 50, True),
        'medium': (300, 200),
    }, delete_orphans=True)
    idProof = StdImageField(upload_to='photo/img', blank=True, variations={
        'large': (600, 400),
        'thumbnail': (50, 50, True),
        'medium': (300, 200),
    }, delete_orphans=True)
    phone = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.CharField(max_length=200, blank=True, null=True)
    username = models.CharField(max_length=200, blank=True, null=True)
    userPassword = models.CharField(max_length=200, blank=True, null=True)
    group = models.CharField(max_length=200, blank=True, null=True)
    user_ID = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    isActive = models.CharField(max_length=200, blank=True, null=True)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)
    isDeleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'b) User List'
