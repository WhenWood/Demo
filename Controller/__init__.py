from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.http import HttpResponse

class baseController:
	
	def __init__(self):
		pass

	def index(self, request):
		#site enter
		pass
		


class homeController(baseController):
	
	def __init__(self):
		pass

	index_template = None

	def index(self):
		# do something
		pass


class apiController(baseController):
	
	def __init__(self, request):
		pass


class loginController(baseController):
	
	def __init__(self, request):
		pass


class requementController(baseController):
	
	def __init__(self, request):
		pass

class versionController(baseController):
	
	def __init__(self, request):
		pass

class staffController(baseController):
	
	def __init__(self, request):
		pass

homeController = homeController().index()