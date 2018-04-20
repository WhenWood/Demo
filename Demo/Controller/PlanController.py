from Demo.Model.PlanOpertate import PlanOperate
from django.urls import path
from django.http import HttpResponseRedirect, HttpResponse
from Demo.Model.Auth import Auth
from django.template.response import TemplateResponse


class PlanController:

    def index(self, request):
        if request.method == 'POST':
            pass
        else:
            if not request.user.is_authenticated:
                return HttpResponseRedirect('%s?next=%s' % ('/admin/login/?next=', request.path))
            create_user_permission = self.has_permission(request.user)
            versions = PlanOperate.get_all_active_plan()
            links = [
                {'site': '/manage/change_password/', 'name': '修改密码'},
            ]
            for version in versions:
                plan = PlanOperate(request.user, version)
                links.append({'site': '/version_plan/?version_name='+version.version_name,})

            if create_user_permission:
                link = {'site': '/manage/add_user/', 'name': '新增用户'}
                links.append(link)
            if request.user.is_superuser:
                link = {'site': '/manage/add_manager/', 'name': '新增管理员'}
                links.append(link)
            links.append({'site': '/admin/logout/', 'name': '退出登录'})
            context = dict(
                links=links,
                user=request.user,
                action=request.path
            )
            return TemplateResponse(request, 'manage/manage.html', context)

    def add(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('%s?next=%s' % ('/admin/login/?next=', request.path))
        plan = PlanOperate(request.user)
        '''
        plan_var_list = {'version_name':'Version 1.0', 'plan_workload': float(10.0), 'used_workload': float(0.0)}
        import datetime
        stage_var_list = {'ST':{ 'plan_start_date': '2018-1-12',
                                 'actual_start_date': '2018-1-12',
                          'plan_end_date': '2018-2-12',
                                 'actual_end_date': None, 'plan_workload':float(1),
                           'used_workload': float(10),'operator':request.user.username}}
        
        plan.create(plan_var_list, stage_var_list)
        '''
        if request.method == 'POST':
            plan_var_list = ['version_name', 'plan_workload', 'used_workload']
            stage_var_list = ['stage', 'plan_start_date', 'actual_start_date',
                              'plan_end_date', 'actual_end_date', 'plan_workload', 'used_workload']

        else:
            return HttpResponse('Edit')

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
                    str1 = str1 + item.__dict__[j].strftime('%y-%m-%d') + j
                else:
                    str1 = str1 + 'NULL' + j
        str1 += plan.user.username
        return HttpResponse(str1)

controller = PlanController()
urlpatterns = [
    path('index', controller.index),
    path('add', controller.add),
    path('update', controller.update)
]