#trade from-to
import json
import inquirer
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
from binance.client import Client
from datetime import datetime

client = Client('API_KEY', 'API_SECRET')

trades = client.get_all_orders(symbol='BTCUSDT')
trades = json_normalize(trades)
trades['data'] = pd.to_datetime(trades['time'], unit='ms')
trades['updateTime'] = pd.to_datetime(trades['updateTime'], unit='ms')
trades = trades[['time','data','price','side','status']]
trades = trades[trades.status != 'CANCELED']
trades['price'] = trades['price'].astype(float)
trades['side'] = trades['side'].astype(str)
trades = trades.reset_index(drop=True)

column = pd.Series(index = range(0,len(trades)))

for i in range(len(trades)):
    if trades['side'][i] == 'SELL':
        column[i] = round((trades['price'][i] - trades['price'][i-1])*100/trades['price'][i-1],2)
    else:
        column[i] = '0'

trades['perc'] = column

print('Inserisci le date di inizio e fine (formato: gg.mm.aaaa hh:mm:ss)')
print('')
datainizio = input('Data inizio: ')
datain = datainizio
datafine = input('Data fine: ')
datafin = datafine

#datainizio
dt_obj = datetime.strptime(datainizio, 
                           '%d.%m.%Y %H:%M:%S,%f')
datainizio = dt_obj.timestamp() * 1000

#datafine
dt_obj = datetime.strptime(datafine, 
                           '%d.%m.%Y %H:%M:%S,%f')
datafine = dt_obj.timestamp() * 1000

trades.insert(5, 'compreso','null')

backtest = trades

compreso = pd.Series(index = range(0,len(backtest)))

for i in range(len(backtest)):
    if backtest['time'][i] > datainizio and backtest['time'][i] < datafine:
        compreso[i] = 'si'
    else: 
        compreso[i] = 'no'

backtest['compreso'] = compreso

backtest['perc']=backtest['perc'].astype(float)

range = backtest[backtest['compreso'] == 'si']
range = range.reset_index(drop=True)
range = range[['data','price','side','perc']]

profittotot = range['perc'].sum()
profittotot = '{} {}'.format(profittotot, '%')
numerooperazioni = len(range)

print('')
print('Il profitto totale dal {} al {} è: {}'.format(datain,datafin,profittotot))
print('Numero di operazioni: {}'.format(numerooperazioni))
print('')

questions = [
  inquirer.List('Excel',
                message="Do you want operations in Excel file?",
                choices=['Yes', 'No'],
            ),
]
excel = inquirer.prompt(questions)
excel = excel['Excel'] 

if excel == 'Yes':
	print('Excel file created')
	range.to_excel("TradeHistory.xlsx", engine='xlsxwriter')
else:
	print('No Excel file created')
