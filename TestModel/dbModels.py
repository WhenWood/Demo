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
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(null=True)


class Staff(models.Model):
    name = models.CharField(max_length=50)
    status = models.IntegerField(10)
    type = models.IntegerField(default=10)
    publish_plan_id = models.IntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class PublishPlan(models.Model):
    sys_name = models.CharField(max_length=500)
    status = models.BooleanField()
    st_actual_start_date = models.DateField(null=True)
    st_actual_end_date = models.DateField(null=True)
    uat1_actual_start_date = models.DateField(null=True)
    uat1_actual_end_date = models.DateField(null=True)
    uat2_actual_start_date = models.DateField(null=True)
    uat2_actual_end_date = models.DateField(null=True)
    mt_actual_start_date = models.DateField(null=True)
    mt_actual_end_date = models.DateField(null=True)
    st_plan_start_date = models.DateField(null=True)
    st_plan_end_date = models.DateField(null=True)
    uat1_plan_start_date = models.DateField(null=True)
    uat1_plan_end_date = models.DateField(null=True)
    uat2_plan_start_date = models.DateField(null=True)
    uat2_plan_end_date = models.DateField(null=True)
    mt_plan_start_date = models.DateField(null=True)
    mt_plan_end_date = models.DateField(null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class AssignVersion(models.Model):
    staff_id = models.IntegerField(default=0)
    staff_name = models.CharField(max_length=500)
    publish_plan_id = models.IntegerField(10)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    status = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class SystemVersion(models.Model):
    sys_id = models.IntegerField(default=0)
    sys_name = models.CharField(max_length=500)
    version = models.CharField(max_length=25)
    status = models.BooleanField(default=False)
    plan_start_date = models.DateField()
    actual_start_date = models.DateField()
    plan_end_date = models.DateField()
    actual_end_date = models.DateField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


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


