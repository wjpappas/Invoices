#! /usr/bin/python3

import re, csv, sys, job_filter as jf, block_head as bh
from datetime import datetime

pca_Regex = re.compile(r'(\S{3,11})\s+PAINTCARE FEE\s+[\d]+\s+\S{2,3}\s+[-]*[,\d]*[.][\d]{2}\s+([-]*[,\d]*[.][\d]{2})$')
BackEndNumRegex = re.compile(r'\s+(\d+)([-]*)\s+\S+\s+([\*]*)\s*([-]*[\d]*[.][\d]{2})\s+([-]*[\d]*[.][\d]{2})([-]*)$')  # rodda numbers
invoiceRegex = re.compile(r'.*INVOICE NUMBER\s*:\s*(\d{6,8})$')  #invoice number
cust_jobRegex = re.compile(r'PURCHASE ORDER\s+:\s(\w*.*)\s+INVOICE TERMS\s+:\s(\W*.*)') #PO number-customer
#dateRegex = re.compile(r'.*ORDER DATE\s+:\s*(\d\s+\/\d\s+\/\d{4})$') #invoice date
dateRegex = re.compile(r'.*INVOICE DATE\s+:\s*(\S+\d{4})') #invoice date
SalesNumRegex = re.compile(r'(\S{4,11})\s\s+(\S+)')     #product sales number
outputnameRegex = re.compile(r'(\S+).txt')
termsRegex = re.compile(r'TERMS:\s(\w*.*),\w*.*$')
valueDescRegex = re.compile(r'(ITEM DESCRIPTION\s+)QUANTITY')
valueTopRegex = re.compile(r'.*REMIT TO:*')
valueDiscRegex = re.compile(r'(DISCOUNT).*([-][\d]+[.][\d]{2})')
valueTaxRegex = re.compile(r'.*(TAX\s+:\s+)([\d]*[.][\d]{2})*[-]*$')
#valueTaxRegex = re.compile(r'.*(TAX\s+:\s+)([\d]*[.][\d]{2})*$')
ColorLineRegex = re.compile(r'Keyed#\s+.*$|Color#\s+.*$|Match#\s+.*$')
CheckClassRegex = re.compile(r'Eastside$|Westside$')
CustAcctRegex = re.compile(r'CUSTOMER ACCOUNT\s+:\s*(\d{6})') #Class ID

overheadRegex =  re.compile(r'22-000')
overhead_last = '21-000'
overhead_now = '22000'

fname = sys.argv[1]
fhand = open(fname)

cust_file = sys.argv[2]
cust_dict = bh.make_dict(cust_file)
#print cust_dict

opf = outputnameRegex.search(fname)
outname = opf.group(1)+'.csv'
outputFile = open(outname, 'w')
outputWriter = csv.writer(outputFile)

errFile = open('errorlog.txt', 'a')
errFile.write(opf.group(1))

classEastside = '525345'
classWestside = '618620'
vendor = 'Rodda Paint Co.'
vend_add1 = 'P.O. Box 24425'
vend_city = 'Pasadena'
vend_state = 'CA'
vend_zip = '91185-4425'
#iterms = '10th of Month'
iterms = 'NET 30'
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
            print(invoice)
        elif (CustAcctRegex.search(line)):
            m_side = CustAcctRegex.search(line).group(1)
            if(m_side == classEastside):
               side = 'Eastside'
#            if(m_side == classWestside):
            else:
               side = 'Westside'
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
#                side = 'Eastside'
#            cust_job = m.group(1)
        elif (dateRegex.search(line)):
            md = dateRegex.search(line)
            idate = md.group(1)
            print(md)
            date_due = bh.datex(idate,term_date)
        else: pass

        print(line)
        line = fhand.readline()
        if (valueDescRegex.search(line)):
            print(line)
            mz = valueDescRegex.search(line)
            mm_start = mz.start()
            print(mz.group(1),'<=>',mm_start) 
            break
        	
    print(invoice, cust_job, idate, iterms, side)
    set_print = ''
    set_prod = ''
    color_s = ''
    sep = ';'
    value_list = ['']
    line = fhand.readline()

    while True:
        phrase = line
        print(phrase) 
