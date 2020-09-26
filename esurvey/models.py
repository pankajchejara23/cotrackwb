from django.db import models
from django.contrib.auth.models import User
import uuid
from django.contrib import admin
import datetime
import os

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return os.path.join(
      "session_%d" % instance.session,"group_%d" % instance.group, "user_%s" % instance.user, filename)


class Session(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    groups = models.IntegerField()
    description = models.CharField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)


class Audiofl(models.Model):
    session = models.IntegerField(blank=True)
    group = models.IntegerField(blank=True)
    user = models.CharField(max_length=250)
    sequence = models.IntegerField(blank=True)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    fl = models.FileField(upload_to=user_directory_path, blank=True, )


class SessionPin(models.Model):
    session = models.OneToOneField(Session, on_delete=models.CASCADE)
    pin = models.CharField(max_length=6)

# Create your models here.
class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    questionnaire_type  = models.CharField(default=False,max_length=100)
    project_name = models.CharField(max_length=100)
    test_project = models.BooleanField(max_length=100)
    project_type = models.IntegerField()
    project_status = models.BooleanField()
    archived = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)



class Survey(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    survey_name = models.CharField(max_length=100)
    product_name = models.CharField(max_length=200)
    product_type = models.CharField(max_length=200)
    product_industry = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=200)
    paragraph = models.TextField(max_length=1000)



class Link(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    url = models.UUIDField(default=uuid.uuid4)
    sequence = models.IntegerField()


class Submission(models.Model):
    link = models.ForeignKey(Link,on_delete=models.CASCADE)
    sub_date = models.DateField(default=datetime.date.today)
    q1 = models.IntegerField()
    q2 = models.IntegerField()
    q3 = models.IntegerField()
    q4 = models.IntegerField()
    q5 = models.IntegerField()
    q6 = models.IntegerField()
    q7 = models.IntegerField()
    q8 = models.IntegerField()
    q9 = models.IntegerField()
    q10 = models.IntegerField()
    q11 = models.IntegerField()
    q12 = models.IntegerField()
    q13 = models.IntegerField()
    q14 = models.IntegerField()

class AnonyData(models.Model):
    submission = models.OneToOneField(Submission,on_delete=models.CASCADE)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)


admin.site.register(Project)
admin.site.register(Survey)
admin.site.register(Link)
admin.site.register(Submission)
admin.site.register(Audiofl)
admin.site.register(Session)
