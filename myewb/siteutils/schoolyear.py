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
    
def prevterm(current, year):
    if current == "Winter":
        return "Fall", int(year)-1
    elif current == "Fall":
        return "Summer", year
    elif current == "Summer":
        return "Winter", year
    
def nextterm(current, year):
    if current == "Winter":
        return "Summer", year
    elif current == "Fall":
        return "Winter", int(year)+1
    elif current == "Summer":
        return "Fall", year