#        print('set_print = ',set_print,'***','set_prod = ', set_prod, '***', ' color_s = ', color_s)
        if (ColorLineRegex.search(phrase)):
            mcl = ColorLineRegex.search(phrase)
            mclx = phrase[8:45]
            color_s = (memo,mclx.strip())
            memo = sep.join(color_s)
            set_print = 'p_flag1'
        else:
            if (SalesNumRegex.match(phrase)):
                if (set_prod):
                    set_print = 'p_flag1'
            if (set_print):
                print(invoice,idate,vendor,iterms,item,memo,quantity,'{:.2f}'.format(float(price)),'{:.2f}'.format(float(amount)),cust_job,' ',side)
                outputWriter.writerow([vendor,idate,invoice,date_due,iterms,'',vendor,vend_add1,'','',vend_city,vend_state,vend_zip,'','','','','','','','',item,quantity,memo,price,side,cust_job,'Y',' '])
                set_print = ''
                set_prod = ''
            if (SalesNumRegex.match(phrase)): # and BackEndRegex.search(phrase):
                iterms = 'NET 30'
                mgn = BackEndNumRegex.search(phrase)
                print(phrase) 
                print(mgn) 
                print(mgn.group(1),'<=>',mgn.group(2),'<=>',mgn.group(3),'<=>',mgn.group(4),mgn.group(5),mgn.group(6)) 
                mg = phrase[mm_start:mm_start+30]
                memo = mg.strip()
                print("Item match is:",mg,memo,mgn) 
                if (mgn.group(6)):
                    iterms = 'Credit'
                quantity = mgn.group(1)
                price = mgn.group(4)
                if (mgn.group(3)):
                    item = 'Supplies'
                else:
                    item = 'Materials'
                if (overheadRegex.search(cust_job)):
                    item = 'Shop Supplies'
#                    m5 = overheadRegex.search(cust_job)
#                    print(m5, cust_job) 
                amount = mgn.group(5)
                set_prod = 'p_flag2'

        line = fhand.readline()

        if (pca_Regex.match(phrase)):
            if (set_prod):
                print(invoice,idate,vendor,iterms,item,memo,quantity,'{:.2f}'.format(float(price)),'{:.2f}'.format(float(amount)),cust_job,' ',side)
                outputWriter.writerow([vendor,idate,invoice,date_due,iterms,'',vendor,vend_add1,'','',vend_city,vend_state,vend_zip,'','','','','','','','',item,quantity,memo,price,side,cust_job,'Y',' '])
            set_print = 'p_flag1'
            pca_temp = pca_Regex.search(phrase)
            item = 'Materials'
            quantity = 1
            memo = 'PAINTCARE FEE'
            price = pca_temp.group(2)        	
            print('New PCA=',pca_temp, price, set_print)

        if (valueTaxRegex.search(line)):
            if (set_prod):
                print(invoice,idate,vendor,iterms,item,memo,quantity,'{:.2f}'.format(float(price)),'{:.2f}'.format(float(amount)),cust_job,' ',side)
                outputWriter.writerow([vendor,idate,invoice,date_due,iterms,'',vendor,vend_add1,'','',vend_city,vend_state,vend_zip,'','','','','','','','',item,quantity,memo,price,side,cust_job,'Y',' '])
            m3 = valueTaxRegex.search(line)
            price = 0
            print(m3.group(1), m3.group(2), price)
            quantity = '1'
            if (m3.group(2)):
                price = m3.group(2) 
                print(m3.group(1), m3.group(2), price)
            item = 'Supplies'
            amount = '0'
            memo = 'SALES TAX' 
            if (overheadRegex.search(cust_job)):
                item = 'Shop Supplies'
            print(invoice,idate,vendor,iterms,item,memo,quantity,'{:.2f}'.format(float(price)),'{:.2f}'.format(float(amount)),cust_job,' ',side)
            if(m3.group(2)):
               print(m3.group(1), m3.group(2), price)
               outputWriter.writerow([vendor,idate,invoice,date_due,iterms,'',vendor,vend_add1,'','',vend_city,vend_state,vend_zip,'','','','','','','','',item,quantity,memo,price,side,cust_job,'Y',' '])
               set_print = ''
            break

    while True:
        line = fhand.readline()
        print(line) 
        if not line: break
        if (valueTopRegex.search(line)): break

    if not line: break

errFile.write('  closed\n')
errFile.close()

fhand.close()
outputFile.close()
