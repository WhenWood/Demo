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
            search = ''
            if 'search' in request.GET:
                search = request.GET['search']
            versions = VersionPlan.objects.filter(status=True, version_name__icontains=search).order_by('-update_time')
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
        days = 30
        search = ''
        if 'start_date' in request.GET:
            start_date = request.GET['start_date']
        if 'days' in request.GET:
            days = request.GET['days']
        if 'search' in request.GET:
            search = request.GET['search']
        date_list = self.get_days(start_date, days)
        versions = VersionPlan.objects.filter(status=True, version_name__icontains=search)
        version_infos = []
        for version in versions:
            stage_obj_plan = ['' for i in range(0, days)]
            stage_obj_actual = ['' for i in range(0, days)]
            plan = PlanOperate(request.user, version)
            for stage in plan.stage_plans:
                if stage.plan_start_date > date_list[-1] or \
                        stage.plan_end_date < date_list[0]:
                    continue
                start_pos = max(0, (stage.plan_start_date-date_list[0]).days)
                end_pos = min(days, (stage.plan_end_date-date_list[-1]).days)
                stage_obj_plan[start_pos:end_pos] = [i + ' ' + stage.stage for i in stage_obj_plan[start_pos:end_pos]]
                if stage.actual_start_date:
                    start_pos = max(0, (stage.actual_start_date-date_list[0]).days)
                    if stage.actual_end_date:
                        end_pos = min(days, (stage.actual_end_date-date_list[-1]).days)
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

    def version_change(self, request):
        self.get_days()


    def get_days(self, date_str='',days=30):
        if date_str == '':
            start_date = datetime.datetime.now().date()
        else:
            start_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        end_date = datetime.timedelta(days=+days)+start_date
        dateList = []
        for i in range(0, days):
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
                if not 'version_file' in request.FILES:
                    return HttpResponse('错误未上传文件')
                file_obj = request.FILES['version_file']
                import time, xlrd

                wb = xlrd.open_workbook(filename=None, file_contents=file_obj.read())
                sheet1 = wb.sheets()[0]
                version_name = sheet1.cell_value(0, 0)
                start_rows = 1
                row_count = sheet1.nrows
                version_info={'version_name': version_name, 'plan_workload': sheet1.cell_value(0, 3)}
                stage_objs = []
                for row in range(start_rows, row_count):
                    stage = sheet1.cell_value(row, 0)
                    plan_start_date = sheet1.cell_value(row, 1)
                    plan_end_date = sheet1.cell_value(row, 2)
                    plan_workload = sheet1.cell_value(row, 3)
                    if isinstance(plan_start_date, float):
                        plan_start_date = datetime.datetime(*xlrd.xldate_as_tuple(plan_start_date, 0))
                    if isinstance(plan_end_date, float):
                        plan_end_date = datetime.datetime(*xlrd.xldate_as_tuple(plan_end_date, 0))
                    if not isinstance(plan_workload, float):
                        plan_workload = float(plan_workload)
                    stage_objs.append(dict(stage=stage, plan_start_date=plan_start_date,
                                           plan_end_date=plan_end_date, plan_workload=plan_workload))

                plan.create(version_info,stage_objs)
                context = dict(version=version_info,stage=stage_objs)
                return TemplateResponse(request, 'plan/upload.html', context)
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

        version_name = request.GET['version_name']
        plan = PlanOperate(request.user, version_name)
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
            if not 'version_name'in request.POST:
                return HttpResponse("版本不存在")
            version_name = request.POST['version_name']

            plan=PlanOperate(request.user, version_name)
            if request.POST['action'] == 'edit_all':
                used_workload = request.POST['version_used_workload']
                if used_workload == 'None':
                    used_workload = None
                version_info = dict(
                    version_name=request.POST['version_name'],
                    plan_workload=request.POST['version_plan_workload'],
                    used_workload=used_workload,
                )
                stage_infos = request.POST.getlist('stage_infos')[0]
                import json
                Arr = json.loads(stage_infos)
                plan.update_all(version_info, Arr)
                return HttpResponse(0)
            if request.POST['action'] == 'suspend':
                plan.suspend_plan()
                return HttpResponse(0)

        else:
            if 'version_name' in request.GET:
                version_name = request.GET['version_name']
                plan = PlanOperate(request.user, version_name)
                stage_arr = []
                for stage in plan.stage_plans:
                    stage_arr.append(stage)
                context = dict({
                    'version_info': plan.version_plan,
                    'stage_info': stage_arr,
                })
                return TemplateResponse(request, 'plan/edit.html', context)
            return HttpResponse("未找到Active的版本计划")


    def history(self, request):
        if request.method == 'POST':
            pass
        else:
            version_name = request.GET.get('version_name')
            search = request.GET.get('search')
            view_type = request.GET.get('view_type')
            if not view_type:
                view_type = 'list'
            if version_name:
                versions = VersionPlan.objects.all().order_by('-update_time')
                version_info = []
                order = 0
                for version in versions:
                    order = order + 1
                    plan = PlanOperate(request.user, version)
                    stage_obj = []
                    for stage in plan.stage_plans:
                        stage_obj.append(dict(
                            stage=stage.stage,
                            plan_start_date=stage.plan_start_date,
                            plan_end_date=stage.plan_end_date,
                            plan_workload=stage.plan_workload,
                            used_workload=stage.used_workload,
                        ))

                    version_info.append({
                        'order': order,
                        'create_date': version.create_time,
                        'stage': stage_obj,
                        'row': len(stage_obj)
                    })
                context = dict({
                    'version_info': version_info,
                    'type': view_type,
                    'types': [{'site': 'history?type=list&version_name='+version_name, 'name': "列表模式"},
                              {'site': 'history?type=table&version_name='+version_name, 'name': "表格模式"}],
                })
                return TemplateResponse(request, 'plan/history.html', context)


            else:
                version_active = VersionPlan.objects.filter(status=True, version_name__icontains=search).order_by('-update_time')
                version_disable = VersionPlan.objects.filter(status=False, version_name__icontains=search).order_by('-update_time')

                active_version_arr = []
                disable_version_arr = []
                for active in version_active:
                    active_version_arr.append(active.version_name)
                for disable in version_disable:
                    disable_version_arr.append(disable.version_name)
                context = dict(
                    active_version=active_version_arr,
                    disable_version=disable_version_arr
                )
                return TemplateResponse(request, 'plan/version_list.html', context)

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