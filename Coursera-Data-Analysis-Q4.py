# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 18:25:42 2016

@author: bwaldie
"""
import re
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind

#file base path
file_path = ("C:\\Users\\Public\\Documents\\Python Scripts\\")

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}

def read_university_towns():
    u_states = list()
    u_regions = list()
    university_towns = pd.DataFrame()
    with open(file_path+"university_towns.txt","r") as fh:
        for line in fh:
            # print(line)
            m1 = re.search(r'(.*?)\s*\[edit\]', line)
            m2 = re.search(r'^(.*?)\s+\(', line)
            if (m1 != None):
                # print(m1.group(1))
                state = m1.group(1)
            elif (m2 != None):
                # print(state, " ",m2.group(1))
                u_states.append(state)
                u_regions.append(m2.group(1))
            else:
                u_states.append(state)
                u_regions.append(line.strip('\n'))
                #print(line)
    university_towns = pd.DataFrame({ 'State': u_states, 'RegionName' : u_regions})
    university_towns = university_towns[['State','RegionName']]
    return university_towns

def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    
    university_towns = pd.DataFrame()
    university_towns = read_university_towns()
    return university_towns
    
def read_gdp_xls():
    GDP = pd.DataFrame()
    GDP = pd.read_excel(file_path+"gdplev.xls",skiprows=7)
    GDP = GDP[['Unnamed: 4', 'Unnamed: 6']]
    GDP = GDP.rename(columns={'Unnamed: 4' : 'Quarter', 'Unnamed: 6':'GDP'})
    GDP['delta']=GDP['GDP'].diff()
    GDP['delta_shifted-1'] = GDP['delta'].shift(-1)
    return GDP

dfGDP = read_gdp_xls()
# print(dfGDP)

def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    mask_start_GDP = ((dfGDP['delta']<0) & (dfGDP['delta_shifted-1']<0) & (dfGDP['Quarter'] >= '2000q1'))
    df_start_GDP = dfGDP[mask_start_GDP]
    return df_start_GDP['Quarter'].iloc[0]

recession_start = get_recession_start()
print("start = " + recession_start)

def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    mask_stop_GDP = ((dfGDP['delta']>=0) & (dfGDP['delta_shifted-1']>=0) & (dfGDP['Quarter'] >= recession_start))
    df_stop_GDP = dfGDP[mask_stop_GDP]
    return df_stop_GDP['Quarter'].iloc[1]

recession_end = get_recession_end()
print("end   = " + recession_end)

def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    mask_bottom_GDP = ((dfGDP['Quarter'] >= recession_start) & (dfGDP['Quarter'] < recession_end))
    df_bottom_GDP = dfGDP[mask_bottom_GDP]
    df_bottom_GDP = df_bottom_GDP.set_index('Quarter')
    bottom_idx =  df_bottom_GDP['GDP'].idxmin()
    return bottom_idx

print(get_recession_bottom())

def read_zillow_data():
    df_zillow = pd.read_csv(file_path+"City_Zhvi_AllHomes.csv")
    df_zillow['State'].replace(states, inplace=True)
    df_zillow.drop(df_zillow.columns[6:51], axis=1, inplace=True)
    df_zillow['2016-09'] = df_zillow[['2016-07', '2016-08']].mean(axis=1)
    return df_zillow

def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    
    df.columns = pd.to_datetime(df.columns)
    res = df.resample('Q', axis=1).mean()

    res = res.rename(columns=lambda col: '{}q{}'.format(col.year, col.quarter))

    pd.concat([df, res], axis=1)
    '''
    df_zillow = read_zillow_data()
    df_zillow.set_index(['State','RegionName'], inplace=True)
    df_zillow.drop(df_zillow[['RegionID','Metro','CountyName','SizeRank']], axis=1, inplace=True)
    # df_zillow.columns = pd.to_datetime(df_zillow.columns) # will work too, but the below covers cases where
    # there are NON-date column headings
    df_zillow.rename(columns = lambda col: pd.to_datetime(col, errors='ignore', format="%Y-%m"), inplace=True)
    df_zillow = df_zillow.resample('Q', axis=1).mean()
    df_zillow.rename(columns = lambda col: '{}q{}'.format(col.year, col.quarter), inplace=True)
    return df_zillow


def add_price_ratio_column():
    ts = pd.Timestamp(pd.Timestamp(get_recession_start())-pd.DateOffset(months=3))
    quarter_before_recession = str(ts.to_period('Q')).lower()
    recession_bottom = get_recession_bottom()
    df_z = convert_housing_data_to_quarters()
    df_z.dropna(axis=0, how='all', subset=[recession_bottom, quarter_before_recession], inplace=True)
    df_z['price_ratio'] = df_z[quarter_before_recession]/df_z[recession_bottom]
    df_z.dropna(axis=0, how='all', subset=['price_ratio'], inplace=True)
    return df_z[['price_ratio']]

def create_data_sets():
    df_full = add_price_ratio_column()
    df_university_towns = get_list_of_university_towns()
    df_university_towns.set_index(['State','RegionName'],inplace=True)
    print(len(df_full), len(df_university_towns))

    df_univ_yes = pd.merge(df_university_towns, df_full, how='inner', left_index=True, right_index=True, indicator=True)
    df_univ_no  = pd.merge(df_university_towns, df_full, how='outer', left_index=True, right_index=True, indicator=True)
    df_univ_yes = df_univ_yes[(df_univ_yes['_merge'] == 'both')]
    df_univ_no  = df_univ_no[(df_univ_no['_merge'] == 'right_only')]

    return (df_univ_yes['price_ratio'], df_univ_no['price_ratio'])


def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    
    df_yes, df_no = create_data_sets()
    # print(len(df_yes), len(df_no))
    # print(df_yes.describe())
    # print(df_no.describe())
    
    ans = ttest_ind(df_no, df_yes, axis=0, equal_var=False, nan_policy='omit')
    # print(ans)
    p = ans[1]
    
    if (p > 0.01):
        different = False
    else:
        different = True
    
    print("university mean ratio: " + str(df_yes.mean(axis=0)))
    print("non-university mean ratio: " + str(df_no.mean(axis=0)))
    
    if (df_yes.mean(axis=0) > df_no.mean(axis=0)):
        better = 'non-university town'
    else:
        better = 'university town'
        
    return (different, p, better)

print(run_ttest())
print('(True, 0.00041476360323563295, \'university town\')')
    