from Demo.Model.PlanOpertate import PlanOperate
from Demo.Model.StaffOperate import StaffOperate
from TestModel.dbModels import VersionPlan
from django.urls import path
from django.http import HttpResponseRedirect, HttpResponse
from Demo.Model.Auth import Auth
from django.template.response import TemplateResponse
import traceback
import datetime
from django.db.models import Q
from django.core.files.uploadedfile import InMemoryUploadedFile


class PlanController:

    def index(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('%s?next=%s' % ('/admin/login/?next=', request.path))

        if request.method == 'POST':
            pass
        else:
            if 'type' in request.GET:
                view_type = request.GET['type']
            else:
                view_type = 'list'

            versions = VersionPlan.objects.filter(status=True).order_by('-update_time')
            version_infos = []
            for version in versions:
                plan = PlanOperate(request.user, version)
                stage_obj = []
                for stage in plan.stage_plans:
                    stage_obj.append(dict(
                        stage=stage.stage,
                        actual_start_date=stage.actual_start_date,
                        actual_end_date=stage.actual_end_date,
                        plan_start_date=stage.plan_start_date,
                        plan_end_date=stage.plan_end_date,
                        plan_workload=stage.plan_workload,
                        used_workload=stage.used_workload,
                    ))


                version_infos.append({
                    'site': '/version_plan/edit?version_name='+version.version_name,
                    'name': version.version_name,
                    'stage': stage_obj,
                    'row': len(stage_obj)
                })
            context = dict({
                'version_infos': version_infos,
                'type': view_type,
                'types': [{'site': 'index?type=list', 'name': "列表模式"},
                          {'site': 'table?type=table', 'name': "表格模式"}],
            })
            return TemplateResponse(request, 'plan/index.html', context)

    def table_view(self, request):
        start_date = ''
        if 'start_date' in request.GET:
            start_date = request.GET['start_date']
        date_list = self.get_thirty_days(start_date)
        versions = VersionPlan.objects.filter(status=True)
        version_infos = []
        for version in versions:
            stage_obj_plan = ['' for i in range(0, 30)]
            stage_obj_actual = ['' for i in range(0, 30)]
            plan = PlanOperate(request.user, version)
            for stage in plan.stage_plans:
                if stage.plan_start_date > date_list[-1] or \
                        stage.plan_end_date < date_list[0]:
                    continue
                start_pos = max(0, (stage.plan_start_date-date_list[0]).days)
                end_pos = min(30, (stage.plan_end_date-date_list[-1]).days)
                stage_obj_plan[start_pos:end_pos] = [i + ' ' + stage.stage for i in stage_obj_plan[start_pos:end_pos]]
                if stage.actual_start_date:
                    start_pos = max(0, (stage.actual_start_date-date_list[0]).days)
                    if stage.actual_end_date:
                        end_pos = min(30, (stage.actual_end_date-date_list[-1]).days)
                    else:
                        end_pos = start_pos
                    stage_obj_actual[start_pos:end_pos] = [i + ' ' + stage.stage for i in stage_obj_actual[start_pos:end_pos]]
            version_infos.append({
                'site': '/version_plan/edit?version_name='+version.version_name,
                'name': version.version_name,
                'stage_plan': stage_obj_plan,
                'stage_actual': stage_obj_actual,
                'row': 2
            })
        context = dict({
            'date_list': date_list,
            'version_infos': version_infos,
            'type': 'table',
            'types': [{'site': 'index?type=list', 'name': "列表模式"},
                      {'site': 'table?type=table', 'name': "表格模式"}],
        })
        return TemplateResponse(request, 'plan/table.html', context)

    def get_thirty_days(self, date_str=''):
        if date_str == '':
            start_date = datetime.datetime.now().date()
        else:
            start_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        end_date = datetime.timedelta(days=+30)+start_date
        dateList = []
        for i in range(0, 30):
            dateList.append(start_date+datetime.timedelta(days=+i))
        return dateList

    def add(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('%s?next=%s' % ('/admin/login/?next=', request.path))
        plan = PlanOperate(request.user)
        if request.method == 'POST':
            if request.POST['action'] == 'add_version':
                version_info = {}
                version_info['version_name'] = request.POST['version_name']
                version_info['plan_workload'] = float(request.POST['plan_workload'])
                if request.POST['used_workload']:
                    version_info['used_workload'] = float(request.POST['used_workload'])
                msg = plan.create_version_plan(version_info)
                return HttpResponse(msg)
            elif request.POST['action'] == 'add_stage':
                return self.add_stage(request)
            elif request.POST['action'] == 'upload_file':
                f = request.FILES['version_file']
                import time, xlrd
                name = str(time.strftime('%Y%m%d%H%M%S'))
                with open('/static/file/'+name+'.xls', 'wb+') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)
                book = xlrd.open_workbook('/Demo/static/file/'+name+'.xls')
                sheet1 = book.sheet_by_index(0)

                return HttpResponse(sheet1.cell_value(1,1))
        else:
            context = dict(
                user=request.user,
                action=request.path
            )
            return TemplateResponse(request, 'plan/add.html', context)

    def add_stage(self, request):
        try:
            plan = PlanOperate(request.user, request.POST['version_name'])
            stage_var_list = ['stage', 'plan_start_date', 'actual_start_date',
                              'plan_end_date', 'actual_end_date', 'plan_workload', 'used_workload']
            version_info = {}
            for item in stage_var_list:
                if item in request.POST:
                    version_info[item] = request.POST[item]
            version_infos = {request.POST['stage']: version_info}
            msg = plan.create_stage_plan(version_infos)
            return HttpResponse(msg)
        except Exception as e:
            return HttpResponse(str(e))

    def update(self, request):
        plan = PlanOperate(request.user)
        plan.get_plan_operate_by_version_obj('Version 1.0')

        if not plan.stage_plans:
            return HttpResponse('000000000')
        str1 = ''
        stage_var_list = ['stage', 'plan_workload', 'used_workload']
        starge_var_list_date = ['plan_start_date', 'actual_start_date',
                          'plan_end_date', 'actual_end_date',]
        for item in plan.stage_plans:
            for i in stage_var_list:
                str1 = str1 + str(item.__dict__[i]) + i
            for j in starge_var_list_date:
                if item.__dict__[j]:
                    str1 = str1 + item.__dict__[j].strftime('%Y-%m-%d') + j
                else:
                    str1 = str1 + 'NULL' + j
        str1 += plan.user.username
        return HttpResponse(str1)

    def edit(self, request):
        if request.method == 'POST':
            pass
        else:
            if 'version_name' in request.GET:
                version_name = request.GET['version_name']
                plan = PlanOperate(request.user, version_name)
                context = dict({
                    'version': plan.version_plan,
                    'stages': plan.stage_plans,
                })
                return TemplateResponse(request, 'plan/table.html', context)

    def history(self, request):
        pass

controller = PlanController()
urlpatterns = [
    path('index', controller.index),
    path('table', controller.table_view),
    path('add_stage', controller.add_stage),
    path('add', controller.add),
    path('update', controller.update),
    path('edit', controller.edit),
    path('history', controller.history),
]