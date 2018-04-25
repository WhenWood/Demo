from TestModel.dbModels import VersionPlan, StagePlan, Staff
from Demo.Model.AssignOperate import AssignOperate
from Demo.Constant import authContant
import datetime

class PlanOperate:
    version_plan = ''
    stage_plans = ''
    user = ''
    plan_var_list = ['version_name', 'plan_workload', 'used_workload']
    stage_var_list = ['stage', 'plan_start_date', 'actual_start_date',
                      'plan_end_date', 'actual_end_date', 'plan_workload', 'used_workload']

    def __init__(self, user, version=''):
        self.user = user
        if isinstance(version, VersionPlan):
            self.version_plan = version
            self.stage_plans = self.version_plan.version_plan_stage_plan.all()
        elif version != '':
            self.get_plan_operate_by_version_name(version)

    def get_plan_operate_by_version_name(self, name):
        if self.version_plan == '' or self.version_plan.version_name != name:
            version_plan_obj = VersionPlan.objects.filter(version_name=name, status=True).order_by('-update_time')
            if version_plan_obj:
                self.version_plan = version_plan_obj[0]
        if self.version_plan:
            self.stage_plans = self.version_plan.version_plan_stage_plan.all()

    def version_active_exist(self):
        return self.version_plan != ''

    def get_all_active_plan(cls):
        return VersionPlan.objects.filter(status=True).order_by('-update_time')

    def create(self, version_info, stage_infos):
        self.suspend_plan(version_info['version_name'])
        self.create_version_plan(version_info)
        self.create_stage_plan(stage_infos)

    def update_all(self, version_info, stage_infos):
        if self.version_plan:
            version = self.version_plan
        else:
            self.get_plan_operate_by_version_name(version_info['version_name'])
            version = self.version_plan
        if not version:
            self.suspend_plan()
            invalid_version_plan = self.version_plan
            self.create(version_info, stage_infos)
            self.update_assign_staff(invalid_version_plan)
        else:
            self.create(version_info, stage_infos)

    def update_versoion(self, version_info):
        for var in self.plan_var_list:
            if var in version_info:
                self.version_plan.__dict__[var] = version_info[var]
        self.version_plan.save()

    def update_stage(self, stage_infos):
        for stage in stage_infos:
            stage_plan = self.stage_plans.get(stage=stage)
            stage_info = stage_infos[stage]
            if not stage_plan:
                stage_plan = StagePlan()
                stage_plan.version_plan = self.version_plan
            for var in self.stage_var_list:
                if var in stage_info:
                    stage_plan.__dict__[var] = stage_info[var]
            stage_plan.save()
        self.stage_plans = self.version_plan.version_plan_stage_plan.all()

    def suspend_plan(self, plan_name=''):
        if plan_name == '' and self.version_plan:
            self.version_plan.status=False
            self.version_plan.save()
        elif plan_name != '':
            plan = VersionPlan.objects.filter(version_name=plan_name, status=True)
            plan.update(status=False)

    def create_version_plan(self, version_info):
        version_plan = VersionPlan()
        for var in self.plan_var_list:
            if var in version_info:
                version_plan.__dict__[var] = version_info[var]
        is_exist = VersionPlan.objects.filter(version_name=version_info['version_name'], status=True)
        if is_exist:
            return '版本已经存在'
        version_plan.status = True
        version_plan.operator = self.user.username
        version_plan.save()
        self.version_plan = version_plan
        return 0

    def create_stage_plan(self, stage_infos):
        for stage in stage_infos:
            stage_plan = StagePlan()
            stage_info = stage
            for var in self.stage_var_list:
                if var in stage_info and stage_info[var] != '':
                    stage_plan.__dict__[var] = stage_info[var]
            stage_plan.version_plan = self.version_plan
            stage_plan.save()
        self.stage_plans = self.version_plan.version_plan_stage_plan.all()
        return 0

    def update_assign_staff(self, invalid_version_plan):
        staffs = invalid_version_plan.assign_staffs
        for staff in staffs:
            invalid_version_plan.assign_staffs.remove(staff)
            self.version_plan.assign_staffs.add(staff)
        invalid_version_plan.save()
        self.version_plan.save()

    def add_staff_to_plan(self, staff_names):
        staffs = Staff.objects.extra(where=['name IN (' + staff_names + ')'])
        for staff in staffs:
            self.version_plan.assign_staffs.add(staff)
            assign_operate = AssignOperate()
            assign_operate.create_record(staff.name, self.version_plan.id, self.version_plan.name, self.user.username)
        self.version_plan.save()

    def remove_staff_to_plan(self, staff_names):
        staffs = Staff.objects.extra(where=['name IN (' + staff_names + ')'])
        for staff in staffs:
            self.version_plan.assign_staffs.remove(staff)
        self.version_plan.save()
        assign_operate = AssignOperate()
        assign_operate.disable_record(staff.name, self.version_plan.id, self.user.username)

    def get_stage(self):
        if not self.stage_plans:
            return {'error': -1, 'stage_status': '计划阶段不存在'}
        stage_proceed = self.stage_plans.filter(actual_end_date=None).exclude(actual_start_date=None)
        if stage_proceed:
            stage_plan = stage_proceed[0]

            return dict(
                error=0,
                stage_status=stage_plan.stage + '阶段正在进行中',
                stage=stage_plan.stage,
                used_days=(datetime.datetime.now().date-stage_plan.actual_start_plan).days,
                left_days=(stage_plan.plan_end_date-datetime.datetime.now().date()).days,
            )
        stage_waiting = self.stage_plans.filter(actual_start_date=None).order_by("plan_start_date")
        if stage_waiting:
            stage_plan = stage_waiting[0]
            return dict(
                error=1,
                stage_status=stage_plan.stage +'阶段尚未开始',
                stage=stage_plan.stage,
                used_days=0,
                left_days=(stage_plan.plan_start_date-datetime.datetime.now().date).days,
            )
        return {'error': -1, 'stage_status': '版本计划中所有阶段均已结束，请终止计划，或修改计划'}



