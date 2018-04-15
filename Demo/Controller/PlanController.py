from Demo.Model.PlanOpertate import PlanOperate
from django.urls import path
from django.http import HttpResponseRedirect, HttpResponse
from Demo.Model.Auth import Auth


class PlanController:

    def index(self, request):
        if request.method == 'POST':
            pass
        else:
            plan_operate = PlanOperate(request.user)
            plan_operate.get_plan_operate_by_version_obj()

controller = PlanController()
urlpatterns = [

]