from django.http import HttpResponse
from django.template.response import TemplateResponse

class homeController:
    request = ''

    def __init__(self,name='test'):
        self.request = name

    def home(self,request):
        return HttpResponse("tst")

    def urls(self,request):
        from django.urls import path
        urls = [
            path('',self.index),
            path('home/', self.home),
            path('index/',self.index)
        ]
        return urls,

    def index(self, request):

        context = dict(
            title='thisTitle',
            app_list='this',
            user = request.user,
            name = self.request,
        )
        return TemplateResponse(request,  'index.html', context)


request = homeController()
