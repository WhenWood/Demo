# -*- coding: UTF-8 -*-

from django.http import HttpResponse
from TestModel.models import Requirement

def db_insert(request):
	item = Requirement(startover_no=1, pro_name='TEST系统', sys_name='TS-V1.1.2', thr_sys_test='10.0', thr_check_test='4.0', thr_mock_test='8.1')
	item.save()
	return HttpResponse(str(request)+"<p>数据添加成功！</p>")

def db_search(request):
	
	response = Requirement.objects.filter(id=1)
	print (response)
	response1 = ''
	mappingList = ['startover_no','pro_name','sys_name','thr_sys_test','thr_check_test','thr_mock_test']
	for item in response:
		for var in mappingList:
			response1 +="<p>" + var + ':' + str(item.__dict__[var]) + "<p>"
	return HttpResponse(response1)

