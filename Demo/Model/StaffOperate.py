from Demo.Constant import authContant
from TestModel.dbModels import Staff, VersionPlan
from Demo.Model.AssignOperate import AssignOperate
from Demo.Model.PlanOpertate import PlanOperate
from django.contrib.auth.models import User
import django.utils.timezone as timezone
from django.contrib.auth import models as authModel

class StaffOperate:
    staffObj = ''
    userObj = ''

    def __init__(self, user, staff=''):
        self.userObj = user
        if staff == '':
            staff_obj = self.get_staff_by_name(user.username)
            if staff_obj:
                self.staffObj = staff_obj
        else:
            self.staffObj = staff

    def create_staff(self, name, password='123456', assigned=authContant.AUTH_STATUS_UNASSIGNED,
                     user_type=authContant.AUTH_TYPE_USER, user_status=authContant.AUTH_USER_ACTIVITY,is_staff=1):
        staff = Staff(name=name, status=assigned, type=user_type, create_time=timezone.now())
        '''
            沿用Django自带的用户登录系统，将Staff作为User对象的外键关联对象 Auth部分简化为Staff的type，
            Auth验证本身就是通过User.Staff.Type，需要额外提供一个管理界面用于添加用户,这个方法是提供管理界面使用
        '''
        user = User.objects.create(username=name, password=password, email=name+'@test.test',
                                   is_active=user_status, is_staff=is_staff)
        user.set_password(password)
        user.save()
        staff.user = user
        staff.save()
        self.staffObj = staff

    def create_manage(self, name, password='123456', assigned=authContant.AUTH_STATUS_UNASSIGNED,
                     user_type=authContant.AUTH_TYPE_MANAGER, user_status=authContant.AUTH_USER_ACTIVITY, is_staff=1):
        staff = Staff(name=name, status=assigned, type=user_type, create_time=timezone.now())
        user = User.objects.create(username=name, password=password, email=name + '@test.test',
                                   is_active=user_status, is_staff=is_staff)
        user.set_password(password)
        user.save()
        staff.user = user
        staff.save()
        self.staffObj = staff

    def get_staff_by_name(self, name):
        staff = Staff.objects.get(name=name)
        return staff

    def create_staffs(self, name_list):
        for name in name_list:
            self.create_staff(name)

    def has_assigned(self):
        return self.staffObj.status == authContant.AUTH_STATUS_ASSIGNED

    def assigned_publish_plan(self):
        return self.staffObj.publish_plan_id

    def has_create_manager_permission(self):
        return self.userObj.is_superuser

    def has_create_user_permission(self):
        return self.has_create_manager_permission() or self.staffObj.type == authContant.AUTH_TYPE_MANAGER

    def assign_plan_to_staff(self, plan_id):
        version_plan = VersionPlan.objects.get(id=plan_id)
        version_plan.assign_saffs.add(self.staffObj)
        version_plan.save()
        assign_operate = AssignOperate()
        assign_operate.create_record(self.staffObj.name, version_plan.id, version_plan.name, self.userObj.name)

    def unassign_plan_to_staff(self, plan_id):
        version_plan = VersionPlan.objects.get(id=plan_id)
        version_plan.assign_saffs.remove(self.staffObj)
        version_plan.save()
        assign_operate = AssignOperate()
        assign_operate.disable_record(version_plan.id, self.staffObj.name, self.userObj.name)

    def get_all_assigned_version(self):
        return self.staff.staff_version_plan.all()

    def get_all_active_version(self):
        planOperateArr = []
        if self.staffObj.type == authContant.AUTH_TYPE_USER:
            version_plans = self.get_all_assigned_version()
            for version_plan in version_plans:
                planOperate = PlanOperate()
                planOperateArr.append(version_plan)

    def get_all_active_staff(self, has_permission=False):
        staff_obj = []
        if has_permission or self.has_create_user_permission():
            staff_obj = Staff.objects.filter(status=authContant.AUTH_USER_ACTIVITY).order_by("name")
        return staff_obj

    def get_all_active_user(self):
        staff_obj = self.get_all_active_staff()
        user_obj = []
        for staff in staff_obj:
            user = authModel.User.objects.get(username=staff.name)
            user_obj.append(user)
        return user_obj

    def get_user_by_username(self, username):
        return authModel.User.objects.get(username=username)



