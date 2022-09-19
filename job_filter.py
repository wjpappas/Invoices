#! usr/bin/python
import re
import liquidmetal


NumFirstRegex = re.compile(r"(\d\d[-]\d\d\d)")
AddDashRegex = re.compile(r"(\d\d\d\d\d)")
stripNumRegex = re.compile(r"(\D*)([\d\d\-\d\d\d])")


def find_job(value1, jobN_dict):
    value = value1.title()
    ad = AddDashRegex.search(value)
    if (ad):
        value = value[:ad.start(1) + 2] + "-" + value[ad.start(1) + 2:]
    m = NumFirstRegex.search(value)
    m2 = stripNumRegex.search(value)
    jobN_list = list(jobN_dict.keys())
    print(value1, value)
    print(m, m2, ad)

    score5 = 0.95
    rxm2 = ""

    if (m):
        #        result =  m.group(1)
        rxm = jobN_dict.get(m.group(1), 0)
        if (rxm):
            result = rxm
            print(result)
            return result
    if (m2):
        abb = m2.group(1)
        for jobN in jobN_list:
            job_value = jobN_dict.get(jobN, 0)
            score0 = liquidmetal.score(job_value, abb)
            if score0 > score5:
                score5 = score0
                rxm2 = job_value
                print(score5, abb)

    if (rxm2):
        result = rxm2
    else:
        result = value

    print(result)
    return result
