from TestModel.dbModels import AssignVersion, Workload
from Demo.Model.PublishOperate import PublishOperate


class AssignOperate:

    assignObj = ''

    def __init__(self, staff_name):
        assign = AssignVersion.objects.filter(staff_id=staff_name, status=True)
        self.assignObj = assign

    def has_assigned(self):
        return self.assignObj is None or self.assignObj.status

    def assign(self, staff_name, version_name):
        if self.has_assigned():
            self.un_assign()
        assign = AssignVersion(staff_name=staff_name, status=True,
                               version_name=version_name)
        assign.save()
        publish = PublishOperate(version_name)
        workload = Workload(staff_name=staff_name, version_name=version_name, stage=publish.get_stage())
        workload.save()

    def un_assign(self):
        self.assignObj.status = False
        self.assignObj.save(update_fields=['status'])


