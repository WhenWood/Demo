from TestModel.dbModels import VersionPlan, StagePlan, Staff, StaffGroup, GroupOperateAuth, GroupVersionAuth
from Demo.Model.AssignOperate import AssignOperate
from Demo.Constant import authContant
from TestModel.dbModels import Redmine_projects
import datetime


class GroupOperate:
    group = ''
    user = ''

    def __init__(self,  user, group_name=""):
        if group_name != "":
            self.group = StaffGroup.objects.filter(group_name=group_name)
        self.user = user

    def create_group(self, group_name):
        if not self.has_create_group_permission():
            return False

        if self.is_duplicate_group_name(group_name):
            return False

        group = StaffGroup()
        group.group_name = group_name
        group.group_owner = self.user
        group.save()
        self.group = group
        group_op_auth = GroupOperateAuth()
        group_op_auth.user = self.user
        group_op_auth.group = self.group
        group_op_auth.user_type = authContant.AUTH_GROUP_ADMIN
        group_op_auth.operator = self.user.username
        group_op_auth.save()
        return True

    def delete_group(self, group_name):
        group = StaffGroup.objects.filter(group_name=group_name)
        if len(group):
            group.delete()
        self.group = ''

    def has_create_group_permission(self):
        staff = self.user.user_staff.all()
        if len(staff):
            staff = staff[0]
            return staff.type == authContant.AUTH_TYPE_MANAGER

    def is_duplicate_group_name(self, group_name):
        group = StaffGroup.objects.filter(group_name=group_name)
        return len(group) != 0

    def apply_to_join_group(self):
        apply = GroupOperateAuth.objects.get(user_id=self.user.id, group_id=self.group.id)
        if not len(apply):
            apply = GroupOperateAuth()
        apply.group = self.group
        apply.user = self.user
        apply.user_type = authContant.AUTH_GROUP_APPLY
        apply.operator = self.user.username
        apply.save()

    def get_my_groups(self):
        group_op_auth = self.user.user_group_operate_auth.all()
        group_info = []
        for op_auth in group_op_auth:
            group_info.append({'group_obj':op_auth.group, 'user_type':op_auth.user_type})
        return group_info

    def get_all_groups(self):
        group_obj = StaffGroup.objects.all()
        return group_obj

    def get_group_all_user(cls, group):
        if not isinstance(group, StaffGroup):
            return []
        group_op_auth = group.staff_group_operate_auth.all()
        user_obj = []
        for op_auth in group_op_auth:
            user_obj.append(op_auth.user)
        return user_obj

    def get_join_group_application(self):
        group_info = self.get_my_groups()
        wait_application = []
        my_application = []
        invalid_application = []
        for info in group_info:
            if info['user_type'] == authContant.AUTH_GROUP_ADMIN:
                apply_infos = GroupOperateAuth.objects.filter(user_type=authContant.AUTH_GROUP_APPLY,
                                                              group_id=info['group_obj'].id)
                for apply in apply_infos:
                    wait_application.append({'user_id':apply.user.id, 'group_id':apply.group.id})
            elif info['user_type'] == authContant.AUTH_GROUP_APPLY:
                my_application.append({'user_id': self.user.id, 'group_id': info['group_obj'].id})
            elif info['user_type'] == authContant.AUTH_GROUP_REFUSE:
                invalid_application.append({'user_id': self.user.id, 'group_id': info['group_obj'].id})
        return wait_application, my_application, invalid_application

    def retract_join_application(self, group_id):
        group_op_auth = GroupOperateAuth.objects.get(group_id=group_id, user_id=self.user.id)
        if group_op_auth:
            group_op_auth.delete()

    def refuse_join_application(self, user_id, group_id):
        group_op_auth = GroupOperateAuth.objects.get(group_id=group_id, user_id=user_id)
        if group_op_auth:
            group_op_auth.user_type = authContant.AUTH_GROUP_REFUSE
            group_op_auth.operator = self.user.username
            group_op_auth.save()

    def accept_join_goup(self, user_id, group_id):
        group_op_auth = GroupOperateAuth.objects.get(group_id=group_id, user_id=user_id)
        if group_op_auth:
            group_op_auth.user_type = authContant.AUTH_GROUP_USER
            group_op_auth.operator = self.user.username
            group_op_auth.save()

    def has_group_operate_permission(self):
        is_group_admin = GroupOperateAuth.objects.filter(user_id=self.user.id, user_type=authContant.AUTH_GROUP_ADMIN)
        return self.user == self.group.group_owner or len(is_group_admin)>0

    def add_user_to_group(self, user_id):
        new_user = GroupOperateAuth()
        new_user.user_id = user_id
        new_user.user_type = authContant.AUTH_GROUP_USER
        new_user.operator = self.user.username
        new_user.save()

    def add_admin_to_group(self, user_id):
        group_user = GroupOperateAuth.objects.get(user_id=user_id, staffgroup_id=self.group.id)
        group_user.user_type = authContant.AUTH_GROUP_ADMIN
        group_user.operator = self.user.username
        group_user.save()

    def revoke_group_admin_auth(self, user_id):
        group_user = GroupOperateAuth.objects.get(user_id=user_id, staffgroup_id=self.group.id)
        group_user.user_type = authContant.AUTH_GROUP_USER
        group_user.operator = self.user.username
        group_user.save()

    def remove_user_from_group(self, user_id):
        group_user = GroupOperateAuth.objects.get(user_id=user_id, staffgroup_id=self.group.id)
        group_user.delete()

    def get_group_user(self):
        group_op_auth = self.group.staff_group_operate_auth.all()
        user_obj = []
        for op_auth in group_op_auth:
            user_obj.append(op_auth.user)
        return user_obj

    def get_group_version_plan(self):
        group_ver_auth = self.group.staff_group_version_auth.all()
        version_obj = []
        for ver_auth in group_ver_auth:
            sys_name = ver_auth.redmine_system
            versions = VersionPlan.objects.filter(sys_name=sys_name)
            for version in versions:
                version_obj.append(version)
        return version_obj

    def add_version_to_group(self, redmine_system):
        ver_auth = GroupVersionAuth()
        ver_auth.group = self.group
        ver_auth.redmine_system = redmine_system
        ver_auth.operator = self.user.username
        ver_auth.save()

    def remove_version_to_group(self, redmine_system):
        ver_auth = GroupVersionAuth.objects.get(redmine_system=redmine_system)
        ver_auth.delete()


