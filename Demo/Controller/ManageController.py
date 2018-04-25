from django.contrib.auth import authenticate, login
from django.urls import path
from django.http import HttpResponseRedirect, HttpResponse
from django.template.response import TemplateResponse
from Demo.Model.Auth import Auth
from Demo.Model.StaffOperate import StaffOperate
from TestModel.dbModels import Staff, VersionPlan
from Demo.Model.PlanOpertate import PlanOperate
from Demo.Constant import authContant
from django.contrib.auth.models import User


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
        if self.has_permission(request.user):
            unassigned_staffs = Staff.objects.filter(status=authContant.AUTH_STATUS_UNASSIGNED)
            versions = VersionPlan.objects.filter(status=True)
            version_staff = []
            for version in versions:
                plan_obj = PlanOperate(self.user, version)
                staffs = version.assign_staff.all()
                staff_info = [staff.name for staff in staffs]
                version_staff.append(dict(
                    stage_info=plan_obj.get_stage(),
                    staff_info=staff_info,
                    version_name=version.version_name,
                    plan_workload=version.plan_workload,
                ))
            unassigned_staff =[staff.name for staff in unassigned_staffs]
            context = dict(
                version_staff=version_staff,
                unassigned_staff=unassigned_staff,
            )
            return TemplateResponse(request, 'manage/staff_status.html', context)
        else:
            return self.my_page(request)

    def my_page(self, request):
        if self.user == '':
            self.user = request.user
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

    def get_all_version(self, requst):
        pass

controller = ManageController()
urlpatterns = [
    path('',controller.index),
    path('add_user/', controller.add_user),
    path('add_manager/', controller.add_manager),
    path('change_password/', controller.change_password),
    path('staff/', controller.staff_status),
]