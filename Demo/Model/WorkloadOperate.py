from TestModel.dbModels import AssignVersion, Staff, PublishPlan
from TestModel.dbModels import Workload
import datetime
import calendar


class WorkloadOperate:

    first_day = ''
    last_day = ''

    def __init__(self, year='', month=''):
        self.get_month_first_day_and_last_day(year, month)


    def get_month_first_day_and_last_day(self, year=None, month=None):
        """
        :param year: 年份，默认是本年，可传int或str类型
        :param month: 月份，默认是本月，可传int或str类型
        :return: firstDay: 当月的第一天，datetime.date类型
                  lastDay: 当月的最后一天，datetime.date类型
        """
        if year:
            year = int(year)
        else:
            year = datetime.date.today().year

        if month:
            month = int(month)
        else:
            month = datetime.date.today().month

        # 获取当月第一天的星期和当月的总天数
        firstDayWeekDay, monthRange = calendar.monthrange(year, month)

        # 获取当月的第一天
        first_day = datetime.date(year=year, month=month, day=1)
        last_day = datetime.date(year=year, month=month, day=monthRange)
        self.first_day = first_day
        self.last_day = last_day

    def create(staff_name, version_name, stage=''):
        workload = Workload(staff_name=staff_name, version_name=version_name, stage=stage)
        workload.save()

    def get_workload_by_date(self, date):
        workload = Workload.objects.filter(date=datetime.datetime.strptime(date, '%Y-%m-%d'), day_off=False)
        return workload

    def get_workload_by_name(self, staff_name):
        workload = Workload.objects.filter(staff_name=staff_name, date__range=(self.first_day, self.last_day))
        return workload

    def get_workload_by_version(self, version_name):
        workload = Workload.objects.filter(version_name=version_name, day_off=False,
                                           date__range=(self.first_day, self.last_day))
        return workload
