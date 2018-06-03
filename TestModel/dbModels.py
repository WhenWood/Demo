# -*- coding: UTF-8 -*-
from django.db import models
from django.contrib.auth import models as authModel


# Create your models here.

class redmine_users(models.Model):
    id = models.IntegerField(primary_key=True, unique=True,db_index=True)
    login = models.CharField(max_length=100,null=True,blank=True)
    HASHED_PASSWORD = models.CharField(max_length=100,null=100,blank=True)
    FIRSTNAME = models.CharField(max_length=100,null=True,blank=True)
    LASTNAME = models.CharField(max_length=100,null=True,blank=True)
    MAIL = models.CharField(max_length=100,null=True,blank=True)
    ADMIN = models.CharField(max_length=100,null=True,blank=True)
    status = models.CharField(max_length=100,null=True,blank=True)
    LAST_LOGIN_ON = models.DateTimeField(null=True,blank=True)
    LANGUAGE = models.CharField(max_length=100,null=True,blank=True)
    AUTH_SOURCE_ID = models.CharField(max_length=100,null=True,blank=True)
    CREATED_ON = models.DateTimeField(null=True,blank=True)
    UPDATED_ON = models.DateTimeField(null=True,blank=True)
    TYPE = models.CharField(max_length=100,null=True,blank=True)
    IDENTITY_URL = models.CharField(max_length=100,null=True,blank=True)
    MAIL_NOTIFICATION = models.CharField(max_length=100,null=True,blank=True)
    SALT = models.CharField(max_length=255,null=True,blank=True)
    MUST_CHANGE_PASSWD = models.CharField(max_length=100,null=True,blank=True)
    PASSWD_CHANGED_ON = models.CharField(max_length=100,null=True,blank=True)

    class Meta:
        db_table = "redmine_users"


class Redmine_projects(models.Model):
    id = models.IntegerField(primary_key=True,unique=True,db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True,blank=True)
    homepage = models.TextField(null=True,blank=True)
    is_public = models.IntegerField(null=True,blank=True)
    parent_id = models.IntegerField(null=True,blank=True)
    created_on = models.DateTimeField(null=True,blank=True)
    updated_on = models.DateTimeField(null=True,blank=True)
    identifier = models.TextField(null=True,blank=True)
    status = models.IntegerField(null=True,blank=True)
    lft = models.IntegerField(null=True,blank=True)
    rgt = models.IntegerField(null=True,blank=True)
    inherit_members = models.IntegerField(null=True,blank=True)
    project_meeting_rooms = models.IntegerField(null=True,blank=True)
    project_name_view = models.IntegerField(null=True,blank=True)
    sys_name = models.CharField(max_length=255,null=True,blank=True)
    version = models.CharField(max_length=255,null=True,blank=True)
    plan_starttime = models.DateTimeField(null=True,blank=True)
    plan_endtime = models.DateTimeField(null=True,blank=True)
    starttime = models.DateTimeField(null=True,blank=True)
    endtime = models.DateTimeField(null=True,blank=True)
    othersys = models.TextField(null=True,blank=True)

    class Meta:
        db_table = "Redmine_projects"


class Staff(models.Model):
    name = models.CharField(max_length=50)
    status = models.IntegerField(10)
    type = models.IntegerField(default=10)
    publish_plan_id = models.IntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(authModel.User, related_name='user_staff', on_delete=models.CASCADE)


class Workload(models.Model):
    staff_name = models.CharField(max_length=25)
    version_name = models.CharField(max_length=100)
    stage = models.CharField(max_length=10)
    test_case_number = models.IntegerField(default=0)
    defect_number = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)
    day_off = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class VersionPlan(models.Model):
    version_name = models.CharField(max_length=100)
    status = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    create_user = models.CharField(max_length=100)
    update_user = models.CharField(max_length=100)
    plan_workload = models.FloatField(null=True)
    used_workload = models.FloatField(null=True)
    sys_name = models.CharField(max_length=255,null=True,blank=True)
    sys_version = models.CharField(max_length=255,null=True,blank=True)
    assign_staffs = models.ManyToManyField(Staff, related_name='staff_version_plan')
    redmine_project = models.ForeignKey(Redmine_projects, null=True, related_name='redmine_project_version_plan', on_delete=models.CASCADE)


class StagePlan(models.Model):
    version_plan = models.ForeignKey(VersionPlan, related_name='version_plan_stage_plan', on_delete=models.CASCADE)
    stage = models.CharField(max_length=50)
    actual_start_date = models.DateField(null=True)
    actual_end_date = models.DateField(null=True)
    plan_start_date = models.DateField()
    plan_end_date = models.DateField()
    plan_workload = models.FloatField(null=True)
    used_workload = models.FloatField(null=True)
    operator = models.CharField(max_length=100)


class AssignActionRecord(models.Model):
    staff_name = models.CharField(max_length=100)
    version_plan_name = models.CharField(max_length=100)
    status = models.BooleanField(default=False)
    operator = models.CharField(max_length=100)
    disable_operator = models.CharField(max_length=100)
    create_time = models.DateTimeField(auto_now_add=True)
    disable_time = models.DateTimeField(null=True)


class StaffGroup(models.Model):
    group_owner = models.ForeignKey(authModel.User, related_name='user_group', on_delete=models.CASCADE)
    group_name = models.CharField(unique=True, max_length=100, default='default_group')
    status = models.BooleanField(default=True)


class GroupVersionAuth(models.Model):
    group = models.ForeignKey(StaffGroup, related_name='staff_group_version_auth', on_delete=models.CASCADE)
    redmine_system = models.CharField(max_length=255)
    operator = models.CharField(max_length=100)


class GroupOperateAuth(models.Model):
    user = models.ForeignKey(authModel.User, related_name='user_group_operate_auth', on_delete=models.CASCADE)
    group = models.ForeignKey(StaffGroup, related_name='staff_group_operate_auth', on_delete=models.CASCADE)
    user_type = models.IntegerField(null=True, blank=True)
    operator = models.CharField(max_length=100)

