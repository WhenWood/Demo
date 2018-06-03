from django.urls import path
from django.http import HttpResponse
from django.template.response import TemplateResponse
from Demo.Model.StaffOperate import StaffOperate
from Demo.Model.GroupOperate import GroupOperate
from Demo.Constant import authContant
from TestModel.dbModels import Redmine_projects


class GroupController:

    def manage(self, request):
        if request.method == 'POST':
            action = request.POST.get("action")
            group_id = request.POST.get("group_id")
            user_id = request.POST.get("user_id")
            staff_name = request.POST.get('staff_name')
            group_op = GroupOperate(request.user, group_id)
            if user_id == "" and staff_name:
                user_obj = group_op.get_user_obj_by_username(staff_name)
                user_id = user_obj.id
            if action == "apply":
                response_text = group_op.apply_to_join_group(group_id)
            elif action == "retract":
                response_text = group_op.retract_join_application(group_id)
            elif action == "refuse":
                response_text = group_op.refuse_join_application(user_id, group_id)
            elif action == "accept":
                response_text = group_op.accept_join_goup(user_id, group_id)
            elif action == "add_staff":
                response_text = group_op.add_user_to_group(user_id, group_id)
            elif action == "remove_staff":
                response_text = group_op.remove_user_from_group(user_id, group_id)
            elif action == "grant_auth":
                response_text = group_op.grant_admin_to_group_user(user_id, group_id)
            elif action == "revoke_auth":
                response_text = group_op.revoke_group_admin_auth(user_id, group_id)
            else:
                response_text= {"code":-2,"msg":"未定义的行为"}
            return HttpResponse(response_text["msg"])
        else:
            group_id = request.GET.get("group_id")
            group_op = GroupOperate(request.user)
            staff_op = StaffOperate(request.user)
            groups = group_op.get_all_groups()
            permission = group_op.get_group_permission_type(group_id)
            if permission == authContant.AUTH_GROUP_ADMIN:
                staff_list = staff_op.get_all_active_staff(True)
            else:
                staff_list = []
                group_id = ""
            apply_users = group_op.get_join_group_application(group_id)
            under_control_group, limited_group, apply_group, refuse_group, other_group = group_op.get_my_groups()
            group_admin, group_user, group_apply, group_owner = group_op.get_group_all_user(group_id)

            context = dict(
                request_user=request.user,
                group_id=group_id,
                group_owner=group_owner,
                group_admin=group_admin,
                group_apply=group_apply,
                group_user=group_user,
                apply_users=apply_users,
                groups=groups,
                staff_list=staff_list,
                under_control_group=under_control_group,
                limited_group=limited_group,
                apply_group=apply_group,
                refuse_group=refuse_group,
                other_group=other_group,
            )
            return TemplateResponse(request, 'group/index.html', context)

    def create_group(self, request):
        if request.method == 'POST':
            group_name = request.POST.get("group_name")
            group_op = GroupOperate(request.user)
            msg = group_op.create_group(group_name)
            msg['request_user'] = request.user
            return TemplateResponse(request, 'group/index.html', msg)
        else:
            return TemplateResponse(request, 'group/index.html', {'request_user':request.user})

    def delete_group(self, request):
        if request.method == 'POST':
            group_id = request.POST.get("group_id")
            group_op = GroupOperate(request.user)
            msg = group_op.delete_group(group_id)
            msg['request_user'] = request.user
            return TemplateResponse(request, 'group/index.html', msg)
        else:
            return TemplateResponse(request, 'group/index.html', {'request_user': request.user})

    def batch_process(self, request):
        if request.method == 'POST':
            response_text = ""
            return HttpResponse(response_text)
        else:
            return TemplateResponse(request, 'group/index.html', {'request_user': request.user})

    def system_select(self, request):
        if request.method == 'POST':
            group_id = request.POST.get("group_id")
            action = request.POST.get("action")
            systems = request.POST.get('systems')
            import json
            system_arr = json.loads(systems)
            group_op = GroupOperate(request.user, group_id)
            response_msg = "无效操作"
            if action == "add_system":
                for system in system_arr:
                    response_text = group_op.add_redmine_system_to_group(system, group_id)
                    if response_text['code'] != 0:
                        return HttpResponse(response_text['msg'])
                    response_msg = response_text['msg']

            elif action == "remove_system":
                for system in system_arr:
                    response_text = group_op.remove_redmine_system_to_group(system, group_id)
                    if response_text['code'] != 0:
                        return HttpResponse(response_text['msg'])
                    response_msg = response_text['msg']
            return HttpResponse(response_msg)

        else:
            group_id = request.GET.get("group_id")
            group_op = GroupOperate(request.user, group_id)
            groups = group_op.get_all_groups()
            redmine_systems = Redmine_projects.objects.values('sys_name').distinct()
            under_control_group, limited_group, apply_group, refuse_group, other_group = group_op.get_my_groups()
            system_names = []
            joined_system = []
            permission = group_op.get_group_permission_type(group_id)
            if permission == authContant.AUTH_GROUP_ADMIN:
                joined_system = group_op.get_group_redmine_system(group_id)
                for item in redmine_systems:
                    system_name = item['sys_name']
                    if system_name not in joined_system:
                        system_names.append(system_name)

            context = dict(
                under_control_group=under_control_group,
                request_user=request.user,
                group_id=group_id,
                groups=groups,
                system_names=system_names,
                joined_system=joined_system,
            )
            return TemplateResponse(request, 'group/system.html', context)


controller = GroupController()
urlpatterns = [
    path('manage/',controller.manage),
    path('create_group/',controller.create_group),
    path('delete_group/', controller.delete_group),
    path('batch_process/', controller.batch_process),
    path('system/', controller.system_select),
]