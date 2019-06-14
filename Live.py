#candele
import json
import numpy as np
import pandas as pd
import time
import ta
from binance.enums import *
from binance.client import Client
from datetime import datetime
from pandas import DataFrame

client = Client('API_KEY', 'API_SECRET')

#indicatori
print('Inserisci gli indicatori separati da virgola (max = 3)')
print('Indicatori disponibili: RSI, MACD, ADX')
print('Formato inserimento: separati da virgola, senza spazione n prima n dopo')
indicatori = input('Indicatori:')
indicatori_sep = indicatori.split(',')
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
    print('Gli indicatori devono essere piu di 0 e minori o uguali a 3')

last_operation = 'Sell'

while True:
    if datetime.now().minute % 5 == 0 and datetime.now().second % 60 == 0: 
        klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_5MINUTE, '150 minutes ago UTC')
        tabella = DataFrame.from_records(klines)
        tabella.columns = ['DateTime','Apertura','Massimo','Minimo','Chiusura','Volume(Asset)','DataChiusura','Volume($)','9','10','11','12']
        tabella['DateTime'] = pd.to_datetime(tabella['DateTime'], unit='ms')
        tabella['DataChiusura'] = pd.to_datetime(tabella['DataChiusura'], unit='ms')
        tabella['Apertura'] = tabella['Apertura'].astype(float)
        tabella['Massimo'] = tabella['Massimo'].astype(float)
        tabella['Minimo'] = tabella['Minimo'].astype(float)
        tabella['Chiusura'] = tabella['Chiusura'].astype(float)
        tabella = tabella[['DateTime','Apertura','Massimo','Minimo','Chiusura','Volume(Asset)','Volume($)']]

        if n_indicatori == 1: 
            if indicatore1 == 'RSI':
                tabella['RSI'] = ta.rsi(tabella['Chiusura'], n=3)
            if indicatore1 == 'MACD':
                tabella['MACD'] = ta.trend.macd(tabella['Chiusura'], n_fast=12, n_slow=26, fillna=False)
            if indicatore1 == 'ADX':
                tabella['ADX'] = ta.trend.macd(tabella['Chiusura'], n_fast=12, n_slow=26, fillna=False)

        if n_indicatori == 2: 
            if indicatore1 == 'RSI' or indicatore2 == 'RSI':
                tabella['RSI'] = ta.rsi(tabella['Chiusura'], n=3)
            if indicatore1 == 'MACD' or indicatore2 == 'MACD':
                tabella['MACD'] = ta.trend.macd(tabella['Chiusura'], n_fast=12, n_slow=26, fillna=False)
            if indicatore1 == 'ADX' or indicatore2 == 'ADX':
                tabella['ADX'] = ta.trend.macd(tabella['Chiusura'], n_fast=12, n_slow=26, fillna=False)

        if n_indicatori == 3: 
            if indicatore1 == 'RSI' or indicatore2 == 'RSI' or indicatore3 == 'RSI':
                tabella['RSI'] = ta.rsi(tabella['Chiusura'], 3)
            if indicatore1 == 'MACD' or indicatore2 == 'MACD' or indicatore3 == 'MACD':
                tabella['MACD'] = ta.trend.macd(tabella['Chiusura'], n_fast=12, n_slow=26, fillna=False)
            if indicatore1 == 'ADX' or indicatore2 == 'ADX' or indicatore3 == 'ADX':
                tabella['ADX'] = ta.trend.macd(tabella['Chiusura'], n_fast=12, n_slow=26, fillna=False)
        
        tabella.insert(10,'Operazione','null')

        #live trading

        if last_operation  == 'Sell':
            if tabella['RSI'][28] < 100 and tabella['MACD'][28] > 0:
                tabella['Operazione'][28] = 'Buy'
                last_operation = 'Buy'
                action_price = tabella['Chiusura'][28]
            else:
                last_operation  = 'Sell'
                tabella['Operazione'][28] = 'Nessuna'
        elif last_operation  == 'Buy':
            if tabella['Chiusura'][28] > action_price*1.01 or tabella['Chiusura'][28] < (action_price - action_price*0.02):
                tabella['Operazione'][28] = 'Sell'
                last_operation = 'Sell'
                action_price = tabella['Chiusura'][28]
            else:
                last_operation  = 'Buy'
                tabella['Operazione'][28] = 'Nessuna' 
       
        ora = datetime.now().timestamp()
        ora = pd.to_datetime(ora, unit='s')
        print('Ora Calcolo: ', ora)
        #operazioni
        price = client.get_orderbook_tickers()
        prezzo = DataFrame.from_records(price)
        prezzo = prezzo[prezzo['symbol']=='BTCUSDT']
        buy = prezzo['askPrice']
        sell = prezzo['bidPrice']
        buy = float(buy)
        sell = float(sell)

        balanceasset= client.get_asset_balance(asset='USDT')
        balancecoin = client.get_asset_balance(asset='BTC')
        balanceUSDT = '20'
        balanceBTC = balancecoin['free']
        balanceUSDT = float(balanceUSDT)
        balanceBTC = float(balanceBTC)
        
        quantbuy = round((balanceUSDT-balanceUSDT*0.01)/buy, 6)
        quantsell = round((balanceBTC-balanceBTC*0.01)/sell, 6)

        if tabella['Operazione'][28] == 'Buy':
            print('RSI: ', tabella['RSI'][28])
            print('MACD: ', tabella['MACD'][28])
            print('ADX: ', tabella['ADX'][28])
            print('Price: ', tabella['Chiusura'][28])
            order = client.create_test_order(
            symbol='BTCUSDT',
            side=SIDE_BUY,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=quantbuy,
            price=buy)
            print('Buy Price: ', buy)
            print('Quantity: ', quantbuy)
            print('')

        elif tabella['Operazione'][28] == 'Sell':
            print('RSI: ', tabella['RSI'][28])
            print('MACD: ', tabella['MACD'][28])
            print('ADX: ', tabella['ADX'][28])
            print('Price: ', tabella['Chiusura'][28])
            order = client.create_test_order(
            symbol='BTCUSDT',
            side=SIDE_SELL,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=quantsell,
            price=sell)
            print('Sell Price: ', sell)
            print('Quantity: ', quantsell)
            print('')


        elif tabella['Operazione'][28] == 'Nessuna':
            print('RSI: ', tabella['RSI'][28])
            print('MACD: ', tabella['MACD'][28])
            print('ADX: ', tabella['ADX'][28])
            print('Price: ', tabella['Chiusura'][28])
            print('Nessuna operazione')
            print('Ultima Operazione: ', last_operation)
            print('')

        time.sleep(60)