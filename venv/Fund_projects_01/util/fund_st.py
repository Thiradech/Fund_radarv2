import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def join_path(relative_path):
    base_dir = os.path.dirname(__file__)
    return os.path.join(base_dir+"/..", relative_path)

# Prepare NAV data
def prepare_nav_data(fund_nav):
    fund_nav.rename(columns={fund_nav.columns[0]: "Date"}, inplace=True)
    fund_nav['Date'] = pd.to_datetime(fund_nav['Date'])
    return fund_nav.melt(id_vars="Date", var_name="Fund Name", value_name="NAV")

