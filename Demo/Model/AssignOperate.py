from TestModel.dbModels import AssignVersion, Staff, PublishPlan


class AssignOperate:

    assignObj = ''

    def __init__(self, staff_obj):
        assign = AssignVersion.objects.filter(staff_id=staff_obj.id, status=True)
        self.assignObj = assign
        self.staffObj = staff_obj

    def has_assigned(self):
        return self.assignObj is None or self.assignObj.status

    def assign(self, staff_obj, publish_obj):
        if self.has_assigned():
            self.un_assign()
        assign = AssignVersion(staff_id=staff_obj.id, staff_name=staff_obj.name, status=True,
                               plan_id=publish_obj.id,end_date=publish_obj.plan_end_date)
        assign.save()

    def un_assign(self):
        self.assignObj.status = False
        self.assignObj.save(update_fields=['status'])


