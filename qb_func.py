import re
from job_filter import find_job

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
