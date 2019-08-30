import tkinter as tk
import pandas as pd

import email_send_with_attachment as es_wa
import email_receive as er
import currency as cur

from datetime import date
from datetime import timedelta


class Application(tk.Frame):
    def __init__(self, master=None, time_interval_days=30):
        super().__init__(master)
        self.master = master
        self.pack()
        self.master.title('Currency')
        self.master.resizable(0,0)
        self.create_widgets()
        self.repeat=True
        self.time_interval_days=time_interval_days
        self.hidden=False
        self.hidden_times=0
        try:
            f= open("hidden_email.txt","r")
            self.hidden_email=f.read()
            f.close()
        except FileNotFoundError:
            self.hidden_email=''
        
        
        		
                               
    def create_widgets(self):
        self.l_bot_email=tk.Label(self, text="Bot's e-mail:")
        self.l_bot_email.pack()
        
        self.e_bot_email=tk.Entry(self, width=35)
        self.e_bot_email.pack()
        
        self.l_bot_passwd=tk.Label(self, text="Bot's password:", anchor='w')
        self.l_bot_passwd.pack()
        
        self.e_bot_passwd=tk.Entry(self, show='*',width=35)
        self.e_bot_passwd.pack()
                
        self.l_user_email=tk.Label(self, text='User e-mail:', anchor='w')
        self.l_user_email.pack()
        
        self.e_user_email=tk.Entry(self, width=35)
        self.e_user_email.pack()
        
        self.l_data_filename=tk.Label(self, text='Data file name:', anchor='w')
        self.l_data_filename.pack()
        
        self.e_data_filename=tk.Entry(self, width=35)
        self.e_data_filename.pack()
        
        self.bf=tk.Frame()
        self.bf.pack()
        
        self.start = tk.Button(self.bf, text="Start", command=self.get_values)
        self.start.pack(side="left")
        
        self.stop = tk.Button(self.bf, text="Stop", state='disabled', command=self.activate_entries)
        self.stop.pack(side="left")
        
        self.hide = tk.Button(self.bf, text="Hide", state='disabled', command=self.hide)
        #button commented due to bugs
		#self.hide.pack(side="left")
		
        self.quit = tk.Button(self.bf, text="Exit", command=self.master.destroy)
        self.quit.pack(side="right")
        
        self.e_bot_email.insert(0,'bot@gmail.com')
        self.e_bot_passwd.insert(0,'passwd')
        self.e_user_email.insert(0,'user@gmail.com')
        self.e_data_filename.insert(0,'actual_data.xlsx')
    
    def get_values(self):
        self.bot_email=self.e_bot_email.get()
        self.bot_passwd=self.e_bot_passwd.get()
        self.user_email=self.e_user_email.get()
        self.filename=self.e_data_filename.get()
        
        self.e_bot_email.config(state='disabled')
        self.e_bot_passwd.config(state='disabled')
        self.e_user_email.config(state='disabled')
        self.e_data_filename.config(state='disabled')
        self.start.config(state='disabled')
        self.stop.config(state='normal')
        self.hide.config(state='normal')
        
        self.rate=self.get_data()
        
        
        self.repeat=True
        try:
            self.last_email=next(er.check_mail(self.bot_email, self.bot_passwd, self.user_email))
        except StopIteration:
            self.last_email=''
            self.compose_and_send_mail()
        except UnboundLocalError:
            tk.messagebox.showerror('Error','Wrong login or password!')
            self.activate_entries()
            
        self.check_mail()
        self.get_time_interval()                      
        self.be_aware()
        
            
    def activate_entries(self):
        self.e_bot_email.config(state='normal')
        self.e_bot_passwd.config(state='normal')
        self.e_user_email.config(state='normal')
        self.e_data_filename.config(state='normal')
        self.start.config(state='normal')
        self.stop.config(state='disabled')
        #code to stop the program
        self.repeat=False
           
    def check_mail(self):
        if self.repeat:
            try:
                self.current_email=next(er.check_mail(self.bot_email, self.bot_passwd, self.user_email))
                if not self.current_email==self.last_email:
                    self.last_email=self.current_email
                    self.get_time_interval()
                    #send new email
                    self.compose_and_send_mail()                
                if (self.hidden and ('show' in self.current_email) and ((self.hidden_email != self.current_email.replace('\r','\n')) and self.hidden_times == 0) or
                    ((self.hidden_email != self.current_email) and self.hidden_times != 0)):
                    self.hidden_times+=1
                    self.hidden_make_false()
                    self.hidden_email=self.current_email
                    f= open("hidden_email.txt","w+")
                    f.write(self.hidden_email)
                    f.close()
                    
            except StopIteration:
                pass
            self.after(int(timedelta(hours=0, minutes=1, seconds=00).total_seconds()*1000), self.check_mail)
            
    def be_aware(self):
        if self.repeat:
            if date.today().weekday() != 0 and date.today().weekday() != 6 and self.check_for_update() != pd.Timestamp(date.today()):
                self.compose_and_send_mail()
            self.after(int(timedelta(days=1, hours=0, minutes=0, seconds=0).total_seconds()*1000), self.be_aware)
    
    def get_time_interval(self):
        if self.repeat:
            time_interval_days_str=''
            if 'time_interval_days' in self.last_email[:self.last_email.find(self.bot_email)]:
                eq_n=self.last_email.find('=')
                while not self.last_email[eq_n].isdigit():
                    eq_n+=1
                while self.last_email[eq_n].isdigit():
                    time_interval_days_str+=self.last_email[eq_n]
                    eq_n+=1
                self.time_interval_days = int(time_interval_days_str)
    
    def get_data(self):
        try:
            rate=pd.read_excel(self.filename, usecols=['data', 'curs'])
        except FileNotFoundError:
            self.datafile_error()
            rate=pd.read_excel(self.filename, usecols=['data', 'curs'])
        
        self.last_entry=rate['data'].iloc[-1].date()
        if date.today().weekday() != 0 and date.today().weekday() != 6 and date.today() != self.last_entry:
            self.update_datafile()
            rate=pd.read_excel(self.filename, usecols=['data', 'curs'])
        return rate
        
    def update_datafile(self):
        try:
            rate0=pd.read_excel(self.filename)
        except FileNotFoundError:
            self.datafile_error()
            rate0=pd.read_excel(self.filename)
        absent_rate={}
        for day in cur.date_generator(self.last_entry):
            absent_rate[pd.Timestamp(day)]=cur.get_currency_rate(current_data=day)
        ndf=pd.DataFrame(pd.Series(absent_rate)).reset_index().rename(columns={'index' : 'data', 0 : 'curs'})
        ndf[rate0.columns[0]]=rate0[rate0.columns[0]].iloc[0]
        ndf[rate0.columns[-1]]=rate0[rate0.columns[-1]].iloc[0]
        ndf=ndf[rate0.columns]
        rate0=pd.concat([rate0, ndf], ignore_index=True, axis=0, sort=False)
        rate0.to_excel(self.filename, index = False)
    
    def create_plot_to_pdf(self):
        rate_i=self.rate[self.rate['data']>pd.Timestamp(date.today()-timedelta(self.time_interval_days))].dropna()
        plot_file_name=cur.make_plot(rate_i['data'], rate_i['curs'], show=False, save=True)
        return plot_file_name
    
    def compose_and_send_mail(self):
        plot_file_name=self.create_plot_to_pdf()
        subject='Currency rate from Python'
        message_body=cur.construct_message(self.rate, self.time_interval_days)
        es_wa.send_message_with_attachment(self.bot_email, self.bot_passwd, self.user_email, subject, message_body, plot_file_name)
        pd.DataFrame(pd.Series(pd.Timestamp(date.today()))).to_csv('when.csv', index=False)
           
    def check_for_update(self):
        try:
            a=pd.read_csv('when.csv')
        except FileNotFoundError:
            pd.DataFrame(pd.Series(pd.Timestamp(date.today()-timedelta(days=1)))).to_csv('when.csv', index=False)
            a=pd.read_csv('when.csv')
        return pd.Timestamp(a['0'].iloc[0])

    def datafile_error(self):
        self.filename='actual_data.xlsx'
        self.e_data_filename.config(state='normal')
        self.e_data_filename.delete(0,len(self.filename))
        self.e_data_filename.insert(0, self.filename)
        self.e_data_filename.config(state='disabled')
        tk.messagebox.showwarning('Warning','Data file is not exist!')
    
    def hide(self):
        self.hidden=True
        self.master.withdraw()
        wait_for=int(timedelta(days=1, hours=0, minutes=0, seconds=0).total_seconds()*1000)
        self.after(wait_for, self.hidden_make_false)
               
    def hidden_make_false(self):
        self.master.deiconify()
        self.hidden=False
                
if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root, time_interval_days=30)
    app.mainloop()