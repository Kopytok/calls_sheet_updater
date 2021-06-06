# -*- coding: UTF-8 -*-

import pandas as pd
import numpy as np

from gspread_pandas import Spread, conf
import gspread, os

CONFIG = conf.get_config(conf_dir=os.getcwd())

from .constants import *
from .preprocessor import Preprocessor


class CallsSheetUpdater (object):

    def __init__(self, spreadsheet_id, platform):
        self.platform = platform
        self.spreadsheet_id = spreadsheet_id

        self.datereg = {
            "betman": DATEREGBM,
            "natasha": DATEREGNT,
        }[platform]

        self.downloader = Spread(spreadsheet_id, config=CONFIG)
        self.uploader = open_spreadsheet(spreadsheet_id)

    def update(self, file_object):
        upd = read_new_data(file_object, self.platform)
        upd[self.datereg] = clean_date(upd[self.datereg])

        groupby = [
            upd[self.datereg].dt.month,
            upd[self.datereg].dt.year,
        ]
        for (month, year), new_data in upd.groupby(groupby):
            self.update_sheet(month, year, new_data)

    def update_sheet(self, month, year, new_data):
        sheet_name = make_sheet_name(month, year)
        old_data = clean_sheet(self.fetch_sheet(sheet_name))
        self.append_rows(
            data=Preprocessor(self.platform).run(new_data, old_data),
            sheet_name=sheet_name,
            start_cell=insert_start_cell(old_data))

    def fetch_sheet(self, sheet_name):
        return self.downloader.sheet_to_df(sheet=sheet_name, start_row=1, index=0)

    def append_rows(self, data, sheet_name, start_cell):
        worksheet = self.uploader.worksheet(sheet_name)
        worksheet.append_rows(
            values=data.values.tolist(),
            table_range=start_cell)


def open_spreadsheet(spreadsheet):
    gc = gspread.service_account(filename="./google_secret.json")
    return gc.open_by_key(spreadsheet)

def read_new_data(file_object, platform):
    if platform == "betman":
        return pd.read_csv(file_object, encoding="cp1251", sep=";")
    if platform == "natasha":
        return pd.read_csv(file_object)

def clean_date(date_col):
    """ Fill time if missing, then convert to datetime """
    return pd.to_datetime(
        np.where(date_col.str.len() < 11,
                 date_col.apply(lambda x: x + " 00:00"),
                 date_col),
            format="%d.%m.%Y %H:%M")

MONTH_NAMES = [
    u"январь", u"февраль", u"март", u"апрель",
    u"май", u"июнь", u"июль", u"август",
    u"сентябрь", u"октябрь", u"ноябрь", u"декабрь",
]

def make_sheet_name(month, year):
    """ Convert month and year to sheet_name """
    return u"Звонки_%s_%s" % (MONTH_NAMES[month-1], str(year))

def clean_sheet(data):
    if is_empty_dataframe(data):
        return data
    ix = data.iloc[:, 1] != ""
    return data.loc[ix].reset_index(drop=True)

def is_empty_dataframe(data):
    """ Check if data len is greater than zero """
    return not len(data)

def insert_start_cell(sheet):
    return "A%d" % (sheet.shape[0] + 2)

if __name__ == "__main__":
    pass
