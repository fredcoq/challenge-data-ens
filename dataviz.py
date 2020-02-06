import numpy as np
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import pytz
from matplotlib.dates import (HourLocator, AutoDateLocator, DateFormatter,
                              ConciseDateFormatter, rrulewrapper, RRuleLocator, drange)

tick=30 # période en minute de la time série
day_ticks=2*24 # durée en ticks d'une journée

def data_slice(data,start_day,period_day=1,columns=None) :
    
# fonction permettant de découper le dataset en temps et en features
# data : dataframe dataset
# start_day  : int numéro du jour en référence au premier jour de l'index du dataset
# period_day : nombre de jours à extraire
# columns : list contenant le noms des colonnes à extraire si vide prend toutes les colonnes

    if columns==None : 
        columns=data.columns
        
    return data.iloc[start_day*day_ticks : (start_day+period_day)*day_ticks][columns]

def data_slice_year(data,year,columns=None) :
    
# fonction permettant de découper le dataset en temps et en features
# argument year : prend une année entière
# columns : list contenant le noms des colonnes à extraire si vide prend toutes les colonnes

    if columns==None : 
        columns=data.columns
        
    return data.loc[date(year,1,1) : date(year,12,31)][columns]

def data_slice_date(data,start_date,end_date,columns=None) :
    
# fonction permettant de découper le dataset en temps et en features
# argument year : prend une année entière
# columns : list contenant le noms des colonnes à extraire si vide prend toutes les colonnes

    if columns==None : 
        columns=data.columns
        
    if start_date==None :
        start_date=data.index[0]
        
    return data.loc[start_date : end_date][columns]

def data_timeplot(data,plot_per_line=5):
    
# focntion permettant de représenter les séries temporelles individuelles 
# pour chacune des colonnes du dataset passer en argument
# distribue les graphiques par défaut 5 par ligne


    paris=pytz.timezone('Europe/Paris')
    locator = AutoDateLocator()
    formatter=ConciseDateFormatter(locator,tz=paris)
    features=data.columns
    ppl=plot_per_line
   
    fig=plt.figure(figsize=(30,ppl*(len(features)-1)//ppl+ppl))
    
    for i,c in enumerate(features) :
        
        ax=fig.add_subplot((len(features)-1)/ppl+1,ppl,i+1)
        ax.plot_date(data.index,data[c],marker=None,linestyle='-');
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_tick_params(rotation=30, labelsize=10)
        ax.set_title(c,fontsize=10)