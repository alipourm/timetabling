__author__ = 'alipour'
from intervaltree import Interval, IntervalTree


TIME_SLOT_LEN = 1

class Worker:
    generated = 0
    def __init__(self, name, max_hour, weighted_preference, seniority):
        """
        :param name:
        :param max_hour:
        :param weighted_preference: dictionary {'time': preference}
        :return:
        """
        self.name = name
        self.max_hour = max_hour
        self.scheduled_hours = 0


        self.availablity = IntervalTree()
        self.prefered_availablity = IntervalTree()
        for (w, (start, finish)) in weighted_preference:
            self.availablity[start:finish] = (start, finish)
            if w > 1:
                self.prefered_availablity[start:finish] = (start, finish)

        self.satisfaction = 0
        self.schedule = []
        self.seniority = seniority
        Worker.generated += 1
        self.id = Worker.generated

    def is_available(self, start, end):
        if self.availablity[start:end]:
            return True
        else:
            return False

    def is_prefer(self, start, end):
        if self.prefered_availablity[start:end]:
            return True
        else:
            return False



    #     if time_slot in self.weigthed_preference[time_slot] > 0:
    #         if time_slot not in self.schedule:
    #             if self.scheduled_hours < self.max_hour:
    #                 return True
    #
    #     return False

    # def assign(self, time_slot):
    #     if self.is_available(time_slot):
    #         # if is available and not been scheduled already
    #         self.schedule.append(time_slot)
    #         self.satisfaction += self.weigthed_preference[time_slot]
    #         self.scheduled_hours += TIME_SLOT_LEN
    #         return True
    #     else:
    #         return False

#     def free(self, time_slot):
#         # It doesn't matter if the worker really been scheduled or not.
#         if time_slot in self.scheduled_hours:
#             self.schedule.remove(time_slot)
#             self.satisfaction -= self.weigthed_preference[time_slot]
#             self.scheduled_hours -= TIME_SLOT_LEN
#
#     def get_priority(self, time_slot):
#         if not self.is_available(time_slot):
#             return 0
#         return self.weigthed_preference[time_slot] + self.seniority
#
# class JobAlreadyScheduled(Exception):
#     pass
#
# class WorkerAlreadyScheduled(Exception):
#     pass



class Job:
    generated = 0
    def __init__(self, name, start, end, priority):
        """
        :param name:
        :param required_time_slots:
        :param priority: some jobs can be optional
        :return:
        """
        self.name = name
        Job.generated += 1
        self.id = Job.generated
        self.start = start
        self.end = end
        self.priority = priority

    def conflict(self, other):
        objs =[self, other]
        for o1 in objs:
            for o2 in objs:
                if o1 != o2:
                    if o1.start <= o2.start <= o1.end or o1.start <= o2.end <= o1.end:
                        return True
        return False
    #
    # def assign_worker(self, time_slot, worker):
    #     if time_slot in self.timetable:
    #         raise JobAlreadyScheduled
    #
    #     if not worker.is_available():
    #         raise WorkerAlreadyScheduled
    #
    #     if worker.assign(time_slot):
    #         self.timetable[time_slot] = worker
    #     else:
    #         raise Exception
    #
    # def free(self, time_slot):
    #     if time_slot in self.timetable:
    #         worker = self.timetable[time_slot]
    #         worker.free(time_slot)
    #         del self.timetable[time_slot]
    #
    # def need_to_schedule(self):
    #     not_scheduled = []
    #     for t in self.requred_time_slots:
    #         if t not in self.timetable:
    #             not_scheduled.append(t)
    #     return not_scheduled
#
# def schedule(jobs, workers):
#     """
#
#     :param jobs: list of jobs
#     :param workers: list of workers
#     :return:
#     """
#     time_slots = []
#     for job in jobs:
#         time_slots = job,need_to_schedule()
#         for t in time_slots:
#             for worker in workers:
#                 if worker.is_available(time_slots):
#                     job.assign_worker(t, worker)
#
#
#     for job in jobs:
#         print(job)
#         print(job.need_to_schedule())