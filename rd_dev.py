#   Read configuration file
#   #   Vendor address info
#   #   Regex patterns unique to vendor data
#   #   index's unique to vendor output
#   Header parsing
#   #   Read and map header values into output
#
#
#
#
#
import logging
import re
import csv
import sys
from configparser import ConfigParser
import job_filter as jf
import block_head as bh

ifile_vendor = sys.argv[1]
ifile_name = sys.argv[2]
cust_file = sys.argv[3]

logging.basicConfig(filename='invoices.log', level=logging.DEBUG, format='%(lineno)d - %(funcName)s - %(levelname)s - %(message)s')
outputname_x = r'(\S+).txt'
outname = ((re.compile(outputname_x)).search(ifile_name)).group(1)+'.csv'
outputFile = open(outname, 'w')
outputWriter = csv.writer(outputFile)

#   Output list templates
qb_record = ['','','','','','','','','','','','','','','','','','','','','','','','','','','','Y',' ']
qb_header = ['Vendor','Transaction Date','RefNumber','Bill Due','Terms','Memo','Address Line1','Address Line2',
'Address Line3','Address Line4','Address City','Address State','Address PostalCode','Address Country','Vendor Acct No',
'Expenses Account','Expenses Amount','Expenses Memo','Expenses Class','Expenses Customer','Expenses Billable','Items Item',
'Items Qty','Items Description','Items Cost','Items Class','Items Customer','Items Billable','AP Account']

#   Keys mapping update and output lists
record_keys = ['name', 'trans_date', 'ref_num', 'bill_due', 'terms', 'memo', 'add_line1', 'add_line2', 'add_line3', 'add_line4', 'add_city', 'add_state', 'postal_code', 'country', 'acct_no', 'exp_acct', 'exp_amt', 'exp_memo', 'exp_class', 'exp_cust', 'exp_bill', 'i_items', 'i_qty', 'i_desc', 'i_cost', 'i-class', 'i_cust', 'i_bill', 'ap_acct']
vendor_keys = ['name', 'terms', 'memo', 'add_line1', 'add_city', 'add_state', 'postal_code']
update_keys = ['i_items', 'i_qty', 'i_desc', 'i_cost']
headr_keys = ['trans_date', 'ref_num', 'bill_due', 'i-class', 'i_cust']
term_key = ['terms']

cash_x = r'(INVOICE)'
eat_color = r'^\s+ T PAINT.*'
scc_x =  r'(\s*\d+\s+)(SUPPLY CHAIN CHRG)(\s+\d+\s+[-]*[\d]+[.][\d]{2}[\ *]*\s+)([-]*[\d]+[.][\d]{2})([N]*)'

def _get_overhead():
    """Fetch the overhead job code from your configuration file.

    Expects a configuration file named "invoices.ini" with structure:

        [overhead_code]
        OH_thisyear=23-000
        OH_lastyear=22-000
    """
    config = ConfigParser()
    config.read("Invfile/invoices.ini")
    thisyear = config["overhead_code"]["OH_thisyear"]
    lastyear = config["overhead_code"]["OH_lastyear"]
    std_file = config["file_spec"]["product"]
    return [thisyear, lastyear, std_file]

def read_vendor(file):
    """Read vendor file into working lists."""
    vend_list = [[], [], []]
    with open(file)as read_v:
        r_val = [int(x.rstrip()) for x in read_v.readline().split(',')]
        for val, bb in zip(r_val, vend_list):
            for line in range(val):
                bb.append(read_v.readline().rstrip())
    return vend_list

def find_header_x(listx, subject, f_head):
    """Filter vendor info from header block."""
    coll, head_x = [], []
    for list in listx:
        regex = re.compile(list)
        for sub in subject:
            if regex.search(sub):
                coll.append((regex.search(sub)).group(1))
    for num, fun in zip(coll, f_head):
        head_x.append(fun(num))
    return head_x

def f_eq_val(x):
    """Filter function."""
    return x

def f_due_date(x):
    """Filter function."""
    x = bh.datex(x, 10)
    return x

def f_credit(x):
    """Filter function."""
    clist = ['CHARGE', 'Pasadena', 'Smith']
    if x in clist:
        return 1
    else:
        return -1

def f_side(x):
    """Filter function."""
    class_east = '525345'
    #class_west = '618620'
    side_list = [class_east, "PASCO", "UNION GAP", "ELLENSBURG", "WENATCHEE", "MOSES LAKE", "YAKIMA", "SPOKANE", "SPOKANE VALLEY", "KENNEWICK", "RICHLAND", "WALLA WALLA", "PULLMAN", "Company"]
    if x in side_list:
        return "Eastside"
    else:
        return "Westside"

def f_cust_job(m7):
    """Filter function."""
