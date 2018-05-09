from TestModel.dbModels import AssignActionRecord


class AssignOperate:

    def create_record(self, staff_name, version_name, operator):
        assign_record = AssignActionRecord(staff_name=staff_name, status=True, operator=operator,
                                           version_plan_name=version_name)
        assign_record.save()

    def disable_record(self, staff_names, version_name, operator):
        assign_record = AssignActionRecord.objects.filter(version_plan_name=version_name, status=True,
                                                          staff_name=staff_names).update(status=False, disable_operator=operator)
