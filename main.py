__author__ = 'alipour'

from worker import *


from pysmt.shortcuts import Symbol, And, Equals, LE, Xor, ExactlyOne, Not, Plus, Implies, Int, GE, Bool, get_model, Min, Iff
from pysmt.typing import BOOL, INT
import glob
import xlrd
import sys
import json


JOBS = 100
WORKER_NUMS =  10


def get_variables(jobs, workers):
    # Assume jobs are in order from 1..N
    sofar = {}
    worksAt = {}
    isFree = {}
    gain = {}
    no_conflict = {}
    jobs_allocated = {}
    # initial constraints
    for w in workers:
        wid = w.id
        jid = 0
        gain[wid, jid] = Symbol('gain_w{0}_at_{1}'.format(wid, jid), INT)
        sofar[wid, jid] = Symbol('sofar_w{0}_j{1}'.format(wid,jid), INT)


    for i in range(0, Job.generated + 1):
        print(i)
        jobs_allocated[i] = Symbol('jobs_allocated_sofar_{0}'.format(i), INT)


    jobs_assigned = {}
    for j1 in jobs:
        jobs_assigned[j1.id, 0] = Symbol('jobs_{0}_assigned_at_step{1}'.format(j1.id, 0), BOOL)
        for j2 in jobs:
            jobs_assigned[j1.id, j2.id] = Symbol('jobs_{0}_assigned_at_step{1}'.format(j1.id, j2.id), BOOL)


    for w in workers:
        wid = w.id
        for j in jobs:
            jid = j.id
            worksAt[wid, jid] = Symbol('w{0}_worksAt_{1}'.format(wid, jid), BOOL)
            gain[wid, jid] = Symbol('gain_w{0}_at_{1}'.format(wid, jid), INT)
            sofar[wid,jid] = Symbol('sofar_w{0}_j{1}'.format(wid,jid), INT)
            isFree[wid,jid] = Symbol('isfree_w{0}_j{1}'.format(wid,jid), BOOL)

    return {'sofar': sofar,
            'worksAt': worksAt,
            'isFree': isFree,
            'gain': gain,
            'assigned': jobs_assigned,
            'jobs_allocated' : jobs_allocated
            }

def get_constraints(jobs, workers):
    res = get_variables(jobs, workers)
    sofar = res['sofar']
    worksAt = res['worksAt']
    isFree = res['isFree']
    gain = res['gain']
    assigned = res['assigned']
    jobs_allocated = res['jobs_allocated']
    constraints = []

    c = Equals(jobs_allocated[0], Int(0))
    constraints.append(c)

    # initially no job has been assigned
    for j1 in jobs:
            c = Not(assigned[j1.id, 0])
            constraints.append(c)
    # at the end all jobs must be assigned
    for j1 in jobs:
            c = assigned[j1.id, Job.generated]
            # constraints.append(c)
    c = GE(jobs_allocated[Job.generated], Int(20))
    for j in jobs:
        c = [worksAt[w.id, j.id] for w in workers]
        # constraints.append(ExactlyOne(c))


    for worker in workers:
        worker_id = worker.id
        constraints.append(GE(sofar[worker_id, Job.generated], Int(min(worker.min_hour,8))))
        # constraints.append(LE(sofar[worker_id, Job.generated], Int(min(worker.max_hour,20))))
        constraints.append(Equals(sofar[worker_id, 0], Int(0)))
        constraints.append(Equals(gain[worker_id, 0], Int(0)))

    for job in jobs:
        cc = []
        for worker in workers:
            worker_id = worker.id
            jid = job.id
            c1 = Implies(isFree[worker_id, jid], Xor(worksAt[worker_id, jid], Not(worksAt[worker_id, jid])))
            c2 = Implies(Not(isFree[worker_id, jid]), Not(worksAt[worker_id, jid]))
            c3 = Iff(worksAt[worker_id, jid], Equals(sofar[worker_id,jid], Plus(sofar[worker_id, jid-1], Int(1))))
            c4 = Iff(Not(worksAt[worker_id, jid]), Equals(sofar[worker_id,jid], Plus(sofar[worker_id, jid-1])))
            cc.append(worksAt[worker_id, jid])
            constraints +=[c1, c2, c3, c4]
        c5 = ExactlyOne(cc)
        constraints.append(c5)
    print(type(constraints))




    return constraints
        #
        #     # worker shall not work more than 20
        #     assign_c = And([
        #         Not(assigned[job.id, job.id - 1]),
        #         assigned[job.id, job.id],
        #         isFree[worker_id, jid],
        #         Equals(sofar[worker_id,jid], Plus(sofar[worker_id, jid-1], Int(1))),
        #         worksAt[worker_id, jid],
        #         Equals(jobs_allocated[jid], Plus(jobs_allocated[jid-1], Int(1)))
        #        ])
        #     cc.append(assign_c)
        #     not_assign_c = And([
        #         Equals(gain[worker_id,jid], gain[worker_id, jid-1]),
        #         Not(worksAt[worker_id, jid]),
        #         Equals(sofar[worker_id,jid], sofar[worker_id, jid-1]),
        #         Equals(jobs_allocated[jid], jobs_allocated[jid-1])
        #         # Iff(assigned[job.id, job.id - 1], assigned[job.id, job.id])
        #         ])
        #     constraints.append(Xor(assign_c, not_assign_c))
        # # constraints.append(ExactlyOne(cc))
    for worker in workers:
        wid = worker.id
        for j1 in jobs:
            jid1 = j1.id
            if worker.is_available(j1.day, j1.start, j1.end):
                c = isFree[wid, j1.id]
            else:
                c = Not(isFree[wid,j1.id])
            constraints.append(c)
            for j2 in jobs:
                if j1 != j2:
                    jid2 = j2.id
                    c = Implies(And(worksAt[wid, jid1], worksAt[wid,jid2]), Bool(not j1.conflicts(j2)))
                    constraints.append(c)
    return constraints





