'''
MIT License

Copyright (c) 2020 Sai Prasanth

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime

cur_date = str(datetime.date.today())

def get_data_from_url(Url):
    resp = requests.get(Url)
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        ### Getting Active Cases ###
        active_cases = soup.find_all('li', class_='bg-blue')[0]
        active_cases = active_cases.get_text().split("\n")[2]
        print(active_cases)
        
        ### Getting Total Recovered ###
        tot_recovered = soup.find_all('li', class_='bg-green')[0]
        tot_recovered = tot_recovered.get_text().split("\n")[2]
        print(tot_recovered)

        ### Getting Total Deaths ###
        tot_death = soup.find_all('li', class_='bg-red')[0]
        tot_death = tot_death.get_text().split("\n")[2]
        print(tot_death)

        ### Getting Table details ###
        table = soup.find_all('table')[0]
        status = soup.find_all('div', class_='status-update')[0]
        Title = str(status.get_text()).split('\n')
        Head = Title[1].split(' ')
        Datetime = Head[6]+' '+Head[5]
        case_stats = Datetime+ ":" +active_cases+ "," + tot_recovered+ "," +tot_death+ "\n"

        ### Getting Table details ###
        columns = []
        for head in table.find_all('th'):
            columns.append(head.get_text())

        rows = 0
        colm = []
        for row in table.find_all('tr'):
            cols = 0
            for col in row.find_all('td'):
                colm.append(col.get_text())
                cols += 1
                
        final = []
        for i in range(0,len(colm)):
            new_colm = []
            for j in range(i,len(colm), 5):
                new_colm.append(colm[j])
            final.append(new_colm)
            
        fin_dict = {}  
        for cnt in range(0,len(columns)):
            fin_dict[columns[cnt]] = final[cnt]
        
        return case_stats,fin_dict,columns,Title[1]

def read_data_from_file(filename):
    read_file = open(filename,"r",encoding = 'utf-8')
    out = read_file.readlines()
    read_file.close()
    return out

def write_data_to_file(filename,case_stats):
    out = read_data_from_file(filename)
    last_entry = out[len(out)-1]
    if last_entry != case_stats:
        if last_entry.split(":")[0] == case_stats.split(":")[0]: #If case data has been updated in the same date
            temp_data = out[:len(out)-1]
            temp_str = ""
            for val in temp_data:
                temp_str = temp_str+val
            temp_str = temp_str+case_stats
            write_file = open(filename,"w")
            write_file.write(temp_str)
            write_file.close()
        else:
            write_file = open(filename,"a")
            write_file.write(case_stats)
            write_file.close()

def get_date_wise_data(input_date,filename):
    out = read_data_from_file(filename)
    input_date = input_date.split('-')[2]
    for data in out:
        data = data.split(":")
        date_data = data[0].split(' ')
        if date_data[1] == input_date:
            case_data = data[1]
            case_data = case_data.split(",")
            active_data = case_data[0]
            recov_data = case_data[1]
            death_data = case_data[2]
            break
##    print('Date: '+input_date+ ', '+ 'Active Cases - '+active_data,'Recovered - '+recov_data, 'Deaths - '+death_data)
    
    return active_data, recov_data, death_data

def plot_state_wise_data(date,states,confirmed,recovered,death,title):

    """
    To Visualize state-wise covid-19 case counts in a bar chart
    X-axis - States/Union Territories
    Y-axis - Counts in range of 100

    Inputs:
    date      - current date to get the total case counts | Data_Type- String | Format- 'yyyy-mm-dd'
    states    - List of corona affected states in india
    confirmed - List of active case counts with respect to states list
    recovered - List of recovered case counts with respect to states list
    death     - List of death case counts with respect to states list

    Outputs:
    returns NULL
    """

    X = np.arange(len(states))
    fig = plt.figure(figsize = (20,10))

    plt.bar(X, confirmed, 0.25, color='g')
    plt.bar(X+0.25, recovered, 0.25, color='b')
    plt.bar(X+0.50, death, 0.25, color='r')

    plt.xticks(X, states, rotation=45)
    max_cnt = sorted(confirmed)
    min_val = 0
    max_val = max_cnt[len(max_cnt)-1]+ 500
    plt.yticks(np.arange(min_val,max_val,200),fontsize = 12)
   
    plt.xlabel('States/UT',fontsize = 15)
    plt.ylabel('Count',fontsize = 15)
    plt.title(title,fontsize = 15)

    active_data, recov_data, death_data = get_date_wise_data(cur_date,filename)
    
    plt.legend(labels=['Active Cases - '+active_data,'Recovered - '+recov_data, 'Deaths - '+death_data],loc ='upper right', fontsize = 15)
    for index, value in enumerate(confirmed):
        plt.text(index, value, str(value), fontsize = 20, color='r',horizontalalignment = 'center',verticalalignment = 'bottom')

    plt.savefig(r'State-wise Reports/State-wise Report-'+cur_date+'.png')

def plot_date_wise_data():

    '''
    To Visualize date-wise covid-19 case counts in a bar chart
    X-axis - Date
    Y-axis - Counts in range of 100

    Inputs:
    No input arguments

    Outputs:
    returns NULL
    '''


    stat_dates = []
    actives = []
    recovs = []
    deaths = []

    out = read_data_from_file(filename)
    for data in out:
        data = data.split(":")
        date_data = data[0]
        case_data = data[1]

        stat_dates.append(date_data)

        case_data = case_data.split(",")
        active_data = case_data[0]
        recov_data = case_data[1]
        death_data = case_data[2]
        
        actives.append(int(active_data))
        recovs.append(int(recov_data))
        deaths.append(int(death_data))
        
    X = np.arange(len(stat_dates))
    fig = plt.figure(figsize = (20,10))

    plt.bar(X, actives, 0.25, color='g')
    plt.bar(X+0.25, recovs, 0.25, color='b')
    plt.bar(X+0.50, deaths, 0.25, color='r')

    plt.xticks(X, stat_dates, fontsize = 12)
    plt.yticks(np.arange(0,10001,1000), fontsize = 12)

    plt.xlabel('Cases',fontsize = 15)
    plt.ylabel('Count',fontsize = 15)
    plt.title('Covid-19 India - Datewise Report',fontsize = 15)

    plt.legend(labels=['Active Cases','Recovered','Deaths'],loc ='upper right', fontsize = 15)
    for index, value in enumerate(actives):
        plt.text(index , value, str(value), fontsize = 20, color='g',horizontalalignment = 'center',verticalalignment = 'bottom')
    for index, value in enumerate(recovs):
        plt.text(index+0.25+0.10 , value, str(value), fontsize = 15, color='b',horizontalalignment = 'center',verticalalignment = 'bottom')
    for index, value in enumerate(deaths):
        plt.text(index+0.50+0.10 , value, str(value), fontsize = 15, color='r',horizontalalignment = 'center',verticalalignment = 'bottom')

    plt.savefig(r'Date-wise Reports/Date-wise Report-'+cur_date+'.png')

def plot_active_vs_recovered_data():
    stat_dates = []
    actives = []
    recovs = []
    deaths = []

    out = read_data_from_file(filename)
    for data in out:
        data = data.split(":")
        date_data = data[0]
        case_data = data[1]

        stat_dates.append(date_data)

        case_data = case_data.split(",")
        active_data = case_data[0]
        recov_data = case_data[1]
        death_data = case_data[2]
        
        actives.append(int(active_data))
        recovs.append(int(recov_data))
        deaths.append(int(death_data))

    fig = plt.figure(figsize=(20,10))

    plt.title("Active vs Recovered", fontsize=15)
    plt.xlabel("Date", fontsize=15)
    plt.ylabel("Cases Counts", fontsize=15)
    plt.plot(stat_dates, actives, color="r", linewidth=5)
    plt.plot(stat_dates, recovs, color="g", linewidth=5)

    plt.yticks(np.arange(0, actives[-1]+3001, 2000))
    plt.legend(labels = ["Active", "Recovered"], fontsize=15)

    for ind, data in enumerate(actives):
        plt.text(ind, data+230, str(data), fontsize = 15, color='r',horizontalalignment = 'center',verticalalignment = 'bottom')

    for ind, data in enumerate(recovs):
        plt.text(ind, data+230, str(data), fontsize = 15, color='g',horizontalalignment = 'center',verticalalignment = 'bottom')

    plt.grid(axis='y')
    plt.savefig(r'Active-vs-Recovered-' + cur_date + '.png')

def plot_active_vs_death_data():
    stat_dates = []
    actives = []
    recovs = []
    deaths = []

    out = read_data_from_file(filename)
    for data in out:
        data = data.split(":")
        date_data = data[0]
        case_data = data[1]

        stat_dates.append(date_data)

        case_data = case_data.split(",")
        active_data = case_data[0]
        recov_data = case_data[1]
        death_data = case_data[2]
        
        actives.append(int(active_data))
        recovs.append(int(recov_data))
        deaths.append(int(death_data))

    fig = plt.figure(figsize=(20,10))

    plt.title("Active vs Death", fontsize=15)
    plt.xlabel("Date", fontsize=15)
    plt.ylabel("Cases Counts", fontsize=15)
    plt.plot(stat_dates, actives, color="r", linewidth=5)
    plt.plot(stat_dates, deaths, color="b", linewidth=5)

    plt.yticks(np.arange(0, actives[-1]+3001, 2000))
    plt.legend(labels = ["Active", "Death"], fontsize=15)
    for ind, data in enumerate(actives):
        plt.text(ind, data+230, str(data), fontsize = 15, color='r',horizontalalignment = 'center',verticalalignment = 'bottom')

    for ind, data in enumerate(deaths):
        plt.text(ind, data+330, str(data), fontsize = 15, color='b',horizontalalignment = 'center',verticalalignment = 'bottom')

    plt.grid(axis='y')
    plt.savefig(r'Active-vs-Death-' + cur_date + '.png')

    
if __name__ == "__main__":
    
    filename = r'Case-stats.txt'
    
    case_stats,fin_dict,columns,title = get_data_from_url("https://www.mohfw.gov.in/")
    write_data_to_file(filename,case_stats)
        
    table = pd.DataFrame(data=fin_dict)
##    table.to_excel(r'excel_data/'+"COVID-19 INDIA "+cur_date+".xlsx",index = False)

    new_table = table[:-1] # Eliminating last row
    
    states = new_table[columns[1]]
    confirmed = new_table[columns[2]].map(int)
    recovered = new_table[columns[3]].map(int)
    death = new_table[columns[4]].map(int)
    
    plot_state_wise_data(cur_date,states,confirmed,recovered,death,title)
    plot_date_wise_data()

    plot_active_vs_recovered_data()
    plot_active_vs_death_data()
