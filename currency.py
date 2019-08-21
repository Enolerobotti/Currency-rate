from datetime import date
#from datetime import datetime
from datetime import timedelta
from lxml import html
#from sklearn import svm

#import datedelta
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def get_currency_rate(current_data=date.today(), currency_name='EUR'):
    url='https://www.cbr.ru/currency_base/daily/?date_req=' + current_data.strftime("%d.%m.%y")
    page = requests.get(url)
    tree = html.fromstring(page.content)
    tr_elements=tree.xpath('//tbody//tr')
    i=0
    while not currency_name in [t.text_content() for t in tr_elements[i]]:
        i+=1
    EUR_row=[t.text_content() for t in tr_elements[i]]
    return float(EUR_row[-1].replace(',','.'))

def make_plot(date_, rate_, graphWidth=800, graphHeight=600):
    f = plt.figure(figsize=(graphWidth/100.0, graphHeight/100.0), dpi=100)
    pd.plotting.register_matplotlib_converters()
    axes = f.add_subplot(111)
    axes.plot(date_, rate_)
    axes.set_xlabel('data')
    axes.set_ylabel('rate')
    plt.show()
    plt.close('all')

def date_generator(from_date, to_date=date.today()):
    while from_date < to_date:
        from_date = from_date + timedelta(days = 1)
        if from_date.weekday() != 0 and from_date.weekday() != 6:
            yield from_date
    
def update_data():
    rate0=pd.read_excel(excel_file_name)
    absent_rate={}
    for day in date_generator(last_entry):
        absent_rate[pd.Timestamp(day)]=get_currency_rate(current_data=day)
    ndf=pd.DataFrame(pd.Series(absent_rate)).reset_index().rename(columns={'index' : 'data', 0 : 'curs'})
    ndf[rate0.columns[0]]=rate0[rate0.columns[0]].iloc[0]
    ndf[rate0.columns[-1]]=rate0[rate0.columns[-1]].iloc[0]
    ndf=ndf[rate0.columns]
    rate0=pd.concat([rate0, ndf], ignore_index=True, axis=0, sort=False)
    rate0.to_excel(excel_file_name, index = False)

def naive_analys(time_interval_days=30, print_messages=True, return_values=False):
    if time_interval_days <= 1:
        print('Warning! Value time_interval_days = {} is not allowed! It replased by 1.'.format(time_interval_days))
        time_interval_days = 1
    rate_interval=rate[rate['data']>pd.Timestamp(date.today()-timedelta(days=time_interval_days))].dropna()
    if print_messages and rate_interval['curs'].values.argmin()==0:
        print('Warning! You may have set the time interval too short because the minimum rate is in the first row')
    date_min_rate=rate_interval['data'].iloc[rate_interval['curs'].values.argmin()]
    if print_messages and (time_interval_days > 5 and pd.Timestamp(date.today())-date_min_rate<timedelta(days=5)):
        print('Considering the past %s days, the lowest rate is in the last five days' % time_interval_days)
    if print_messages and pd.Timestamp(date.today())-date_min_rate == timedelta(days=0):
        print("Congrats! Today the lowest rate within the last %s days is observed!" % time_interval_days)
    how_chanred=rate_interval.diff().sum()['curs']
    if print_messages and how_chanred<0:
        print('Over the past {} days, the currency has fallen in price by {:.2f} rubles'.format(time_interval_days,  -how_chanred))
    elif print_messages and how_chanred>0:
        print('Over the past {} days, the currency has risen in price by {:.2f} rubles'.format(time_interval_days,  how_chanred))
    elif print_messages and how_chanred==0:
        print('Over the past %s days, currency prices have not changed' % time_interval_days)
    if return_values:
        return (date_min_rate, how_chanred)
            

if __name__ == "__main__":
    #today_rate=get_currency_rate()
    excel_file_name='actual_data.xlsx'
    rate=pd.read_excel(excel_file_name, usecols=['data', 'curs'])
    last_entry=rate['data'].iloc[-1].date()
    if date.today().weekday() != 0 and date.today().weekday() != 6 and date.today() != last_entry:
        update_data()
        rate=pd.read_excel(excel_file_name, usecols=['data', 'curs'])
    
    
    #date_min_rate, how_chanred = naive_analys(time_interval_days=2, return_values=True)
    
#    rate0=rate.copy()['curs']
#    rate0=np.sign(np.diff(rate0))
#    rate0=rate0.reshape(-1,1)
#    numb=5
#    my_target=np.array([(-1)**d for d in range(len(rate0)-numb)])
#    clf = svm.SVC(gamma=0.001, C=100.)
#    clf.fit(rate0[:-numb],my_target)
#    result0=clf.predict(rate0[-numb:])
    
    rate['y']=rate['data'].apply(lambda x: x.year)
    rate['m']=rate['data'].apply(lambda x: x.month)
    rate['d']=rate['data'].apply(lambda x: x.day)
    
    #sign_diff_rate=pd.pivot_table(rate, values='curs', index=['m','d'], columns=['y'], aggfunc=lambda x: np.sign(np.diff(x)))
    
#    sign_sum_diff_rate=pd.pivot_table(rate, values='curs', index=['m'], columns=['y'], aggfunc=lambda x: np.sign(np.sum(np.diff(x))))
#    my_data_set0=sign_sum_diff_rate[[d for d in range(2001, 2018)]].values.T
#    my_target0=np.array([(-1)**d for d in range(len(my_data_set0)-1)])
#    clf = svm.SVC(gamma=0.001, C=100.)
#    clf.fit(my_data_set0[:-1],my_target0)
#    result0=clf.predict(my_data_set0[-1:])



    mean_rate=pd.pivot_table(rate, values='curs', index=['m'], columns=['y'])
    sum_diff_rate=pd.pivot_table(rate, values='curs', index=['m'], columns=['y'], aggfunc=lambda x: np.sum(np.diff(x)))
    
#    rate=rate.set_index(['y', 'm', 'd'])
#    years=rate.index.get_level_values(0).unique()
#    corr_list={}
#    corr_list_based_mean={}
#    for d in range(years[0],years[-1]):
#        corr_list[d+1]=rate['curs'].loc[d+1].corr(rate['curs'].loc[d])
#        corr_list_based_mean[d+1]=mean_rate[d+1].corr(mean_rate[d])
        
    #rate within the last month
    #rate_last_month=rate[rate['data']>pd.Timestamp(date.today()-datedelta.MONTH)].dropna()
    #date_min_rate_within_month=rate_last_month['data'].iloc[rate_last_month['curs'].values.argmin()]
    #how_chanred_rate_within_month=rate_last_month.diff().sum()['curs']
    
    
    #print(rate.head())
    #data_start='2019-01-01' #year-month-day
    #data_end='2019-02-01'
    #data_start=date.today()-datedelta.MONTH #year-month-day
    #data_end=date.today()
    #make_plot(rate['data'].where(rate['data']>data_start).where(rate['data']<data_end), rate['curs'].where(rate['data']>data_start).where(rate['data']<data_end))
    