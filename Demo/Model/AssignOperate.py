from TestModel.dbModels import AssignActionRecord


class AssignOperate:

    def create_record(self, staff_name, version_name, operator):
        assign_record = AssignActionRecord(staff_name=staff_name, status=True, operator=operator,
                                           version_plan_name=version_name)
        assign_record.save()

    def disable_record(self, version_name, staff_names, operator):
        AssignActionRecord.objects.filter(version_name=version_name, status=True).extra(
            where=['staff_name IN (' + staff_names + ')']).update(status=False, disable_operator=operator)
