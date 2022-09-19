#! /usr/bin/python3

import re
from datetime import datetime


def make_dict(cust_file):

    job_keyRegex = re.compile(r':([\d]{2}[-][\d]{3})')

    jobN_dict = {}
    jobN_dict['22-000'] = '22-000 OH'
    with open(cust_file) as f:
        for line in f:
            #            print(line)
            line = line.rstrip()
            (cust_job, jclass) = line.split(',,')

            cust_job = cust_job.strip('"')
#            print(cust_job, jclass)

            jk = job_keyRegex.search(cust_job)

            if (jk):
                job_key = jk.group(1)
                cust_job_class = cust_job + jclass
#                print(job_key,cust_job_class,'<<<<')
                jobN_dict[job_key] = cust_job_class

    return jobN_dict


def datex(idate, termd):

    datx = datetime.strptime(idate, "%m/%d/%Y")
    m1 = datx.month
    y1 = datx.year
    d1 = datx.day

#   print(m1,d1,y1)
    if d1 >= 1:
        m1 = m1 + 1
    if m1 == 13:
        m1 = 1
        y1 = y1 + 1
#   print(m1,d1,y1)
    a1 = datx.replace(month=m1, day=termd, year=y1)
#   print(a1)
    date_due = a1.strftime("%m/%d/%Y")
#   print(date_due)
    return date_due
