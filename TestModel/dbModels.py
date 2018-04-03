# -*- coding: UTF-8 -*-
from django.db import models


# Create your models here.
# 签报与需求条目记录
class Requirement(models.Model):
    startover_no = models.CharField(max_length=500)
    pro_name = models.CharField(max_length=500)
    sys_name = models.CharField(max_length=500)
    sys_id = models.IntegerField(default=10)
    thr_sys_test = models.FloatField()
    thr_check_test = models.FloatField()
    thr_mock_test = models.FloatField()


# 各系统小版本 版本记录	
class ReleaseNote(models.Model):
    requirement_id = models.IntegerField(default=0)
    sys_name = models.CharField(max_length=500)
    sys_id = models.IntegerField(default=0)
    create_time = models.DateField(auto_now_add=True)
    update_time = models.DateField(null=True)


class Staff(models.Model):
    name = models.CharField(max_length=50)
    status = models.IntegerField(10)
    type = models.IntegerField(default=10)
    publish_plan_id = models.IntegerField(default=0)
    create_time = models.DateField(auto_now_add=True)
    update_time = models.DateField(auto_now=True)


class PublishPlan(models.Model):
    sys_id = models.IntegerField(default=0)
    sys_name = models.CharField(max_length=500)
    stage = models.CharField(max_length=10)
    status = models.BooleanField()
    plan_start_date = models.DateField()
    actual_start_date = models.DateField(null=True)
    plan_end_date = models.DateField()
    actual_end_date = models.DateField(null=True)
    create_time = models.DateField(auto_now_add=True)
    update_time = models.DateField(auto_now=True)


class AssignVersion(models.Model):
    staff_id = models.IntegerField(default=0)
    staff_name = models.CharField(max_length=500)
    publish_plan_id = models.IntegerField(10)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    status = models.BooleanField(False)
    create_time = models.DateField(auto_now_add=True)
    update_time = models.DateField(auto_now=True)
