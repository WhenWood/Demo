from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.http import HttpResponse

def homeController(request):
	return HttpResponse(str(request)+"<p>testApply！</p>")

	context= {'a':11}
	return TemplateResponse(request, self.index_template or 'View/index.html', context)

