#! /usr/bin/python3

import os
import sys
import re
import csv
import datetime
import logging
from block_head import _get_overhead
from qb_head import header

'''
 Run for each vendor to consolidate QB input files

 Successively addin complete records to "allrdy_mmdd.csv" and "credit_mmdd.csv
 while checking for jobless records. These records are stored in
 "vendor name_ck.csv" and notes are stored in "mmdd_cklog.txt"

'''
def new_header(outname, head, rgx):
    f = open(outname, 'a')
    f.close()
    with open(outname, 'r') as f:
        line = f.readline()
    if not (rgx.search(line)):
        with open(outname, 'w') as f:
            f.write(head)

oh_codes = _get_overhead()
overhead_now, overhead_last, std_file, input_list = oh_codes
combi = overhead_now + '|' + overhead_last
overhead_rgx = r'.*(Eastside|Westside).*(:\d\d-\d\d\d|%s)'%combi

CatchNumRegex = re.compile(r'^([\"]*\w+[-,& \w+\.\"]*,\d{1,2}/\d{1,2}/\d{4}),(\w+[/-]*\w),.*,(Eastside|Westside),(.*),\w,')
CheckClassRegex = re.compile(overhead_rgx)
CheckHeaderRegex = re.compile(r'Vendor,Transaction Date,Ref')
CheckCreditRegex = re.compile(r'.*,\d{1,2}/\d{1,2}/\d{4},Credit,.*')

input_name = sys.argv[1]              # vendor prefix "inv" | "rod" | "std"
vend_name = sys.argv[2]               # vendor name "sherwin"|"rodda"|"standard"

dt = datetime.datetime.now()
#with open('output_temp.csv') as file_obj:
#    header = next(file_obj)

outname2 = vend_name + dt.strftime('%m%d') + '_ck.csv'
jobless_record = open(outname2, 'w')
jobless_record.write(header)

outname3 = dt.strftime('%m%d') + '_cklog.log'
logging.basicConfig(filename=outname3, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info('Invoices missing Job# %s', vend_name)

outname4 = 'allrdy_' + dt.strftime('%m%d') + '.csv'
new_header(outname4, header, CheckHeaderRegex)
invoice_rdy = open(outname4, 'a')

outname5 = 'credit_' + dt.strftime('%m%d') + '.csv'
new_header(outname5, header, CheckHeaderRegex)
credit_rdy = open(outname5, 'a')

dirlocal = os.getcwd()
dirlist = os.listdir(dirlocal)
for x in dirlist:
    if (x.startswith(input_name) and x.endswith('.csv')):
#        logging.debug('Line one %s', x)
        tfile = open(x)
        line = tfile.readline()
#        logging.debug('top setup %s', line)
        if (CheckHeaderRegex.search(line)):
            line = tfile.readline()
#            logging.debug('under setup %s', line)
            see_tree = CatchNumRegex.search(line)
            invoiceNum = ''
#            logging.debug('Invoice#: %s see_tree: %s', invoiceNum, see_tree)
            while True:
#                logging.debug('Lower loop')
                if (CheckCreditRegex.search(line)):
                    credit_rdy.write(line)
                    invoiceNum = ''
                elif (CheckClassRegex.search(line)):
                    invoice_rdy.write(line)
                    invoiceNum = ''
                else:
                    jobless_record.write(line)
                    if not (invoiceNum):
                        invoiceNum = see_tree.group(2)
                        jobNum = see_tree.group(4)
                        logging.info('%s,  %s, %s ', x, invoiceNum, jobNum)
#                    logging.debug('Block 02 %s %s', x, invoiceNum)
#                    logging.debug(line)
                line = tfile.readline()
                if not line:
                    break
                see_tree = CatchNumRegex.search(line)
#                logging.debug('%s', line)
#                logging.debug('Invoice#: %s see_tree: %s', invoiceNum, see_tree.group(2))
                if not (invoiceNum == see_tree.group(2)):
                    invoiceNum = ''
            tfile.close()

jobless_record.close()
invoice_rdy.close()
credit_rdy.close()
