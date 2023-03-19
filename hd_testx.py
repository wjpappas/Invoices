#! /usr/bin/python3

import re
import csv
import sys
import logging
from datetime import datetime
import pandas as pd
from block_head import make_dict, read_vendor, set_dict, update_dict, print_record, prt_value, _get_overhead, listFile
from qb_func import f_side, f_cust_job, item_ck

logging.basicConfig(filename='invoices.log', level=logging.DEBUG, format='%(lineno)d - %(funcName)s - %(levelname)s - %(message)s')

def date_form(xdate):
    a1 = datetime.strptime(xdate, "%Y-%m-%d")
    date_new = a1.strftime("%m/%d/%Y")
    return date_new

def tool_text(row, unit_max, fileid):
    unitprice = float((row[7]).lstrip('$'))
    if (unitprice >= unit_max):
        outputTools.writerow(row)

outputnameRegex = re.compile(r'(\S+).csv')

sep = ';'
unit_max = 50.00

logging.debug('argv[0]: %s ', sys.argv[0])
ifile_vendor = sys.argv[1]
logging.debug('argv[1]: %s ', ifile_vendor)
ifile_name = sys.argv[2]
logging.debug('argv[1]: %s argv[2]: %s ', ifile_vendor, ifile_name)
cust_file = sys.argv[3]

oh_codes = _get_overhead()
overhead_now, overhead_last, std_file, input_list = oh_codes
overhead_x = r'%s'%overhead_now
qb_header, qb_record, record_keys, vendor_keys, update_keys, headr_keys, term_key = [x for x in listFile(input_list)]
cust_dict = make_dict(cust_file, overhead_now)

opf = outputnameRegex.search(ifile_name)
outname = opf.group(1)+'qb.csv'
outputFile = open(outname, 'w', newline='', encoding='utf-8')
toolName = opf.group(1)+'Tools.txt'
toolsFile = open(toolName, 'w')
outputInvoice = csv.writer(outputFile)
outputTools = csv.writer(toolsFile)

# outputInvoice.writerow(qb_header)
header_dict = set_dict(record_keys, qb_header)
print_record(outputInvoice, header_dict, record_keys)

vendor_val, a, b = read_vendor(ifile_vendor)
record_dict = set_dict(record_keys, qb_record)
update_dict(record_dict, vendor_keys, vendor_val)
i_terms = vendor_val[1]

print(ifile_name, ifile_vendor, cust_file)
data = pd.read_csv(ifile_name, header=5, usecols=['Invoice Date', 'Store Number and Name', 'Invoice Number', 'Invoice Due Date', 'PO# / Job Name', 'SKU Description', 'Quantity', 'Original Unit Price', 'Invoice Total'], nrows=550)

rowls = iter(data.values.tolist())
browls = next(rowls)

desc_list = [browls[5]]
inv_num = browls[2]

browlsx = next(rowls, 'x')
while browlsx != 'x':
    logging.debug('row: %s ', str(browls))
    logging.debug('d list: %s invoice #: %s', desc_list, inv_num)
    logging.debug('row: %s ', str(browlsx))

    tool_text(browls, unit_max, toolName)

#  assign stuff
    if inv_num == browlsx[2]:
        desc = browlsx[5]
        logging.debug('d list: %s invoice #: %s', browlsx[2], inv_num)
        logging.debug('d list: %s invoice #: %s', desc_list, inv_num)
        if desc not in desc_list:
            desc_list.append(desc)
        desc = browlsx[5]
        browls = browlsx
        logging.debug('d list: %s invoice #: %s', desc_list, inv_num)

#            print(desc_list)
    else:
        idate, location, inv_num, date_due, ijobn, desc, qty, unitcost, cost = browls
        logging.debug('yes row: %s ', str(browls))
        desc_str = sep.join(desc_list)
        cust_job = f_cust_job(ijobn, overhead_now, overhead_last, cust_dict)
        side = f_side(location)
        item_val = re.compile(overhead_x).search(cust_job)
        item = item_ck(item_val, 'Shop Supplies', 'Supplies')
        quantity = '1'
        memo = desc_str
        price = float(cost.lstrip('$'))

        head_x = [date_form(idate), inv_num, date_form(date_due), side, cust_job]
        update_dict(record_dict, headr_keys, head_x)
        prt_list = [update_keys, outputInvoice, record_keys]
        prt_value(item, quantity, memo, price, record_dict, prt_list)

        desc_list = [browlsx[5]]
        inv_num = browlsx[2]
        browls = browlsx

    logging.debug('old row: %s ', str(browls))
    browlsx = next(rowls, 'x')
    logging.debug('new row: %s ', str(browlsx))

outputFile.close()
toolsFile.close()
