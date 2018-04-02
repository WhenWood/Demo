from Demo.Constant import authContant
from TestModel.dbModels import Staff


class Auth:
    staff_id = ''
    status = ''
    type = ''
    staff_name = ''
    isStaff = False

    def __init__(self, staff_name):
        staff = Staff.objects().filter(staff_name=staff_name)
        if not staff:
            self.isStaff = False
        else:
            self.isStaff = True
            self.type = staff['type']
            self.staff_name = staff_name
            self.staff_id = staff['staff_id']
            self.publish_plan_id = staff['publish_plan_id']

    def has_assigned(self):
        return self.status == authContant.AUTH_STATUS_ASSIGNED

    def assigned_publish_plan(self):
        return self.publish_plan_id

    def has_manage_permission(self):
        return self.type == authContant.AUTH_TYPE_MANAGER or self.type == authContant.AUTH_TYP_DEVELOPER

