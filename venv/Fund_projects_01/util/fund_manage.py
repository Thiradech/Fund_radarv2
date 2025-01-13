#import lseg.data as ld
import refinitiv.data as ld
import pandas as pd
#from dotenv import load_dotenv
#import os
from datetime import date, timedelta
#ld.open_session(name="desktop.workspace")
def session(open=True):
    if open:
        ld.open_session(config_name="Configuration/lseg-data.config.json")
    else:
        ld.close_session()
    return session

class Fund_ov:
    def change_ric_to_sec(ric, list_=False):
        df = pd.read_csv("Fund_projects_01/data/sec_code.csv") #universe
        if list_ == False:    
            if ric in df["Instrument"].tolist():
                #print("in!")
                sec = df[df["Instrument"] == ric]['SEC_CODE'].values[0]
                return sec
            else:
                #print("~in!")
                return
        elif list_ == True:
            df_lst = pd.DataFrame(ric, columns=["Instrument"])
            df_lst = df_lst.merge(df, on="Instrument", how="left")
            return df_lst["SEC_CODE"].tolist()
        
    def change_sec_code_to_ric(sec_code, list_=False):
        df = pd.read_csv("Fund_projects_01/data/sec_code.csv") #universe
        if not list_:    
            if sec_code in df["SEC_CODE"].tolist():
                #print("in!")
                ric = df[df["SEC_CODE"] == sec_code]['Instrument'].values[0]
                return ric
            else:
                #print("~in!")
                return
        elif list_:
            df_lst = pd.DataFrame(sec_code, columns=["SEC_CODE"])
            df_lst = df.merge(df, on="SEC_CODE", how="left")
            return df_lst["Instrument"].tolist()
        
    def get_th_funds_active_universe(type_="all"):
        if type_ == "primary":
            universe = pd.read_csv("Fund_projects_01/data/sec_code_primary.csv")["Instrument"].tolist()
            return universe
        elif type_ == "all":
            universe = pd.read_csv("Fund_projects_01/data/sec_code.csv")["Instrument"].tolist()
            return universe
        return
    
    def get_all_funds_overview(type_="all"):
        fields = [          
           'TR.FundName',
           'TR.FundType',
           'TR.FundGeographicFocus',
           'TR.FundTotalNetAssets',
           'TR.FundLegalStructure',
           'TR.FundLaunchDate',
           'TR.FundCompany',
           'TR.FundPortfolioManager',
           'TR.FundCustodian',
           'TR.FundMinInitialInv',
           'TR.FundMinRegularInv',
           'TR.FundMinIrregularInv',
           'TR.FundIncDistributionIndicator',
           'TR.FundExDividendDate',
           'TR.FundDividendPayment',
           'TR.FundNumberOfDividendPaymentPerYear',
           'TR.FundObjective',
           'TR.FundMinInitialCharge',
           'TR.FundMaxInitialCharge',
           'TR.FundCurrInitialCharge',
           'TR.FundMinAnnualCharge',
           'TR.FundMaxAnnualCharge',
           'TR.FundCurrAnnualCharge',
           'TR.FundMinRedemptionCharge',
           'TR.FundMaxRedemptionCharge',
           'TR.FundCurrRedemptionCharge',
           'TR.FundClassificationSectorScheme',
           'TR.FundClassificationSectorName',
           'TR.FundCrossReferenceIdentifiersType',
           'TR.FundCrossReferenceIdentifiers',
           'TR.FundRegisteredCountry',
           'TR.FundRegisterCountryofSalesFlag',
           'TR.FundTER',
           'TR.FundTERDate',
           'TR.FundProjectedYield'
        ]
        if type_ == "all":
            universe = Fund_ov.get_th_funds_active_universe(type_="all")
        elif type_ == "primary":
            universe = Fund_ov.get_th_funds_active_universe(type_="primary")

        lst = []
        for i in range(int(len(universe) / 50) + 1):
            retry_count = 5  # จำนวนครั้งที่ลองใหม่
            while retry_count > 0:
                try:
                    if i != int(len(universe) / 50): 
                        df = ld.get_data(
                            universe=universe[i * 50:(i + 1) * 50],
                            fields=fields
                        )
                    else:
                        df = ld.get_data(
                            universe=universe[i * 50:len(universe)],
                            fields=fields
                        )
                    lst.append(df)
                    break  # ถ้าสำเร็จ ให้หลุดจากลูป while
                except Exception as e:
                    retry_count -= 1
                    if retry_count == 0:
                        print(f"Error fetching data for batch {i}: {e}")
                        raise  # หากยังไม่สำเร็จหลัง retry ครบแล้ว ให้ส่ง error ออกไป

        sec_code = pd.read_csv("Fund_projects_01/data/sec_code.csv").set_index("Instrument")
        combined_df = pd.concat(lst, axis=0).set_index("Instrument")
        combined_df = combined_df.merge(sec_code, left_index=True, right_index=True, how="left")

        th_code = combined_df.pop("SEC_CODE")
        combined_df.insert(0, "TH_CODE", th_code)
        if type_ == "primary":
            combined_df.to_csv("Fund_projects_01/data/primary_active_funds_TH_overview.csv", index=True)
        elif type_ == "all":
            combined_df.to_csv("Fund_projects_01/data/all_active_funds_TH_overview.csv", index=True)

        return combined_df
    
    def get_all_funds_NAV_history(universe = "all", chunk_size = 60): #get_price_history of all active TH funds
        
        if universe == "all":
            universe = pd.read_csv("Fund_projects_01/data/sec_code.csv")["Instrument"].tolist()
        elif universe == "primary":
            universe = pd.read_csv("Fund_projects_01/data/sec_code_primary.csv")["Instrument"].tolist()
        
        # แบ่ง universe ออกเป็น chunks
        chunks = [universe[i:i + chunk_size] for i in range(0, len(universe), chunk_size)]

        # ทำการดึงข้อมูลทีละ chunk
        all_data = []
        for idx, chunk in enumerate(chunks, start=1):
            while True:
                try:
                    print(f"Processing chunk {idx}/{len(chunks)}...")  # แสดงสถานะของ chunk ที่กำลังประมวลผลอยู่
                    data = ld.get_data(
                        universe=chunk,
                        fields=['TR.FundNAV(SDate=-5Y,EDate=1D)', 'TR.FundNAV(SDate=-5Y,EDate=1D).date'],
                        
                    )
                    all_data.append(data)
                    break
                except:
                    print(f"There's problem in loop number {idx} re-trying...")

        # รวมผลลัพธ์ทั้งหมด
        final_data = pd.concat(all_data, axis=0)
        print("Data processing complete.")

        df = final_data.pivot(index="Date", columns="Instrument", values="NAV").sort_index(ascending=True).iloc[:, :-1]
        df.columns = Fund_ov.change_ric_to_sec(df.columns.tolist(), list_=True)
        df.to_csv("Fund_projects_01/data/fund_NAV_history.csv", index=True)
        return df