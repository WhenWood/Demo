from TestModel.dbModels import VersionPlan, StagePlan, Staff, StaffGroup, GroupOperateAuth, GroupVersionAuth
from Demo.Model.AssignOperate import AssignOperate
from Demo.Constant import authContant
from TestModel.dbModels import Redmine_projects
import datetime
from django.contrib.auth import models as authModel

class GroupOperate:
    group = ''
    user = ''

    def __init__(self,  user, group_id=""):
        if group_id != "":
            group = StaffGroup.objects.filter(id=group_id)
            if group:
                self.group = group[0]
        self.user = user

    def create_group(self, group_name):
        try:
            if not self.has_create_group_permission():
                return {"code": 1, "msg": "没有组的编辑权限"}

            if self.is_duplicate_group_name(group_name):
                return {"code": 2, "msg": "同名组已经存在"}

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
            return {"code":0, "msg":"创建组成功"}
        except Exception as e:
            return {"code":-1, "msg":"创建组出错，错误信息为"+ str(e)}

    def delete_group(self, group_id):
        group = StaffGroup.objects.filter(id=group_id)
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

    def apply_to_join_group(self, group_id=""):
        try:
            if group_id == "":
                group_id = self.group.id
            apply_filter = GroupOperateAuth.objects.filter(user_id=self.user.id, group_id=group_id)
            if not len(apply_filter):
                apply = GroupOperateAuth()
            else:
                apply = apply_filter[0]
                if apply.user_type == authContant.AUTH_GROUP_APPLY:
                    return {"code":1,"msg":"已经申请，请不要重复提交"}
                elif apply.user_type == authContant.AUTH_GROUP_REFUSE:
                    return {"code":2,"msg":"申请加入已被拒绝，请联系组管理员"}
                else:
                    return {"code":3, "msg": "已经是组成员，无需再次申请"}
            apply.group = self.group
            apply.user = self.user
            apply.user_type = authContant.AUTH_GROUP_APPLY
            apply.operator = self.user.username
            print(apply)
            apply.save()
            print(3)
            return {"code":0, "msg":"成功申请，请等待管理员审批"}
        except Exception as e:
            print(4)
            return {"code":-1, "msg":"申请加入组出错，出错信息为" + str(e)}

    def get_my_groups(self):
        group_op_auth = self.user.user_group_operate_auth.all()
        under_control_group = []
        limited_group = []
        apply_group = []
        refuse_group = []
        other_group = []
        for op_auth in group_op_auth:
            group = op_auth.group
            if op_auth.user_type == authContant.AUTH_GROUP_ADMIN:
                under_control_group.append(group)
            elif op_auth.user_type == authContant.AUTH_GROUP_USER:
                limited_group.append(group)
            elif op_auth.user_type == authContant.AUTH_GROUP_APPLY:
                apply_group.append(group)
            elif op_auth.user_type == authContant.AUTH_GROUP_REFUSE:
                refuse_group.append(group)
            else:
                other_group.append(group)
        return under_control_group, limited_group, apply_group, refuse_group, other_group

    def get_all_groups(self):
        group_obj = StaffGroup.objects.all()
        return group_obj

    def get_group_all_user(self, group=""):
        if not isinstance(group, StaffGroup) and group:
            group = StaffGroup.objects.filter(id=group)
        if not group:
            return [], [], [], None
        else:
            group = group[0]
        group_op_auth = group.staff_group_operate_auth.all()
        user_obj = []
        admin_obj = []
        apply_obj = []
        group_owner = group.group_owner
        for op_auth in group_op_auth:
            if op_auth.user == group_owner:
                continue
            elif op_auth.user_type == authContant.AUTH_GROUP_ADMIN:
                admin_obj.append(op_auth.user)
            elif op_auth.user_type == authContant.AUTH_GROUP_USER:
                user_obj.append(op_auth.user)
            elif op_auth.user_type == authContant.AUTH_GROUP_APPLY:
                apply_obj.append(op_auth.user)
        return admin_obj, user_obj, apply_obj, group_owner

    def has_admin_permission(self):
        pass

    def get_join_group_application(self, group_id):
        if group_id == "":
            return None
        user_obj = []
        group_op_auth = GroupOperateAuth.objects.filter(user_type=authContant.AUTH_GROUP_APPLY,
                                                      group_id=group_id)
        for op_auth in group_op_auth:
            user_obj.append(op_auth.user)
        return user_obj

    def retract_join_application(self, group_id):
        try:
            group_op_auth = GroupOperateAuth.objects.filter(group_id=group_id, user_id=self.user.id)
            if group_op_auth:
                group_op_auth.delete()
                return {"code":0, "msg":"撤回申请/退出组操作成功"}
            return {"code":1, "msg":"撤回申请/退出组操作失败"}
        except Exception as e:
            return {"code":-1, "msg":"撤回申请/退出组出错，出错信息为" + str(e)}

    def get_user_obj_by_username(cls, username):
        user_obj = authModel.User.objects.filter(username=username)
        if user_obj:
            user_obj = user_obj[0]
        else:
            user_obj = None
        return user_obj

    def refuse_join_application(self, user_id, group_id):
        try:
            group_op_auth = GroupOperateAuth.objects.filter(group_id=group_id, user_id=user_id)
            if group_op_auth:
                group_op_auth = group_op_auth[0]
                group_op_auth.user_type = authContant.AUTH_GROUP_REFUSE
                group_op_auth.operator = self.user.username
                group_op_auth.save()
                return {"code":0, "msg":"拒绝申请操作成功"}
            return {"code": 1, "msg": "拒绝申请操作失败， 信息不存在"}
        except Exception as e:
            return {"code":-1, "msg":"拒绝申请时出错，出错信息为" + str(e)}

    def accept_join_goup(self, user_id, group_id):
        try:
            group_op_auth = GroupOperateAuth.objects.filter(group_id=group_id, user_id=user_id)
            if group_op_auth:
                group_op_auth = group_op_auth[0]
                group_op_auth.user_type = authContant.AUTH_GROUP_USER
                group_op_auth.operator = self.user.username
                group_op_auth.save()
                return {"code": 0, "msg": "同意申请操作成功"}
            return {"code": 1, "msg": "同意申请操作失败， 信息不存在"}
        except Exception as e:
            return {"code": -1, "msg": "同意申请时出错，出错信息为" + str(e)}

    def has_group_operate_permission(self, group_id=""):
        is_group_admin = GroupOperateAuth.objects.filter(group_id=group_id, user_id=self.user.id, user_type=authContant.AUTH_GROUP_ADMIN)
        return len(is_group_admin) > 0

    def get_group_permission_type(self, group_id=""):
        is_group_member = GroupOperateAuth.objects.filter(group_id=group_id, user_id=self.user.id)
        if is_group_member:
            return is_group_member[0].user_type
        else:
            return ""

    def add_user_to_group(self, user_id, group_id=""):
        try:
            group_op_auth = GroupOperateAuth.objects.filter(user_id=user_id, group_id=group_id)
            if len(group_op_auth):
                return {"code": 2, "msg": "增加成员失败，改成员已经在组内"}
            new_user = GroupOperateAuth()
            if group_id == "":
                group_id = self.group.id
            if not group_id:
                return {"code": 1, "msg": "增加成员失败，组编号获取失败"}
            new_user.group_id = group_id
            new_user.user_id = user_id
            new_user.user_type = authContant.AUTH_GROUP_USER
            new_user.operator = self.user.username
            new_user.save()
            return {"code":0,"msg":"增加成员成功"}
        except Exception as e:
            return {"code":-1,"msg":"增加成员出错，错误信息为" + str(e)}

    def grant_admin_to_group_user(self, user_id, group_id=""):
        try:
            if group_id == "":
                group_id = self.group.id
            if not group_id:
                return {"code": 1, "msg": "赋予管理员权限失败，组编号获取失败"}
            group_user = GroupOperateAuth.objects.filter(user_id=user_id, group_id=group_id)
            if group_user:
                group_user = group_user[0]
            else:
                return {"code": 2, "msg": "赋予管理员权限失败，组编号为"+str(group_id)+"的组不存在"}
            group_user.user_type = authContant.AUTH_GROUP_ADMIN
            group_user.operator = self.user.username
            group_user.save()
            return {"code":0,"msg":"赋予管理员权限成功"}
        except Exception as e:
            return {"code":-1, "msg":"赋予管理员权限出错，错误信息为"+str(e)}

    def revoke_group_admin_auth(self, user_id, group_id=""):
        try:
            if group_id == "":
                group_id = self.group.id
            if not group_id:
                return {"code": 1, "msg": "撤销管理员权限失败，组编号获取失败"}
            group_user = GroupOperateAuth.objects.filter(user_id=user_id, group_id=group_id)
            if group_user:
                group_user = group_user[0]
            else:
                return {"code": 2, "msg": "赋予管理员权限失败，组编号为"+str(group_id)+"的组不存在"}
            group_user.user_type = authContant.AUTH_GROUP_USER
            group_user.operator = self.user.username
            group_user.save()
            return {"code":0,"msg":"撤销管理员权限成功"}
        except Exception as e:
            return {"code":-1, "msg":"撤销管理员权限出错，错误信息为"+str(e)}

    def remove_user_from_group(self, user_id, group_id=""):
        try:
            if group_id == "":
                group_id = self.group.id
            if not group_id:
                return {"code": 1, "msg": "移除组成员失败，组编号获取失败"}
            group_user = GroupOperateAuth.objects.filter(user_id=user_id, group_id=group_id)
            group_user.delete()
            return {"code":0,"msg":"移除组成员成功"}
        except Exception as e:
            return {"code":-1,"msg":"移除组成员出错" + str(e)}

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
        ver_auth = GroupVersionAuth.objects.filter(redmine_system=redmine_system)
        ver_auth.delete()


