from django.db import models

# Create your models here.
# 签报与需求条目记录
class Requirement(models.Model):
	startover_no = models.CharField(max_length=500)
	pro_name = models.CharField(max_length=500)
	sys_name = models.CharField(max_length=500)
	thr_sys_test = models.FloatField()
	thr_check_test = models.FloatField()
	thr_mock_test = models.FloatField()

# 各系统版本记录	
class ReleaseNote(models.Model):
	requirement_id = models.IntegerField()
	sys_name = models.CharField(max_length=500)
	create_time = models.DateField()
	update_time = models.DateField(null=True)