def load_data():
    jobs = []
    data = json.load(open("sample.json"))
    job_name = data["JobName"]
    for day, start, end, step in data["JobTime"]:
        for l in range(start, end, step):
            job = Job("{0}:{1}: {2}-{3}".format(job_name, day, l, l + step), day,  l, l + step, 10)
            jobs.append(job)


    workers_obj = data["workers"]

    # maybe an assistant decision system is better.
    workers = []
    for w in workers_obj:
        w_name = w["name"]
        max_hour = w["maxtime"]
        min_hour = w["mintime"]

        seniority = w["senior"]
        availability = IntervalTree()
        preference = IntervalTree()
        for day, start, end, step in w['availability']:
            availability[start:end] = day
        for day, start, end, step in w['preference']:
            preference[start:end] = day
        w = Worker(w_name, availability, preference, seniority, max_hour, min_hour)
        workers.append(w)

    return workers, jobs


# def main():
#     for f in glob.glob("/home/alipour/Desktop/*.xls"):
#         print(f)
#         get_availability(f)
#
#
#
# def get_availability(f):
#     color_set = set()
#     book = xlrd.open_workbook(f, formatting_info=True)
#     sheets = book.sheet_names()
#     print "sheets are:", sheets
#     for index, sh in enumerate(sheets):
#         sheet = book.sheet_by_index(index)
#         print "Sheet:", sheet.name
#         rows, cols = sheet.nrows, sheet.ncols
#         print "Number of rows: %s   Number of cols: %s" % (rows, cols)
#         for row in range(rows):
#             for col in range(cols):
#                # print "row, col is:", row+1, col+1,
#                 thecell = sheet.cell(row, col)
#                 # could get 'dump', 'value', 'xf_index'
#               #  print thecell.value,
#                 xfx = sheet.cell_xf_index(row, col)
#                 xf = book.xf_list[xfx]
#                 bgx = xf.background.pattern_colour_index
#               #  print bgx
#                 color_set.add(bgx)
#     print(color_set)
#     return color_set
#
#

if __name__ == "__main__":
    workers, jobs = load_data()

    k = IntervalTree()
    # for w in workers:
    #     k = k|w.availability
    #
    # print(k)
    #
    # exit(0)

    print(workers)
    const = get_constraints(jobs, workers)
    formula = And(const)
    model = get_model(formula)
    if model:
        print(model)
    else:
        print("No solution found")