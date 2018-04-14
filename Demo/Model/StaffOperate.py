from Demo.Constant import authContant
from TestModel.dbModels import Staff, VersionPlan
from django.contrib.auth.models import User
import django.utils.timezone as timezone


class StaffOperate:
    staffObj = ''
    userObj = ''
    staffObj2 = ''

    def __init__(self, user):
        self.userObj = user
        #self.staffObj = user.staff_set.all()
        #self.staffObj2 = user.user_staff.all()


    def create_staff(self, name, password='123456', assigned=authContant.AUTH_STATUS_UNASSIGNED,
                     user_type=authContant.AUTH_TYPE_USER, user_status=authContant.AUTH_USER_ACTIVITY,is_staff=1):
        staff = Staff(name=name, status=assigned, type=user_type, create_time=timezone.now(), )
        '''
            沿用Django自带的用户登录系统，将Staff作为User对象的外键 Auth部分简化为Staff的type，
            Auth验证本身就是通过User.Staff.Type，需要额外提供一个管理界面用于添加用户,这个方法是提供管理界面使用
        '''
        user = User.objects.create(username=name, password=password, email=name+'@test.test', is_active=user_status,is_staff=is_staff)
        user.set_password(password)
        user.save()
        staff.user = user
        self.staffObj = staff
        self.assignObj = None

    def get_staff_by_name(self, name):
        staff = Staff.objects.filer(name=name)
        if staff:
            self.staffObj = staff[0]
        return staff

    def create_staffs(self, name_list):
        for name in name_list:
            self.create_staff(name)

    def has_assigned(self):
        return self.staffObj.status == authContant.AUTH_STATUS_ASSIGNED

    def assigned_publish_plan(self):
        return self.staffObj.publish_plan_id

    def has_create_manager_permission(self):
        return self.staffObj.type == authContant.AUTH_TYP_DEVELOPER

    def has_create_user_permission(self):
        return self.has_create_manager_permission() or self.staffObj.type == authContant.AUTH_TYP_DEVELOPER

    def assign_plan_to_staff(self, plan_id):
        version_plan = VersionPlan.objects.filter(id=plan_id)
        version_plan.assign_saffs.add(self.staffObj)
        version_plan.save()

    def unassign_plan_to_staff(self, plan_id):
        version_plan = VersionPlan.objects.filter(id=plan_id)
        version_plan.assign_saffs.remove(self.staffObj)
        version_plan.save()

    def get_all_assigned_version(self):
        return self.staff.staff_version_plan.all()