#    logging.debug("overhead inside cust job (last, now)%s %s", overhead_last, overhead_now)
    check_class = r'Eastside$|Westside$'

    low_job = m7.lower()
    if (low_job.find('shop', 0, len(low_job)) >= 0):
        m7 = overhead_now
    if (low_job.find(overhead_last, 0, len(low_job)) >= 0):
        m7 = overhead_now
    cj = jf.find_job(m7, cust_dict)
    regex = re.compile(check_class)
    if regex.search(cj):
        cust_job = cj[:len(cj)-8]
    else:
        cust_job = cj
    return cust_job.strip()

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

def item_ck(item_val, par_01, par_02):
    """Item checking."""
    if item_val:
        item_supply = par_01
    else:
        item_supply = par_02
        logging.debug('value: %s item supply: %s   %s;  %s', item_val, item_supply,par_01,par_02)
    return item_supply

def credit_ck(ck, term_key, iterms, cterms):
    """Is credit? for Sherwin."""
    if ck != 1:
        update_dict(record_dict, term_key, cterms)
        return -1
    else:
        update_dict(record_dict, term_key, iterms)
        return 1

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

oh_codes = _get_overhead()
overhead_now, overhead_last, std_file = oh_codes
overhead_x = r'%s'%overhead_now
logging.debug('OH codes: %s overhead_x: %s', oh_codes, overhead_x)
cust_dict = bh.make_dict(cust_file, overhead_now)
header_dict = set_dict(record_keys, qb_header)
print_record(outputWriter, header_dict, record_keys)
prt_list = [update_keys, outputWriter, record_keys]

vendor_val, reg_val, grp_val = read_vendor(ifile_vendor)
salenum_rgx, backend_rgx, color_rgx, disc_rgx, tax_rgx, pca_rgx = reg_val[8:]
#print(reg_val[8:13])
pca_grp, item_grp, qty_grp, tax_grp, price_grp = grp_val
#print(grp_val)
record_dict = set_dict(record_keys, qb_record)
update_dict(record_dict, vendor_keys, vendor_val)
i_terms = vendor_val[1]

std_list = read_std_file(grp_val[1], std_file)
listx = [reg_val[2], reg_val[4], reg_val[2], reg_val[7], reg_val[5], reg_val[6]]
f_head = [f_eq_val, f_eq_val, f_due_date, f_side, f_cust_job, f_credit]

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
            straye.append(haye)
        head_x = find_header_x(listx, straye, f_head)   # invoice header
        cust_job = head_x[4]
        itSign = credit_ck(head_x[-1], term_key, [i_terms], ['Credit'])
        logging.debug('headx =' + str(head_x))

        update_dict(record_dict, headr_keys, head_x)

        memo_len = 40
        rec_pos = db.start(1)
        item_val = re.compile(overhead_x).search(cust_job)
        item_supply = item_ck(item_val, 'Shop Supplies', 'Supplies')
        logging.debug('DB position: %s; DB: %s', rec_pos, db)
        disc_total = 0
        pca_total = 0
        scc_total = 0
        haye = reader.readline()
        haye_last = haye

        while True:
            pca_temp = re.compile(pca_rgx).search(haye)
            if pca_temp:
                pca_total += float(pca_temp.group(int(pca_grp)))
                haye = reader.readline()

            scc_temp = re.compile(scc_x).search(haye)
            if scc_temp:
                scc_total += float(scc_temp.group(4))
                haye = reader.readline()

            if re.compile(salenum_rgx).search(haye):             # sales number
                memo = (haye[rec_pos:rec_pos+memo_len]).strip()
                back_end = re.compile(backend_rgx).search(haye)  # backend
                logging.debug('item value: %s, nine? %s', item_val, item_grp)
                if item_grp == '4':
                    item_val = std_item(memo, std_list)
                    par01, par02 = 'Materials', item_supply
                else:
                    if item_grp == '3':
                        par01, par02 = item_supply, 'Materials'
                    if item_grp == '7':
                        par01, par02 = 'Materials', item_supply
                    item_val = back_end.group(int(item_grp))
                item = item_ck(item_val, par01, par02)
                logging.debug('item value: %s, item-supply: %s', item_val, item_supply)
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
                    tax_val = float(sale_tax.group(int(tax_grp)))
                prt_value(item_supply, 1, "SALES TAX", tax_val, record_dict, prt_list)
                prt_value("Supplies", 1, "DISCOUNT", disc_total,record_dict, prt_list)
                prt_value("Materials", 1, "PAINTCARE FEE", pca_total,record_dict, prt_list)
                prt_value("Materials", 1, "SUPPLY CHAIN CHARGE", scc_total,record_dict, prt_list)

                logging.debug('BREAK - sales tax')
                break

            logging.debug('this-line: %s  last-line:  %s', haye, haye_last)
            if haye == haye_last:
                haye = reader.readline()
            haye_last = haye

        while True:
            haye = reader.readline()
            ucode = re.search('\u000C', haye)
            logging.debug("check unicode EOP %s", ucode)
            if re.search('\u000C', haye):
                logging.debug('parse to header')
                break
        logging.debug("Is new header? %s", str(haye))
        haye = reader.readline()
        if not haye:
            logging.debug("BREAK - EOF")
            break
