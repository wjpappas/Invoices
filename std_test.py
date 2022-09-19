#! /usr/bin/python3

import re, csv, sys, job_filter as jf, block_head as bh
from datetime import datetime

pca_Regex = re.compile(r'(\s*PAINT[ ]*CARE\s.*)\s+([\d]*[.][\d]{2})')
BackEndNumRegex = re.compile(r'([\d]+)\s+\S{2,3}\s+([-]*[,\d]*[.][\d]{2})\s+\S{2,4}\s+([-]*[,\d]*[.][\d]{2})*\s*([*RONS]*)$')  # rodda numbers
invoiceRegex = re.compile(r'^.*Invoice No\s*(\d{2,6})')  #invoice number
cust_jobRegex = re.compile(r'^.*Your Ref\s*(\w*.*)\s*$') #PO number-customer
dateRegex = re.compile(r'^.*Invoice Date\s*(\d{1,2}/\d{1,2}/\d{4})$') #invoice date
SalesNumRegex = re.compile(r'^\s+([\d]{1,2})\s+\s+[\w-]{2,17} - (.{40})')     #product sales number
outputnameRegex = re.compile(r'(\S+).txt')
termsRegex = re.compile(r'TERMS:\s(\w*.*),\w*.*$')
valueDescRegex = re.compile(r'^\s*(Line\s*Description)\w*')
valueTopRegex = re.compile(r'.*Sales Invoice.*')
valueDiscRegex = re.compile(r'(DISCOUNT).*([-][\d]+[.][\d]{2})')
valueTaxRegex = re.compile(r'^.*(Sales Tax\s*([\d]{1,2}.[\d]{1,2}[%])*\s+[$])([\d]*[.][\d]{2})')
ColorLineRegex = re.compile(r'RP-.*$|  TINT\s+.*$|\d{4}-\d{2}\s+.*$|[\w]+.*$')
CheckClassRegex = re.compile(r'Eastside$|Westside$')

overheadRegex =  re.compile(r'22-000')
overhead_last = '21-000'
overhead_now = '22000'

fname = sys.argv[1]
fhand = open(fname)

cust_file = sys.argv[2]
cust_dict = bh.make_dict(cust_file)

f_prod = open('prod_file.txt', 'r')
prod_list = [pline for pline in f_prod.read().splitlines()]
f_prod.close()

opf = outputnameRegex.search(fname)
outname = opf.group(1)+'.csv'
outputFile = open(outname, 'w')
outputWriter = csv.writer(outputFile)

errFile = open('errorlog.txt', 'a')
errFile.write(opf.group(1))

vendor = 'Standard Paint & Flooring, LLC'
vend_add1 = '130 S 72nd Ave'
vend_city = 'Yakima'
vend_state = 'WA'
vend_zip = '98908'
iterms = 'NET 10TH'
term_date = 10

outputWriter.writerow(['Vendor','Transaction Date','RefNumber','Bill Due','Terms','Memo','Address Line1','Address Line2',
'Address Line3','Address Line4','Address City','Address State','Address PostalCode','Address Country','Vendor Acct No',
'Expenses Account','Expenses Amount','Expenses Memo','Expenses Class','Expenses Customer','Expenses Billable','Items Item',
'Items Qty','Items Description','Items Cost','Items Class','Items Customer','Items Billable','AP Account'])

