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
from TestModel.dbModels import redmine_users
from Demo.Model.GroupOperate import GroupOperate


class GroupController:

    def manage(self, request):
        if request.method == 'POST':
            pass
        else:
            t_groups = GroupOperate(request.user)
            groups = t_groups.get_all_groups()
            my_group = t_groups.get_my_groups()
            context = dict(
                groups=groups,
                my_group=my_group,
            )
            return TemplateResponse(request, 'group/index.html', context)

        pass
    pass

    def create_group(self, request):
        if request.method == 'POST':
            group_name = request.POST.get("group_name")
            group_op = GroupOperate(request.user)
            group_op.create_group(group_name)


            return HttpResponse(0)
        else:


            context = dict(

            )
            return TemplateResponse(request, 'group/index.html', context)



controller = GroupController()
urlpatterns = [
    path('manage/',controller.manage),
    path('create_group/',controller.create_group),
]