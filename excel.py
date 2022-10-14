import time

import openpyxl


def create(rows: list, s=None, e=None):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'sheet'
    for row in rows:
        sheet.append(row)
    if s is not None and e is not None:
        workbook.save("Period {}-{}.xlsx".format(s, e))
    else:
        workbook.save("Summary {}.xlsx".format(time.strftime("%Y-%m-%d"), time.time()))
