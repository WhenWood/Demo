from TestModel.dbModels import VersionPlan, StagePlan, Staff, StaffGroup, GroupOperateAuth, GroupVersionAuth
from Demo.Model.AssignOperate import AssignOperate
from Demo.Constant import authContant
from TestModel.dbModels import Redmine_projects
import datetime
from django.contrib.auth import models as authModel
from django.db.models import Q

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

    def get_my_groups(self, group_type=""):
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
        if group_type == "valid":
            return under_control_group + limited_group
        elif group_type == "apply":
            return apply_group
        elif group_type == "refuse":
            return refuse_group
        elif group_type == "admin":
            return under_control_group
        elif group_type == "invalid":
            return apply_group + refuse_group
        return under_control_group, limited_group, apply_group, refuse_group, other_group

    def get_all_groups(self):
        group_obj = StaffGroup.objects.all()
        return group_obj

    def get_group_all_user(self, group=""):
        if not isinstance(group, StaffGroup) and group:
            group = StaffGroup.objects.filter(id=group)
            if len(group):
                group = group[0]
        if not group:
            return [], [], [], None

        group_op_auth = group.staff_group_operate_auth.all()
        user_obj = []
        admin_obj = []
        apply_obj = []
        group_owner = group.group_owner
        for op_auth in group_op_auth:
            if op_auth.user.id == group_owner.id:
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

    def get_group_version_plans(self, version_type="valid"):
        groups = self.get_my_groups("valid")
        sys_name_record = []
        version_obj = set()
        for group in groups:
            group_ver_auth = group.staff_group_version_auth.all()
            for ver_auth in group_ver_auth:
                sys_name = ver_auth.redmine_system
                if sys_name in sys_name_record:
                    continue
                sys_name_record.append(sys_name)
                if version_type == "all":
                    versions = VersionPlan.objects.filter(sys_name=sys_name)
                elif version_type == "invalid":
                    versions = VersionPlan.objects.filter(sys_name=sys_name, status=False)
                else:
                    versions = VersionPlan.objects.filter(sys_name=sys_name, status=True)
                for version in versions:
                    version_obj.add(version)
        return version_obj

    def get_group_system_info(self):
        groups = self.get_my_groups("admin")
        system_info = {}
        for group in groups:
            group_ver_auth = group.staff_group_version_auth.all()
            admin_obj, user_obj, apply_obj, group_owner = self.get_group_all_user(group)
            for ver_auth in group_ver_auth:
                sys_name = ver_auth.redmine_system
                if sys_name in system_info:
                    for item in admin_obj+user_obj:
                        if item not in system_info[sys_name]['user_obj']:
                            system_info[sys_name]['user_obj'].append(item)
                    continue
                versions = VersionPlan.objects.filter(sys_name=sys_name)
                version_obj = []
                for version in versions:
                    version_obj.append(version)
                all_user_obj = admin_obj+user_obj
                system_info[sys_name] = {'version_obj':version_obj, 'user_obj': all_user_obj}
        return system_info

    def get_group_redmine_system(self, group_id=""):
        if isinstance(self.group, StaffGroup) and group_id == "":
            group_id = self.group.id
        group_ver_auth = GroupVersionAuth.objects.filter(group_id=group_id)
        system = []
        for ver_auth in group_ver_auth:
            system.append(ver_auth.redmine_system)
        return system

    def add_redmine_system_to_group(self, redmine_system, group_id=""):
        try:
            if not isinstance(self.group, StaffGroup):
                group = StaffGroup.objects.filter(id=group_id)
                if len(group):
                    group = group[0]
            else:
                group = self.group
            if not group:
                return {"code":1,"msg":"增加组关联系统失败：未选择组编号，或组编号无效"}
            ver_auth = GroupVersionAuth()
            ver_auth.group = group
            ver_auth.redmine_system = redmine_system
            ver_auth.operator = self.user.username
            ver_auth.save()
            return {"code": 0, "msg": "增加组关联系统成功"}
        except Exception as e:
            return {"code": -1, "msg": "增加组关联系统出错，错误信息为" + str(e)}

    def remove_redmine_system_to_group(self, redmine_system, group_id=""):
        try:
            if isinstance(self.group, StaffGroup) and group_id == "":
                group = StaffGroup.objects.filter(id=group_id)
                if len(group):
                    self.group = group[0]
                    group_id = group[0].id
                else:
                    return {"code":1,"msg":"移除组关联系统失败：未选择组编号，或组编号无效"}
            ver_auth = GroupVersionAuth.objects.filter(redmine_system=redmine_system, group_id=group_id)
            ver_auth.delete()
            return {"code": 0, "msg": "移除组关联系统成功"}
        except Exception as e:
            return {"code":-1, "msg":"移除组关联系统出错，错误信息为"+str(e)}