line = fhand.readline()
while True:
#    line = fhand.readline()
    while True:
        if (invoiceRegex.search(line)):
            m6 = invoiceRegex.search(line)
            invoice = m6.group(1)
        elif (cust_jobRegex.search(line)):

            m7 = cust_jobRegex.search(line).group(1)
            low_job = m7.lower()
            if (low_job.find('shop',0,len(low_job)) >= 0):
                m7 = overhead_now
            if (low_job.find(overhead_last,0,len(low_job)) >= 0):
                m7 = overhead_now

            cj = jf.find_job(m7,cust_dict)
            if (CheckClassRegex.search(cj)):
                cust_job = cj[:len(cj)-8]
                side = cj[-8:]
            else:
                cust_job = cj
                side = 'Eastside'
        elif (dateRegex.search(line)):
            md = dateRegex.search(line)
            idate = md.group(1)
            date_due = bh.datex(idate,term_date)
        else: pass

        line = fhand.readline()
        if (valueDescRegex.search(line)):
            mz = valueDescRegex.search(line)
            mm_start = mz.start()
            break

    pca_total = 0
    set_print = ''
    set_prod = ''
    set_item = ''
    color_s = ''
    sep = ';'
    value_list = ['']
    line = fhand.readline()

    while True:
        phrase = line
        if (set_item):
            mcl = phrase
            mclx = phrase
            mclx = phrase[10:65]
            color_s = (memo,mclx.strip())
#            color_s = (memo,mcl)
            memo = sep.join(color_s)
            set_print = 'p_flag1'
            set_item = ''
        else:
            if (SalesNumRegex.match(phrase)):
                if (set_prod):
                    set_print = 'p_flag1'
            if (set_print):
                outputWriter.writerow([vendor,idate,invoice,date_due,iterms,'',vendor,vend_add1,'','',vend_city,vend_state,vend_zip,'','','','','','','','',item,quantity,memo,price,side,cust_job,'Y',' '])
                set_print = ''
                set_prod = ''
            if (pca_Regex.match(phrase)):
                pca_temp = pca_Regex.search(phrase)
                pca_total = pca_total + float(pca_temp.group(2))
            if (SalesNumRegex.match(phrase)): # and BackEndRegex.search(phrase):
                msn = SalesNumRegex.search(phrase)
                mgn = BackEndNumRegex.search(phrase)
                mg = msn.group(2)
                memo = mg.strip()
                set_item = 'is_item'
                quantity = mgn.group(1)
                price = mgn.group(2)
                item = 'Supplies'
                if (overheadRegex.search(cust_job)):
                    item = 'Shop Supplies'
                prod_tup = (prod_list)
                for p_str in prod_tup:
                    low_memo = memo.lower()
                    bob = low_memo.find(p_str)
                    if (low_memo.find(p_str) > -1):
                        item = 'Materials'
                        break
                amount = mgn.group(2)
                set_prod = 'p_flag2'

        line = fhand.readline()

        if (valueTaxRegex.search(line)):
            if (set_prod):
                outputWriter.writerow([vendor,idate,invoice,date_due,iterms,'',vendor,vend_add1,'','',vend_city,vend_state,vend_zip,'','','','','','','','',item,quantity,memo,price,side,cust_job,'Y',' '])
            m3 = valueTaxRegex.search(line)
            price = 0
            quantity = '1'
            if (m3.group(3)):
                price = m3.group(3)
            item = 'Supplies'
            amount = '0'
            memo = 'SALES TAX'
            if (overheadRegex.search(cust_job)):
                item = 'Shop Supplies'
            if (price != '0.00'):
                outputWriter.writerow([vendor,idate,invoice,date_due,iterms,'',vendor,vend_add1,'','',vend_city,vend_state,vend_zip,'','','','','','','','',item,quantity,memo,price,side,cust_job,'Y',' '])
                set_print = ''
            if (pca_total != 0):
                item = 'Materials'
                quantity = 1
                memo = 'PAINTCARE FEE'
                price = '{:.2f}'.format(pca_total)
                outputWriter.writerow([vendor,idate,invoice,date_due,iterms,'',vendor,vend_add1,'','',vend_city,vend_state,vend_zip,'','','','','','','','',item,quantity,memo,price,side,cust_job,'Y',' '])
            break

    while True:
        line = fhand.readline()
        if not line:
            break
        if (valueTopRegex.search(line)):
            break

    if not line:
        break

errFile.write('   closed\n')
errFile.close()

fhand.close()
outputFile.close()
