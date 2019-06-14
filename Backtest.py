#candele
import json
import numpy as np
import pandas as pd
import time
import ta
from binance.client import Client
from datetime import datetime
from pandas import DataFrame

client = Client('API_KEY', 'API_SECRET')

datainizio = input('Data inizio: ')
datain = datainizio
datafine = input('Data fine: ')
datafin = datafine

#datainizio
dt_obj = datetime.strptime(datainizio, 
                           '%d.%m.%Y %H:%M:%S,%f')
datainizio = dt_obj.timestamp()*1000
#datafine
dt_obj = datetime.strptime(datafine, 
                           '%d.%m.%Y %H:%M:%S,%f')
datafine = dt_obj.timestamp()*1000
datainizio = int(datainizio)
datafine = int(datafine)
klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_5MINUTE, datainizio, datafine)
tabella = DataFrame.from_records(klines)
tabella.columns = ['DateTime','Apertura','Massimo','Minimo','Chiusura','Volume(Asset)','DataChiusura','Volume($)','9','10','11','12']
tabella['DateTime'] = pd.to_datetime(tabella['DateTime'], unit='ms')
tabella['DataChiusura'] = pd.to_datetime(tabella['DataChiusura'], unit='ms')
tabella['Apertura'] = tabella['Apertura'].astype(float)
tabella['Massimo'] = tabella['Massimo'].astype(float)
tabella['Minimo'] = tabella['Minimo'].astype(float)
tabella['Chiusura'] = tabella['Chiusura'].astype(float)
tabella = tabella[['DateTime','Apertura','Massimo','Minimo','Chiusura','Volume(Asset)','Volume($)']]

#indicatori
print('')
print('Inserisci gli indicatori separati da virgola max(3)')
print('Indicatori disponibili: RSI, MACD, ADX')
print('Formato inserimento: separati da virgola, senza spazione nè prima nè dopo')
indicatori = input('Indicatori:')
indicatori_sep = indicatori.split(",")
n_indicatori = len(indicatori_sep)

if n_indicatori == 1:
    indicatore1 = indicatori_sep[0] 
elif n_indicatori == 2:
    indicatore1 = indicatori_sep[0] 
    indicatore2 = indicatori_sep[1] 
elif n_indicatori == 3:
    indicatore1 = indicatori_sep[0] 
    indicatore2 = indicatori_sep[1]
    indicatore3 = indicatori_sep[2] 
else: 
    print('Gli indicatori devono essere più di 0 e minori o uguali a 3')


if n_indicatori == 1: 
    if indicatore1 == 'RSI':
        tabella['RSI'] = ta.rsi(tabella['Chiusura'], 3)
    if indicatore1 == 'MACD':
        tabella['MACD'] = ta.trend.macd(tabella['Chiusura'], n_fast=12, n_slow=26, fillna=False)
    if indicatore1 == 'ADX':
        tabella['ADX'] = ta.trend.macd(tabella['Chiusura'], n_fast=12, n_slow=26, fillna=False)
    tabella['MediaVolumi'] = ta.utils.ema(tabella['Volume(Asset)'], 20)
    
if n_indicatori == 2: 
    if indicatore1 == 'RSI' or indicatore2 == 'RSI':
        tabella['RSI'] = ta.rsi(tabella['Chiusura'], n=3, fillna=False)
    if indicatore1 == 'MACD' or indicatore2 == 'MACD':
        tabella['MACD'] = ta.trend.macd(tabella['Chiusura'], n_fast=12, n_slow=26, fillna=False)
    if indicatore1 == 'ADX' or indicatore2 == 'ADX':
        tabella['ADX'] = ta.trend.macd(tabella['Chiusura'], n_fast=12, n_slow=26, fillna=False)
    tabella['MediaVolumi'] = ta.utils.ema(tabella['Volume(Asset)'], 20)
    
if n_indicatori == 3: 
    if indicatore1 == 'RSI' or indicatore2 == 'RSI' or indicatore3 == 'RSI':
        tabella['RSI'] = ta.rsi(tabella['Chiusura'], 3)
    if indicatore1 == 'MACD' or indicatore2 == 'MACD' or indicatore3 == 'MACD':
        tabella['MACD'] = ta.trend.macd(tabella['Chiusura'], n_fast=12, n_slow=26, fillna=False)
    if indicatore1 == 'ADX' or indicatore2 == 'ADX' or indicatore3 == 'ADX':
        tabella['ADX'] = ta.trend.macd(tabella['Chiusura'], n_fast=12, n_slow=26, fillna=False) 
    tabella['MediaVolumi'] = ta.utils.ema(tabella['Volume(Asset)'], 20)
    
tabella.insert(10,'Operazione','null')

print('')
valmacd = -5
#backtest
last_operation = 'Sell'
for i in range(len(tabella)):
    percentuale = round((i/len(tabella))*100, 2)
    float(percentuale)
    print('Percentuale di completamento: {} %'.format(percentuale), end='\r'),
    if last_operation  == 'Sell':
        if tabella['RSI'][i] < 5 and tabella['MACD'][i] > valmacd:
            tabella['Operazione'][i] = 'Buy'
            last_operation = 'Buy'
            action_price = tabella['Chiusura'][i]
        else:
            last_operation  = 'Sell'
            tabella['Operazione'][i] = 'Nessuna'
    elif last_operation  == 'Buy':
        if tabella['Chiusura'][i] > action_price*1.005 or tabella['Chiusura'][i] < (action_price - action_price*0.01):
            tabella['Operazione'][i] = 'Sell'
            last_operation = 'Sell'
            action_price = tabella['Chiusura'][i]
        else:
            last_operation  = 'Buy'
            tabella['Operazione'][i] = 'Nessuna' 
print('Percentuale di completamento: Completato', end='\r') 
print('')

#only operations
backtest = tabella[tabella['Operazione'] != 'Nessuna']
backtest.insert(11, 'Perc','0')
backtest = backtest.reset_index(drop=True)
backtest['Perc']=backtest['Perc'].astype(float)

#stats 
for i in range(1,len(backtest)):
    if backtest['Operazione'][i] == 'Sell':
        backtest['Perc'][i] = round(((backtest['Chiusura'][i] - backtest['Chiusura'][i-1])*100/backtest['Chiusura'][i-1])-0.2,2)
    else:
        backtest['Perc'][i] = '0'

print('')
numerooperazioni = len(backtest)
profittotot = backtest['Perc'].sum()
profittotot = '{} {}'.format(profittotot, '%')
print('Il profitto totale dal {} al {} è: {}'.format(datain,datafin,profittotot))
print('Numero di operazioni: {}'.format(numerooperazioni))
print('')
backtest
