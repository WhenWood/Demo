from Demo.Constant import authContant
from TestModel.dbModels import Staff,Requirement
from django.http import HttpResponseRedirect, HttpResponse

class Auth:
    staff_id = ''
    status = ''
    type = ''
    staff_name = ''
    isStaff = False

    def __init__(self, staff_name='admin'):

        staff = Staff.objects.filter(id=1)

        if not staff:
            self.isStaff = False
        else:
            staff1 = staff[0]
            self.isStaff = True
            self.type = staff1.type
            self.name = staff_name
            self.publish_plan_id = staff1.publish_plan_id

    def has_assigned(self):
        return self.status == authContant.AUTH_STATUS_ASSIGNED

    def assigned_publish_plan(self):
        return self.publish_plan_id

    def has_manage_permission(self):
        return self.type == authContant.AUTH_TYPE_MANAGER or self.type == authContant.AUTH_TYP_DEVELOPER

