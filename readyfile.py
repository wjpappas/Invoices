#!/usr/bin/python

import os, sys, re, datetime

CatchNumRegex = re.compile(r'^([\"]*\w+[-,& \w+\.\"]*,\d{1,2}/\d{1,2}/\d{4}),(\w+[/-]*\w),.*,(Eastside|Westside),(.*),\w,')
CheckClassRegex = re.compile(r'.*(Eastside|Westside).*(:\d\d-\d\d\d|21-000|22-000)')
CheckHeaderRegex = re.compile(r'Vendor,Transaction Date,Ref')

input_name = sys.argv[1]
vend_name = sys.argv[2]
header = 'Vendor,Transaction Date,RefNumber,Bill Due,Terms,Memo,Address Line1,Address Line2,Address Line3,Address Line4,Address City,Address State,Address PostalCode,Address Country,Vendor Acct No,Expenses Account,Expenses Amount,Expenses Memo,Expenses Class,Expenses Customer,Expenses Billable,Items Item,Items Qty,Items Description,Items Cost,Items Class,Items Customer,Items Billable,AP Account\n'

dt = datetime.datetime.now()

# outname1 = vend_name + dt.strftime('%m%d') + '_rdy.csv'
outname2 = vend_name + dt.strftime('%m%d') + '_ck.csv'
outname3 = dt.strftime('%m%d') + '_cklog.txt'
#outname3 = vend_name + dt.strftime('%m%d') + '_log.txt'
outname4 = 'allrdy_' + dt.strftime('%m%d') + '.csv'

#outputFile1 = open(outname1,'w')
outputFile2 = open(outname2,'w')

outputFile3 = open(outname3,'a')
#vend_header = '\n' + vend_name + 'Invoices missing Job#\n'
#outputFile3.write(vend_header)
outputFile3.write('\n' + vend_name + 'Invoices missing Job#\n')

outputFile4 = open(outname4,'a')
outputFile4.close()

readFile4 = open(outname4)
line4 = readFile4.readline()
readFile4.close()

if not(CheckHeaderRegex.search(line4)):
    outputFile4 = open(outname4,'w')
    outputFile4.write(header)
    outputFile4.close()

outputFile4 = open(outname4,'a')

pflag = 1

dirlocal = os.getcwd()
dirlist =  os.listdir(dirlocal)
for x in dirlist:
    if(x.startswith(input_name) and x.endswith('.csv')):
        print(x,'01')
        tfile = open(x)
        line = tfile.readline()
        print("top setup", line)
        if (CheckHeaderRegex.search(line)):
            if (pflag):
                outputFile2.write(line)
                pflag = 0
            print('found header',pflag)
            line =   tfile.readline()
            see_tree = CatchNumRegex.search(line)
            invoiceNum = ''
            while True:

                print("lower  loop", line)
                if (CheckClassRegex.search(line)):
                    see_me = CheckClassRegex.search(line).group(2)
                    see_too = line.find(see_me)
                    print(see_me, see_too,invoiceNum)
                    outputFile4.write(line)
                    invoiceNum = ''
                else:
                    outputFile2.write(line)
                    if not (invoiceNum):
                        invoiceNum = see_tree.group(2)
                        jobNum = see_tree.group(4)
                        outputFile3.write(x + '  ' + invoiceNum + '  ' +jobNum + '\n')
                    print(x,invoiceNum,'02')
                    print(line)
                line =   tfile.readline()
                if not line:
                    break
                see_tree = CatchNumRegex.search(line)
                if not (invoiceNum == see_tree.group(2)):
                    invoiceNum = ''
            tfile.close()

#outputFile1.close()
outputFile2.close()
outputFile3.close()
outputFile4.close()
