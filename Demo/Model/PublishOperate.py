from TestModel.dbModels import AssignVersion, Staff, PublishPlan
import datetime


class PublishOperate:

    publishObj = ''
    date_list = [
        'st_actual_start_date',
        'st_actual_end_date',
        'uat1_actual_start_date',
        'uat1_actual_end_date',
        'uat2_actual_start_date',
        'uat2_actual_end_date',
        'mt_actual_start_date',
        'mt_actual_end_date',
        'st_plan_start_date',
        'st_plan_end_date',
        'uat1_plan_start_date',
        'uat1_plan_end_date',
        'uat2_plan_start_date',
        'uat2_plan_end_date',
        'mt_plan_start_date',
        'mt_plan_end_date',
    ]

    def __init__(self, sys_name):
        publish = PublishPlan.objects.filter(sys_name=sys_name, status=True)
        self.publishObj = publish
        
    def copy(self, publish):
        for index in self.date_list:
            publish.__dict__[index] = self.publishObj.__dict__[index]
        return publish

    def edit(self, sys_name, plan_dict):
        publish = PublishPlan(sys_name=sys_name, status=True)
        if self.publishObj is not None:
            self.disable()
            publish = self.copy(publish)

        for index in self.date_list:
            if index in plan_dict.has_key:
                publish.__dict__[index] = datetime.datetime.strptime(plan_dict[index], '%Y-%m-%d')

        publish.save()
        self.publishObj = publish

    def disable(self):
        self.publishObj.status = False
        self.publishObj.save(update_fields=['status'])

    def get_stage(self):
        if self.publishObj is None:
            return None
        if self.publishObj.uat1_actual_start_date is not None and self.publishObj.uat1_actual_end_date is None:
            return 'UAT1'
        if self.publishObj.uat1_actual_end_date is not None and self.publishObj.uat2_actual_start_date is None:
            return 'UAT2'
        if self.publishObj.uat2_actual_end_date is not None and self.publishObj.mt_actual_start_date is None:
            return 'MT'


