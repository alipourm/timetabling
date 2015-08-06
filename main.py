__author__ = 'alipour'

import sys
import json
from worker import *

from pysmt.shortcuts import Symbol, And, Equals, LE, Xor, ExactlyOne, Not, Plus, Implies
from pysmt.typing import FunctionType, BOOL, INT, BVType


JOBS = 100
WORKER_NUMS =  10


def get_variables(jobs, workers):
    # Assume jobs are in order from 1..N
    sofar = {}
    worksAt = {}
    isFree = {}
    gain = {}
    no_conflict = {}
    # initial constraints
    for w in workers:
        wid = w.id
        jid = 0
        gain[wid, jid] = Symbol('gain_w{0}_at_{1}'.format(wid, jid), INT)
        sofar[wid, jid] = Symbol('sofar_w{0}_j{1}'.format(wid,jid), INT)

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
            'gain': gain
            }

def constraints(jobs, workers):
    res =  get_variables(jobs, workers)
    sofar = res['sofar']
    worksAt = res['worksAt']
    isFree = res['isFree']
    gain = res['gain']
    constraints = []

    for worker in workers:
        worker_id = worker.id
        constraints.append(Equals(sofar[worker_id, 0], 0))
        constraints.append(Equals(gain[worker_id, 0], 0))
        c = [worksAt[worker_id, n.id] for n in jobs]
        constraints.append(ExactlyOne(c))
        for job in jobs:
            jid = job.id

            # worker shall not work more than 20
            constraints.append(LE(sofar[worker_id, jid], 20))


            assign_c = And([isFree[worker_id, jid],
                           Equals(sofar[worker_id,j], Plus(sofar[worker_id, jid-1], 1)),
                           worksAt[worker_id, j]
                           ])
            not_assign_c = And([Equals(gain[worker_id,j], gain[worker_id, jid-1]),
                           Equals(worksAt[worker_id, j], worksAt[worker_id, jid]),
                           Equals(sofar[worker_id,j], sofar[worker_id, jid-1]),
                           ])
            constraints.append(Xor(assign_c, not_assign_c))


    for worker in workers:
        wid = worker.id
        for j1 in jobs:
            jid1 = j1.id
            Equals(isFree[wid,j1.id], worker.is_available(j1.start, j1.end))
            for j2 in jobs:
                if j1 != j2:
                    jid2 = j2.id
                    Implies(And(worksAt[wid, jid1], worksAt[wid,jid2]), not j1.conflicts(j2))

    return constraints




import glob
import xlrd
import sys

def main():
    for f in glob.glob("/home/alipour/Desktop/*.xls"):
        print(f)
        get_availability(f)



def get_availability(f):
    color_set = set()
    book = xlrd.open_workbook(f, formatting_info=True)
    sheets = book.sheet_names()
    print "sheets are:", sheets
    for index, sh in enumerate(sheets):
        sheet = book.sheet_by_index(index)
        print "Sheet:", sheet.name
        rows, cols = sheet.nrows, sheet.ncols
        print "Number of rows: %s   Number of cols: %s" % (rows, cols)
        for row in range(rows):
            for col in range(cols):
               # print "row, col is:", row+1, col+1,
                thecell = sheet.cell(row, col)
                # could get 'dump', 'value', 'xf_index'
              #  print thecell.value,
                xfx = sheet.cell_xf_index(row, col)
                xf = book.xf_list[xfx]
                bgx = xf.background.pattern_colour_index
              #  print bgx
                color_set.add(bgx)
    print(color_set)
    return color_set



if __name__ == "__main__":
    main()
