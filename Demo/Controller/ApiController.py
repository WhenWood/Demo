from Demo.Model.PlanOpertate import PlanOperate
from django.urls import path
from django.http import HttpResponseRedirect, HttpResponse
from Demo.Model.Auth import Auth

class ApiController:
    pass
    def version(self, request):
        post_info = request.POST


controller = ApiController()
urlpatterns = [
    path('version_add', controller.version),
    path('stage_add', controller.stage),
    path('version_update', controller.version),
    path('stage_update', controller.stage),
]