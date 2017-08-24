import numpy as np
import pandas as pd

def load_all_data(data_folder = '../data/'):
    df = pd.read_csv(data_folder + "prc.csv")  # TBA price
    FN_issue = pd.read_csv(data_folder + "FN_issuance.csv")  # issuance 
    rr_daily = pd.read_excel(data_folder + "ILM3NAVG_daily.xlsx") # Use Bankrate.com US Home Mortgage 30year Fixed Natinal Avg
    TR_10 = pd.read_excel(data_folder + "USGG10YR.xlsx")
    CMMFIX=pd.read_excel(data_folder + "CMMFIX.xlsx",skiprows = 6) # treasury rate approxy
    CMMFIX.sort_values(by='Date', axis=0, ascending=True,inplace=True) 
    CMMFIX = CMMFIX.reset_index(drop=True)
    MTGFNCL=pd.read_excel(data_folder + "MTGEFNCL.xlsx",skiprows = 5) # treasury rate approxy
    MTGFNCL.sort_values(by='Date', axis=0, ascending=True,inplace=True) 
    MTGFNCL = MTGFNCL.reset_index(drop=True)
    
    rate_base_raw=pd.DataFrame(MTGFNCL.merge(CMMFIX,how='left', on="Date"),columns = ['Date','PX_LAST_x','PX_LAST_y'])
    rate_Base_raw=pd.DataFrame(rate_base_raw.merge(TR_10,how='left', on="Date"),columns = ['Date','PX_LAST_x','PX_LAST_y','PX_LAST'])
    rate_Base_raw=rate_Base_raw.rename(columns={'PX_LAST_x': 'MTGFNCL', 'PX_LAST_y': 'CMMFIX','PX_LAST': 'TR'})

    rate_Base=rate_Base_raw[:][['Date','MTGFNCL']]
    rate_Base.set_index('Date', inplace = True)
    coupon_rates=df['coupon'].unique()
    coupon_rates.sort()
    df['Date']=pd.to_datetime(df['date'], format='%Y%m%d')
    df.set_index('Date', inplace = True)
    df=df.drop('date',axis=1)

    TBAs = {}
    for i in np.arange(0, len(coupon_rates)):
        TBAs[coupon_rates[i]] = df[(df['coupon']==coupon_rates[i])].dropna()
        TBAs[coupon_rates[i]] = pd.concat([TBAs[coupon_rates[i]], rate_Base], axis=1, join='inner')
        TBAs[coupon_rates[i]]['Spread']  = coupon_rates[i] - TBAs[coupon_rates[i]]['MTGFNCL']
        TBAs[coupon_rates[i]]['Year'] = TBAs[coupon_rates[i]].index.year

    FN_issue.set_index('Date', inplace = True)
    rr_daily.set_index('Date', inplace = True)
    rr_daily.columns = ['Last rate', 'Mid rate']
    TR_10.set_index('Date', inplace = True)
    TR_10.columns = ['10 year rate']

    all_coupons = []
    for s in FN_issue.columns:
        all_coupons.append(float(s.split()[4][:-1]))

    params = {}
    n = 20
    for i in all_coupons:
        indexes = TBAs[i].index[n:]
        ret = (TBAs[i]['price'].values[n:] - TBAs[i]['price'].values[:-n])/TBAs[i]['price'].values[:-n]
        params[i] = pd.DataFrame({'Date':indexes, 'Return':ret})
        params[i].set_index('Date', inplace = True)
        params[i]['Rate Change'] = (TBAs[i]['Spread'].values[n:] - TBAs[i]['Spread'].values[:-n]) / 100

    return df, TBAs, params, all_coupons, rate_Base_raw, FN_issue, rate_Base
