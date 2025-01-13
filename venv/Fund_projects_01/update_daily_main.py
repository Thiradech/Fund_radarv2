import util.fund_manage as fm
import lseg.data as ld
import pandas as pd
#fm.Fund_ov.get_all_funds_overview()
#fm.Fund_ov.get_all_funds_NAV_history()
ld.open_session(config_name="Configuration/lseg-data.config.json")
universe = pd.read_csv("Fund_projects_01/data/sec_code.csv")["Instrument"].tolist()
universe = universe[:50]
data = ld.get_data(
    universe=universe,
    fields=['TR.FundNAV(SDate=-5Y,EDate=1D)', 
            'TR.FundNAV(SDate=-5Y,EDate=1D).date'],
    
)
print(data)