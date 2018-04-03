from Demo.Constant import authContant
from TestModel.dbModels import Staff, AssignVersion, PublishPlan
from django.contrib.auth.models import User
import django.utils.timezone as timezone


class StaffOperate:
    staffObj = ''
    assignObj = ''
    publishObj = ''

    def create_staff(self, name, password, assigned=authContant.AUTH_STATUS_UNASSIGNED,
                     user_type=authContant.AUTH_TYPE_USER, user_status=authContant.AUTH_USER_ACTIVITY):
        staff = Staff(name=name, status=assigned, type=user_type,create_time=timezone.now(), )
        staff.save()
        user = User.objects.create(username=name, password=password, email=name+'@test.test', is_active=user_status)
        user.set_password(password)
        user.save()
        self.staffObj = staff
        self.assignObj = None
        self.publishObj = None

    def get_staff_by_name(self, name):
        staff = Staff.objects.filer(name)
        if staff:
            self.staffObj = staff[0]
        assgin = AssignVersion()

    def staff_assign(self, plan_id):
        pass

    def has_assigned(self):
        return self.assignObj is None or self.assignObj.status

    def assign(self, plan_id):
        if self.has_assigned():
            self.un_assign()
        assign = AssignVersion()

    def un_assign(self):
        self.assignObj.status = False
        self.assignObj.save(update_fields=['status'])
