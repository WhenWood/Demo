from Demo.Constant import authContant
from TestModel.dbModels import Staff

class AuthOpertate:
    user = ''
    staff = ''

    def __init__(self, user):
        assign = ''

    def has_assigned(self, username):
        try:
            staff = Staff.objects.get(name=username)
            return staff.status == authContant.AUTH_STATUS_ASSIGNED
        except Exception as e:
            return False

    def has_manage_permission(self):
        return self.staff.type == authContant.AUTH_TYPE_MANAGER or self.staff.type == authContant.AUTH_TYP_DEVELOPER

