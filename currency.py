from datetime import date
#from datetime import datetime
from datetime import timedelta
from matplotlib.dates import ConciseDateFormatter
from matplotlib.dates import AutoDateLocator
from lxml import html
from getpass import getpass
#from sklearn import svm


#import datedelta
import requests
import pandas as pd
#import numpy as np
import matplotlib.pyplot as plt

import email_receive as er
import email_send as es

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

def make_plot(date_, rate_, show=True, save=False, plot_filename = 'plot.pdf', graphWidth=800, graphHeight=600):
    locator=AutoDateLocator()
    myFmt = ConciseDateFormatter(locator, formats=['%Y', '%b', '%d', '%H:%M', '%H:%M', '%S.%f'])
    f = plt.figure(figsize=(graphWidth/100.0, graphHeight/100.0), dpi=100)
    pd.plotting.register_matplotlib_converters()
    axes = f.add_subplot(111)
    axes.plot(date_, rate_)
    axes.set_xlabel('Date')
    axes.set_ylabel('Rubles per Euro')
    plt.gca().xaxis.set_major_formatter(myFmt)
    if show:
        plt.show()
    if save:
        f.savefig(plot_filename)
    plt.close('all')
    return plot_filename

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

def construct_message(rate, time_interval_days=30):
    warning0=''
    warning1=''
    mes0=''
    mes1=''
    if time_interval_days <= 1:
        warning0 = 'Warning! Value time_interval_days = {} is not allowed! time_interval_days is replased by 1.\n'.format(time_interval_days)
        time_interval_days = 1
    rate_interval=rate[rate['data']>pd.Timestamp(date.today()-timedelta(days=time_interval_days))].dropna()
    if rate_interval['curs'].values.argmin()==0:
        warning1 = 'Warning! You may have set the time interval too short because the minimum rate is in the first row.\n'
    date_min_rate=rate_interval['data'].iloc[rate_interval['curs'].values.argmin()]
    dubl=True
    if pd.Timestamp(date.today())-date_min_rate == timedelta(days=0):
        mes1="Congrats! Today the lowest rate within the last {} days is observed!\n".format(time_interval_days)
        dubl=False
    if dubl and time_interval_days > 5 and pd.Timestamp(date.today())-date_min_rate<timedelta(days=5):
        mes0='Considering the past {} days, the lowest rate is in the last five days.\n'.format(time_interval_days)    
    how_chanred=rate_interval.diff().sum()['curs']
    if how_chanred<0:
        mes2='Over the past {} days, the currency has fallen in price by {:.2f} rubles.'.format(time_interval_days,  -how_chanred)
    elif how_chanred>0:
        mes2='Over the past {} days, the currency has risen in price by {:.2f} rubles.'.format(time_interval_days,  how_chanred)
    elif how_chanred==0:
        mes2='Over the past {} days, currency prices have not changed.'.format(time_interval_days)
    return (warning0 + warning1 + mes0 + mes1 + mes2 +
            "\nTo change time interval, please reply 'time_interval_days = <required int value>'.")

def get_time_interval():
    the_last_email=next(er.check_mail(bot_login, bot_password, sender_login))
    time_interval_days_str=''
    time_interval_days=30
    if 'time_interval_days' in the_last_email:
        eq_n=the_last_email.find('=')
        while not the_last_email[eq_n].isdigit():
            eq_n+=1
        while the_last_email[eq_n].isdigit():
            time_interval_days_str+=the_last_email[eq_n]
            eq_n+=1
        time_interval_days=int(time_interval_days_str)
    return time_interval_days    

if __name__ == "__main__":
    bot_login = "bot@gmail.com"
    sender_login='user@gmail.com'
    bot_password = getpass(prompt='Bot password: ', stream=None)
    excel_file_name='actual_data.xlsx'
    
    rate=pd.read_excel(excel_file_name, usecols=['data', 'curs'])
    last_entry=rate['data'].iloc[-1].date()
    if date.today().weekday() != 0 and date.today().weekday() != 6 and date.today() != last_entry:
        update_data()
        rate=pd.read_excel(excel_file_name, usecols=['data', 'curs'])
            
    es.send_email(bot_login, bot_password, sender_login, "Subject: Currency rate from Python\n\n" + construct_message(rate, get_time_interval()))
    #rate_i=rate[rate['data']>pd.Timestamp(date.today()-timedelta(get_time_interval()))].dropna()
    #make_plot(rate_i['data'], rate_i['curs'], save=True)
    print('Done')