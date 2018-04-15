# -*- coding: UTF-8 -*-
from django.db import models
from django.contrib.auth import models as authModel


# Create your models here.


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
    complete_time = models.DateTimeField(auto_now=True)
    operator = models.CharField(max_length=20)
    plan_workload = models.FloatField()
    used_workload = models.FloatField()
    assign_staffs = models.ManyToManyField(Staff, related_name='staff_version_plan')


class StagePlan(models.Model):
    version_plan = models.ForeignKey(VersionPlan, related_name='version_plan_stage_plan', on_delete=models.CASCADE)
    stage = models.CharField(max_length=50)
    actual_start_date = models.DateField(null=True)
    actual_end_date = models.DateField(null=True)
    plan_start_date = models.DateField(null=True)
    plan_end_date = models.DateField(null=True)
    plan_workload = models.FloatField()
    used_workload = models.FloatField()


class AssignActionRecord(models.Model):
    staff_name = models.CharField(max_length=100)
    version_plan_name = models.CharField(max_length=100)
    status = models.BooleanField(default=False)
    operator = models.CharField(max_length=100)
    disable_operator = models.CharField(max_length=100)
    version_plan_name = models.CharField(max_length=100)
    create_time = models.DateTimeField(auto_now_add=True)


