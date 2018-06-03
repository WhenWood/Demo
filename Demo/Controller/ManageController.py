from django.urls import path
from django.http import HttpResponseRedirect, HttpResponse
from django.template.response import TemplateResponse
from Demo.Model.StaffOperate import StaffOperate
from TestModel.dbModels import Staff, VersionPlan
from Demo.Model.PlanOpertate import PlanOperate
from Demo.Constant import authContant
from TestModel.dbModels import redmine_users
from Demo.Controller.GroupController import GroupOperate

class ManageController:
    user = ''
    staff = ''
    permission = ''

    def redirect_login(self, request): 
       return HttpResponseRedirect('%s?next=%s' % ('/admin/login/?next=', request.path))

    def has_permission(self, user):
        staff = user.user_staff.all()
        self.user = user
        if staff:
            staff = staff[0]
            self.staff = staff
            staffOperate = StaffOperate(user, staff)
            self.permission = staffOperate.has_create_user_permission()
        else:
            self.permission = False
        return self.permission

    def index(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('%s?next=%s' % ('/admin/login/?next=', request.path))
        create_user_permission = self.has_permission(request.user)
        links = [
            {'site': '/manage/change_password/', 'name': '修改密码'},
        ]
        if create_user_permission:
            link = {'site': '/manage/add_user/', 'name': '新增用户'}
            links.append(link)
        if request.user.is_superuser:
            link = {'site': '/manage/add_manager/', 'name': '新增管理员'}
            links.append(link)
        if self.has_permission(request.user):
            links.append({'site': '/manage/staff/', 'name': '人员管理'})
        links.append({'site': '/admin/logout/', 'name': '退出登录'})
        context = dict(
            links=links,
            user=request.user,
            action=request.path

        )
        return TemplateResponse(request, 'manage/manage.html', context)

    def add_user(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('%s?next=%s' % ('/admin/login/?next=', request.path))
        if request.method == 'POST':
            user_names = request.POST['user_names']
            user_arr = user_names.split(',')
            staff_operate = StaffOperate(request.user)
            for user in user_arr:
                staff_operate.create_staff(user)
            return HttpResponse('《创建用户' + user_names + '成功》')
        else:
            context = dict(
                title='thisTitle',
                user=request.user,
            )
            return TemplateResponse(request, 'manage/addUser.html', context)

    def add_manager(self, request):
        if request.user.is_anonymous:
            request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect('%s?next=%s' % ('/admin/login/', request.path))
        user = request.user
        if not user.is_superuser:
            return HttpResponse('《只有超级用户才可以应急创建管理员》')
        if request.method == 'POST':
            user_names = request.POST['user_names']
            user_arr = user_names.split(',')
            staff_operate = StaffOperate(request.user)
            for user in user_arr:
                staff_operate.create_manage(user, '123456')
            return HttpResponse('《创建管理员' + user_names + '成功》')
        else:
            context = dict(
                title='thisTitle',
                user=request.user,
                action=request.path

            )
            return TemplateResponse(request, 'manage/emergencyCreateManager.html', context)

    def change_password(self, request):
        if request.user.is_anonymous:
            request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect('%s?next=%s' % ('/admin/login/', request.path))

        if request.method == 'POST':
            username = request.user.username
            valid_password = request.POST['valid_password']
            password_confirm = request.POST['password_confirm']
            if valid_password != password_confirm:
                return HttpResponse('《两次密码输入不一致》')
            username.set_password(valid_password)
            username.save()
            return HttpResponse('《密码修改成功》')

        else:
            context = dict(
                title='修改密码',
                user=request.user,
                action=request.path
            )
            return TemplateResponse(request, 'manage/changePassword.html', context)

    def staff_status(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('%s?next=%s' % ('/admin/login/?next=', request.path))

        if self.has_permission(request.user):
            unassigned_staffs = Staff.objects.filter(status=authContant.AUTH_STATUS_UNASSIGNED)
            versions = VersionPlan.objects.filter(status=True)
            version_staff = []
            for version in versions:
                plan_obj = PlanOperate(self.user, version)
                staffs = version.assign_staffs.all()
                staff_info = [staff.name for staff in staffs]
                version_staff.append(dict(
                    stage_info=plan_obj.get_stage(),
                    staff_info=staff_info,
                    version_name=version.version_name,
                    plan_workload=version.plan_workload,
                ))
            unassigned_staff = [staff.name for staff in unassigned_staffs]
            context = dict(
                version_row=len(version_staff),
                version_staff=version_staff,
                unassigned_staff=unassigned_staff,
            )
            return TemplateResponse(request, 'manage/staff_status.html', context)
        else:
            return self.my_page(request)

    def staff_status_for_group_admin(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('%s?next=%s' % ('/admin/login/?next=', request.path))

        group_op = GroupOperate(request.user)

        if group_op:
            all_system_info = group_op.get_group_system_info()
            system_version_staff = []
            for system in all_system_info:
                versions = all_system_info[system]['version_obj']
                users = all_system_info[system]['user_obj']
                unassigned_staff = []
                for user in users:
                    staff = user.user_staff.all()[0]
                    if staff.status == authContant.AUTH_STATUS_UNASSIGNED:
                        unassigned_staff.append(staff)
                version_staff = []
                version_name_arr = []
                for version in versions:
                    plan_obj = PlanOperate(self.user, version)
                    assigned_staff = version.assign_staffs.all()
                    version_name_arr.append(version.version_name)
                    version_staff.append(dict(
                        stage_info=plan_obj.get_stage(),
                        assigned_staff=assigned_staff,
                        version_name=version.version_name,
                    ))
                import json
                system_version_staff.append(dict(
                    version_name_arr=json.dumps(version_name_arr),
                    version_staff=version_staff,
                    unassigned_staff=unassigned_staff,
                    system_rowspan=max(len(version_staff),1),
                    system=system,
                ))

            context = dict(
                system_version_staff=system_version_staff,
                is_supper_user=request.user.is_superuser,
            )
            return TemplateResponse(request, 'manage/manage.html', context)
        else:
            return self.my_page(request)

    def my_page(self, request):
        if self.user == '':
            self.user = request.user
        if self.staff == '':
            self.staff = self.user.user_staff.all()[0]
        my_version = self.staff.staff_version_plan.filter(status=True)
        if not my_version:
            return self.free_work()
        else:
            version_info = []
            staff_self = request.user.user_staff.all()[0]
            for version in my_version:
                plan = PlanOperate(request.user, version)
                staffs = version.assign_staff.filter(status=True).exclude(self)
                staff_info = [staff.name for staff in staffs]
                version_info.append(dict(
                    staff_info=staff_info,
                    stage_info=plan.get_stage(),
                    version_name=version.version_name,
                ))
            context = dict(
                version_info=version_info,
                staff_self=staff_self,
            )
            return TemplateResponse(request, 'manage/my_page.html', context)

    def free_work(self):
        return HttpResponse("今日空闲")

    def get_all_version(self, request):
        pass

    def assign(self, request):
        if request.method == 'POST':
            version_name = request.POST.get('version_name')
            staff_name = request.POST.get('staff_name')
            if (not version_name) or (not staff_name):
                return HttpResponse('fail')
            plan = PlanOperate(request.user, version_name)
            plan.add_staff_to_plan(staff_name)
            return HttpResponse('success')
        return HttpResponse('fail')

    def unassign(self, request):
        if request.method == 'POST':
            version_name = request.POST.get('version_name')
            staff_name = request.POST.get('staff_name')
            if (not version_name) or (not staff_name):
                return HttpResponse('111')
            plan = PlanOperate(request.user, version_name)
            plan.remove_staff_to_plan(staff_name)
            return HttpResponse('success')
        return HttpResponse('fail')

    def add_staff_to_group(self, staff_name, group_name):

        pass

    def add_system_to_group(self, staff_name, system):
        pass

    def hard_code(self, request):
        hard_code_token = request.GET.get('hard_code_token')

        if hard_code_token == "cfets":
            hard_code = request.GET.get('hard_code')
        else:
            return HttpResponse("Invalid Command")
        if hard_code == 'init_redmine_user':
            try:
                ru = redmine_users.objects.all()
                for usr in ru:
                    if usr.status != "1" or usr.login == '' or len(Staff.objects.filter(name=usr.login)) > 0:
                        continue
                    else:
                        print ("init " + usr.login + "!")
                        operator = StaffOperate(request.user)
                        operator.create_staff(usr.login)
                return HttpResponse("Init Redmine User Success!")
            except Exception as e:
                return HttpResponse("Init Redmine User Fail!" + str(e))
        elif hard_code == 'testredmine':
            from TestModel.dbModels import Redmine_projects
            t = Redmine_projects.objects.values('sys_name', 'version').distinct()
            xstr = ''
            for item in t:
                xstr += str(item['version'])
                print(item)
            return HttpResponse(xstr)
        elif hard_code == 'testview':
            from TestModel.dbModels import RedmineSystem
            t = RedmineSystem.objects.values('sys_name', 'sys_version')
            xstr = ''
            for item in t:
                xstr += str(item['sys_name'])
                print(item)
            return HttpResponse(xstr)
        elif hard_code == "add_user_group":
            t = GroupOperate(request.user)
            for id in range(3,10):
                t.add_user_to_group(id, 7)
            return HttpResponse(0)
        else:
            return HttpResponse("Can not find Command")

    def user_auth_control(self, request):
        if not request.user.is_superuser:
            return HttpResponse("无权限操作")
        if request.method == "POST":
            pass
        else:
            staff_op = StaffOperate(request.user)
            staff_list = staff_op.get_all_active_staff(True)




controller = ManageController()
urlpatterns = [
    path('',controller.staff_status_for_group_admin),
    path('add_user/', controller.add_user),
    path('add_manager/', controller.add_manager),
    path('change_password/', controller.change_password),
    path('staff/', controller.staff_status),
    path('assign/', controller.assign),
    path('unassign/', controller.unassign),
    path('hard_code/', controller.hard_code),

]