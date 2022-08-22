import re

def arial():
    font = "Arial"
    
    return {
        "config" : {
             "title": {'font': font},
             "axis": {
                  "labelFont": font,
                  "titleFont": font
             }
        }
    }

def format_number(n):
    if n>9999:
        return re.sub(r"(\d)(?=(\d{3})+(?!\d))", r"\1,", str(n))
    else:
        return str(n)