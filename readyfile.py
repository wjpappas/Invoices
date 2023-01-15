#!/usr/bin/python

import os
import sys
import re
import datetime
import logging

"""     Run for each vendor to consolidate QB input file

Successively addin complete records to "allrdy_mmdd.csv" while checking for jobless records. These records are stored in "vendor name_ch.csv" and notes are stored in "mmdd_cklog.txt"
"""

CatchNumRegex = re.compile(r'^([\"]*\w+[-,& \w+\.\"]*,\d{1,2}/\d{1,2}/\d{4}),(\w+[/-]*\w),.*,(Eastside|Westside),(.*),\w,')
CheckClassRegex = re.compile(r'.*(Eastside|Westside).*(:\d\d-\d\d\d|21-000|22-000)')
CheckHeaderRegex = re.compile(r'Vendor,Transaction Date,Ref')

input_name = sys.argv[1]              # vendor prefix "inv" | "rod" | "std"
vend_name = sys.argv[2]               # vendor name "sherwin"|"rodda"|"standard"
header = 'Vendor,Transaction Date,RefNumber,Bill Due,Terms,Memo,Address Line1,Address Line2,Address Line3,Address Line4,Address City,Address State,Address PostalCode,Address Country,Vendor Acct No,Expenses Account,Expenses Amount,Expenses Memo,Expenses Class,Expenses Customer,Expenses Billable,Items Item,Items Qty,Items Description,Items Cost,Items Class,Items Customer,Items Billable,AP Account\n'

dt = datetime.datetime.now()

outname2 = vend_name + dt.strftime('%m%d') + '_ck.csv'
outname3 = dt.strftime('%m%d') + '_cklog.log'
outname4 = 'allrdy_' + dt.strftime('%m%d') + '.csv'

jobless_record = open(outname2, 'w')

logging.basicConfig(filename=outname3, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info('Invoices missing Job# %s', vend_name)

invoice_rdy = open(outname4, 'a')
invoice_rdy.close()

with open(outname4, 'r') as f:
    line4 = f.readline()

if not (CheckHeaderRegex.search(line4)):
    with open(outname4, 'w') as f:
        f.write(header)

invoice_rdy = open(outname4, 'a')

pflag = 1

dirlocal = os.getcwd()
dirlist = os.listdir(dirlocal)
for x in dirlist:
    if (x.startswith(input_name) and x.endswith('.csv')):
#        logging.debug('Line one %s', x)
        tfile = open(x)
        line = tfile.readline()
#        logging.debug('top setup %s', line)
        if (CheckHeaderRegex.search(line)):
            if (pflag):
                jobless_record.write(line)
                pflag = 0
#            logging.debug('found header %s', pflag)
            line = tfile.readline()
            see_tree = CatchNumRegex.search(line)
            invoiceNum = ''
            while True:
#                logging.debug('Lower loop')
                if (CheckClassRegex.search(line)):
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
                logging.debug('%s', line)
                logging.debug('Invoice#: %s see_tree: %s', invoiceNum, see_tree.group(2))
                if not (invoiceNum == see_tree.group(2)):
                    invoiceNum = ''
            tfile.close()

jobless_record.close()
invoice_rdy.close()
