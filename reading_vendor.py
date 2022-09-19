import re
import csv
import sys
import job_filter as jf
import block_head as bh

ifile_vendor = sys.argv[1]
ifile_name = sys.argv[2]
cust_file = sys.argv[3]

outputname_x = r'(\S+).txt'
outname = ((re.compile(outputname_x)).search(ifile_name)).group(1)+'.csv'
outputFile = open(outname, 'w')
outputWriter = csv.writer(outputFile)

#qb_record = [vendor,idate,invoice,date_due,iterms,'',vendor,vend_add1,'','',vend_city,vend_state,vend_zip,'','','','','','','','',item,quantity,memo,price,side,cust_job,'Y',' ']

qb_record = ['','','','','','','','','','','','','','','','','','','','','','','','','','','','Y',' ']

qb_header = ['Vendor','Transaction Date','RefNumber','Bill Due','Terms','Memo','Address Line1','Address Line2',
'Address Line3','Address Line4','Address City','Address State','Address PostalCode','Address Country','Vendor Acct No',
'Expenses Account','Expenses Amount','Expenses Memo','Expenses Class','Expenses Customer','Expenses Billable','Items Item',
'Items Qty','Items Description','Items Cost','Items Class','Items Customer','Items Billable','AP Account']

record_keys = ['name', 'trans_date', 'ref_num', 'bill_due', 'terms', 'memo', 'add_line1', 'add_line2', 'add_line3', 'add_line4', 'add_city', 'add_state', 'postal_code', 'country', 'acct_no', 'exp_acct', 'exp_amt', 'exp_memo', 'exp_class', 'exp_cust', 'exp_bill', 'i_items', 'i_qty', 'i_desc', 'i_cost', 'i-class', 'i_cust', 'i_bill', 'ap_acct']

vendor_keys = ['name', 'terms', 'memo', 'add_line1', 'add_city', 'add_state', 'postal_code']

update_keys = ['i_items', 'i_qty', 'i_desc', 'i_cost']

headr_keys = ['trans_date', 'ref_num', 'bill_due', 'i-class', 'i_cust']

term_key = ['terms']

desc_block_x = r'(DESCRIPTION\s+)'
rec_block_x = r'THE SHERWIN WILLIAMS CO\.'
date_x = r'DATE:\s(\w*.*)$'
terms_x = r'TERMS:\s(\w*.*),\w*.*$'
invoice_x = r'No\. ([\d]{4}[-][\d])$'
cust_job_x = r'PO#\s(\w*.*)$'
credit_x = r'.*(CREDIT|CORRECT|CHARGE)\s*$'
side_x = r'^\s*(\D+[ \D*])( WA \d{5} \d*[^WA 98108 \d*])'
sales_num_x = r'(^\s{2,6}(\d{3,4}[-]\d{4,5})\s+).*'   #product sales number
back_end_x =  r'(\s+)(\d+)(\s+)([-]*[\d]+[.][\d]{2})([\ *]*\s+)([-]*[\d]+[.][\d]{2})([N]*)$'
color_x = r'Color:.*$|Custom:.*$|\s{20}\d{4}-\d{5}\s\S\S+.*$'
discount_x = r'(DISCOUNT).*([-][\d]+[.][\d]{2})$'
tax_x = r'.*(SALES TAX:)\S+\s+([-]*[\d]+[.][\d]{2})$'
pca_x = r'(\s*\d+\s+)(PAINT RECYCLING FEE)(\s+\d+\s+[-]*[\d]+[.][\d]{2}[\ *]*\s+)([-]*[\d]+[.][\d]{2})([N]*)'
cash_x = r'(INVOICE)'
eat_color = r'^\s+ T PAINT.*'
scc_x =  r'(\s*\d+\s+)(SUPPLY CHAIN CHRG)(\s+\d+\s+[-]*[\d]+[.][\d]{2}[\ *]*\s+)([-]*[\d]+[.][\d]{2})([N]*)'
overhead_x = r'22-000'

def read_vendor(file):
    list_dt, list_re, list_gp = [], [], []
    with open(file)as read_v:
        for line in range(8):
            line = read_v.readline()
            list_dt.append(line.strip())
        for line in range(14):
            line = read_v.readline()
            list_re.append(line.strip())
        for line in range(3):
            line = read_v.readline()
            list_gp.append(line.strip())
        return (list_dt, list_re, list_gp)

def find_header_x(listx, subject, f_head):
    coll = []
    head_x = []
    for list in listx:
        regex = re.compile(list)
        for sub in subject:
            if regex.search(sub):
                coll.append((regex.search(sub)).group(1))
    for num, fun in zip(coll, f_head):
        head_x.append(fun(num))
    return head_x

def f_eq_val(x):
    return x

def f_due_date(x):
    x = bh.datex(x, 10)
    return x

def f_credit(x):
    clist = ['CHARGE', 1]
    if x in clist:
        return 1
    else:
        return -1

def f_side(x):
    print(x)
    class_east = '525345'
    #class_west = '618620'
    side_list = [class_east, "PASCO", "UNION GAP", "ELLENSBURG", "WENATCHEE", "MOSES LAKE", "YAKIMA", "SPOKANE", "SPOKANE VALLEY", "KENNEWICK", "RICHLAND", "WALLA WALLA", "PULLMAN"]
    if x in side_list:
        return "Eastside"
    else:
        return "Westside"

