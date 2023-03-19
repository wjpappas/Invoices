#! /usr/bin/python3

import logging
import re
import csv
import sys
from block_head import make_dict, read_vendor, set_dict, update_dict, print_record, prt_value, _get_overhead, listFile
from qb_func import f_side, f_cust_job, item_ck, find_header_x, f_eq_val, f_due_date, f_credit, item_par

ifile_vendor = sys.argv[1]
ifile_name = sys.argv[2]
cust_file = sys.argv[3]

logging.basicConfig(filename='invoices.log', level=logging.DEBUG, format='%(lineno)d - %(funcName)s - %(levelname)s - %(message)s')
outputname_x = r'(\S+).txt'
outname = ((re.compile(outputname_x)).search(ifile_name)).group(1)+'.csv'
outputFile = open(outname, 'w', newline='', encoding='utf-8')
outputWriter = csv.writer(outputFile)

#term_key = ['terms']
cash_x = r'(INVOICE)'
eat_color = r'^\s+ T PAINT.*'
scc_x =  r'(\s*\d+\s+)(SUPPLY CHAIN CHRG)(\s+\d+\s+[-]*[\d]+[.][\d]{2}[\ *]*\s+)([-]*[\d]+[.][\d]{2})([N]*)'

def read_std_file(val, sfile):
    """Read to list "Material' product file for Standard."""
    if val == '4':
        std_list = []
        with open(sfile, 'r') as std_read:
            while True:
                line = std_read.readline()
                if not line:
                    break
                std_list.append(line.rstrip())
        return std_list

def std_item(memo, s_list):
    """Determine item value for Standard."""
    value = False
    for p_str in s_list:
        if (memo.lower()).find(p_str) != -1:
            value = True
    logging.debug('product %s; T/F: %s %s', memo, value, type(p_str))
    return value

def credit_ck(ck, term_key, iterms, cterms):
    """Is credit? for Sherwin."""
    if ck != 1:
        update_dict(record_dict, term_key, cterms)
        return -1
    else:
        update_dict(record_dict, term_key, iterms)
        return 1

oh_codes = _get_overhead()
overhead_now, overhead_last, std_file, input_list = oh_codes
overhead_x = r'%s'%overhead_now
logging.debug('OH codes: %s overhead_x: %s', oh_codes, overhead_x)
cust_dict = make_dict(cust_file, overhead_now)
qb_header, qb_record, record_keys, vendor_keys, update_keys, headr_keys, term_key = [x for x in listFile(input_list)]
header_dict = set_dict(record_keys, qb_header)
print_record(outputWriter, header_dict, record_keys)
prt_list = [update_keys, outputWriter, record_keys]

vendor_val, reg_val, grp_val = read_vendor(ifile_vendor)
salenum_rgx, backend_rgx, color_rgx, disc_rgx, tax_rgx, pca_rgx = reg_val[8:]
pca_grp, item_grp, qty_grp, tax_grp, price_grp = grp_val
record_dict = set_dict(record_keys, qb_record)
update_dict(record_dict, vendor_keys, vendor_val)
i_terms = vendor_val[1]

std_list = read_std_file(grp_val[1], std_file)
listx = [reg_val[2], reg_val[4], reg_val[2], reg_val[7], reg_val[5], reg_val[6]]
f_head = [f_eq_val, f_eq_val, f_due_date, f_side, f_eq_val, f_credit]

with open(ifile_name, 'r') as reader:

    haye = ''
    straye = []
    desc_b = re.compile(reg_val[0])

    while True:
        straye.clear()
        db = None
        while not db:                                   # read  header block
            haye = reader.readline()
            db = desc_b.search(haye)
            if re.search('\u000C', haye):
                logging.debug('parse to header')
                break
            straye.append(haye)
        if db:
            logging.debug('straye =' + str(straye))
            head_x = find_header_x(listx, straye, f_head)   # invoice header
            cust_job = head_x[4]
            head_x[4] = f_cust_job(cust_job, overhead_now, overhead_last, cust_dict)
            itSign = credit_ck(head_x[-1], term_key, [i_terms], ['Credit'])
            logging.debug('headx =' + str(head_x))

            update_dict(record_dict, headr_keys, head_x)

            memo_len = 40
            rec_pos = db.start(1)
            item_val = re.compile(overhead_x).search(cust_job)
            item_supply = item_ck(item_val, 'Shop Supplies', 'Supplies')
            logging.debug('DB position: %s; DB: %s', rec_pos, db)
            disc_total, pca_total, scc_total = 0, 0, 0
            haye = reader.readline()
            haye_last = haye

        while True:
            if not db:
                break
            pca_temp = re.compile(pca_rgx).search(haye)
            if pca_temp:
                pca_total += float(pca_temp.group(int(pca_grp)))*itSign
                haye = reader.readline()

            scc_temp = re.compile(scc_x).search(haye)
            if scc_temp:
                scc_total += float(scc_temp.group(4))
                haye = reader.readline()

            front_end = re.compile(salenum_rgx).search(haye) # sales number
            back_end = re.compile(backend_rgx).search(haye)  # backend
            if front_end and back_end:                       # complete line
                memo = (haye[rec_pos:rec_pos+memo_len]).strip()
                logging.debug('item value: %s, four-three-seven? %s, ItemS: %s', item_val, item_grp, item_supply)
                item = item_par(item_grp, memo, back_end, item_supply, std_list)
                quantity = back_end.group(int(qty_grp))
                price = float((back_end.group(int(price_grp))).replace(",", ""))*itSign
                haye = reader.readline()
                if re.compile(eat_color).match(haye):
                    haye = reader.readline()
                color = re.compile(color_rgx).search(haye)
                if color:
                    color_s = (memo, (color.group()).strip())
                    memo = ";".join(color_s)
                    haye = reader.readline()
                    logging.debug('color  %s; %s', memo, item)
                else:
                    logging.debug('no color  %s; %s', memo, item)
                prt_value(item, quantity, memo, price, record_dict, prt_list)

            discount = re.compile(disc_rgx).search(haye)
            if discount:
                disc_total += float(discount.group(2))
                haye = reader.readline()

            sale_tax = re.compile(tax_rgx).search(haye)
            if sale_tax:
                if not sale_tax.group(int(tax_grp)):
                    tax_val = 0.00
                else:
                    tax_val = float(sale_tax.group(int(tax_grp)))*itSign
                prt_value(item_supply, 1, "SALES TAX", tax_val, record_dict, prt_list)
                prt_value(item_supply, 1, "DISCOUNT", disc_total,record_dict, prt_list)
                prt_value("Materials", 1, "PAINTCARE FEE", pca_total,record_dict, prt_list)
                prt_value("Materials", 1, "SUPPLY CHAIN CHARGE", scc_total,record_dict, prt_list)

                logging.debug('BREAK - sales tax')
                break

            logging.debug('this-line: %s  last-line:  %s', haye, haye_last)
            if haye == haye_last:
                haye = reader.readline()
            haye_last = haye

        while True:
            ucode = re.search('\u000C', haye)
            logging.debug("check unicode EOP %s", ucode)
            if re.search('\u000C', haye):
                logging.debug('parse to header')
                break
            haye = reader.readline()
        logging.debug("Is new header? %s", str(haye))
        haye = reader.readline()
        if not haye:
            logging.debug("BREAK - EOF")
            break
