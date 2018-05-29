from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import path


class HomeController:
    request = ''

    def __init__(self, name='test'):
        self.request = name

    def home(self, request):
        a = request.GET['test']
        return HttpResponse("tst" + str(a))

    def workload(self, request):

        pass

    def index(self, request, action="index"):

        context = dict(
            title='thisTitle',
            app_list=action,
            user=request.user,
            name=self.request,

        )
        return TemplateResponse(request,  'index.html', context)


controller = HomeController()
urlpatterns = [
    path('', controller.index, name='index'),
    path('home/', controller.home, name='home'),
    path('index/', controller.index, name='index'),
]