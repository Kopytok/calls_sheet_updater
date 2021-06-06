import pandas as pd
import numpy as np

from functools import reduce
import re

from .constants import PLATFORM_COLNAMES

class Preprocessor(object):

    def __init__(self, platform):
        self.platform = platform
        self.select_platform_colnames(platform)

    def select_platform_colnames(self, platform):
        self.account, self.telno, self.datereg = PLATFORM_COLNAMES[platform]

    def run(self, new_data, old_data):
        self.upd = preprocess(new_data, *PLATFORM_COLNAMES[self.platform])
        return self.filter_irrelevant_rows(old_data)

    def filter_irrelevant_rows(self, old_data):
        c = [
            (
                self.upd[self.telno].str.startswith("375") |
                (self.upd[self.telno] == "")
            ),
        ]
        if len(old_data):
            c.append(~self.upd[self.account].isin(seen_accounts(old_data)))
        ix = reduce(lambda x, y: x & y, c)
        return self.upd.loc[ix].reset_index(drop=True)


def preprocess(data, account, telno, datereg):
        upd = data.reindex(columns=[
            "col1", account, "col2", "col3", "col4",
            "col5", "col6", "col7", telno,
        ])
        upd = upd.where(pd.notnull(upd), None)
        upd[datereg] = data[datereg].dt.strftime("%d.%m.%Y %H:%M")
        upd[telno] = format_telno(upd[telno])
        return upd.sort_values([datereg, telno])

def seen_accounts(data):
    accounts = data.iloc[:, 1].astype(np.int32)
    return set(accounts.tolist())

def seen_phones(data):
    phones = data.iloc[:, 8]
    return set(phones.tolist())

def format_telno(values):
    return values.apply(str_telno).str.replace("^80", "375", regex=True)

def str_telno(x):
    if x and not pd.isna(x):
        if isinstance(x, str):
            return str(int(re.sub("[^0-9]", "", x)))
        return str(int(x))
    return ""

if __name__ == "__main__":
    pass
