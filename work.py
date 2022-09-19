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

def set_dict(rec_keys, rec_val):
    return dict(zip(rec_keys, rec_val))

file = 'sherwin.txt'
xside_list = ["PASCO", "UNION GAP", "ELLENSBURG", "WENATCHEE", "MOSES LAKE", "YAKIMA", "SPOKANE VALLEY", "SPOKANE", "KENNEWICK", "RICHLAND", "WALLA WALLA", "PULLMAN"]
side_list = ["pasco", "union gap", "ellensburg", "wenatchee", "moses lake", "spokane valley", "spokane", "kennewick", "richland", "walla walla", "pullman"]

def item_val(memo, s_list):
    value = True
    for p_str in s_list:
        if ((memo.lower()).find(p_str) != -1):
            value = False
            break
    return value


print(item_val("LAKSJLKAS SPOKANE VALLEY LASKJDLAS", side_list))
print(item_val("LAKSJLKAS SPOKANE VALLEY LASKJDLAS", side_list))
print(item_val("LAKSJLKAS ASKJDLAS", side_list))
print(item_val("LAKSJLKAS SPOKANE VA LASKJDL000AS", side_list))
print(item_val("LAKSJL ELLENSBURG KAS  LASKJDLAS", side_list))

