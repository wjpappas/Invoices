import re
import logging
from job_filter import find_job
from block_head import datex

def f_side(x):
    """Filter function."""
    class_east = '525345'
    #class_west = '618620'
    side_list = [class_east, "PASCO", "UNION GAP", "ELLENSBURG", "WENATCHEE", "MOSES LAKE", "YAKIMA", "SPOKANE", "SPOKANE VALLEY", "KENNEWICK", "RICHLAND", "WALLA WALLA", "PULLMAN", "HERMISTON", "WEST RICHLAND", "E KENNEWICK", "N SPOKANE", "E SPOKANE", "LIBERTY LAKE", "COLLEGE PLACE", "OMAK", "Company"]
    if x in side_list:
        return "Eastside"
    else:
        return "Westside"

def f_cust_job(m7, overhead_now, overhead_last, cust_dict):
    """Filter function."""
#    logging.debug("overhead inside cust job (last, now)%s %s", overhead_last, overhead_now)
    check_class = r'Eastside$|Westside$'

    low_job = m7.lower()
    if (low_job.find('shop', 0, len(low_job)) >= 0):
        m7 = overhead_now
    if (low_job.find(overhead_last, 0, len(low_job)) >= 0):
        m7 = overhead_now

    cj = find_job(m7, cust_dict)
    regex = re.compile(check_class)
    if regex.search(cj):
        cust_job = cj[:len(cj)-8]
    else:
        cust_job = cj
    return cust_job.strip()

def item_ck(item_val, par_01, par_02):
    """Item checking."""
    if item_val:
        item_supply = par_01
    else:
        item_supply = par_02
#        logging.debug('value: %s item supply: %s   %s;  %s', item_val, item_supply, par_01, par_02)
    return item_supply
'''
def find_header_x(listx, subject, f_head):
    """Filter vendor info from header block."""
    coll, head_x = [], []
    for list in listx:
        regex = re.compile(list)
        for sub in subject:
            if regex.search(sub):
                coll.append((regex.search(sub)).group(1))
                logging.debug('list value: %s match: %s ', list, (regex.search(sub)).group(1))
    for num, fun in zip(coll, f_head):
        head_x.append(fun(num))
    return head_x
'''
def find_header_x(listx, subject, f_head):
    """Filter vendor info from header block."""
    coll, head_x = [], []
    for list in listx:
        regex = re.compile(list)
        collx = [((regex.search(sub)).group(1)) for sub in subject if regex.search(sub)]
        if collx:
            coll.append(collx[0])
        else:
            coll.append("Company")
        logging.debug('list value: %s match: %s ', list, collx)
    head_x = [fun(num) for num, fun in zip(coll, f_head)]
    return head_x

def f_eq_val(x):
    """Filter function."""
    return x

def f_due_date(x):
    """Filter function."""
    x = datex(x, 10)
    return x

def f_credit(x):
    """Filter function."""
    clist = ['INVOICE', 'Pasadena', 'Fax: 509-453']
    if x in clist:
        return 1
    else:
        return -1
