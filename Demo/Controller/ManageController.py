from django.contrib.auth import authenticate, login
from django.urls import path
from django.http import HttpResponseRedirect, HttpResponse
from Demo.Model.Auth import Auth
from Demo.Model.StaffOperate import StaffOperate


class ManageController:
    def addUser(self, request):
        username = request.GET['username']
        staffOp = StaffOperate(request.user)
        staffOp.create_staff(username)


controller = ManageController()
urlpatterns = [
    path('addUser', controller.addUser, name='addUser'),
]