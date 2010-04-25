from datetime import date, datetime

def school_year(today=None):
    if today == None:
        today = date.today()

    year = today.year
    if today.month < 5:
        year = year - 1
        
    return year

def school_year_name(today=None):
    year = school_year(today)
    return "%d-%d" % (year, year+1)

def term(today=None):
    if today == None:
        today = date.today()
        
    if today.month < 5:
        return "Winter"
    elif today.month < 9:
        return "Summer"
    else:
        return "Fall"