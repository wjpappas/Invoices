#! /usr/bin/python3

import re
import csv
from configparser import ConfigParser
from datetime import datetime

def _get_overhead():
    """Fetch the overhead job code from your configuration file.

    Expects a configuration file named "invoices.ini" with structure:

        [overhead_code]
        OH_thisyear=23-000
        OH_lastyear=22-000
    """
    config = ConfigParser()
    config.read("Invfile/invoices.ini")
    # config.read("invoices.ini")
    thisyear = config["overhead_code"]["OH_thisyear"]
    lastyear = config["overhead_code"]["OH_lastyear"]
    std_file = config["file_spec"]["product"]
    out_file = config["file_spec"]["header"]
    return [thisyear, lastyear, std_file, out_file]

job_keyRegex = re.compile(r':([\d]{2}[-][\d]{3})')

def make_dict(cust_file, oh_key):

    jobN_dict = {}
    jobN_dict[oh_key] = oh_key + ' OH'

    with open(cust_file) as csvf:
        cfr = csv.reader(csvf)
        for line in cfr:
            (cust_job, jclass) = line
            cust_job = cust_job.strip('"')
            jk = job_keyRegex.search(cust_job)
            if (jk):
                job_key = jk.group(1)
                cust_job_class = cust_job + jclass
                jobN_dict[job_key] = cust_job_class
    return jobN_dict

def datex(idate, termd):

    datx = datetime.strptime(idate, "%m/%d/%Y")
    m1, y1, d1 = datx.month, datx.year, datx.day

    if d1 >= 1:
        m1 = m1 + 1
    if m1 == 13:
        m1 = 1
        y1 = y1 + 1
    a1 = datx.replace(month=m1, day=termd, year=y1)
    date_due = a1.strftime("%m/%d/%Y")
    return date_due

def read_vendor(file):
    """Read vendor file into working lists."""
    vend_list = [[], [], []]
    with open(file)as read_v:
        r_val = [int(x.rstrip()) for x in read_v.readline().split(',')]
        for val, bb in zip(r_val, vend_list):
            for line in range(val):
                bb.append(read_v.readline().rstrip())
    return vend_list

def set_dict(rec_keys, rec_val):
    """Set values for dictionary."""
    return dict(zip(rec_keys, rec_val))

def update_dict(rec_dict, rec_keys, rec_val):
    """Incrimental udate of output dictionary."""
    up_dict = set_dict(rec_keys, rec_val)
    return rec_dict.update(up_dict)

def print_record(file, record_dict, record_keys):
    """Write record, duh."""
    out_list = [record_dict[key] for key in record_dict]
    file.writerow(out_list)
    return  # print("hello, print record")

def prt_value(item, qty, desc, value, r_dict, p_list):
    """Load record values and print."""
    if value != 0.00:
        u_list = [item, qty, desc, '{:.2f}'.format(value)]
        update_dict(r_dict, p_list[0], u_list)
        print_record(p_list[1], r_dict, p_list[2])

def listFile(infile):
    """Read file into list."""
    with open(infile) as in_file:
        file_read = csv.reader(in_file, quotechar="'")
        array = list(file_read)
    return array
