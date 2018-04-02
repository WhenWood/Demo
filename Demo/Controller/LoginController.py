from django.contrib.auth import authenticate, login
from django.urls import path
from django.http import HttpResponseRedirect, HttpResponse
from Demo.Model.Auth import Auth

class LoginController:

    next_page = ''
    is_manager = False
    has_assigned_plan = False

    def __init__(self):
        pass

    def login(self, request):
        if request.user is not None:
            auth = Auth(request.user)
            return HttpResponse(auth.publish_plan_id)
            #return HttpResponseRedirect('/admin/index/')

        if request.method == 'GET':
            if 'next_page' in request.GET:
                pass

        elif request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            next_page = request.GET['next'] or request.POST['next']
            self.next_page = next_page
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # 跳转到成功页面.
                    return HttpResponseRedirect(self.next_page)
                else:
                    pass
            # 返回一个无效帐户的错误
            else:
                pass
        # 返回登录失败页面。


controller = LoginController()
urlpatterns = [
    path('', controller.login, name='login'),
    path('home/', controller.login, name='home'),
    path('index/', controller.login, name='index')
]