def f_cust_job(m7):
    cust_dict = bh.make_dict(cust_file)
    overhead_last = '21-000'
    overhead_now = '22-000'
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
    return cust_job

def item_ck(item_val, par_01, par_02):
    if item_val:
        item_supply = par_01
    else:
        item_supply = par_02
    return item_supply

def credit_ck(ck, term_key, iterms, cterms):
    if ck != 1:
        update_dict(record_dict, term_key, cterms)
        return -1
    else:
        update_dict(record_dict, term_key, iterms)
        return 1

def set_dict(rec_keys, rec_val):
    return dict(zip(rec_keys, rec_val))

def update_dict(rec_dict, rec_keys, rec_val):
    up_dict = set_dict(rec_keys, rec_val)
    return rec_dict.update(up_dict)

def print_record(file, record_dict, record_keys):
    out_list = [record_dict[key] for key in record_dict]
    file.writerow(out_list)
    return #print("hello, print record")

listx = [date_x, invoice_x, date_x, side_x, cust_job_x, credit_x]
f_head = [f_eq_val, f_eq_val, f_due_date, f_side, f_cust_job, f_credit]

header_dict = set_dict(record_keys, qb_header)
print_record(outputWriter, header_dict, record_keys)

vendor_val = read_vendor(ifile_vendor)
record_dict = set_dict(record_keys, qb_record)
update_dict(record_dict, vendor_keys, vendor_val[0])
i_terms = vendor_val[1]
#print(i_terms, vendor_val)

with open(ifile_name, 'r') as reader:

    haye = ''
    straye = []
    desc_b = re.compile(desc_block_x)

    while True:
        straye.clear()
        db = None
        while not db:
            haye = reader.readline()
            db = desc_b.search(haye)
            straye.append(haye)
        head_x = find_header_x(listx, straye, f_head)
        print(head_x)

        update_dict(record_dict, headr_keys, head_x)
        #print_record(outputWriter, record_dict, record_keys)

        memo_len = 30
        rec_pos = db.start()
        cust_job = head_x[3]
        item_val = re.compile(overhead_x).search(cust_job)
        item_supply = item_ck(item_val, 'Shop Supplies', 'Supplies')
        itSign = credit_ck(head_x[-1], term_key, [i_terms], ['Credit'])
        disc_total = 0
        pca_total = 0
        scc_total = 0
        haye_last = haye

        while True:
            if re.compile(pca_x).search(haye):
                pca_temp = re.compile(pca_x).search(haye)
                pca_total += float(pca_temp.group(4))
                haye = reader.readline()

            if re.compile(scc_x).search(haye):
                scc_temp = re.compile(scc_x).search(haye)
                scc_total += float(scc_temp.group(4))
                haye = reader.readline()

            if re.compile(sales_num_x).search(haye):
                back_end = re.compile(back_end_x).search(haye)
                item = item_ck(back_end.group(7), 'Materials', item_supply)
                quantity = back_end.group(2)
                memo = (haye[rec_pos:rec_pos+memo_len]).strip()
                price = float(back_end.group(4))*itSign
                haye = reader.readline()
                color = re.compile(color_x).search(haye)
                if color:
                    color_s = (memo, color.group())
                    memo = ";".join(color_s)
                    haye = reader.readline()
                    print("color", memo)
                else:
                    print("no color", memo)
                uplist = [item, quantity, memo, price]
                update_dict(record_dict, update_keys, uplist)
                print_record(outputWriter, record_dict, record_keys)

            if re.compile(discount_x).search(haye):
                discount = re.compile(discount_x).search(haye)
                disc_total += float(discount.group(2))
                haye = reader.readline()

            if re.compile(tax_x).search(haye):
                sale_tax = re.compile(tax_x).search(haye)
                tax_val = float(sale_tax.group(2))
                if tax_val != 0.00:
                    uplist = [item_supply, 1, sale_tax.group(1), '{:.2f}'.format(tax_val)]
                    update_dict(record_dict, update_keys, uplist)
                    print_record(outputWriter, record_dict, record_keys)

                if disc_total != 0:
                    uplist = ['Supplies', 1, discount.group(1), '{:.2f}'.format(disc_total)]
                    update_dict(record_dict, update_keys, uplist)
                    print_record(outputWriter, record_dict, record_keys)

                if pca_total != 0:
                    uplist = ['Materials', 1, 'PAINTCARE FEE', '{:.2f}'.format(pca_total)]
                    update_dict(record_dict, update_keys, uplist)
                    print_record(outputWriter, record_dict, record_keys)

                if scc_total != 0:
                    uplist = ['Materials', 1, 'SUPPLY CHAIN CHARGE', '{:.2f}'.format(scc_total)]
                    update_dict(record_dict, update_keys, uplist)
                    print_record(outputWriter, record_dict, record_keys)

                print("BREAK")
                break

            if haye == haye_last:
                haye = reader.readline()
            haye_last = haye

        rb = None
        rec_b = re.compile(rec_block_x)
        while True:
            haye = reader.readline()
            if not haye:
                break
            rb = rec_b.search(haye)
            if rb:
                print('parse to header')
                break
        print(haye)
        if not haye:
            break
