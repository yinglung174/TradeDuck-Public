import sys
import importlib.util
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QPushButton, \
    QTableView, QLabel, QLineEdit, QHeaderView, QDateEdit, QListView, QFileDialog, QDialog, QStyledItemDelegate, \
    QRadioButton, QCheckBox, QComboBox, QButtonGroup, QGroupBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPalette, QColor, QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread, QDate, QAbstractListModel, QAbstractTableModel, QVariant
from PyQt5.QtMultimedia import QSound

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression

import numpy as np
import asyncio
import matplotlib.pyplot as plt
from io import BytesIO
import pandas_market_calendars as mcal
from futu import *
import time  as timemodule
import random
from datetime import datetime, timedelta, time
from decimal import Decimal, getcontext
from collections import defaultdict

import os
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import threading
import queue
import csv
import subprocess
import logging, pytz

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, Updater

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('Neverland')
file_handler = logging.FileHandler('app.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

api_key = 'Q4HS1CE7298ANN7M'

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

configurations = []
config_timeframe = "30min"
config_subtimeframe ="15min"
telegram_instant_sell = queue.Queue()
telegram_instant_array = []
telegram_pattern_array = []
config_path_extension = '_public'

# Open the file in read mode
with open("configuration.txt", "r") as file:
    for line in file:
        configurations.append(line.strip())
    if not configurations:
        for i in range(9):
            configurations.append("Allow")


def initializeIndicator():
    global ema_values_1
    ema_values_1 = 0.0
    for timestamp_ema, values_ema in ema.items():
        if timestamp_ema in time_1:
            ema_values_1 = float(values_ema['EMA'])
        for verify in verify_array:
            if timestamp_ema in verify[2]:
                verify[6] = float(values_ema['EMA'])
        if ema_values_1 != 0.0 and verify_array[11][6] != 0.0:
            break


def defineCandleSticksFUTU(data):
    global isLastGreen
    global isLastRed
    global isLast2Green
    global isLast2Red
    global lastUpperDistance
    global lastLowerDistance
    global lastOpen
    global lastClose
    global lastHigh
    global lastLow
    global last2Open
    global last2Close
    global last2High
    global last2Low
    global lastTime
    global lastEMA10
    global lastLargestDistance
    global last2LargestDistance
    global lastMiddleDistance
    global last2MiddleDistance
    global isLastLongBody
    global isLastShortBody
    global isLastUpperBody
    global isLastLowerBody
    global isLast2LongBody
    global isLast2ShortBody
    global isLast2UpperBody
    global isLast2LowerBody
    ema_10 = data['close'].ewm(span=5, adjust=False).mean()
    isLastGreen = False
    isLastRed = False
    isLastLongBody = False
    isLastShortBody = False
    isLastUpperBody = False
    isLastLowerBody = False
    lastOpen = 0
    lastClose = 0
    lastHigh = 0
    lastLow = 0
    last2Open = 0
    last2Close = 0
    last2High = 0
    last2Low = 0
    lastTime = data['time_key'][len(data) - 2]
    lastOpen = data['open'][len(data) - 2]
    lastClose = data['close'][len(data) - 2]
    lastHigh = data['high'][len(data) - 2]
    lastLow = data['low'][len(data) - 2]
    lastEMA10 = ema_10[len(data) - 2]
    lastLargestDistance = lastHigh - lastLow
    if (lastOpen < lastClose):
        isLastGreen = True
        lastMiddleDistance = lastClose - lastOpen
        lastUpperDistance = lastHigh - lastClose
        lastLowerDistance = lastOpen - lastLow
    else:
        isLastRed = True
        lastMiddleDistance = lastOpen - lastClose
        lastUpperDistance = lastHigh - lastOpen
        lastLowerDistance = lastClose - lastLow
    if (lastMiddleDistance > lastUpperDistance and lastMiddleDistance > lastLowerDistance):
        isLastLongBody = True
    elif (lastMiddleDistance < lastUpperDistance and lastMiddleDistance < lastLowerDistance):
        isLastShortBody = True
    elif (lastMiddleDistance > lastUpperDistance and lastMiddleDistance < lastLowerDistance):
        isLastUpperBody = True
    elif (lastMiddleDistance < lastUpperDistance and lastMiddleDistance > lastLowerDistance):
        isLastLowerBody = True

def defineCandleSticksFUTUMini(data):
    global isLastGreen
    global isLastRed
    global isLast2Green
    global isLast2Red
    global lastUpperDistance
    global lastLowerDistance
    global lastOpen
    global lastClose
    global lastHigh
    global lastLow
    global last2Open
    global last2Close
    global last2High
    global last2Low
    global lastTime
    global lastEMA10
    global lastLargestDistance
    global last2LargestDistance
    global lastMiddleDistance
    global last2MiddleDistance
    global isLastLongBody
    global isLastShortBody
    global isLastUpperBody
    global isLastLowerBody
    global isLast2LongBody
    global isLast2ShortBody
    global isLast2UpperBody
    global isLast2LowerBody
    ema_10 = data['close'].ewm(span=5, adjust=False).mean()
    isLastGreen = False
    isLastRed = False
    isLast2Green = False
    isLast2Red = False
    isLastLongBody = False
    isLastShortBody = False
    isLastUpperBody = False
    isLastLowerBody = False
    isLast2LongBody = False
    isLast2ShortBody = False
    isLast2UpperBody = False
    isLast2LowerBody = False
    lastUpperDistance = 0
    lastLowerDistance = 0
    last2UpperDistance = 0
    last2LowerDistance = 0
    lastOpen = 0
    lastClose = 0
    lastHigh = 0
    lastLow = 0
    last2Open = 0
    last2Close = 0
    last2High = 0
    last2Low = 0
    lastTime = data['time_key'][len(data) - 2]
    lastOpen = data['open'][len(data) - 2]
    lastClose = data['close'][len(data) - 2]
    lastHigh = data['high'][len(data) - 2]
    lastLow = data['low'][len(data) - 2]
    lastEMA10 = ema_10[len(data) - 2]
    lastLargestDistance = lastHigh - lastLow
    if (lastOpen < lastClose):
        isLastGreen = True
        lastMiddleDistance = lastClose - lastOpen
        lastUpperDistance = lastHigh - lastClose
        lastLowerDistance = lastOpen - lastLow
    else:
        isLastRed = True
        lastMiddleDistance = lastOpen - lastClose
        lastUpperDistance = lastHigh - lastOpen
        lastLowerDistance = lastClose - lastLow
    if (lastMiddleDistance > lastUpperDistance and lastMiddleDistance > lastLowerDistance):
        isLastLongBody = True
    elif (lastMiddleDistance < lastUpperDistance and lastMiddleDistance < lastLowerDistance):
        isLastShortBody = True
    elif (lastMiddleDistance > lastUpperDistance and lastMiddleDistance < lastLowerDistance):
        isLastUpperBody = True
    elif (lastMiddleDistance < lastUpperDistance and lastMiddleDistance > lastLowerDistance):
        isLastLowerBody = True
    if "09:45:00" not in data['time_key'][len(data) - 2]:
        last2Open = data['open'][len(data) - 3]
        last2Close = data['close'][len(data) - 3]
        last2High = data['high'][len(data) - 3]
        last2Low = data['low'][len(data) - 3]
        last2LargestDistance = lastHigh - lastLow
        if (last2Open < last2Close):
            isLast2Green = True
            last2MiddleDistance = last2Close - last2Open
            last2UpperDistance = last2High - last2Close
            last2LowerDistance = last2Open - last2Low
        else:
            isLast2Red = True
            last2MiddleDistance = last2Open - last2Close
            last2UpperDistance = last2High - last2Open
            last2LowerDistance = last2Close - last2Low
        if (last2MiddleDistance > last2UpperDistance and last2MiddleDistance > last2LowerDistance):
            isLast2LongBody = True
        elif (last2MiddleDistance < last2UpperDistance and last2MiddleDistance < last2LowerDistance):
            isLast2ShortBody = True
        elif (last2MiddleDistance > last2UpperDistance and last2MiddleDistance < last2LowerDistance):
            isLast2UpperBody = True
        elif (last2MiddleDistance < last2UpperDistance and last2MiddleDistance > last2LowerDistance):
            isLast2LowerBody = True

def callBuyConditionFUTU(data):
    global isBuySignal
    global buyPattern
    # price pattern (color > self distance > compare)
    isBuySignal = False
    buyPattern = "None"
    a = "Null"
    c = "Null"
    if isLastLongBody == True:
        a = "Long"
    elif isLastShortBody == True:
        a = "Short"
    elif isLastUpperBody == True:
        a = "Upper"
    elif isLastLowerBody == True:
        a = "Bottom"
    if isLastGreen == True:
        c = "Green"
    elif isLastRed == True:
        c = "Red"
    buyPattern = "-".join([a, c])
    if "Null" not in buyPattern and "10:00" in lastTime and isBuySignal == False:
        isBuySignal = True

def callBuyConditionFUTUMini(data):
    global isBuySignalMini
    global buyPatternMini
    # price pattern (color > self distance > compare)
    a = "Null"
    b = "Null"
    c = "Null"
    d = "Null"
    if isLastLongBody == True:
        a = "Long"
    elif isLastShortBody == True:
        a = "Short"
    elif isLastUpperBody == True:
        a = "Upper"
    elif isLastLowerBody == True:
        a = "Bottom"
    if isLast2LongBody == True:
        b = "Long"
    elif isLast2ShortBody == True:
        b = "Short"
    elif isLast2UpperBody == True:
        b = "Upper"
    elif isLast2LowerBody == True:
        b = "Bottom"
    if isLastGreen == True:
        c = "Green"
    elif isLastRed == True:
        c = "Red"
    if isLast2Green == True:
        d = "Green"
    elif isLast2Red == True:
        d = "Red"
    buyPatternMini = "-".join([a, b, c, d])
    if "Null" not in buyPatternMini and "10:00" in lastTime and isBuySignalMini == False:
        isBuySignalMini = True


def defineCandleSticks(i):
    global isLastGreen
    global isLastRed
    global isLast2Green
    global isLast2Red
    global lastUpperDistance
    global lastLowerDistance
    global last2UpperDistance
    global last2LowerDistance
    global lastOpen
    global lastClose
    global lastHigh
    global lastLow
    global last2Open
    global last2Close
    global last2High
    global last2Low
    global lastTime
    global lastEMA10
    global lastLargestDistance
    global last2LargestDistance
    global lastMiddleDistance
    global last2MiddleDistance
    global isLastLongBody
    global isLastShortBody
    global isLastUpperBody
    global isLastLowerBody
    global isLast2LongBody
    global isLast2ShortBody
    global isLast2UpperBody
    global isLast2LowerBody

    isLastGreen = False
    isLastRed = False
    isLast2Green = False
    isLast2Red = False
    isLastLongBody = False
    isLastShortBody = False
    isLastUpperBody = False
    isLastLowerBody = False
    isLast2LongBody = False
    isLast2ShortBody = False
    isLast2UpperBody = False
    isLast2LowerBody = False
    lastUpperDistance = 0
    lastLowerDistance = 0
    last2UpperDistance = 0
    last2LowerDistance = 0
    lastOpen = 0
    lastClose = 0
    lastHigh = 0
    lastLow = 0
    last2Open = 0
    last2Close = 0
    last2High = 0
    last2Low = 0
    lastTime = verify_array[i][0]
    lastOpen = float(verify_array[i][9])
    lastClose = float(verify_array[i][1])
    lastHigh = float(verify_array[i][5])
    lastLow = float(verify_array[i][3])
    lastEMA10 = float(verify_array[i][8])
    lastLargestDistance = lastHigh - lastLow
    if (float(verify_array[i][9]) < float(verify_array[i][1])):
        isLastGreen = True
        lastMiddleDistance = float(verify_array[i][1]) - float(verify_array[i][9])
        lastUpperDistance = float(verify_array[i][5]) - float(verify_array[i][1])
        lastLowerDistance = float(verify_array[i][9]) - float(verify_array[i][3])
    else:
        isLastRed = True
        lastMiddleDistance = float(verify_array[i][9]) - float(verify_array[i][1])
        lastUpperDistance = float(verify_array[i][5]) - float(verify_array[i][9])
        lastLowerDistance = float(verify_array[i][1]) - float(verify_array[i][3])
    if (lastMiddleDistance > lastUpperDistance and lastMiddleDistance > lastLowerDistance):
        isLastLongBody = True
    elif (lastMiddleDistance < lastUpperDistance and lastMiddleDistance < lastLowerDistance):
        isLastShortBody = True
    elif (lastMiddleDistance > lastUpperDistance and lastMiddleDistance < lastLowerDistance):
        isLastUpperBody = True
    elif (lastMiddleDistance < lastUpperDistance and lastMiddleDistance > lastLowerDistance):
        isLastLowerBody = True
    if i - 1 >= 0:
        last2Open = float(verify_array[i - 1][9])
        last2Close = float(verify_array[i - 1][1])
        last2High = float(verify_array[i - 1][5])
        last2Low = float(verify_array[i - 1][3])
        last2LargestDistance = lastHigh - lastLow
        if (float(verify_array[i - 1][9]) < float(verify_array[i - 1][1])):
            isLast2Green = True
            last2MiddleDistance = float(verify_array[i - 1][1]) - float(
                verify_array[i - 1][9])
            last2UpperDistance = float(verify_array[i - 1][5]) - float(
                verify_array[i - 1][1])
            last2LowerDistance = float(verify_array[i - 1][9]) - float(
                verify_array[i - 1][3])
        else:
            isLast2Red = True
            last2MiddleDistance = float(verify_array[i - 1][9]) - float(
                verify_array[i - 1][1])
            last2UpperDistance = float(verify_array[i - 1][5]) - float(
                verify_array[i - 1][9])
            last2LowerDistance = float(verify_array[i - 1][1]) - float(
                verify_array[i - 1][3])
        if (last2MiddleDistance > last2UpperDistance and last2MiddleDistance > last2LowerDistance):
            isLast2LongBody = True
        elif (last2MiddleDistance < last2UpperDistance and last2MiddleDistance < last2LowerDistance):
            isLast2ShortBody = True
        elif (last2MiddleDistance > last2UpperDistance and last2MiddleDistance < last2LowerDistance):
            isLast2UpperBody = True
        elif (last2MiddleDistance < last2UpperDistance and last2MiddleDistance > last2LowerDistance):
            isLast2LowerBody = True


def callBuyCondition(i):
    global isBuySignal
    global buyPattern
    # price pattern (color > self distance > compare)
    isBuySignal = False
    buyPattern = "None"
    a = "Null"
    c = "Null"
    if isLastLongBody == True:
        a = "Long"
    elif isLastShortBody == True:
        a = "Short"
    elif isLastUpperBody == True:
        a = "Upper"
    elif isLastLowerBody == True:
        a = "Bottom"
    if isLastGreen == True:
        c = "Green"
    elif isLastRed == True:
        c = "Red"
    buyPattern = "-".join([a, c])
    if "Null" not in buyPattern and "09:30" in lastTime and isBuySignal == False:
        isBuySignal = True


def defineCandleSticksMini(i):
    global isLastGreen
    global isLastRed
    global isLast2Green
    global isLast2Red

    global lastUpperDistance
    global lastLowerDistance
    global last2UpperDistance
    global last2LowerDistance

    global lastOpen
    global lastClose
    global lastHigh
    global lastLow
    global last2Open
    global last2Close
    global last2High
    global last2Low

    global lastTime2
    global lastLargestDistance
    global last2LargestDistance

    global lastMiddleDistance
    global last2MiddleDistance

    global isLastLongBody
    global isLastShortBody
    global isLastUpperBody
    global isLastLowerBody
    global isLast2LongBody
    global isLast2ShortBody
    global isLast2UpperBody
    global isLast2LowerBody

    isLastGreen = False
    isLastRed = False
    isLast2Green = False
    isLast2Red = False
    isLastLongBody = False
    isLastShortBody = False
    isLastUpperBody = False
    isLastLowerBody = False
    isLast2LongBody = False
    isLast2ShortBody = False
    isLast2UpperBody = False
    isLast2LowerBody = False
    lastUpperDistance = 0
    lastLowerDistance = 0
    last2UpperDistance = 0
    last2LowerDistance = 0
    lastOpen = 0
    lastClose = 0
    lastHigh = 0
    lastLow = 0
    last2Open = 0
    last2Close = 0
    last2High = 0
    last2Low = 0
    lastTime2 = time_7
    lastOpen = price_7_open
    lastClose = price_7
    lastHigh = price_7_high
    lastLow = price_7_low
    lastLargestDistance = lastHigh - lastLow
    if (lastOpen < lastClose):
        isLastGreen = True
        lastMiddleDistance = lastClose - lastOpen
        lastUpperDistance = lastHigh - lastClose
        lastLowerDistance = lastOpen - lastLow
    else:
        isLastRed = True
        lastMiddleDistance = lastOpen - lastClose
        lastUpperDistance = lastHigh - lastOpen
        lastLowerDistance = lastClose - lastLow
    if (lastMiddleDistance > lastUpperDistance and lastMiddleDistance > lastLowerDistance):
        isLastLongBody = True
    elif (lastMiddleDistance < lastUpperDistance and lastMiddleDistance < lastLowerDistance):
        isLastShortBody = True
    elif (lastMiddleDistance > lastUpperDistance and lastMiddleDistance < lastLowerDistance):
        isLastUpperBody = True
    elif (lastMiddleDistance < lastUpperDistance and lastMiddleDistance > lastLowerDistance):
        isLastLowerBody = True
    if i - 1 >= 0:
        last2Open = price_6_open
        last2Close = price_6
        last2High = price_6_high
        last2Low = price_6_low
        last2LargestDistance = last2High - last2Low
        if (last2Open < last2Close):
            isLast2Green = True
            last2MiddleDistance = last2Close - last2Open
            last2UpperDistance = last2High - last2Close
            last2LowerDistance = last2Open - last2Low
        else:
            isLast2Red = True
            last2MiddleDistance = last2Open - last2Close
            last2UpperDistance = last2High - last2Open
            last2LowerDistance = last2Close - last2Low
        if (last2MiddleDistance > last2UpperDistance and last2MiddleDistance > last2LowerDistance):
            isLast2LongBody = True
        elif (last2MiddleDistance < last2UpperDistance and last2MiddleDistance < last2LowerDistance):
            isLast2ShortBody = True
        elif (last2MiddleDistance > last2UpperDistance and last2MiddleDistance < last2LowerDistance):
            isLast2UpperBody = True
        elif (last2MiddleDistance < last2UpperDistance and last2MiddleDistance > last2LowerDistance):
            isLast2LowerBody = True


def callBuyConditionMini(i):
    global isBuySignalMini
    global buyPatternMini
    # price pattern (color > self distance > compare)
    isBuySignalMini = False
    buyPatternMini = "None"
    if i - 1 >= 0:
        a = "Null"
        b = "Null"
        c = "Null"
        d = "Null"
        if isLastLongBody == True:
            a = "Long"
        elif isLastShortBody == True:
            a = "Short"
        elif isLastUpperBody == True:
            a = "Upper"
        elif isLastLowerBody == True:
            a = "Bottom"
        if isLast2LongBody == True:
            b = "Long"
        elif isLast2ShortBody == True:
            b = "Short"
        elif isLast2UpperBody == True:
            b = "Upper"
        elif isLast2LowerBody == True:
            b = "Bottom"
        if isLastGreen == True:
            c = "Green"
        elif isLastRed == True:
            c = "Red"
        if isLast2Green == True:
            d = "Green"
        elif isLast2Red == True:
            d = "Red"
        buyPatternMini = "-".join([a, b, c, d])
        if "Null" not in buyPatternMini and "09:45" in lastTime2 and isBuySignalMini == False:
            isBuySignalMini = True


def callSellCondition(i):
    global isSellSignal
    global sellPattern

    isSellSignal = False
    sellPattern = "None"
    a = "Null"
    c = "Null"
    if isLastLongBody == True:
        a = "Long"
    elif isLastShortBody == True:
        a = "Short"
    elif isLastUpperBody == True:
        a = "Upper"
    elif isLastLowerBody == True:
        a = "Bottom"
    if isLastGreen == True:
        c = "Green"
    elif isLastRed == True:
        c = "Red"
    sellPattern = "-".join([a, c])
    if "10:00" in lastTime and isSellSignal == False:
        isSellSignal = True

def backtestData(month, model):
    global ema
    global sma_daily
    global sma_daily_10
    global sma_daily_20
    global time_series_daily
    global time_1
    global verify_array
    global array_overall
    global isBuySignal
    global buyPattern
    global isBuySignalMini
    global buyPatternMini
    global price_6
    global price_6_open
    global price_6_high
    global price_6_low
    global time_7
    global price_7
    global price_7_open
    global price_7_high
    global price_7_low

    with lock:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&month={month}&symbol={symbol}&interval=30min&outputsize=full&apikey={api_key}&entitlement=delayed"
        response = session.get(url)

        url6 = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&month={month}&symbol={symbol}&interval=15min&outputsize=full&apikey={api_key}&entitlement=delayed"
        response_6 = session.get(url6)

        url_ema = f"https://www.alphavantage.co/query?function=EMA&symbol={symbol}&month={month}&interval=30min&time_period=5&series_type=close&apikey={api_key}&entitlement=delayed"
        response_4 = session.get(url_ema)

        if response.status_code == 200:
            data_15 = response_6.json()
            data = response.json()
            data_ema = response_4.json()
            time_series = data['Time Series (30min)']
            time_series_15 = data_15['Time Series (15min)']
            ema = data_ema['Technical Analysis: EMA']
            is3DailySMATrend = False
            isVersionTwo = False
            time_1 = ""
            verify_array = []
            verify_array_format = "00"
            num_of_minute = 12
            row = [f'09:30:00', 0.0, '', 0.0, 0.0, 0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0,
                   0.0]
            verify_array.append(row)
            hours = 10
            for i in range(num_of_minute):
                if int(verify_array_format) == 60:
                    hours = hours + 1
                    verify_array_format = "00"
                row = [f'{hours}:{verify_array_format}:00', 0.0, '', 0.0, 0.0, 0.0, 0.0, 0.0,
                       0.0, 0.0, 0.0, 0.0,
                       0.0]  # time, closed, date, low, SMA-5, high, EMA-5, SMA-10, EMA-10, open, macd, rsi, SMA-20
                verify_array.append(row)
                verify_array_format = int(verify_array_format) + 30
            total_chance = 0
            total_bingo_chance = 0
            array_csv = []

            for timestamp, values in time_series.items():
                every_trade_chance = -1
                if "09:00:00" in timestamp:
                    # print(f"{timestamp} : {values['4. close']}")
                    price_1 = float(values['4. close'])
                    price_1_low = float(values['3. low'])
                    price_1_high = float(values['2. high'])
                    time_1 = timestamp
                    if verify_array[11][1] != 0.0 and price_1 != 0.0:
                        initializeIndicator()
                        if True:  # condition 1
                            # if False:
                            isBuySignal = False
                            isBuySignalMini = False
                            buyAlready = False
                            buyPattern = ""
                            buyPatternMini = ""
                            price_6 = 0.0
                            price_6_low = 0.0
                            price_6_high = 0.0
                            price_6_open = 0.0
                            price_7 = 0.0
                            price_7_low = 0.0
                            price_7_high = 0.0
                            price_7_open = 0.0
                            time_6 = ""
                            time_7 = ""
                            date30 = time_1[:10]
                            for m in range(len(verify_array)):
                                if m > 0:
                                    this_min_date = verify_array[m][2][:10]
                                    before_min_date = verify_array[m - 1][2][:10]
                                    if this_min_date != before_min_date:
                                        verify_array[m][1] = verify_array[m - 1][9]
                                        datetime_obj = datetime.strptime(verify_array[m - 1][2], '%Y-%m-%d %H:%M:%S')
                                        next_minute = datetime_obj + timedelta(minutes=30)
                                        next_minute_str = next_minute.strftime('%Y-%m-%d %H:%M:%S')
                                        verify_array[m][2] = next_minute_str
                                        verify_array[m][3] = verify_array[m - 1][9]
                                        verify_array[m][5] = verify_array[m - 1][9]
                                        verify_array[m][9] = verify_array[m - 1][9]
                                        verify_array[m][4] = verify_array[m - 1][4]
                                        verify_array[m][6] = verify_array[m - 1][6]
                                        verify_array[m][7] = verify_array[m - 1][7]
                                        verify_array[m][8] = verify_array[m - 1][8]
                                        verify_array[m][12] = verify_array[m - 1][12]

                            for i in range(len(verify_array)):  # start adding buy condition
                                defineCandleSticks(i)
                                callBuyCondition(i)
                                if isBuySignal == True and buyAlready == False and "09" in lastTime:
                                    for timestamp15, values15 in time_series_15.items():
                                        if price_6 != 0.0 and price_7 != 0.0:
                                            defineCandleSticksMini(1)
                                            callBuyConditionMini(1)
                                            if isBuySignalMini == True:
                                                print(f"{time_6} : {price_6}")
                                                break
                                        if f"{date30} 09:30:00" in timestamp15:
                                            price_6_open = float(values15['1. open'])
                                            time_6 = timestamp15
                                            price_6_low = float(values15['3. low'])
                                            price_6_high = float(values15['2. high'])
                                            price_6 = float(values15['4. close'])
                                        if f"{date30} 09:45:00" in timestamp15:
                                            price_7_open = float(values15['1. open'])
                                            time_7 = timestamp15
                                            price_7_low = float(values15['3. low'])
                                            price_7_high = float(values15['2. high'])
                                            price_7 = float(values15['4. close'])
                                    print(f"{time_1} : {price_1_low}")
                                    print(
                                        f"{verify_array[i][2]} : {lastClose} - CALL BUY Signal, Pattern: {buyPattern}")
                                    model.add_output(
                                        f"{verify_array[i][2]} : {lastClose} - CALL BUY Signal, Pattern: {buyPattern}")
                                    ema_10_time = 'None'
                                    ema_10_earn = 0.0
                                    is_sell_ema_10 = 0
                                    highest_sell_time = 'None'
                                    highest_sell_earn = 0.0
                                    sell_time = 'None'
                                    sell_price = 0.0
                                    trigger_sell_time = 'None'
                                    trigger_sell_price = 0.0
                                    price_action_earn = 0.0
                                    is_sell_price_action = 0
                                    k = 2
                                    chance_bingo = 0
                                    chance_bingo_correct = 0
                                    buyAlready = True
                                    for j in range(len(verify_array) - 2 - i):
                                        if is_sell_price_action == 0:
                                            defineCandleSticks(k + i - 1)
                                            callSellCondition(k + i - 1)
                                        print(f"{verify_array[k + i][2]} : {verify_array[k + i][9]}")
                                        model.add_output(f"{verify_array[k + i][2]} : {verify_array[k + i][9]}")
                                        if isSellSignal == True and is_sell_price_action == 0 and is_sell_ema_10 == 0 and buyAlready == True:
                                            print(f"SELL BUY Signal, Pattern: {sellPattern}")
                                            model.add_output(f"SELL BUY Signal, Pattern: {sellPattern}")
                                            sell_time = verify_array[i + k][0]
                                            sell_price = verify_array[i + k][9]
                                            price_action_earn = (verify_array[i + k][9] - verify_array[i + 1][9]) / \
                                                                verify_array[i + k][9] * 100
                                            # buyAlready = False
                                            is_sell_price_action = 1
                                            if float(verify_array[i + k][9]) > float(verify_array[i + 1][9]):
                                                every_trade_chance = 1
                                            else:
                                                every_trade_chance = 0
                                        if float(verify_array[i + k][6]) > float(verify_array[i + k][1]) and float(
                                                verify_array[i + k][9]) > float(
                                            verify_array[i + k][1]) and is_sell_ema_10 == 0 and buyAlready == True:
                                            print(f"Sell CALL! (EMA-5 Method)")  # sell method 3
                                            model.add_output(f"Sell CALL! (EMA-5 Method)")
                                            ema_10_time = verify_array[i + k][0]
                                            ema_10_earn = (verify_array[i + k][9] - verify_array[i + 1][9]) / \
                                                          verify_array[i + k][9] * 100
                                            is_sell_ema_10 = 1
                                            if is_sell_price_action == 0:
                                                if float(verify_array[i + k][9]) > float(
                                                        verify_array[i + 1][9]):
                                                    every_trade_chance = 1
                                                else:
                                                    every_trade_chance = 0
                                            buyAlready = False
                                        if (highest_sell_earn < float(verify_array[i + k][9]) - float(
                                                verify_array[i + 1][9])):
                                            highest_sell_time = verify_array[i + k][0]
                                            highest_sell_earn = (verify_array[i + k][9] - verify_array[i + 1][9]) / \
                                                                verify_array[i + k][9] * 100
                                        chance_bingo = chance_bingo + 1
                                        k = k + 1
                                    if (highest_sell_earn < verify_array[len(verify_array) - 1][9] - float(
                                            verify_array[i + 1][9])):
                                        highest_sell_time = verify_array[len(verify_array) - 1][0]
                                        highest_sell_earn = (verify_array[len(verify_array) - 1][9] -
                                                             verify_array[i + 1][9]) / \
                                                            verify_array[len(verify_array) - 1][9] * 100
                                    if is_sell_ema_10 == 0:
                                        ema_10_time = verify_array[len(verify_array) - 1][0]
                                        ema_10_earn = (verify_array[len(verify_array) - 1][9] - verify_array[i + 1][
                                            9]) / verify_array[len(verify_array) - 1][9] * 100
                                        if float(verify_array[len(verify_array) - 1][9]) > float(
                                                verify_array[i + 1][9]):
                                            every_trade_chance = 1
                                        else:
                                            every_trade_chance = 0
                                    print("Increasing Direction")
                                    print("Total Chance of Trigger Bingo Rise:")
                                    model.add_output("Increasing Direction")
                                    model.add_output("Total Chance of Trigger Bingo Rise:")
                                    print(every_trade_chance)
                                    model.add_output(every_trade_chance)
                                    total_bingo_chance = total_bingo_chance + chance_bingo_correct
                                    total_chance = total_chance + chance_bingo
                                    row = [verify_array[i][2].split(' ')[0],
                                           verify_array[i + 1][0],
                                           verify_array[i + 1][9], buyPattern, buyPatternMini,
                                           sell_time, sell_price, f"{price_action_earn:.5g}", sellPattern,
                                           f"{every_trade_chance:.5g}", ema_10_time,
                                           f"{ema_10_earn:.5g}", highest_sell_time,
                                           f"{highest_sell_earn:.5g}"]
                                    array_csv.append(row)
                                    print("--------------")
                                    model.add_output("--------------")
                                    break
                for verify in verify_array:
                    if verify[0] in timestamp:
                        verify[9] = float(values['1. open'])
                        verify[2] = timestamp
                        verify[3] = float(values['3. low'])
                        verify[5] = float(values['2. high'])
                        verify[1] = float(values['4. close'])

            array_overall = array_overall + array_csv
            print("Monthly Total Chance of Trigger Bingo:")
            monthly_trade_chance = 0
            if total_chance != 0:
                monthly_trade_chance = total_bingo_chance / total_chance
            print(monthly_trade_chance)
            model.add_output("Monthly Total Chance of Trigger Bingo:")
            model.add_output(monthly_trade_chance)
        else:
            print(f"Error: {response.status_code} - {response.text}")
            model.add_output(f"Error: {response.status_code} - {response.text}")


def execute_backtest(input_symbol, model):
    global lock
    global symbol
    global array_overall
    global array_month
    global session
    global bt_array

    symbol = input_symbol

    current_date = QDate.currentDate().toString("yyyy-MM-dd")
    current_date_obj = QDate.fromString(current_date, 'yyyy-MM-dd')
    array_month = []
    for i in range(60):
        month = current_date_obj.addMonths(-i)
        month_str = month.toString('yyyy-MM')
        array_month.append(month_str)

    array_month.reverse()

    array_overall = []

    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504]
    )

    adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=retry_strategy)

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    lock = threading.Lock()

    threads = []
    for month in array_month:
        thread = threading.Thread(target=backtestData, args=(month, model))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    if len(array_overall) != 0:
        file_path = f'data/history{config_path_extension}/{symbol}.csv'
        header = ['Date', 'BUY Time',
                  'BUY Price', 'BUY Pattern', 'BUY Pattern 2', 'SELL Time', 'SELL Price', 'SELL Earning(%)',
                  'SELL Pattern',
                  'Num of Chance', 'EMA-5 Sell Time', 'EMA-5 Earning(%)', 'Highest Sell Time', 'Highest Earning(%)']
        bt_array = np.vstack([header, array_overall])
        np.savetxt(file_path, bt_array, delimiter=',', fmt='%s')
        print(f"Array exported to {file_path} successfully.")
        model.add_output(f"Array exported to {file_path} successfully.")
    else:
        print(f"No Data Updated.")
        model.add_output(f"No Data Updated.")


def handleData(given_date,name_symbol):
    global highest_method
    global average_chance
    global earning_probability
    global earning_probability_pa
    global chance_set
    global chance_values
    global sellWinPA_set
    global sellLostPA_set
    global sellWinEMA_set
    global sellLostEMA_set
    global sellWinH_set
    global sellLostH_set
    global numPattern_set
    global chance_set_2
    global chance_values_2
    global sellWinPA_set_2
    global sellLostPA_set_2
    global sellWinEMA_set_2
    global sellLostEMA_set_2
    global sellWinH_set_2
    global sellLostH_set_2
    global numPattern_set_2

    rawHistoricalData = pd.read_csv(f'{folder_path}/{name_symbol}.csv')
    historicalData = rawHistoricalData[rawHistoricalData['Date'] < given_date]
    average_chance = historicalData.iloc[:, 9].mean()
    sum_of_sma = historicalData.iloc[:, 11].sum()
    sum_of_sma_10 = historicalData.iloc[:, 11].sum()
    sum_of_ema = historicalData.iloc[:, 11].sum()
    highest_number = max(sum_of_sma, sum_of_sma_10, sum_of_ema)
    highest_method = ''
    total = len(historicalData)
    if highest_number == sum_of_sma:
        highest_method = 'EMA-5'
        count = len(historicalData[historicalData['EMA-5 Earning(%)'] < 0])
    elif highest_number == sum_of_sma_10:
        highest_method = 'EMA-5'
        count = len(historicalData[historicalData['EMA-5 Earning(%)'] < 0])
    elif highest_number == sum_of_ema:
        highest_method = 'EMA-5'
        count = len(historicalData[historicalData['EMA-5 Earning(%)'] < 0])
    else:
        highest_method = 'EMA-5'
        count = len(historicalData[historicalData['EMA-5 Earning(%)'] < 0])
    earning_probability = count / total
    earning_probability_pa = len(historicalData[historicalData['SELL Earning(%)'] < 0]) / total
    chances_price_actions = defaultdict(list)
    for index, row in historicalData.iterrows():
        chance = row[9]
        type_val = row[3]
        chances_price_actions[type_val].append(chance)
    average_chances_price_actions = {}
    for type_val, chances in chances_price_actions.items():
        if chances:
            average_chances_price_actions[type_val] = sum(chances) / len(chances)
        else:
            average_chances_price_actions[type_val] = 0
    a = ["Long", "Short", "Upper", "Bottom"]
    b = ["Long", "Short", "Upper", "Bottom"]
    c = ["Green", "Red"]
    d = ["Green", "Red"]
    chance_set = []
    chance_values = []
    sellWinPA_set = []
    sellLostPA_set = []
    sellWinEMA_set = []
    sellLostEMA_set = []
    sellWinH_set = []
    sellLostH_set = []
    numPattern_set = []
    for i in range(len(a)):
        for k in range(len(c)):
            combined_string = "-".join([a[i], c[k]])
            chance_set.append(combined_string)
            chance_values.append(0)
    for n in range(len(chance_set)):
        for type_val in average_chances_price_actions:
            if (chance_set[n] == type_val):
                chance_values[n] = average_chances_price_actions.get(type_val, 0)
                telegram_pattern_array.append([chance_set[n], chance_values[n]])
                abstracted_string = ''.join(word[0] for word in type_val.split('-'))
                handlePattern(name_symbol, abstracted_string,given_date)
                sellWinPA_set.append(numSellWinTimePA)
                sellLostPA_set.append(numSellLostTimePA)
                sellWinEMA_set.append(numSellWinTimeEMA)
                sellLostEMA_set.append(numSellLostTimeEMA)
                sellWinH_set.append(numSellWinTimeH)
                sellLostH_set.append(numSellLostTimeH)
                numPattern_set.append(numPattern)

    chances_price_actions_2 = defaultdict(list)
    for index, row in historicalData.iterrows():
        chance = row[9]
        type_val = row[4]
        if not pd.isnull(type_val):
            chances_price_actions_2[type_val].append(chance)
    average_chances_price_actions_2 = {}
    for type_val, chances in chances_price_actions_2.items():
        if chances:
            average_chances_price_actions_2[type_val] = sum(chances) / len(chances)
        else:
            average_chances_price_actions_2[type_val] = 0
    chance_set_2 = []
    chance_values_2 = []
    sellWinPA_set_2 = []
    sellLostPA_set_2 = []
    sellWinEMA_set_2 = []
    sellLostEMA_set_2 = []
    sellWinH_set_2 = []
    sellLostH_set_2 = []
    numPattern_set_2 = []
    for i in range(len(a)):
        for j in range(len(b)):
            for k in range(len(c)):
                for l in range(len(d)):
                    combined_string = "-".join([a[i], b[j], c[k], d[l]])
                    chance_set_2.append(combined_string)
                    chance_values_2.append(0)
                    sellWinPA_set_2.append(0)
                    sellLostPA_set_2.append(0)
                    sellWinEMA_set_2.append(0)
                    sellLostEMA_set_2.append(0)
                    sellWinH_set_2.append(0)
                    sellLostH_set_2.append(0)
                    numPattern_set_2.append(0)

    for n in range(len(chance_set_2)):
        for type_val in average_chances_price_actions_2:
            if (chance_set_2[n] == type_val and 'Null' not in type_val):
                chance_values_2[n] = average_chances_price_actions_2.get(type_val, 0)
                telegram_pattern_array.append([chance_set_2[n], chance_values_2[n]])
                abstracted_string = ''.join(word[0] for word in type_val.split('-'))
                handlePatternMini(name_symbol, abstracted_string,given_date)
                sellWinPA_set_2[n] = numSellWinTimePAMini
                sellLostPA_set_2[n] = numSellLostTimePAMini
                sellWinEMA_set_2[n] = numSellWinTimeEMAMini
                sellLostEMA_set_2[n] = numSellLostTimeEMAMini
                sellWinH_set_2[n] = numSellWinTimeHMini
                sellLostH_set_2[n] = numSellLostTimeHMini
                numPattern_set_2[n] = numPatternMini
                break


def handlePattern(name_symbol, pattern,given_date):
    global numPattern
    global numSellLostTimePA
    global numSellWinTimePA
    global numSellLostTimeEMA
    global numSellWinTimeEMA
    global numSellLostTimeH
    global numSellWinTimeH
    global numRecord

    rawHistoricalData = pd.read_csv(f'data/history{config_path_extension}/{name_symbol}.csv')
    historicalData = rawHistoricalData[rawHistoricalData['Date'] < given_date]
    numPattern = 0
    numRecord = 0
    numSellLostTimePA = 0
    numSellWinTimePA = 0
    numSellLostTimeEMA = 0
    numSellWinTimeEMA = 0
    numSellLostTimeH = 0
    numSellWinTimeH = 0
    for index, row in historicalData.iterrows():
        type_val = row[3]
        abstracted_string = ''.join(word[0] for word in type_val.split('-'))
        if abstracted_string == pattern:
            date = row[0]
            chance = row[9]
            sell_timePA = row[5]
            sell_timeEMA = row[10]
            sell_earnEMA = row[11]
            sell_earnPA = row[6]
            sell_timeH = row[12]
            sell_earnH = row[13]
            telegram_pattern_array.append(
                [date, chance, sell_timePA, sell_earnPA, sell_timeEMA, sell_earnEMA, sell_timeH, sell_earnH])
            numPattern = numPattern + 1
            if sell_timePA == "10:30:00":
                numSellLostTimePA = numSellLostTimePA + 1
            if sell_timePA != "10:30:00":
                numSellWinTimePA = numSellWinTimePA + 1
            if sell_timeEMA == "10:30:00":
                numSellLostTimeEMA = numSellLostTimeEMA + 1
            if sell_timeEMA == "15:30:00":
                numSellWinTimeEMA = numSellWinTimeEMA + 1
            if sell_timeH == "10:30:00":
                numSellLostTimeH = numSellLostTimeH + 1
            if sell_timeH == "15:30:00":
                numSellWinTimeH = numSellWinTimeH + 1
        numRecord = numRecord + 1


def handlePatternMini(name_symbol, pattern,given_date):
    global numPatternMini
    global numSellLostTimePAMini
    global numSellWinTimePAMini
    global numSellLostTimeEMAMini
    global numSellWinTimeEMAMini
    global numSellLostTimeHMini
    global numSellWinTimeHMini
    global numRecordMini

    rawHistoricalData = pd.read_csv(f'data/history{config_path_extension}/{name_symbol}.csv')
    historicalData = rawHistoricalData[rawHistoricalData['Date'] < given_date]
    numPatternMini = 0
    numRecordMini = 0
    numSellLostTimePAMini = 0
    numSellWinTimePAMini = 0
    numSellLostTimeEMAMini = 0
    numSellWinTimeEMAMini = 0
    numSellLostTimeHMini = 0
    numSellWinTimeHMini = 0
    for index, row in historicalData.iterrows():
        type_val = row[4]
        if not pd.isnull(type_val) and "Null" not in type_val:
            abstracted_string = ''.join(word[0] for word in type_val.split('-'))
            if abstracted_string == pattern:
                date = row[0]
                chance = row[9]
                sell_timePA = row[5]
                sell_timeEMA = row[10]
                sell_earnEMA = row[11]
                sell_earnPA = row[6]
                sell_timeH = row[12]
                sell_earnH = row[13]
                telegram_pattern_array.append(
                    [date, chance, sell_timePA, sell_earnPA, sell_timeEMA, sell_earnEMA, sell_timeH, sell_earnH])
                numPatternMini = numPatternMini + 1
                if sell_timePA == "10:30:00":
                    numSellLostTimePAMini = numSellLostTimePAMini + 1
                if sell_timePA != "10:30:00":
                    numSellWinTimePAMini = numSellWinTimePAMini + 1
                if sell_timeEMA == "10:30:00":
                    numSellLostTimeEMAMini = numSellLostTimeEMAMini + 1
                if sell_timeEMA == "15:30:00":
                    numSellWinTimeEMAMini = numSellWinTimeEMAMini + 1
                if sell_timeH == "10:30:00":
                    numSellLostTimeHMini = numSellLostTimeHMini + 1
                if sell_timeH == "15:30:00":
                    numSellWinTimeHMini = numSellWinTimeHMini + 1
        numRecordMini = numRecordMini + 1


def execute_preanalysis(date_2, model):
    global overall_csv
    global pa_array
    global verify_array
    global isBuySignal
    global buyPattern
    global isBuySignalMini
    global buyPatternMini
    global price_6
    global price_6_open
    global price_6_high
    global price_6_low
    global time_7
    global price_7
    global price_7_open
    global price_7_high
    global price_7_low
    global folder_path

    month = QDate.fromString(date_2, 'yyyy-MM-dd').toString('yyyy-MM')
    input_date = datetime.strptime(date_2, "%Y-%m-%d")
    us_calendar = mcal.get_calendar('NYSE')
    previous_trading_day = input_date - timedelta(days=1)
    while len(us_calendar.valid_days(start_date=previous_trading_day, end_date=previous_trading_day)) <= 0:
        previous_trading_day -= timedelta(days=1)
    yesterday_date = previous_trading_day.strftime('%Y-%m-%d')
    try:
        pre_data_csv = pd.read_csv(f'data/ranking{config_path_extension}/{date_2}_list.csv')

        pre_datas = pre_data_csv.values
        headers = pre_data_csv.columns
        overall_csv = []

        for pre_data in pre_datas:

            model.add_output(f"Checking condition for {pre_data[0]} ......")

            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={pre_data[0]}&interval={config_timeframe}&outputsize=full&apikey={api_key}&month={month}&entitlement=delayed"
            response = requests.get(url)

            url6 = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&month={month}&symbol={pre_data[0]}&interval={config_subtimeframe}&outputsize=full&apikey={api_key}&entitlement=delayed"
            response_6 = requests.get(url6)

            url_vwap = f"https://www.alphavantage.co/query?function=VWAP&symbol={pre_data[0]}&interval={config_timeframe}&apikey={api_key}&entitlement=delayed&month={month}"
            response_7 = requests.get(url_vwap)

            url_bbbands_15 = f"https://www.alphavantage.co/query?function=BBANDS&symbol={pre_data[0]}&interval={config_subtimeframe}&time_period=20&series_type=close&apikey={api_key}&entitlement=delayed&month={month}"
            response_9 = requests.get(url_bbbands_15)

            try:
                if response.status_code == 200:
                    data = response.json()
                    data_15 = response_6.json()
                    data_vwap = response_7.json()
                    data_bbbands_15 = response_9.json()
                    time_series = data[f'Time Series ({config_timeframe})']
                    time_series_15 = data_15[f'Time Series ({config_subtimeframe})']
                    vwap = data_vwap['Technical Analysis: VWAP']
                    bbbands_15 = data_bbbands_15['Technical Analysis: BBANDS']
                    array_csv = []
                    preday_array = []
                    verify_array = []
                    verify_array_format = "00"
                    num_of_minute = 12
                    countVWAP = 0
                    vwapTrend = "None"
                    overHigh = False
                    overLow = False
                    overHigh_15 = False
                    overLow_15 = False
                    jumpUp = False
                    jumpDown = False
                    signal = "None"
                    row = [f'09:30:00', 0.0, '', 0.0, 0.0, 0.0, 0.0, 0.0,
                           0.0, 0.0, 0.0, 0.0,0.0,0.0,
                           0.0,0.0,0.0]  # time, closed, date, low, SMA-5, high, EMA-5, SMA-10, EMA-10, open, macd, rsi, SMA-20, bb high, bb low
                    verify_array.append(row)
                    hours = 10
                    for i in range(num_of_minute):
                        if int(verify_array_format) == 60:
                            hours = hours + 1
                            verify_array_format = "00"
                        row = [f'{hours}:{verify_array_format}:00', 0.0, '', 0.0, 0.0, 0.0, 0.0, 0.0,
                               0.0, 0.0, 0.0, 0.0,0.0,0.0,
                               0.0,0.0,0.0]  # time, closed, date, low, SMA-5, high, EMA-5, SMA-10, EMA-10, open, macd, rsi, SMA-20,  bb high, bb low
                        verify_array.append(row)
                        verify_array_format = int(verify_array_format) + 30
                    verify_array_format = "00"
                    hours = 13
                    for i in range(6):
                        if int(verify_array_format) == 60:
                            hours = hours + 1
                            verify_array_format = "00"
                        row = [f'{hours}:{verify_array_format}:00', 0.0, '', 0.0, 0.0, 0.0, 0.0, 0.0,
                               0.0, 0.0, 0.0, 0.0,
                               0.0,0.0]  # time, closed, date, low, SMA-5, high, EMA-5, SMA-10, EMA-10, open, macd, rsi, SMA-20, vwap
                        preday_array.append(row)
                        verify_array_format = int(verify_array_format) + 30

                    for timestamp, values in time_series.items():
                        if verify_array[0][1] != 0.0 and verify_array[11][1] != 0.0 and preday_array[0][1] != 0.0 and preday_array[5][1] != 0.0:
                            break
                        for verify in preday_array:
                            if f"{yesterday_date} {verify[0]}" in timestamp:
                                verify[9] = float(values['1. open'])
                                verify[2] = timestamp
                                verify[3] = float(values['3. low'])
                                verify[5] = float(values['2. high'])
                                verify[1] = float(values['4. close'])
                        for verify in verify_array:
                            if f"{date_2} {verify[0]}" in timestamp:
                                verify[9] = float(values['1. open'])
                                verify[2] = timestamp
                                verify[3] = float(values['3. low'])
                                verify[5] = float(values['2. high'])
                                verify[1] = float(values['4. close'])
                    for timestamp_vwap, values_vwap in vwap.items():
                        for verify in preday_array:
                            if timestamp_vwap in verify[2]:
                                verify[13] = float(values_vwap['VWAP'])
                                if verify[13] < verify[1]:
                                    countVWAP = countVWAP + 1
                                else:
                                    countVWAP = countVWAP - 1
                    if countVWAP > 0 and preday_array[5][1] > preday_array[5][13]:
                        vwapTrend = "Upward"
                        signal = "CALL"
                    elif countVWAP < 0 and preday_array[5][1] < preday_array[5][13]:
                        vwapTrend = "Downward"
                        signal = "PUT"
                    else:
                        vwapTrend = "Sideway"
                    for m in range(len(verify_array) - 1):
                        if date_2 not in verify_array[m][2]:
                            verify_array[m][1] = verify_array[m - 1][9]
                            datetime_obj = datetime.strptime(verify_array[m - 1][2], '%Y-%m-%d %H:%M:%S')
                            next_minute = datetime_obj + timedelta(minutes=30)
                            next_minute_str = next_minute.strftime('%Y-%m-%d %H:%M:%S')
                            verify_array[m][2] = next_minute_str
                            verify_array[m][3] = verify_array[m - 1][9]
                            verify_array[m][5] = verify_array[m - 1][9]
                            verify_array[m][9] = verify_array[m - 1][9]
                            verify_array[m][4] = verify_array[m - 1][4]
                            verify_array[m][6] = verify_array[m - 1][6]
                            verify_array[m][7] = verify_array[m - 1][7]
                            verify_array[m][8] = verify_array[m - 1][8]
                            verify_array[m][12] = verify_array[m - 1][12]
                    if True:  # condition 1
                        isBuySignal = False
                        isBuySignalMini = False
                        buyAlready = False
                        buyPattern = ""
                        buyPatternMini = ""
                        buy_chance = 0
                        buy_chance_mini = 0
                        price_6 = 0.0
                        price_6_low = 0.0
                        price_6_high = 0.0
                        price_6_open = 0.0
                        price_7 = 0.0
                        price_7_low = 0.0
                        price_7_high = 0.0
                        price_7_open = 0.0
                        price_8 = 0.0
                        price_8_low = 0.0
                        price_8_high = 0.0
                        price_8_open = 0.0
                        price_6_bbhigh = 0.0
                        price_6_bblow = 0.0
                        price_7_bbhigh = 0.0
                        price_7_bblow = 0.0
                        firstBB = "None"
                        secondBB = "None"
                        time_6 = ""
                        time_7 = ""
                        date30 = verify_array[0][2][:10]
                        for i in range(len(verify_array) - 1):  # start adding buy condition
                            defineCandleSticks(i)
                            callBuyCondition(i)
                            if isBuySignal == True and buyAlready == False and "09" in lastTime:
                                for timestamp15, values15 in time_series_15.items():
                                    if price_6 != 0.0 and price_7 != 0.0 and price_8 != 0.0:
                                        defineCandleSticksMini(1)
                                        callBuyConditionMini(1)
                                        if isBuySignalMini == True:
                                            print(f"{time_6} : {price_6_low}")
                                            for timestamp_bb, values_bb in bbbands_15.items():
                                                if price_6_bbhigh != 0.0 and price_7_bbhigh != 0.0:
                                                    if price_6 > price_6_bbhigh:
                                                        firstBB = "High"
                                                    if price_6 < price_6_bblow:
                                                        firstBB = "Low"
                                                    if price_6 > price_6_bbhigh and price_6 < price_6_bblow:
                                                        firstBB = "Extreme"
                                                    if price_6_open > price_6_bbhigh and price_6 > price_6_bbhigh:
                                                        firstBB = "OverHigh"
                                                    if price_6_open < price_6_bblow and price_6 < price_6_bblow:
                                                        firstBB = "OverLow"
                                                    if price_7 > price_7_bbhigh:
                                                        secondBB = "High"
                                                    if price_7 < price_7_bblow:
                                                        secondBB = "Low"
                                                    if price_7 > price_7_bbhigh and price_7 < price_7_bblow:
                                                        secondBB = "Extreme"
                                                    if price_7_open > price_7_bbhigh and price_7 > price_7_bbhigh:
                                                        secondBB = "OverHigh"
                                                    if price_7_open < price_7_bblow and price_7 < price_7_bblow:
                                                        secondBB = "OverLow"
                                                    break
                                                if f"{date30} 09:30" in timestamp_bb:
                                                    price_6_bbhigh = float(values_bb['Real Upper Band'])
                                                    price_6_bblow = float(values_bb['Real Lower Band'])
                                                if f"{date30} 09:45" in timestamp_bb:
                                                    price_7_bbhigh = float(values_bb['Real Upper Band'])
                                                    price_7_bblow = float(values_bb['Real Lower Band'])
                                            if price_6 > price_6_bbhigh or price_7 > price_7_bbhigh:
                                                overHigh_15 = True
                                            if price_6 < price_6_bblow or price_7 < price_7_bblow:
                                                overLow_15 = True
                                            if price_6_low > price_8_high:
                                                jumpUp = True
                                            if price_6_high < price_8_low:
                                                jumpDown = True
                                            break
                                    if f"{date30} 09:30:00" in timestamp15:
                                        price_6_open = float(values15['1. open'])
                                        time_6 = timestamp15
                                        price_6_low = float(values15['3. low'])
                                        price_6_high = float(values15['2. high'])
                                        price_6 = float(values15['4. close'])
                                    if f"{date30} 09:45:00" in timestamp15:
                                        price_7_open = float(values15['1. open'])
                                        time_7 = timestamp15
                                        price_7_low = float(values15['3. low'])
                                        price_7_high = float(values15['2. high'])
                                        price_7 = float(values15['4. close'])
                                    if f"{yesterday_date} 15:45:00" in timestamp15:
                                        price_8_open = float(values15['1. open'])
                                        time_8 = timestamp15
                                        price_8_low = float(values15['3. low'])
                                        price_8_high = float(values15['2. high'])
                                        price_8 = float(values15['4. close'])
                                abstracted_string = ''.join(word[0] for word in buyPattern.split('-'))
                                abstracted_string_2 = ''.join(word[0] for word in buyPatternMini.split('-'))
                                k = 0
                                for head in headers:
                                    if abstracted_string == head:
                                        buy_chance = pre_data[k]
                                        handlePattern(pre_data[0], abstracted_string, date_2)
                                        break
                                    k = k + 1
                                k = 0
                                for head in headers:
                                    if abstracted_string_2 == head:
                                        buy_chance_mini = pre_data[k]
                                        handlePatternMini(pre_data[0], abstracted_string_2, date_2)
                                        break
                                    k = k + 1
                                print(
                                    f"{pre_data[0]} : {lastClose} - Ready to CALL, Pattern: {buyPattern} ({buy_chance}), (Chance: {pre_data[1]} with Earning {pre_data[3]}")
                                model.add_output(
                                    f"{pre_data[0]} : {lastClose} - Ready to CALL, Pattern: {buyPattern} ({buy_chance}), (Chance: {pre_data[1]} with Earning {pre_data[3]}")
                                row = [pre_data[0], buyPattern, buy_chance, buyPatternMini, buy_chance_mini, signal,
                                       pre_data[1], pre_data[3], pre_data[11], vwapTrend,firstBB, secondBB,overHigh_15, overLow_15, jumpUp, jumpDown]
                                array_csv.append(row)
                                print("--------------")
                                model.add_output("--------------")
                                buyAlready = True
                                break
                    overall_csv = overall_csv + array_csv
                else:
                    print(f"Error: {response.status_code} - {response.text}")
                    model.add_output(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                pass
    except FileNotFoundError:
        model.add_output(f"The file '{date_2}_afterMarket.csv' does not exist.")

    if len(overall_csv) != 0:
        rearranged_array = sorted(overall_csv, key=lambda x: float(x[6]), reverse=True)
        file_path = f'data/pre-analysis{config_path_extension}/{date_2}_afterMarket.csv'
        header = ['Symbol', 'Buy Pattern (30)', 'Pattern Chance (30)', 'Buy Pattern (15)', 'Pattern Chance (15)',
                  'Signal', 'Total Chance', 'Earning Probability', 'Total Record', 'Trend','1st BBand','2nd BBand','Over High(15)','Over Low(15)','Jump Up','Jump Down']
        pa_array = np.vstack([header, rearranged_array])
        np.savetxt(file_path, pa_array, delimiter=',', fmt='%s')
        print(f"Array exported to {file_path} successfully.")
        model.add_output(f"Array exported to {file_path} successfully.")
    else:
        print(f"No Data Updated.")
        model.add_output(f"No Data Updated.")

def execute_postanalysis(date, date_2, model):
    global overall_csv
    global pta_array
    global verify_array
    global isBuySignal
    global buyPattern
    global isBuySignalMini
    global buyPatternMini
    global ema_10
    global price_6
    global price_6_open
    global price_6_high
    global price_6_low
    global time_7
    global price_7
    global price_7_open
    global price_7_high
    global price_7_low

    month = QDate.fromString(date_2, 'yyyy-MM-dd').toString('yyyy-MM')
    date = QDate.currentDate().toString('yyyy-MM-dd')
    try:

        pre_analysis_csv = pd.read_csv(f'data/pre-analysis{config_path_extension}/{date_2}_afterMarket.csv')
        pre_datas = pre_analysis_csv.values
        headers = pre_analysis_csv.columns
        array_csv = []
        overall_csv = []
        for pre_data in pre_datas:
            abstracted_string = ''.join(word[0] for word in pre_data[1].split('-'))
            abstracted_string_2 = ''.join(word[0] for word in pre_data[3].split('-'))
            buy_chance = pre_data[2]
            handlePattern(pre_data[0], abstracted_string, date_2)
            buy_chance_mini = pre_data[4]
            handlePatternMini(pre_data[0], abstracted_string_2, date_2)
            if numSellLostTimePA + numSellWinTimePA == 0:
                dividePA = 0
            else:
                dividePA = (numSellWinTimePA / (numSellLostTimePA + numSellWinTimePA))
            if numSellLostTimeH + numSellWinTimeH == 0:
                divideH = 0
            else:
                divideH = (numSellWinTimeH / (numSellLostTimeH + numSellWinTimeH))
            if numSellLostTimeEMA + numSellWinTimeEMA == 0:
                divideEMA = 0
            else:
                divideEMA = (numSellWinTimeEMA / (numSellLostTimeEMA + numSellWinTimeEMA))
            if numSellLostTimePAMini + numSellWinTimePAMini == 0:
                dividePAMini = 0
            else:
                dividePAMini = (numSellWinTimePAMini / (numSellLostTimePAMini + numSellWinTimePAMini))
            if numSellLostTimeHMini + numSellWinTimeHMini == 0:
                divideHMini = 0
            else:
                divideHMini = (numSellWinTimeHMini / (numSellLostTimeHMini + numSellWinTimeHMini))
            if numSellLostTimeEMAMini + numSellWinTimeEMAMini == 0:
                divideEMAMini = 0
            else:
                divideEMAMini = (numSellWinTimeEMAMini / (numSellLostTimeEMAMini + numSellWinTimeEMAMini))
            totalChance = ((numPatternMini / numPattern) * 1) + \
                            ((numPattern / numRecord) * 0.9) + \
                            (divideEMAMini * 0.8) + \
                            (divideEMA * 0.7) + \
                            (divideHMini * 0.6) + \
                            (divideH * 0.5) + \
                            (buy_chance_mini * 0.4) + \
                            (dividePAMini * 0.3) + \
                            (dividePA * 0.2) + \
                            (buy_chance * 0.1)
            print(
                f"{pre_data[0]} Ready to CALL, Pattern: {pre_data[1]} ({pre_data[2]}), (Sub-Chance: {pre_data[4]} with Earning {pre_data[7]}")
            model.add_output(
                f"{pre_data[0]} Ready to CALL, Pattern: {pre_data[1]} ({pre_data[2]}), (Sub-Chance: {pre_data[4]} with Earning {pre_data[7]}")
            row = [pre_data[0], pre_data[1], pre_data[2], pre_data[3], pre_data[4], pre_data[5],
                    pre_data[6], pre_data[7], pre_data[9], pre_data[10], pre_data[11],pre_data[12],pre_data[13],pre_data[14],pre_data[15],
                   numSellLostTimePA, numSellWinTimePA, numSellLostTimeEMA,
                    numSellWinTimeEMA, numSellLostTimeH, numSellWinTimeH, numPattern,
                    numSellLostTimePAMini, numSellWinTimePAMini, numSellLostTimeEMAMini, numSellWinTimeEMAMini,
                    numSellLostTimeHMini, numSellWinTimeHMini, numPatternMini,
                    numRecord, f'{totalChance:.2g}']
            array_csv.append(row)
            print("--------------")
            model.add_output("--------------")
            buyAlready = True
        overall_csv = overall_csv + array_csv


    except FileNotFoundError:
        model.add_output(f"The file '{date}_afterMarket.csv' does not exist.")

    if len(overall_csv) != 0:
        rearranged_array = sorted(overall_csv, key=lambda x: float(x[23]), reverse=True)
        file_path = f'data/post-analysis{config_path_extension}/{date_2}_beforeMarket.csv'
        header = ['Symbol', 'Buy Pattern (30)', 'Pattern Chance (30)', 'Buy Pattern (15)', 'Pattern Chance (15)',
                  'Signal', 'Total Chance', 'Earning Probability','Trend','1st BBand','2nd BBand','Over High(15)','Over Low(15)','Jump Up','Jump Down',
                 'SLT-PA(30)', 'SWT-PA(30)', 'SLT-EMA(30)',
                  'SWT-EMA(30)', 'SLT-H(30)', 'SWT-H(30)', 'PT(30)', 'SLT-PA(15)', 'SWT-PA(15)', 'SLT-EMA(15)',
                  'SWT-EMA(15)', 'SLT-H(15)', 'SWT-H(15)', 'PT(15)', 'Total Record', 'Calculated Chance']
        pta_array = np.vstack([header, rearranged_array])
        np.savetxt(file_path, pta_array, delimiter=',', fmt='%s')
        print(f"Array exported to {file_path} successfully.")
        model.add_output(f"Array exported to {file_path} successfully.")
    else:
        print(f"No Data Updated.")
        model.add_output(f"No Data Updated.")

def execute_setup(date_2, model):
    global overall_csv
    global s_array
    global verify_array
    global folder_path

    month = QDate.fromString(date_2, 'yyyy-MM-dd').toString('yyyy-MM')
    try:
        pre_data_csv = pd.read_csv(f'data/ranking{config_path_extension}/{date_2}_list.csv')

        pre_datas = pre_data_csv.values
        headers = pre_data_csv.columns
        overall_csv = []

        for pre_data in pre_datas:

            model.add_output(f"Checking condition for {pre_data[0]} ......")

            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={pre_data[0]}&interval=30min&outputsize=full&apikey={api_key}&month={month}&entitlement=delayed"
            response = requests.get(url)

            url_vwap = f"https://www.alphavantage.co/query?function=VWAP&symbol={pre_data[0]}&interval=30min&apikey={api_key}&entitlement=delayed&month={month}"
            response_7 = requests.get(url_vwap)


            try:
                if response.status_code == 200:
                    data = response.json()
                    data_vwap = response_7.json()
                    time_series = data['Time Series (30min)']
                    vwap = data_vwap['Technical Analysis: VWAP']
                    array_csv = []
                    preday_array = []
                    verify_array = []
                    verify_array_format = "00"
                    num_of_minute = 12
                    countVWAP = 0
                    vwapTrend = "None"
                    signal = "None"
                    hours = 13
                    for i in range(6):
                        if int(verify_array_format) == 60:
                            hours = hours + 1
                            verify_array_format = "00"
                        row = [f'{hours}:{verify_array_format}:00', 0.0, '', 0.0, 0.0, 0.0, 0.0, 0.0,
                               0.0, 0.0, 0.0, 0.0,
                               0.0,0.0]  # time, closed, date, low, SMA-5, high, EMA-5, SMA-10, EMA-10, open, macd, rsi, SMA-20, vwap
                        verify_array.append(row)
                        verify_array_format = int(verify_array_format) + 30

                    for timestamp, values in time_series.items():
                        if verify_array[0][1] != 0.0 and verify_array[5][1] != 0.0:
                            break
                        for verify in verify_array:
                            if f"{date_2} {verify[0]}" in timestamp:
                                verify[9] = float(values['1. open'])
                                verify[2] = timestamp
                                verify[3] = float(values['3. low'])
                                verify[5] = float(values['2. high'])
                                verify[1] = float(values['4. close'])
                    for timestamp_vwap, values_vwap in vwap.items():
                        for verify in verify_array:
                            if timestamp_vwap in verify[2]:
                                verify[13] = float(values_vwap['VWAP'])
                                if verify[13] < verify[1]:
                                    countVWAP = countVWAP + 1
                                else:
                                    countVWAP = countVWAP - 1
                    if countVWAP > 0 and verify_array[5][1] > verify_array[5][13]:
                        vwapTrend = "Upward"
                        signal = "CALL"
                    elif countVWAP < 0 and verify_array[5][1] < verify_array[5][13]:
                        vwapTrend = "Downward"
                        signal = "PUT"
                    else:
                        vwapTrend = "Sideway"
                    for m in range(len(verify_array) - 1):
                        if date_2 not in verify_array[m][2]:
                            verify_array[m][1] = verify_array[m - 1][9]
                            datetime_obj = datetime.strptime(verify_array[m - 1][2], '%Y-%m-%d %H:%M:%S')
                            next_minute = datetime_obj + timedelta(minutes=30)
                            next_minute_str = next_minute.strftime('%Y-%m-%d %H:%M:%S')
                            verify_array[m][2] = next_minute_str
                            verify_array[m][3] = verify_array[m - 1][9]
                            verify_array[m][5] = verify_array[m - 1][9]
                            verify_array[m][9] = verify_array[m - 1][9]
                            verify_array[m][4] = verify_array[m - 1][4]
                            verify_array[m][6] = verify_array[m - 1][6]
                            verify_array[m][13] = verify_array[m - 1][13]
                    print(
                        f"{pre_data[0]} : Ready to {signal}")
                    model.add_output(
                        f"{pre_data[0]} : Ready to {signal}")
                    row = [pre_data[0],signal, vwapTrend]
                    array_csv.append(row)
                    print("--------------")
                    model.add_output("--------------")
                    overall_csv = overall_csv + array_csv
                else:
                    print(f"Error: {response.status_code} - {response.text}")
                    model.add_output(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                pass
    except FileNotFoundError:
        model.add_output(f"The file '{date_2}_setup.csv' does not exist.")

    if len(overall_csv) != 0:
        rearranged_array = sorted(overall_csv, key=lambda x: x[0], reverse=True)
        file_path = f'data/setup{config_path_extension}/{date_2}_setup.csv'
        header = ['Symbol', 'Signal','Trend']
        s_array = np.vstack([header, rearranged_array])
        np.savetxt(file_path, s_array, delimiter=',', fmt='%s')
        print(f"Array exported to {file_path} successfully.")
        model.add_output(f"Array exported to {file_path} successfully.")
    else:
        print(f"No Data Updated.")
        model.add_output(f"No Data Updated.")

def backtestDailyData(symbol, date, model):
    # for month in array_month:
    global ema
    global time_1
    global time_3
    global time_4
    global time_5
    global verify_array
    global array_overall
    global time_series_daily
    global isBuySignal
    global buyPattern
    global isBuySignalMini
    global buyPatternMini
    global price_6
    global price_6_open
    global price_6_high
    global price_6_low
    global time_7
    global price_7
    global price_7_open
    global price_7_high
    global price_7_low

    model.add_output(f"Checking condition for {symbol} ......")

    # Make the API request to retrieve the current price for AAPL in the US market
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=30min&outputsize=full&apikey={api_key}&entitlement=delayed"
    response = session.get(url)

    url6 = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=15min&outputsize=full&apikey={api_key}&entitlement=delayed"
    response_6 = session.get(url6)

    url_ema = f"https://www.alphavantage.co/query?function=EMA&symbol={symbol}&interval=30min&time_period=5&series_type=close&apikey={api_key}&entitlement=delayed"
    response_4 = session.get(url_ema)

    if response.status_code == 200:
        data = response.json()
        data_15 = response_6.json()
        data_ema = response_4.json()
        time_series_15 = data_15['Time Series (15min)']
        time_series = data['Time Series (30min)']
        ema = data_ema['Technical Analysis: EMA']

        price_1 = 0.0
        price_1_low = 0.0
        time_1 = ""
        verify_array = []
        verify_array_format = "00"
        num_of_minute = 12
        row = [f'{date} 09:30:00', 0.0, '', 0.0, 0.0, 0.0, 0.0, 0.0,
               0.0, 0.0, 0.0, 0.0,
               0.0]
        verify_array.append(row)
        hours = 10
        for i in range(num_of_minute):
            if int(verify_array_format) == 60:
                hours = hours + 1
                verify_array_format = "00"
            row = [f'{date} {hours}:{verify_array_format}:00', 0.0, '', 0.0, 0.0, 0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0,
                   0.0]  # time, closed, date, low, SMA-5, high, EMA-5, SMA-10, EMA-10, open, macd, rsi, SMA-20
            verify_array.append(row)
            verify_array_format = int(verify_array_format) + 30
        total_chance = 0
        total_bingo_chance = 0
        array_csv = []

        for timestamp, values in time_series.items():
            every_trade_chance = -1
            if "09:00:00" in timestamp:
                # print(f"{timestamp} : {values['4. close']}")
                time_1 = timestamp
                if verify_array[11][1] != 0.0 and verify_array[0][1] != 0.0:
                    initializeIndicator()
                    # if verify_array[0][3] > price_1_high:  # condition 1
                    if True:
                        isBuySignal = False
                        isBuySignalMini = False
                        buyAlready = False
                        buyPattern = ""
                        buyPatternMini = ""
                        price_6 = 0.0
                        price_6_low = 0.0
                        price_6_high = 0.0
                        price_6_open = 0.0
                        price_7 = 0.0
                        price_7_low = 0.0
                        price_7_high = 0.0
                        price_7_open = 0.0
                        time_6 = ""
                        time_7 = ""
                        date30 = time_1[:10]
                        for m in range(len(verify_array)):
                            if m > 0:
                                this_min_date = verify_array[m][2][:10]
                                before_min_date = verify_array[m - 1][2][:10]
                                if this_min_date != before_min_date:
                                    verify_array[m][1] = verify_array[m - 1][9]
                                    datetime_obj = datetime.strptime(verify_array[m - 1][2], '%Y-%m-%d %H:%M:%S')
                                    next_minute = datetime_obj + timedelta(minutes=30)
                                    next_minute_str = next_minute.strftime('%Y-%m-%d %H:%M:%S')
                                    verify_array[m][2] = next_minute_str
                                    verify_array[m][3] = verify_array[m - 1][9]
                                    verify_array[m][5] = verify_array[m - 1][9]
                                    verify_array[m][9] = verify_array[m - 1][9]
                                    verify_array[m][4] = verify_array[m - 1][4]
                                    verify_array[m][6] = verify_array[m - 1][6]
                                    verify_array[m][7] = verify_array[m - 1][7]
                                    verify_array[m][8] = verify_array[m - 1][8]
                                    verify_array[m][12] = verify_array[m - 1][12]

                        for i in range(len(verify_array)):  # start adding buy condition
                            defineCandleSticks(i)
                            callBuyCondition(i)
                            if isBuySignal == True and buyAlready == False and "09" in lastTime:
                                for timestamp15, values15 in time_series_15.items():
                                    if price_6 != 0.0 and price_7 != 0.0:
                                        defineCandleSticksMini(1)
                                        callBuyConditionMini(1)
                                        if isBuySignalMini == True:
                                            print(f"{time_6} : {price_6}")
                                            break
                                    if f"{date30} 09:30:00" in timestamp15:
                                        price_6_open = float(values15['1. open'])
                                        time_6 = timestamp15
                                        price_6_low = float(values15['3. low'])
                                        price_6_high = float(values15['2. high'])
                                        price_6 = float(values15['4. close'])
                                    if f"{date30} 09:45:00" in timestamp15:
                                        price_7_open = float(values15['1. open'])
                                        time_7 = timestamp15
                                        price_7_low = float(values15['3. low'])
                                        price_7_high = float(values15['2. high'])
                                        price_7 = float(values15['4. close'])
                                print(f"{time_1} : {price_1_low}")
                                print(
                                    f"{verify_array[i][2]} : {lastClose} - CALL BUY Signal, Pattern: {buyPattern}")
                                model.add_output(
                                    f"{verify_array[i][2]} : {lastClose} - CALL BUY Signal, Pattern: {buyPattern}")
                                ema_10_time = 'None'
                                ema_10_earn = 0.0
                                is_sell_ema_10 = 0
                                highest_sell_time = 'None'
                                highest_sell_earn = 0.0
                                sell_time = 'None'
                                sell_price = 0.0
                                trigger_sell_time = 'None'
                                trigger_sell_price = 0.0
                                price_action_earn = 0.0
                                is_sell_price_action = 0
                                k = 2
                                chance_bingo = 0
                                chance_bingo_correct = 0
                                buyAlready = True
                                for j in range(len(verify_array) - 2 - i):
                                    if is_sell_price_action == 0:
                                        defineCandleSticks(k + i - 1)
                                        callSellCondition(k + i - 1)
                                    print(f"{verify_array[k + i][2]} : {verify_array[k + i][9]}")
                                    model.add_output(f"{verify_array[k + i][2]} : {verify_array[k + i][9]}")
                                    if isSellSignal == True and is_sell_price_action == 0 and is_sell_ema_10 == 0 and buyAlready == True:
                                        print(f"SELL BUY Signal, Pattern: {sellPattern}")
                                        model.add_output(f"SELL BUY Signal, Pattern: {sellPattern}")
                                        sell_time = verify_array[i + k][0]
                                        sell_price = verify_array[i + k][9]
                                        price_action_earn = (verify_array[i + k][9] - verify_array[i + 1][9]) / \
                                                            verify_array[i + k][9] * 100
                                        # buyAlready = False
                                        is_sell_price_action = 1
                                        if float(verify_array[i + k][9]) > float(verify_array[i + 1][9]):
                                            every_trade_chance = 1
                                        else:
                                            every_trade_chance = 0
                                    if float(verify_array[i + k][6]) > float(verify_array[i + k][1]) and float(
                                            verify_array[i + k][9]) > float(
                                        verify_array[i + k][1]) and is_sell_ema_10 == 0 and buyAlready == True:
                                        print(f"Sell CALL! (EMA-5 Method)")  # sell method 3
                                        model.add_output(f"Sell CALL! (EMA-5 Method)")
                                        ema_10_time = verify_array[i + k][0]
                                        ema_10_earn = (verify_array[i + k][9] - verify_array[i + 1][9]) / \
                                                      verify_array[i + k][9] * 100
                                        is_sell_ema_10 = 1
                                        if is_sell_price_action == 0:
                                            if float(verify_array[i + k][9]) > float(
                                                    verify_array[i + 1][9]):
                                                every_trade_chance = 1
                                            else:
                                                every_trade_chance = 0
                                        buyAlready = False
                                    if (highest_sell_earn < float(verify_array[i + k][9]) - float(
                                            verify_array[i + 1][9])):
                                        highest_sell_time = verify_array[i + k][0]
                                        highest_sell_earn = (verify_array[i + k][9] - verify_array[i + 1][9]) / \
                                                            verify_array[i + k][9] * 100
                                    chance_bingo = chance_bingo + 1
                                    k = k + 1
                                if (highest_sell_earn < verify_array[len(verify_array) - 1][9] - float(
                                        verify_array[i + 1][9])):
                                    highest_sell_time = verify_array[len(verify_array) - 1][0]
                                    highest_sell_earn = (verify_array[len(verify_array) - 1][9] -
                                                         verify_array[i + 1][9]) / \
                                                        verify_array[len(verify_array) - 1][9] * 100
                                if is_sell_ema_10 == 0:
                                    ema_10_time = verify_array[len(verify_array) - 1][0]
                                    ema_10_earn = (verify_array[len(verify_array) - 1][9] - verify_array[i + 1][
                                        9]) / verify_array[len(verify_array) - 1][9] * 100
                                    if float(verify_array[len(verify_array) - 1][9]) > float(
                                            verify_array[i + 1][9]):
                                        every_trade_chance = 1
                                    else:
                                        every_trade_chance = 0
                                print("Increasing Direction")
                                print("Total Chance of Trigger Bingo Rise:")
                                model.add_output("Increasing Direction")
                                model.add_output("Total Chance of Trigger Bingo Rise:")
                                print(every_trade_chance)
                                model.add_output(every_trade_chance)
                                total_bingo_chance = total_bingo_chance + chance_bingo_correct
                                total_chance = total_chance + chance_bingo
                                row = [verify_array[i][2].split(' ')[0],
                                       verify_array[i + 1][0].split(' ')[1],
                                       verify_array[i + 1][9], buyPattern, buyPatternMini,
                                       sell_time, sell_price, f"{price_action_earn:.5g}", sellPattern,
                                       f"{every_trade_chance:.5g}", ema_10_time,
                                       f"{ema_10_earn:.5g}", highest_sell_time,
                                       f"{highest_sell_earn:.5g}"]
                                array_csv.append(row)
                                print("--------------")
                                model.add_output("--------------")
                                break
                    break
            for verify in verify_array:
                if verify[0] in timestamp:
                    verify[9] = float(values['1. open'])
                    verify[2] = timestamp
                    verify[3] = float(values['3. low'])
                    verify[5] = float(values['2. high'])
                    verify[1] = float(values['4. close'])

        array_overall = array_overall + array_csv
    else:
        print(f"Error: {response.status_code} - {response.text}")
        model.add_output(f"Error: {response.status_code} - {response.text}")


def updateData(input_date, model):
    global array_overall
    global session
    global ud_array

    date = input_date

    try:
        pre_data_csv = pd.read_csv(f'data/post-analysis{config_path_extension}/{date}_beforeMarket.csv')
        symbols = pre_data_csv.iloc[:, 0]

        array_overall = []

        session = requests.Session()

        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )

        adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=retry_strategy)

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        for symbol in symbols:

            array_overall = []

            backtestDailyData(symbol, date, model)

            file_path = f'data/history{config_path_extension}/{symbol}.csv'
            # header = ['Date','16:00','09:30','09:31', 'Num of Chance','SMA-5 Sell Time','SMA-5 Earning(%)','SMA-10 Sell Time','SMA-10 Earning(%)','EMA-5 Sell Time','EMA-5 Earning(%)','EMA-10 Sell Time','EMA-10 Earning(%)', 'Best Sell Method', 'Best Sell Time', 'Max Earning(%)', 'Earliest Sell Method', 'Earliest Sell Time', 'Min Earning(%)', 'Highest Sell Time', 'Highest Earning(%)']
            # np_array = np.vstack([header,array_overall])
            if len(array_overall) != 0:
                ud_array = np.array(array_overall)
                telegram_pattern_array.append([symbol, array_overall[0][3], array_overall[0][4], array_overall[0][7]])
                with open(file_path, mode='a', newline='') as file:
                    csv_writer = csv.writer(file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                    for row in ud_array:
                        csv_writer.writerow(row.astype(str))

                # np.savetxt(file_path, np_array, delimiter=',', fmt='%s')
                print(f"Array exported to {file_path} successfully.")
                model.add_output(f"Array exported to {file_path} successfully.")
                telegram_instant_array.append(f"{symbol}的數據庫已更新.")
            else:
                print(f"No Data Updated.")
                model.add_output(f"No Data Updated.")
                telegram_instant_array.append(f"沒有數據可以更新.")
    except FileNotFoundError:
        model.add_output(f"The file '{date}_beforeMarket.csv' does not exist.")

def execute_newsanalysis(input_date, model):
    global lock
    global symbol
    global overall_csv
    global session
    global news_array
    global date
    global folder_path

    folder_path = f'data/history{config_path_extension}'
    symbols_raw = [os.path.splitext(f)[0] for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    date = input_date
    symbols = [x for x in symbols_raw if "QQQ" not in x and "SPY" not in x]
    overall_csv = []
    current_date_obj = QDate.fromString(input_date, 'yyyy-MM-dd')
    month = current_date_obj.toString('MM')
    year = current_date_obj.toString('yyyy')

    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504]
    )

    adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=retry_strategy)

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        for symbol in symbols:
            endDate = 30
            if '02' in month:
                endDate = 28
            elif '12' in month or '10' in month or '08' in month or '07' in month or '05' in month or '03' in month or '01' in month:
                endDate = 31
            url_news = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&apikey={api_key}&time_from={year}{month}01T0000&time_to={year}{month}{endDate}T2359&limit=1000"
            response = requests.get(url_news)

            if response.status_code == 200:

                data_news = response.json()
                news_series = data_news['feed']
                array_csv = []
                news_title = []
                news_score = []
                news_time = []
                related_score = []
                keyword = ['Why', 'What Happened', 'Today', 'Dividend Stock', 'to Buy', 'Unusual Options Activity',
                           'StockNews.com', 'Going On',
                           'What You Should Know', 'ighlights', 'Which Stock', 'to Consider', 'Which Is the Better',
                           'Stocks To Watch', 'Forecasts', 'Momentum',
                           'Top Research Reports', 'Top Analyst Report', 'Watch These', 'Retail Stock', 'vs.',
                           'Value Investor', 'Better Buy', 'Need To Know',
                           'What Whales', 'Buy Now', 'AI Stock', 'Software Stock', 'Right Now', 'biggest moves',
                           'Chip Stocks', 'Tech Stocks',
                           'Need to Know', 'This Week', 'Should You', 'How Much You Would Have', 'Stock for More',
                           'Weekly Gain', 'Will Investors', '?', 'Growth Stock',
                           'Trading Trends', 'Things to Know', 'Earnings Report', 'Top Stocks', 'Stock Of The Day',
                           'Price Target', 'Deserves Your Attention', 'Stock Upgrades',
                           'Resilient Stock', 'Growth Stock', 'Stocks Fit', 'Stay Invested', 'stock drops',
                           'Chart of the Day', 'bullish activity', 'Trading Chalkboards', 'Stocks I Will Never',
                           'The Stock', 'Displays Resilience', 'Cramer', 'Buy Point', 'Emerging Market',
                           'This Would Be It',
                           'things you can', 'Will \"Never\" Sell', 'Stocks to Watch', 'Buying This Stock',
                           'Business Excellence', '1 Reason', 'US Stocks', 'We\'re', 'Are Selling''It\'s Safe',
                           'Wall Street Loves AI', 'Other Stocks', 'ESG Stock', 'Competitor Analysis',
                           'Performance Comparison', 'With My Shares', 'Final Trades', 'Options Traders',
                           'Top Companies',
                           'Growth Investors', 'Strong Outlook', 'Forecast', 'Top Artificial Intelligence',
                           'Bullish', 'Bearish', 'Weak Outlook', 'Moving Lower', 'Market Buy', 'Top five',
                           'Trading Volume',
                           'Bear Market', 'New Investor', 'Options Trading', 'Top-Performing',
                           'Futures Trading', 'stock surges', 'most traded', 'Bitcoin Mining Boom', 'Investor Optimism',
                           'New Highs', ':', 'Cathie Wood', 'Moved the Market', 'Global Stock', 'Market Share',
                           'Prediction',
                           'bullish', 'bearish', 'Moved Upward', 'Blockware analyst', 'beat estimates',
                           'top ETF performers', 'If', 'Speculative Stock', 'Analyst Predicts', 'After Earnings',
                           'Looks Better', 'highlighted',
                           'best week', 'best day', 'Chip Stock', 'Should Know', 'Buys Up Stock', 'Bought Up Stock',
                           'Surging', 'stock sheds a bear', 'Market Rebounds', 'How He', 'a Pop', 'Buy-Rated Stocks',
                           'the Fizz in the Biz', 'Technical Benchmark', 'Smart Investors Know', 'Getting Richer',
                           'Worst Performing', 'Watchlist', 'Stocks Run', 'Market climbs', 'Nasdaq Stocks',
                           'bank-stock investors', 'Stocks a Boost', 'It\'s Time to', 'Top Stock Reports',
                           'Magnificent Seven', 'Warren Buffett', 'Stocks to Invest', 'Smartest Investors',
                           'Sales Outlook',
                           'Red Flag', 'Top Ranked Stocks', 'Green Flag', 'Absolutely Crushed', 'Shouldn\'t Sell',
                           'stock can rocket', 'Invest', 'Must-Owns', 'upside', 'Key Market','bulls','Energy Stocks',
                           'Stocks Have Led','Great Choice','Moving Average','Red-Hot','Stock to Choose','Must-Buy',
                           'Hot Earnings','Winning Streak','Regret Not Buying','Magnificent Stock','Highly Ranked Stocks'
                           'You Can']
                count = False
                model.add_output(f"{input_date}: Analyze the news of {symbol}...")
                print(f"{input_date}: Analyze the news of {symbol}...")
                for item in news_series:
                    datetime2 = datetime.strptime(input_date, "%Y-%m-%d")
                    datetime1 = datetime.strptime(item['time_published'][:8], "%Y%m%d")
                    if datetime1 == datetime2:
                        for subitem in item["ticker_sentiment"]:
                            if subitem["ticker"] == symbol and float(subitem["ticker_sentiment_score"]) >= 0.35 and float(subitem["relevance_score"]) >= 0.15 and all(word not in item["title"] for word in keyword):
                                news_title.append(item["title"])
                                news_score.append(subitem["ticker_sentiment_score"])
                                related_score.append(subitem["relevance_score"])
                                news_time.append(item["time_published"][9:13])
                                row = [symbol, news_score[len(news_score)-1],
                                       related_score[len(related_score)-1], news_time[len(news_time)-1], news_title[len(news_title)-1]]
                                telegram_instant_array.append(row)
                                if count == False:
                                    array_csv.append(row)
                                    model.add_output(f"Title: {news_title[len(news_title)-1]}")
                                    print(f"Title: {news_title[len(news_title)-1]}")
                                    count = True
                                    break

                overall_csv = overall_csv + array_csv
    except FileNotFoundError:
        model.add_output(f"The file '{input_date}.csv' does not exist.")

    if len(overall_csv) != 0:
        rearranged_array = sorted(overall_csv, key=lambda x: x[0], reverse=True)
        file_path = f'data/news-analysis{config_path_extension}/{input_date}_afterNews.csv'
        header = ['Symbol',  'Sentiment Score', 'Relevance Score', 'Published Time', 'News Title']
        news_array = np.vstack([header, rearranged_array])
        df = pd.DataFrame(news_array)
        df.to_csv(file_path, index=False, header=False, encoding='utf-8')
        print(f"Array exported to {file_path} successfully.")
        model.add_output(f"Array exported to {file_path} successfully.")
    else:
        print(f"No Data Updated.")
        model.add_output(f"No Data Updated.")

def monitorAV(symbol, date, model):
    global overall_csv
    global np_array

    try:
        pre_data_csv = pd.read_csv(f'data/post-analysis{config_path_extension}/{date}_beforeMarket.csv')

        mask = pre_data_csv.iloc[:, 0] == symbol

        pre_data = pre_data_csv[mask].values.tolist()

        overall_csv = []

        month = QDate.fromString(date, 'yyyy-MM-dd').toString('yyyy-MM')

        if len(pre_data) != 0:

            pre_data = pre_data[0]

            is_buy = True

            while (is_buy):

                url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={pre_data[0]}&interval=1min&outputsize=full&apikey={api_key}&month={month}&entitlement=delayed"
                response = requests.get(url)

                url2 = f"https://www.alphavantage.co/query?function=EMA&symbol={pre_data[0]}&interval=1min&time_period=10&series_type=close&apikey={api_key}&month={month}&entitlement=delayed"
                response2 = requests.get(url2)

                if response.status_code == 200:
                    data = response.json()
                    time_series = data['Time Series (1min)']

                    data2 = response2.json()
                    ema_10 = data2['Technical Analysis: EMA']

                    latest_time = max(time_series.keys())
                    latest_ema_time = max(ema_10.keys())
                    lastest_ema = ema_10[latest_ema_time]["EMA"]

                    if pre_data[7] == "CALL":
                        lastest_price = time_series[latest_time]["3. low"]
                        print(f"{pre_data[0]} - {latest_time} : {lastest_price} with EMA {lastest_ema}")
                        model.add_output(f"{pre_data[0]} - {latest_time} : {lastest_price} with EMA {lastest_ema}")
                        if lastest_ema > time_series[latest_time]["4. close"] and time_series[latest_time]["4. close"] < \
                                time_series[latest_time]["1. open"]:
                            print(f"{pre_data[0]}: Sell CALL!")
                            model.add_output(f"{pre_data[0]}: Sell CALL!")
                            is_buy = False
                    else:
                        lastest_price = time_series[latest_time]["2. high"]
                        print(f"{pre_data[0]} - {latest_time} : {lastest_price} with EMA {lastest_ema}")
                        model.add_output(f"{pre_data[0]} - {latest_time} : {lastest_price} with EMA {lastest_ema}")
                        if lastest_ema < time_series[latest_time]["4. close"] and time_series[latest_time]["4. close"] > \
                                time_series[latest_time]["1. open"]:
                            print(f"{pre_data[0]}: Sell PUT!")
                            model.add_output(f"{pre_data[0]}: Sell PUT!")
                            is_buy = False

                else:
                    print(f"Error: {response.status_code} - {response.text}")
                    model.add_output(f"Error: {response.status_code} - {response.text}")
        else:
            print(f"Stock Code Not Found!")
            model.add_output(f"Stock Code Not Found!")
    except FileNotFoundError:
        model.add_output(f"The file '{date}_beforeMarket.csv' does not exist.")

def executeFullMultipleMachineLearning(types,data,bmodel):
    global predictionRF
    global predictionSVC
    global predictionDT
    global predictionLR

    df2 = pd.read_csv(f'data/performance{config_path_extension}/train_data_full_list.csv')
    npp_array = df2.iloc[1:].values
    filter_array = []
    expected_output = []
    df2 = pd.read_csv(f'data/performance{config_path_extension}/train_data_full_list.csv')
    npp_array = df2.iloc[1:].values
    filter_array = []
    expected_output = []
    for row in npp_array:
        if pd.notna(row[14]) and 'Null' not in row[4] and 'Null' not in row[5]  and 'Null' not in row[26]  and 'Null' not in row[27]  and 'Null' not in row[28]  and 'Null' not in row[29]:
            pattern = row[4].split('-')
            bigPattern = row[5].split('-')
            patternSPY = row[26].split('-')
            patternQQQ = row[27].split('-')
            bigPatternSPY = row[28].split('-')
            bigPatternQQQ = row[29].split('-')
            new_row = [pattern[0],pattern[1],bigPattern[0],bigPattern[1],bigPattern[2],bigPattern[3],
                       row[6],row[7],row[8],row[9],row[10],row[13],row[15],row[16],row[17],row[18],
                       row[19],row[20],row[21],row[22],row[23],row[24],
                       patternSPY[0],patternSPY[1],patternQQQ[0],patternQQQ[1],
                       bigPatternSPY[0],bigPatternSPY[1],bigPatternSPY[2],bigPatternSPY[3],
                       bigPatternQQQ[0],bigPatternQQQ[1],bigPatternQQQ[2],bigPatternQQQ[3]]
            filter_array.append(new_row)
            expected_output.append(row[11])

    df = pd.DataFrame(filter_array)
    df[6] = df[6].fillna('None')
    df[7] = df[7].fillna('None')
    df[0] = df[0].map({'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3})
    df[1] = df[1].map({'Green': 0, 'Red': 1})
    df[2] = df[2].map({'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3})
    df[3] = df[3].map({'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3})
    df[4] = df[4].map({'Green': 0, 'Red': 1})
    df[5] = df[5].map({'Green': 0, 'Red': 1})
    df[6] = df[6].map({'None': 0, 'High': 1, 'OverHigh': 2,'Low': 3,'OverLow': 4})
    df[7] = df[7].map({'None': 0, 'High': 1, 'OverHigh': 2,'Low': 3,'OverLow': 4})
    df[8] = df[8].map({'Upward': 0, 'Downward': 1, 'Sideway': 2})
    df[9] = df[9].map({True: 0, False: 1})
    df[10] = df[10].map({True: 0, False: 1})
    df[11] = df[11].map({'CALL': 0, 'PUT': 1})
    df[12] = df[12].map({'Upward': 0, 'Downward': 1, 'Sideway': 2})
    df[13] = df[13].map({'Upward': 0, 'Downward': 1, 'Sideway': 2})
    df[14] = df[14].map({True: 0, False: 1})
    df[15] = df[15].map({True: 0, False: 1})
    df[16] = df[16].map({True: 0, False: 1})
    df[17] = df[17].map({True: 0, False: 1})
    df[18] = df[18].map({True: 0, False: 1})
    df[19] = df[19].map({True: 0, False: 1})
    df[20] = df[20].map({True: 0, False: 1})
    df[21] = df[21].map({True: 0, False: 1})
    df[22] = df[22].map({'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3})
    df[23] = df[23].map({'Green': 0, 'Red': 1})
    df[24] = df[24].map({'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3})
    df[25] = df[25].map({'Green': 0, 'Red': 1})
    df[26] = df[26].map({'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3})
    df[27] = df[27].map({'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3})
    df[28] = df[28].map({'Green': 0, 'Red': 1})
    df[29] = df[29].map({'Green': 0, 'Red': 1})
    df[30] = df[30].map({'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3})
    df[31] = df[31].map({'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3})
    df[32] = df[32].map({'Green': 0, 'Red': 1})
    df[33] = df[33].map({'Green': 0, 'Red': 1})


    new_data = pd.DataFrame(data)
    new_data[6] = new_data[6].fillna('None')
    new_data[7] = new_data[7].fillna('None')
    new_data_encoded = new_data.apply(
        lambda x: x.map({
                        'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3,
                    'Green': 0, 'Red': 1,
                    'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3,
                    'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3,
                    'Green': 0, 'Red': 1,
                    'Green': 0, 'Red': 1,
                    'None': 0, 'High': 1, 'OverHigh': 2,'Low': 3,'OverLow': 4,
                    'None': 0, 'High': 1, 'OverHigh': 2,'Low': 3,'OverLow': 4,
                    'Upward': 0, 'Downward': 1, 'Sideway': 2,
                    True: 0, False: 1,
                        True: 0, False: 1,
                        'CALL': 0, 'PUT': 1,
                        'Upward': 0, 'Downward': 1, 'Sideway': 2,
                        'Upward': 0, 'Downward': 1, 'Sideway': 2,
                        True: 0, False: 1,
                        True: 0, False: 1,
                        True: 0, False: 1,
                        True: 0, False: 1,
                        True: 0, False: 1,
                        True: 0, False: 1,
                        True: 0, False: 1,
                        True: 0, False: 1,
                    'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3,
                    'Green': 0, 'Red': 1,
                    'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3,
                    'Green': 0, 'Red': 1,
                    'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3,
                    'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3,
                    'Green': 0, 'Red': 1,
                    'Green': 0, 'Red': 1,
                    'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3,
                    'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3,
                    'Green': 0, 'Red': 1,
                    'Green': 0, 'Red': 1
                    }))

    model = RandomForestClassifier()
    model.fit(df, expected_output)
    predictionRF = model.predict(new_data_encoded)
    print(f'Random Forest: {predictionRF}')
    bmodel.add_output(f'Random Forest: {predictionRF}')
    model = DecisionTreeClassifier()
    model.fit(df, expected_output)
    predictionDT = model.predict(new_data_encoded)
    print(f'Decision Tree: {predictionDT}')
    bmodel.add_output(f'Decision Tree: {predictionDT}')
    model = SVC()
    model.fit(df, expected_output)
    predictionSVC = model.predict(new_data_encoded)
    print(f'SVC: {predictionSVC}')
    bmodel.add_output(f'SVC: {predictionSVC}')
    model = LogisticRegression()
    #model = LogisticRegression(solver='lbfgs', max_iter=1000)
    model.fit(df, expected_output)
    predictionLR = model.predict(new_data_encoded)
    print(f'Logistic Regression: {predictionLR}')
    bmodel.add_output(f'Logistic Regression: {predictionLR}')

def execute_predictAnalysisFUTU(input_date, model):
    global symbol
    global overall_csv
    global full_array
    global date
    global folder_path

    overall_csv = []
    full_array = []

    pre_date_csv = pd.read_csv(f'data/post-analysis(futu){config_path_extension}/{input_date}_beforeMarket.csv')
    post_datas = pre_date_csv.values
    rate_csv = pd.read_csv(f'data/performance{config_path_extension}/max_list_detail.csv')
    rate_datas = rate_csv.values
    numsLongGreen = 0
    numsLongRed = 0
    buyType = "None"
    for post_data in post_datas:
        if post_data[0] == "QQQ":
            patternQQQ = post_data[1].split('-')
            bigPatternQQQ = post_data[3].split('-')
            trendQQQ = post_data[8]
            highQQQ = post_data[11]
            lowQQQ = post_data[12]
            jumpUpQQQ = post_data[13]
            jumpDownQQQ = post_data[14]
        if post_data[0] == "SPY":
            patternSPY = post_data[1].split('-')
            bigPatternSPY = post_data[3].split('-')
            trendSPY = post_data[8]
            highSPY = post_data[11]
            lowSPY = post_data[12]
            jumpUpSPY = post_data[13]
            jumpDownSPY = post_data[14]
        if "Long-Red" in post_data[1]:
            numsLongRed = numsLongRed + 1
        if "Long-Green" in post_data[1]:
            numsLongGreen = numsLongGreen + 1
    if numsLongGreen > numsLongRed:
        buyType = "CALL"
    else:
        buyType = "PUT"
    temp_data = []
    for post_data in post_datas:
        if post_data[0] != "SPY" and post_data[0] != "QQQ" and "Null" not in post_data[1] and "Null" not in post_data[3]:
            firstBB = post_data[9]
            secondBB = post_data[10]
            pattern = post_data[1].split('-')
            bigPattern = post_data[3].split('-')
            row = [pattern[0],pattern[1],bigPattern[0],bigPattern[1],bigPattern[2],bigPattern[3],
                   firstBB,secondBB,post_data[8],post_data[13],post_data[14], buyType,
                   trendSPY, trendQQQ, highSPY, lowSPY, highQQQ, lowQQQ, jumpUpSPY, jumpDownSPY,
                   jumpUpQQQ, jumpDownQQQ, patternSPY[0], patternSPY[1], patternQQQ[0], patternQQQ[1],
                   bigPatternSPY[0],bigPatternSPY[1],bigPatternSPY[2],bigPatternSPY[3],
                   bigPatternQQQ[0],bigPatternQQQ[1],bigPatternQQQ[2],bigPatternQQQ[3]]
            temp_data.append(row)
    model.add_output(f"Predicting ...")
    executeFullMultipleMachineLearning(buyType,temp_data,model)
    i = 0
    for post_data in post_datas:
        if post_data[0] != "SPY" and post_data[0] != "QQQ" and "Null" not in post_data[1] and "Null" not in post_data[3]:
            callChance = 0
            putChance = 0
            totalRecord = 0
            for rate_data in rate_datas:
                if rate_data[0] == predictionRF[i] and rate_data[1] == predictionSVC[i] and rate_data[2] == predictionDT[i] and rate_data[3] == predictionLR[i]:
                    callChance = rate_data[17]
                    putChance = rate_data[18]
                    totalRecord = rate_data[4]
                    break
            new_row = [post_data[0],post_data[1],post_data[3],post_data[8],post_data[9],
                        post_data[10],post_data[13],post_data[14],buyType,
                        predictionRF[i], predictionSVC[i], predictionDT[i], predictionLR[i],totalRecord,callChance,putChance]
            overall_csv.append(new_row)
            if predictionRF[i] == "Long-Green" and predictionSVC[i] == "Long-Green" and predictionDT[
                i] == "Long-Green" and predictionLR[i] == "Long-Green":
                if post_data[1] == "Long-Green" and post_data[3] != "Long-Long-Green-Green":
                    ai_row = [post_data[0], post_data[1], post_data[3], predictionRF[i], predictionSVC[i],
                              predictionDT[i], predictionLR[i], totalRecord, callChance, putChance, "AA1", "CALL"]
                    telegram_ai_array.append(ai_row)
            if predictionRF[i] == "Long-Green" and predictionSVC[i] == "Long-Green" and predictionDT[
                i] == "Long-Green" and predictionLR[i] == "Long-Red":
                if post_data[1] == "Long-Red" and post_data[3] != "Long-Long-Red-Red":
                    ai_row = [post_data[0], post_data[1], post_data[3], predictionRF[i], predictionSVC[i],
                              predictionDT[i], predictionLR[i], totalRecord, callChance, putChance, "AA2", "PUT"]
                    telegram_ai_array.append(ai_row)
            i = i + 1



    if len(overall_csv) != 0:
        file_path = f'data/predict{config_path_extension}/{input_date}_prediction.csv'
        header = ['Symbol', 'BUY Pattern(30)', 'BUY Pattern(15)', 'Trend', '1st Band', '2nd Band',
                  'Jump Up', 'Jump Down','Type','Predict(RF)',"Predict(SVC)","Predict(DT)","Predict(LR)","#Record","CALL Chance","PUT Chance"]
        full_array = np.vstack([header, overall_csv])
        np.savetxt(file_path, full_array, delimiter=',', fmt='%s')
        print(f"Array exported to {file_path} successfully.")
        model.add_output(f"Array exported to {file_path} successfully.")
    else:
        print(f"No Data Updated.")
        model.add_output(f"No Data Updated.")

def execute_predictAnalysis(input_date, model):
    global symbol
    global overall_csv
    global full_array
    global date
    global folder_path

    overall_csv = []
    full_array = []

    pre_date_csv = pd.read_csv(f'data/post-analysis{config_path_extension}/{input_date}_beforeMarket.csv')
    post_datas = pre_date_csv.values
    numsLongGreen = 0
    numsLongRed = 0
    buyType = "None"
    for post_data in post_datas:
        if post_data[0] == "QQQ":
            patternQQQ = post_data[1].split('-')
            bigPatternQQQ = post_data[3].split('-')
            trendQQQ = post_data[8]
            highQQQ = post_data[11]
            lowQQQ = post_data[12]
            jumpUpQQQ = post_data[13]
            jumpDownQQQ = post_data[14]
        if post_data[0] == "SPY":
            patternSPY = post_data[1].split('-')
            bigPatternSPY = post_data[3].split('-')
            trendSPY = post_data[8]
            highSPY = post_data[11]
            lowSPY = post_data[12]
            jumpUpSPY = post_data[13]
            jumpDownSPY = post_data[14]
        if "Long-Red" in post_data[1]:
            numsLongRed = numsLongRed + 1
        if "Long-Green" in post_data[1]:
            numsLongGreen = numsLongGreen + 1
    if numsLongGreen > numsLongRed:
        buyType = "CALL"
    else:
        buyType = "PUT"
    temp_data = []
    for post_data in post_datas:
        if post_data[0] != "SPY" and post_data[0] != "QQQ" and "Null" not in post_data[1] and "Null" not in post_data[3]:
            firstBB = post_data[9]
            secondBB = post_data[10]
            pattern = post_data[1].split('-')
            bigPattern = post_data[3].split('-')
            row = [pattern[0],pattern[1],bigPattern[0],bigPattern[1],bigPattern[2],bigPattern[3],
                   firstBB,secondBB,post_data[8],post_data[13],post_data[14], buyType,
                   trendSPY, trendQQQ, highSPY, lowSPY, highQQQ, lowQQQ, jumpUpSPY, jumpDownSPY,
                   jumpUpQQQ, jumpDownQQQ, patternSPY[0], patternSPY[1], patternQQQ[0], patternQQQ[1],
                   bigPatternSPY[0],bigPatternSPY[1],bigPatternSPY[2],bigPatternSPY[3],
                   bigPatternQQQ[0],bigPatternQQQ[1],bigPatternQQQ[2],bigPatternQQQ[3]]
            temp_data.append(row)
    model.add_output(f"Predicting ...")
    executeFullMultipleMachineLearning(buyType,temp_data,model)
    i = 0
    for post_data in post_datas:
        if post_data[0] != "SPY" and post_data[0] != "QQQ" and "Null" not in post_data[1] and "Null" not in post_data[3]:
            new_row = [post_data[0],post_data[1],post_data[3],post_data[8],post_data[9],
                       post_data[10],post_data[13],post_data[14],buyType,
                       predictionRF[i], predictionSVC[i], predictionDT[i], predictionLR[i]]
            overall_csv.append(new_row)
            i = i + 1


    if len(overall_csv) != 0:
        file_path = f'data/predict{config_path_extension}/{input_date}_prediction.csv'
        header = ['Symbol', 'BUY Pattern(30)', 'BUY Pattern(15)', 'Trend', '1st Band', '2nd Band',
                  'Jump Up', 'Jump Down','Type','Predict(RF)',"Predict(SVC)","Predict(DT)","Predict(LR)"]
        full_array = np.vstack([header, overall_csv])
        np.savetxt(file_path, full_array, delimiter=',', fmt='%s')
        print(f"Array exported to {file_path} successfully.")
        model.add_output(f"Array exported to {file_path} successfully.")
    else:
        print(f"No Data Updated.")
        model.add_output(f"No Data Updated.")


def execute_fullList(input_date, model):
    global symbol
    global overall_csv
    global full_array
    global date
    global folder_path

    overall_csv = []
    full_array = []

    for file in os.listdir(f'data/earning{config_path_extension}/'):
        if os.path.isfile(os.path.join(f'data/earning{config_path_extension}/', file)):
            dateK = file.split('_')[0]
            pre_date_csv = pd.read_csv(f'data/earning{config_path_extension}/{dateK}_earning.csv')
            post_datas = pre_date_csv.values
            performance_csv = pd.read_csv(f'data/performance{config_path_extension}/performance_train_data.csv')
            performances = performance_csv.values
            for performance in performances:
                for post_data in post_datas:
                    if performance[0] == dateK:
                        result = "Null"
                        if "CALL" in performance[2]:
                            if float(post_data[11]) > 0:
                                result = "Win"
                            else:
                                result = "Lost"
                        if "PUT" in performance [2]:
                            if float(post_data[11]) < 0:
                                result = "Win"
                            else:
                                result = "Lost"
                        row = [dateK,post_data[0],post_data[1],post_data[2],post_data[3],post_data[4],post_data[5],post_data[6],post_data[7],
                               post_data[8],post_data[9],post_data[10],post_data[11], performance[2],result, performance[8],performance[9],
                               performance[11],performance[12],performance[13],performance[14],performance[15],performance[16],performance[17],performance[18],
                               performance[20],performance[21],performance[22],performance[23],performance[24]]
                        overall_csv.append(row)

    if len(overall_csv) != 0:
        file_path = f'data/performance{config_path_extension}/train_data_full_list.csv'
        header = ['Date','Symbol', 'Buy Price','Sell Price', 'BUY Pattern(30)', 'BUY Pattern(15)', '1st Band', '2nd Band', 'Trend',
                  'Jump Up', 'Jump Down', 'SELL Pattern','Earning','Type','Result','SPY Trend','QQQ Trend','High(SPY)','Low(SPY)','High(QQQ)','Low(QQQ)','Up(SPY)','Down(SPY)','Up(QQQ)','Down(QQQ)','GR Ratio','SPY(30)','QQQ(30)','SPY(15)','QQQ(15)']
        full_array = np.vstack([header, overall_csv])
        np.savetxt(file_path, full_array, delimiter=',', fmt='%s')
        print(f"Array exported to {file_path} successfully.")
        model.add_output(f"Array exported to {file_path} successfully.")
    else:
        print(f"No Data Updated.")
        model.add_output(f"No Data Updated.")


def executeMultipleMachineLearning(types,data):
    df2 = pd.read_csv(f'data/performance{config_path_extension}/performance_train_data.csv')
    npp_array = df2.iloc[1:].values
    filter_array = []
    expected_output = []
    df2 = pd.read_csv(f'data/performance{config_path_extension}/performance_train_data.csv')
    npp_array = df2.iloc[1:].values
    filter_array = []
    expected_output = []
    for row in npp_array:
        if pd.notna(row[4]) and pd.notna(row[21]) and pd.notna(row[11]) and pd.notna(row[8]) and pd.notna(row[14]) and 'Null' not in row[23] and 'Null' not in row[24]:
            patternSPY = row[21].split('-')
            patternQQQ = row[22].split('-')
            bigPatternSPY = row[23].split('-')
            bigPatternQQQ = row[24].split('-')
            new_row = [row[2], row[8], row[9], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                       patternSPY[0], patternSPY[1], patternQQQ[0], patternQQQ[1], bigPatternSPY[0], bigPatternSPY[1],
                       bigPatternSPY[2], bigPatternSPY[3], bigPatternQQQ[0], bigPatternQQQ[1], bigPatternQQQ[2],
                       bigPatternQQQ[3]]
            filter_array.append(new_row)
            expected_output.append(row[4])

    df = pd.DataFrame(filter_array)
    df[0] = df[0].map({'CALL': 0, 'PUT': 1})
    df[1] = df[1].map({'Upward': 0, 'Downward': 1, 'Sideway': 2})
    df[2] = df[2].map({'Upward': 0, 'Downward': 1, 'Sideway': 2})
    df[3] = df[3].map({True: 0, False: 1})
    df[4] = df[4].map({True: 0, False: 1})
    df[5] = df[5].map({True: 0, False: 1})
    df[6] = df[6].map({True: 0, False: 1})
    df[7] = df[7].map({True: 0, False: 1})
    df[8] = df[8].map({True: 0, False: 1})
    df[9] = df[9].map({True: 0, False: 1})
    df[10] = df[10].map({True: 0, False: 1})
    df[11] = df[11].map({'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3})
    df[12] = df[12].map({'Green': 0, 'Red': 1})
    df[13] = df[13].map({'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3})
    df[14] = df[14].map({'Green': 0, 'Red': 1})
    df[15] = df[15].map({'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3})
    df[16] = df[16].map({'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3})
    df[17] = df[17].map({'Green': 0, 'Red': 1})
    df[18] = df[18].map({'Green': 0, 'Red': 1})
    df[19] = df[19].map({'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3})
    df[20] = df[20].map({'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3})
    df[21] = df[21].map({'Green': 0, 'Red': 1})
    df[22] = df[22].map({'Green': 0, 'Red': 1})

    patternSPY = data[3].split('-')
    patternQQQ = data[4].split('-')
    bigPatternSPY = data[17].split('-')
    bigPatternQQQ  = data[18].split('-')
    new_data = pd.DataFrame([
        [types, data[5], data[6], data[9], data[10], data[11], data[12], data[13], data[14], data[15], data[16], patternSPY[0], patternSPY[1], patternQQQ[0], patternQQQ[1], bigPatternSPY[0], bigPatternSPY[1],bigPatternSPY[2], bigPatternSPY[3], bigPatternQQQ[0], bigPatternQQQ[1], bigPatternQQQ[2], bigPatternQQQ[3]]

    ])
    new_data_encoded = new_data.apply(
        lambda x: x.map({'CALL': 0, 'PUT': 1,
                        'Upward': 0, 'Downward': 1, 'Sideway': 2,
                        'Upward': 0, 'Downward': 1, 'Sideway': 2,
                        True: 0, False: 1,
                        True: 0, False: 1,
                        True: 0, False: 1,
                        True: 0, False: 1,
                        True: 0, False: 1,
                        True: 0, False: 1,
                        True: 0, False: 1,
                        True: 0, False: 1,
                    'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3,
                    'Green': 0, 'Red': 1,
                    'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3,
                    'Green': 0, 'Red': 1,
                    'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3,
                    'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3,
                    'Green': 0, 'Red': 1,
                    'Green': 0, 'Red': 1,
                    'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3,
                    'Long': 0, 'Short': 1, 'Bottom': 2, 'Upper': 3,
                    'Green': 0, 'Red': 1,
                    'Green': 0, 'Red': 1
                    }))

    model = RandomForestClassifier()
    model.fit(df, expected_output)
    prediction = model.predict(new_data_encoded)
    print(f'Random Forest: {prediction}')
    telegram_ai_array.append(["Random Forest",prediction[0]])
    model = DecisionTreeClassifier()
    model.fit(df, expected_output)
    prediction = model.predict(new_data_encoded)
    print(f'Decision Tree: {prediction}')
    telegram_ai_array.append(["Decision Tree",prediction[0]])
    model = SVC()
    model.fit(df, expected_output)
    prediction = model.predict(new_data_encoded)
    print(f'SVC: {prediction}')
    telegram_ai_array.append(["SVC",prediction[0]])
    model = LogisticRegression()
    model.fit(df, expected_output)
    prediction = model.predict(new_data_encoded)
    print(f'Logistic Regression: {prediction}')
    telegram_ai_array.append(["Logistic Regression",prediction[0]])

def executeFUTU(symbol,signal,trend, model):
    global isBuySignal
    global buyPattern
    global isBuySignalMini
    global buyPatternMini

    mask = pre_data_csv.iloc[:, 0] == symbol

    pre_data = pre_data_csv[mask].values.tolist()
    numSLTPA = 0
    numSWTPA = 0
    numSLTEMA = 0
    numSWTEMA = 0
    numSLTH = 0
    numSWTH = 0
    numP = 0
    numSLTPA2 = 0
    numSWTPA2 = 0
    numSLTEMA2 = 0
    numSWTEMA2 = 0
    numSLTH2 = 0
    numSWTH2 = 0
    numP2 = 0

    if len(pre_data) != 0:

        pre_data = pre_data[0]

        ret_sub, err_message = quote_ctx.subscribe([f'US.{pre_data[0]}'], [SubType.K_30M], subscribe_push=False)
        ret_sub2, err_message2 = quote_ctx.subscribe([f'US.{pre_data[0]}'], [SubType.K_15M], subscribe_push=False)

        if ret_sub == RET_OK and ret_sub2 == RET_OK:

            is_time = True

            while (is_time):

                ret, data = quote_ctx.get_cur_kline(f'US.{pre_data[0]}', 26, SubType.K_30M, AuType.QFQ)
                ret2, data2 = quote_ctx.get_cur_kline(f'US.{pre_data[0]}', 26, SubType.K_15M, AuType.QFQ)
                # assume data=[[09:31:00,400],[09:32:00,500]]
                if ret == RET_OK and ret2 == RET_OK:

                    window_size = 20
                    num_std = 2
                    rolling_mean = data['close'].rolling(window=window_size).mean()
                    rolling_std = data['close'].rolling(window=window_size).std()
                    data_upper_band = rolling_mean + (rolling_std * num_std)
                    data_lower_band = rolling_mean - (rolling_std * num_std)
                    rolling_mean2 = data2['close'].rolling(window=window_size).mean()
                    rolling_std2 = data2['close'].rolling(window=window_size).std()
                    data_upper_band2 = rolling_mean2 + (rolling_std2 * num_std)
                    data_lower_band2 = rolling_mean2 - (rolling_std2 * num_std)
                    isBuySignal = False
                    buyPattern = ""
                    buyAlready = False
                    limitedTime = "10:"
                    firstBB = "None"
                    secondBB = "None"
                    overHigh2 = False
                    overLow2 = False
                    jumpUp = False
                    jumpDown = False

                    if "10:00:00" in data['time_key'][len(data) - 2]:
                        # if True: #testing
                        if True:
                            # if data['low'][len(data) - 2] > data['low'][len(data) - 3]: #testing
                            print(f"{symbol}: Ready to CALL... Please Wait the buy signal...")
                            while buyAlready == False:
                                if ret == RET_OK:
                                    isBuySignal = False
                                    buyPattern = "Null"
                                    buy_chance = 0
                                    defineCandleSticksFUTU(data)
                                    callBuyConditionFUTU(data)
                                    if isBuySignal == True and limitedTime in lastTime:
                                        isBuySignalMini = False
                                        buyPatternMini = "Null"
                                        buy_chance_mini = 0
                                        defineCandleSticksFUTUMini(data2)
                                        callBuyConditionFUTUMini(data2)
                                        if lastClose > data_upper_band2[len(data2) - 2]:
                                            overHigh2 = True
                                        if lastClose < data_lower_band2[len(data2) - 2]:
                                            overLow2 = True
                                        if data2['high'][len(data2) - 4] < data2['low'][len(data2) - 3]:
                                            jumpUp = True
                                        if data2['low'][len(data2) - 4] > data2['high'][len(data2) - 3]:
                                            jumpDown = True
                                        if data2['close'][len(data2) - 3] > data_upper_band2[len(data2) - 3]:
                                            firstBB = "High"
                                        if data2['close'][len(data2) - 3] < data_lower_band2[len(data2) - 3]:
                                            firstBB = "Low"
                                        if data2['close'][len(data2) - 3] > data_upper_band2[len(data2) - 3] and data2['close'][len(data2) - 3] < data_lower_band2[len(data2) - 3]:
                                            firstBB = "Extreme"
                                        if data2['open'][len(data2) - 3] > data_upper_band2[len(data2) - 3] and data2['close'][len(data2) - 3] > data_upper_band2[len(data2) - 3]:
                                            firstBB = "OverHigh"
                                        if data2['open'][len(data2) - 3] < data_lower_band2[len(data2) - 3] and data2['close'][len(data2) - 3] < data_lower_band2[len(data2) - 3]:
                                            firstBB = "OverLow"
                                        if data2['close'][len(data2) - 2] > data_upper_band2[len(data2) - 2]:
                                            secondBB = "High"
                                        if data2['close'][len(data2) - 2] < data_lower_band2[len(data2) - 2]:
                                            secondBB = "Low"
                                        if data2['close'][len(data2) - 2] > data_upper_band2[len(data2) - 2] and data2['close'][len(data2) - 2] < data_lower_band2[len(data2) - 2]:
                                            secondBB = "Extreme"
                                        if data2['open'][len(data2) - 2] > data_upper_band2[len(data2) - 2] and data2['close'][len(data2) - 2] > data_upper_band2[len(data2) - 2]:
                                            secondBB = "OverHigh"
                                        if data2['open'][len(data2) - 2] < data_lower_band2[len(data2) - 2] and data2['close'][len(data2) - 2] < data_lower_band2[len(data2) - 2]:
                                            secondBB = "OverLow"
                                        abstracted_string = ''.join(word[0] for word in buyPattern.split('-'))
                                        abstracted_string_2 = ''.join(word[0] for word in buyPatternMini.split('-'))
                                        k = 0
                                        for head in headers:
                                            if f'{abstracted_string}' == head:
                                                buy_chance = pre_data[k]
                                            if f'SLT-PA-{abstracted_string}' == head:
                                                numSLTPA = pre_data[k]
                                            if f'SWT-PA-{abstracted_string}' == head:
                                                numSWTPA = pre_data[k]
                                            if f'SLT-EMA-{abstracted_string}' == head:
                                                numSLTEMA = pre_data[k]
                                            if f'SWT-EMA-{abstracted_string}' == head:
                                                numSWTEMA = pre_data[k]
                                            if f'SLT-H-{abstracted_string}' == head:
                                                numSLTH = pre_data[k]
                                            if f'SWT-H-{abstracted_string}' == head:
                                                numSWTH = pre_data[k]
                                            if f'NUM-{abstracted_string}' == head:
                                                numP = pre_data[k]
                                            if f'{abstracted_string_2}' == head:
                                                buy_chance_mini = pre_data[k]
                                            if f'SLT-PA-{abstracted_string_2}' == head:
                                                numSLTPA2 = pre_data[k]
                                            if f'SWT-PA-{abstracted_string_2}' == head:
                                                numSWTPA2 = pre_data[k]
                                            if f'SLT-EMA-{abstracted_string_2}' == head:
                                                numSLTEMA2 = pre_data[k]
                                            if f'SWT-EMA-{abstracted_string_2}' == head:
                                                numSWTEMA2 = pre_data[k]
                                            if f'SLT-H-{abstracted_string_2}' == head:
                                                numSLTH2 = pre_data[k]
                                            if f'SWT-H-{abstracted_string_2}' == head:
                                                numSWTH2 = pre_data[k]
                                            if f'NUM-{abstracted_string_2}' == head:
                                                numP2 = pre_data[k]
                                            k = k + 1
                                        print(
                                            f"{symbol} - {data['time_key'][len(data) - 2]} : {lastClose} - CALL!, Pattern: {buyPattern} ({buy_chance}), (Chance: {buy_chance_mini:.2g} with Earning {pre_data[3]}")
                                        model.add_output(
                                            f"{symbol} - {data['time_key'][len(data) - 2]} : {lastClose} - CALL!, Pattern: {buyPattern} ({buy_chance}), (Chance: {buy_chance_mini:.2g} with Earning {pre_data[3]}")
                                        row = [pre_data[0], buyPattern, buy_chance,buyPatternMini,buy_chance_mini,signal,
                                                       pre_data[1], pre_data[3],trend,firstBB,secondBB,overHigh2,overLow2,jumpUp,jumpDown,
                                               numSLTPA, numSWTPA, numSLTEMA, numSWTEMA, numSLTH, numSWTH, numP,
                                                       numSLTPA2, numSWTPA2, numSLTEMA2, numSWTEMA2, numSLTH2, numSWTH2, numP2,
                                                pre_data[11]]
                                        overall_csv.append(row)
                                        buyAlready = True
                                        break
                                    elif isBuySignal == False and limitedTime in lastTime:
                                        break
                                        print(f"{symbol} - Waiting data of next minutes...")
                                        timemodule.sleep(5)
                                        ret, data = quote_ctx.get_cur_kline(f'US.{pre_data[0]}', 26, SubType.K_30M,
                                                                            AuType.QFQ)
                                        ret2, data2 = quote_ctx.get_cur_kline(f'US.{pre_data[0]}', 26, SubType.K_15M,
                                                                              AuType.QFQ)
                                    else:
                                        print(
                                            f"{symbol} - {data['time_key'][len(data) - 3]} - {data['time_key'][len(data) - 2]} : doesn't meet requirement. (Expired Time)'")
                                        model.add_output(
                                            f"{symbol} - {data['time_key'][len(data) - 3]} - {data['time_key'][len(data) - 2]} : doesn't meet requirement. (Expired Time)'")
                                        buyAlready = True
                                        break
                                    print("--------------")
                                    # model.add_output("--------------")

                        is_time = False

                    else:
                        if "10:" not in data['time_key'][len(data) - 2]:
                            is_time = False
                            break
                        print(f"Time {data['time_key'][len(data) - 1]} is not ready.")
                        model.add_output(f"The Time - {data['time_key'][len(data) - 1]} is not ready.")
                        timemodule.sleep(60)

                else:
                    print(f"Error: Connection Problem")
                    model.add_output(f"Error: Connection Problem")
    else:
        print("Stock Code Not Found.")
        model.add_output("Stock Code Not Found.")


def instantAnalysisFUTU(date, model):
    global pre_data_csv
    global overall_csv
    global futu_array
    global headers

    overall_csv = []
    input_date = datetime.strptime(date, "%Y-%m-%d")
    us_calendar = mcal.get_calendar('NYSE')
    previous_trading_day = input_date - timedelta(days=1)
    while len(us_calendar.valid_days(start_date=previous_trading_day, end_date=previous_trading_day)) <= 0:
        previous_trading_day -= timedelta(days=1)
    yesterday_date = previous_trading_day.strftime('%Y-%m-%d')

    try:
        pre_data_csv = pd.read_csv(f'data/ranking{config_path_extension}/{date}_list.csv')
        setup_csv = pd.read_csv(f'data/setup{config_path_extension}/{yesterday_date}_setup.csv')
        symbols = []

        pre_datas = pre_data_csv.values
        setup_datas = setup_csv.values
        headers = pre_data_csv.columns
        for pre_data in pre_datas:
            for setup_data in setup_datas:
                if setup_data[0] == pre_data[0]:
                    symbols.append([setup_data[0],setup_data[1],setup_data[2]])

        for symbol in symbols:
            executeFUTU(symbol[0],symbol[1],symbol[2], model)
            timemodule.sleep(0.3)

        chances_long_red = []
        chances_long_green = []
        row = []
        trendQQQ = "None"
        trendSPY = "None"
        jumpUpQQQ = "None"
        jumpDownQQQ = "None"
        jumpUpSPY = "None"
        jumpDownSPY = "None"
        overHighQQQ = "None"
        overHighSPY = "None"
        overLowQQQ = "None"
        overLowSPY = "None"
        patternQQQ = "None"
        patternSPY = "None"
        bigPatternQQQ = "None"
        bigPatternSPY = "None"
        lowestChanceLongRed = 0
        lowestSymbolLongRed = "None"
        highestChanceLongGreen = 0
        highestSymbolLongGreen = "None"
        for post_data in overall_csv:
            if post_data[0] == "SPY":
                trendSPY = post_data[8]
                patternSPY = post_data[1]
                bigPatternSPY = post_data[3]
                jumpUpSPY = post_data[13]
                jumpDownSPY = post_data[14]
                overHighSPY = post_data[11]
                overLowSPY = post_data[12]
            if post_data[0] == "QQQ":
                trendQQQ = post_data[8]
                bigPatternQQQ = post_data[3]
                patternQQQ = post_data[1]
                jumpUpQQQ = post_data[13]
                jumpDownQQQ = post_data[14]
                overHighQQQ = post_data[11]
                overLowQQQ = post_data[12]
            if post_data[1] == "Long-Red" and "Null" not in post_data[3] and float(post_data[4]) != 0.0:
                chances_long_red.append(post_data)
            if post_data[1] == "Long-Green" and "Null" not in post_data[3] and float(post_data[4]) != 1.0 and not post_data[3].startswith('Bottom'):
                chances_long_green.append(post_data)

        isCondition = 0
        if len(chances_long_red) > len(chances_long_green):  # put condition
            if ("Sideway" in trendSPY and "Sideway" in trendQQQ):
                if overLowSPY and overLowQQQ and jumpDownSPY and not jumpDownQQQ:
                    isCondition = 1
                if patternSPY == patternQQQ and 'Short' not in patternQQQ:
                    if 'Long-Long-Red-Red' in bigPatternSPY and 'Long-Long-Red-Red' in bigPatternQQQ:
                        isCondition = 1
                    if jumpUpSPY and jumpUpQQQ:
                        isCondition = 1
            if ("Upward" in trendSPY and "Downward" in trendQQQ):
                if "Long-Red" in patternQQQ and patternQQQ == patternSPY:
                    isCondition = 1
            if ("Sideway" in trendSPY and "Downward" in trendQQQ) or ("Downward" in trendSPY and "Sideway" in trendQQQ):
                if patternQQQ == patternSPY:
                    if ("Short-Red" in patternQQQ or "Short-Green" in patternQQQ) and jumpDownSPY:
                        isCondition = 1
                    if "Long-Red" in patternQQQ:
                        if not overLowSPY and overLowQQQ and jumpDownSPY and jumpDownQQQ:
                            isCondition = 1
                        if overLowSPY and overLowQQQ and not jumpDownSPY and jumpDownQQQ:
                            isCondition = 1
                        if overLowSPY and not overLowQQQ and jumpDownSPY and jumpDownQQQ:
                            isCondition = 1
                if "Upper-Red" in patternSPY and "Long-Red" in patternQQQ:
                    isCondition = 1
            if ("Sideway" in trendSPY and "Upward" in trendQQQ) or ("Upward" in trendSPY and "Sideway" in trendQQQ):
                if "Long-Red" in patternSPY and "Bottom-Red" in patternQQQ:
                    isCondition = 1
                if "Bottom-Red" in patternSPY and "Long-Red" in patternQQQ:
                    isCondition = 1
                if "Short-Red" in patternSPY and ("Upper-Red" in patternQQQ or "Bottom-Green" in patternQQQ):
                    isCondition = 1
            if ("Downward" in trendSPY and "Downward" in trendQQQ):
                if not jumpUpQQQ and not jumpUpSPY and not jumpDownQQQ and not jumpDownSPY:
                    if 'Short' not in patternQQQ and 'Short' not in patternSPY and 'Bottom' not in patternQQQ and 'Bottom' not in patternSPY:
                        if overLowSPY and overLowQQQ:
                            isCondition = 1
                if not overLowQQQ and not overLowSPY and not overHighQQQ and not overHighSPY:
                    if jumpUpQQQ and jumpUpSPY and patternQQQ == patternSPY and 'Red' in patternSPY and 'Bottom' not in patternSPY:
                        isCondition = 1
                    if jumpUpSPY and not jumpUpQQQ:
                        isCondition = 1
                if overLowQQQ and overLowSPY and jumpDownQQQ:
                    if jumpDownSPY and patternSPY == patternQQQ and (
                            'Long-Short' in bigPatternSPY and 'Long-Short' in bigPatternQQQ or 'Long-Upper' in bigPatternSPY and 'Long-Upper' in bigPatternQQQ):
                        isCondition = 1
                    if not jumpDownSPY:
                        isCondition = 1
                if overLowQQQ and jumpUpSPY and patternQQQ == patternSPY:
                    isCondition = 1
                if overHighQQQ and jumpDownSPY:
                    isCondition = 1
                if overHighSPY and not overHighQQQ and jumpUpQQQ and jumpUpSPY and 'Long-Green' not in patternSPY:
                    isCondition = 1
                if overHighSPY and overHighQQQ and jumpUpQQQ and jumpUpSPY:
                    isCondition = 1
                if overLowQQQ and not overLowSPY and jumpDownQQQ and not jumpDownSPY and patternQQQ == patternSPY:
                    isCondition = 1
                if not overHighSPY and overHighQQQ and jumpDownSPY:
                    isCondition = 1
                if jumpUpSPY and not jumpUpQQQ and not overHighSPY:
                    isCondition = 1
                if not jumpUpSPY and jumpUpQQQ and (
                        bigPatternQQQ.startswith("Long") or bigPatternSPY.startswith("Long")):
                    isCondition = 1
                if jumpDownSPY and not jumpDownQQQ and patternQQQ == patternSPY:
                    isCondition = 1
            if ("Upward" in trendSPY and "Upward" in trendQQQ):
                if jumpUpQQQ and jumpUpSPY and not (
                        overLowSPY or overHighQQQ) and 'Red' in patternQQQ and 'Red' in patternSPY and 'Upper-Short' not in bigPatternQQQ:
                    isCondition = 1
                if overLowQQQ and jumpUpSPY and not overHighSPY and not (jumpUpQQQ and overLowSPY):
                    isCondition = 1
                if overLowQQQ and not overLowSPY and jumpDownQQQ and not jumpDownSPY and 'Short' not in patternQQQ and 'Short' not in patternSPY:
                    isCondition = 1
                if overLowQQQ and overLowSPY and jumpDownQQQ and jumpDownSPY:
                    if not bigPatternQQQ.startswith('Long-Short') and not bigPatternSPY.startswith(
                            'Long-Short') and not bigPatternSPY.startswith('Bottom') and not (
                            bigPatternQQQ.startswith('Upper') and bigPatternSPY.startswith(
                            'Upper')) and 'Bottom' not in patternSPY:
                        isCondition = 1
                if overHighSPY and not overHighQQQ and not jumpUpQQQ and not jumpUpSPY and patternQQQ == patternSPY:
                    isCondition = 1
                if overHighQQQ and not (overHighSPY and jumpUpQQQ and jumpUpSPY) and (overLowQQQ or overLowSPY):
                    isCondition = 1
                if overLowSPY and not overLowQQQ and "Bottom" not in patternQQQ and "Bottom" not in patternSPY and "Long-Long-Green-Red" not in bigPatternQQQ:
                    isCondition = 1

        if len(chances_long_red) < len(chances_long_green):  # call condition
            if ("Sideway" in trendSPY and "Sideway" in trendQQQ):
                if not bigPatternSPY.startswith('Bottom') and not bigPatternQQQ.startswith(
                        'Bottom') and 'Short' not in patternSPY and patternQQQ == patternSPY:
                    if overHighQQQ and overHighSPY and not jumpUpQQQ:
                        isCondition = 1
                    if not overHighQQQ and not overHighSPY and jumpUpQQQ and jumpUpSPY:
                        isCondition = 1
                    if overHighQQQ and overHighSPY and jumpUpQQQ and jumpUpSPY and bigPatternQQQ == bigPatternSPY:
                        isCondition = 1
            if ("Upward" in trendSPY and "Downward" in trendQQQ):
                if "Long-Green" in patternQQQ and patternQQQ == patternSPY:
                    isCondition = 1
            if ("Sideway" in trendSPY and "Upward" in trendQQQ) or ("Upward" in trendSPY and "Sideway" in trendQQQ):
                if patternQQQ == patternSPY:
                    if jumpDownQQQ and jumpDownSPY and not bigPatternSPY.startswith(
                            "Bottom") and not bigPatternSPY.startswith("Upper"):
                        isCondition = 1
                    if overHighSPY and not overHighQQQ and jumpUpSPY and jumpUpQQQ:
                        isCondition = 1
                    if overHighSPY and overHighQQQ and jumpUpSPY and jumpUpQQQ and bigPatternQQQ.startswith("Short"):
                        isCondition = 1
            if ("Sideway" in trendSPY and "Downward" in trendQQQ) or ("Downward" in trendSPY and "Sideway" in trendQQQ):
                if (jumpDownQQQ or jumpDownSPY) and not overHighSPY and not overLowQQQ:
                    isCondition = 1
                if not overHighQQQ and overLowQQQ and not jumpDownSPY:
                    isCondition = 1
                if overLowSPY and overLowQQQ:
                    isCondition = 1
                if overLowSPY and overHighQQQ and jumpUpQQQ:
                    isCondition = 1
                if not jumpUpQQQ and not jumpUpSPY and not jumpDownQQQ and not jumpDownSPY:
                    if "Red" not in patternQQQ and "Red" not in patternSPY and "Bottom" not in patternQQQ and "Bottom" not in patternSPY and not bigPatternSPY.startswith(
                            'Upper') and not bigPatternSPY.startswith('Short'):
                        isCondition = 1
            if ("Downward" in trendSPY and "Downward" in trendQQQ):
                if overHighSPY and overHighQQQ and jumpUpQQQ and jumpUpSPY:
                    if not bigPatternQQQ.startswith("Bottom") and not bigPatternSPY.startswith(
                            "Bottom") and not bigPatternQQQ.startswith("Upper-Long") and not bigPatternSPY.startswith(
                            "Upper-Long"):
                        isCondition = 1
                if overHighSPY and overHighQQQ and jumpDownQQQ and jumpDownSPY and patternQQQ == patternSPY:
                    isCondition = 1
                if overHighSPY and not overHighQQQ and not jumpUpSPY and not jumpDownSPY:
                    isCondition = 1
                if not overHighSPY and overHighQQQ and not (jumpDownQQQ and jumpDownSPY) and (
                        jumpDownQQQ or overLowSPY):
                    isCondition = 1
                if jumpDownQQQ and jumpDownSPY and not overHighSPY and not overHighQQQ and not overLowSPY and not overLowQQQ and "Green" in patternQQQ and "Green" in patternSPY and not (
                        "Short" in patternQQQ and "Short" in patternSPY):
                    isCondition = 1
                if overLowSPY and overLowQQQ and patternQQQ == patternSPY and not overHighSPY:
                    isCondition = 1
                if jumpUpSPY and not jumpUpQQQ and patternQQQ == patternSPY:
                    isCondition = 1
                if not jumpUpSPY and jumpUpQQQ and overHighSPY and overHighQQQ:
                    isCondition = 1
                if overLowSPY and not overLowQQQ and overHighQQQ and jumpUpSPY:
                    isCondition = 1
                if not overLowSPY and overLowQQQ and not jumpDownSPY:
                    isCondition = 1
                if not jumpDownSPY and jumpDownQQQ and not overLowQQQ and 'Green' in patternSPY and 'Green' in patternQQQ:
                    isCondition = 1
            if ("Upward" in trendSPY and "Upward" in trendQQQ):
                if overHighSPY and overHighQQQ and jumpUpQQQ and jumpUpSPY and patternQQQ == patternSPY and not (
                        'Long-Long' in bigPatternSPY and 'Long-Long' in bigPatternQQQ):
                    isCondition = 1
                if not overHighSPY and not overHighQQQ and not overLowSPY and not jumpDownSPY and not jumpDownQQQ and 'Red' not in patternQQQ and 'Red' not in patternSPY:
                    isCondition = 1
                if not overHighSPY and overHighQQQ and not jumpUpQQQ and not (
                        jumpDownSPY and jumpDownQQQ) and not jumpUpSPY:
                    isCondition = 1
                if not overHighQQQ and overHighSPY and patternQQQ == patternSPY and "Upper-Green" not in patternSPY and 'Long-Long' not in bigPatternSPY:
                    isCondition = 1
                if jumpUpQQQ and jumpUpSPY and overHighSPY and not overHighQQQ:
                    if "Short-Short" not in bigPatternSPY and "Short-Short" not in bigPatternQQQ and "Upper-Green" not in patternSPY and "Upper-Green" not in patternQQQ:
                        isCondition = 1
                if not jumpDownSPY and jumpDownQQQ and patternQQQ == patternSPY and "Long-Green" in patternSPY:
                    isCondition = 1
                if jumpDownSPY and not jumpDownQQQ and patternQQQ == patternSPY and "Short-Green" not in patternSPY:
                    isCondition = 1

        if isCondition == 1:

            if chances_long_red and len(chances_long_red) > len(chances_long_green):
                filtered_chances_long_red = [x for x in chances_long_red]
                if filtered_chances_long_red:
                    lowestChanceLongRed = min(filtered_chances_long_red, key=lambda x: x[4])[4]
                    lowestSymbolLongRed = min(filtered_chances_long_red, key=lambda x: x[4])[0]
                    lowestTrendLongRed = min(filtered_chances_long_red, key=lambda x: x[4])[8]
                    lowestPatternLongRed = min(filtered_chances_long_red, key=lambda x: x[4])[3]
                    print(f'{lowestSymbolLongRed} with {lowestChanceLongRed} with {lowestPatternLongRed} with {patternSPY} with {patternQQQ}')
                    row = [lowestSymbolLongRed, lowestChanceLongRed, lowestPatternLongRed, patternSPY, patternQQQ,
                           trendSPY, trendQQQ, "PUT", lowestTrendLongRed, overHighSPY, overHighQQQ, overLowSPY,
                           overLowQQQ, jumpUpSPY, jumpDownSPY, jumpUpQQQ, jumpDownQQQ, bigPatternSPY, bigPatternQQQ,
                           f'{len(chances_long_green)}:{len(chances_long_red)}']
                    telegram_instant_array.append(row)
            if chances_long_green and len(chances_long_red) < len(chances_long_green):
                filtered_chances_long_green = [x for x in chances_long_green]
                if filtered_chances_long_green:
                    highestChanceLongGreen = max(filtered_chances_long_green, key=lambda x: x[4])[4]
                    highestSymbolLongGreen = max(filtered_chances_long_green, key=lambda x: x[4])[0]
                    highestTrendLongGreen = max(filtered_chances_long_green, key=lambda x: x[4])[8]
                    highestPatternLongGreen = max(filtered_chances_long_green, key=lambda x: x[4])[3]
                    print(f'{highestSymbolLongGreen} with {highestChanceLongGreen} with {highestPatternLongGreen} with {patternSPY} with {patternQQQ}')
                    row = [highestSymbolLongGreen, highestChanceLongGreen, highestPatternLongGreen, patternSPY,
                           patternQQQ, trendSPY, trendQQQ, "CALL", highestTrendLongGreen, overHighSPY, overHighQQQ,
                           overLowSPY, overLowQQQ, jumpUpSPY, jumpDownSPY, jumpUpQQQ, jumpDownQQQ, bigPatternSPY,
                           bigPatternQQQ, f'{len(chances_long_green)}:{len(chances_long_red)}']
                    telegram_instant_array.append(row)
        else:
            row = ['None', 0, 'None', patternSPY, patternQQQ, trendSPY, trendQQQ, "None", "None", overHighSPY,
                   overHighQQQ, overLowSPY, overLowQQQ, jumpUpSPY, jumpDownSPY, jumpUpQQQ, jumpDownQQQ, bigPatternSPY,
                   bigPatternQQQ, f'{len(chances_long_green)}:{len(chances_long_red)}']
            telegram_instant_array.append(row)

        if len(chances_long_red) > len(chances_long_green):
            executeMultipleMachineLearning("PUT", row)
        else:
            executeMultipleMachineLearning("CALL", row)

        if len(overall_csv) != 0:
            rearranged_array = sorted(overall_csv, key=lambda x: float(x[4]), reverse=True)
            file_path = f'data/post-analysis(futu){config_path_extension}/{date}_beforeMarket.csv'
            header = ['Symbol', 'Buy Pattern (30)', 'Pattern Chance (30)', 'Buy Pattern (15)', 'Pattern Chance (15)',
                      'Signal','Total Chance', 'Earning Probability',
                      'Trend', '1st BBand', '2nd BBand',
                      'Over High(15)', 'Over Low(15)', 'Jump Up', 'Jump Down',
                      'SLT-PA(30)', 'SWT-PA(30)', 'SLT-EMA(30)',
                      'SWT-EMA(30)', 'SLT-H(30)', 'SWT-H(30)', 'PT(30)', 'SLT-PA(15)', 'SWT-PA(15)', 'SLT-EMA(15)',
                      'SWT-EMA(15)', 'SLT-H(15)', 'SWT-H(15)', 'PT(15)', 'Total Record']
            futu_array = np.vstack([header, rearranged_array])
            np.savetxt(file_path, futu_array, delimiter=',', fmt='%s')
            print(f"Array exported to {file_path} successfully.")
            model.add_output(f"Array exported to {file_path} successfully.")
        else:
            print(f"No Data Updated.")
            model.add_output(f"No Data Updated.")
    except FileNotFoundError:
        model.add_output(f"The file '{date}_list.csv' does not exist.")


class DiagramWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()

        # Create a QLabel for displaying the diagram
        self.label = QLabel()
        self.layout.addWidget(self.label)

        # Set the layout for the widget
        self.setLayout(self.layout)

    def update_diagram(self, index, symbol, postDate):
        selected_date = postDate
        if "202" not in selected_date:  # handle post-analysis data
            symbol = selected_date
            selected_date = postDate
        input_date = datetime.strptime(selected_date, "%Y-%m-%d")
        month_format = input_date.strftime("%Y-%m")
        us_calendar = mcal.get_calendar('NYSE')
        previous_trading_day = input_date - timedelta(days=1)
        while len(us_calendar.valid_days(start_date=previous_trading_day, end_date=previous_trading_day)) <= 0:
            previous_trading_day -= timedelta(days=1)
        yesterday_date = previous_trading_day.strftime('%Y-%m-%d')

        dates = []
        opens = []
        highs = []
        lows = []
        closes = []
        emas = []
        macds = []

        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=30min&outputsize=full&apikey={api_key}&month={month_format}&entitlement=delayed"
        response = requests.get(url)
        url_ema_10 = f"https://www.alphavantage.co/query?function=EMA&symbol={symbol}&month={month_format}&interval=30min&time_period=5&series_type=close&apikey={api_key}&entitlement=delayed"
        response2 = requests.get(url_ema_10)
        if response.status_code == 200 and response2.status_code == 200:
            data_temp = response.json()
            time_series = data_temp['Time Series (30min)']
            data_ema = response2.json()
            ema_series = data_ema['Technical Analysis: EMA']
            price_1 = 0.0
            price_1_low = 0.0
            price_1_high = 0.0
            price_1_open = 0.0
            price_3 = 0.0
            price_3_low = 0.0
            price_3_high = 0.0
            price_3_close = 0.0
            price_4 = 0.0
            price_4_low = 0.0
            price_4_high = 0.0
            price_4_close = 0.0
            time_1 = ""
            time_3 = ""
            time_4 = ""
            verify_array = []
            verify_array_format = "00"
            num_of_minute = 10
            row = [f'10:30:00', 0.0, '', 0.0, 0.0, 0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0,
                   0.0]
            verify_array.append(row)
            hours = 11
            for i in range(num_of_minute):
                if int(verify_array_format) == 60:
                    hours = hours + 1
                    verify_array_format = "00"
                row = [f'{hours}:{verify_array_format}:00', 0.0, '', 0.0, 0.0, 0.0, 0.0, 0.0,
                       0.0, 0.0, 0.0, 0.0,
                       0.0]  # time, closed, date, low, SMA-5, high, EMA-5, SMA-10, EMA-10, open, macd, rsi, SMA-20
                verify_array.append(row)
                verify_array_format = int(verify_array_format) + 30
            for timestamp, values in time_series.items():
                if f"{selected_date} 09:00:00" in timestamp:
                    price_1 = float(values['4. close'])
                    price_1_low = float(values['3. low'])
                    price_1_high = float(values['2. high'])
                    price_1_open = float(values['1. open'])
                    time_1 = timestamp
                    if price_4 != 0.0 and price_3 != 0.0 and verify_array[9][1] != 0.0 and price_1 != 0.0:
                        ema_values_1 = 0.0
                        ema_values_3 = 0.0
                        ema_values_4 = 0.0
                        for timestamp_ema, values_ema in ema_series.items():
                            if timestamp_ema in time_1:
                                ema_values_1 = float(values_ema['EMA'])
                            if timestamp_ema in time_4:
                                ema_values_4 = float(values_ema['EMA'])
                            if timestamp_ema in time_3:
                                ema_values_3 = float(values_ema['EMA'])
                            for verify in verify_array:
                                if timestamp_ema in verify[2]:
                                    verify[6] = float(values_ema['EMA'])
                            if ema_values_1 != 0.0 and ema_values_3 != 0.0 and verify_array[9][
                                6] != 0.0 and ema_values_4 != 0.0:
                                break
                        for m in range(len(verify_array)):
                            if m > 0:
                                this_min_date = verify_array[m][2][:10]
                                before_min_date = verify_array[m - 1][2][:10]
                                if this_min_date != before_min_date:
                                    verify_array[m][1] = verify_array[m - 1][9]
                                    datetime_obj = datetime.strptime(verify_array[m - 1][2], '%Y-%m-%d %H:%M:%S')
                                    next_minute = datetime_obj + timedelta(minutes=1)
                                    next_minute_str = next_minute.strftime('%Y-%m-%d %H:%M:%S')
                                    verify_array[m][2] = next_minute_str
                                    verify_array[m][3] = verify_array[m - 1][9]
                                    verify_array[m][5] = verify_array[m - 1][9]
                                    verify_array[m][9] = verify_array[m - 1][9]
                                    verify_array[m][6] = verify_array[m - 1][6]
                        dates.append("16:00:00")
                        opens.append(price_1_open)
                        highs.append(price_1_high)
                        lows.append(price_1_low)
                        closes.append(price_1)
                        dates.append("09:30:00")
                        opens.append(price_4)
                        highs.append(price_4_high)
                        lows.append(price_4_low)
                        closes.append(price_4_close)
                        dates.append("10:00:00")
                        opens.append(price_3)
                        highs.append(price_3_high)
                        lows.append(price_3_low)
                        closes.append(price_3_close)
                        for verify in verify_array:
                            dates.append(verify[0])
                            opens.append(verify[1])
                            highs.append(verify[5])
                            lows.append(verify[3])
                            closes.append(verify[9])
                        emas.append(ema_values_1)
                        emas.append(ema_values_4)
                        emas.append(ema_values_3)
                        for verify in verify_array:
                            emas.append(verify[6])
                        break
                for verify in verify_array:
                    if verify[0] in timestamp:
                        verify[1] = float(values['1. open'])
                        verify[2] = timestamp
                        verify[3] = float(values['3. low'])
                        verify[5] = float(values['2. high'])
                        verify[9] = float(values['4. close'])
                if f"{selected_date} 10:00:00" in timestamp:
                    # print(f"{timestamp} : {values['1. open']}")
                    price_3 = float(values['1. open'])
                    price_3_low = float(values['3. low'])
                    price_3_high = float(values['2. high'])
                    price_3_close = float(values['4. close'])
                    time_3 = timestamp
                if f"{selected_date} 09:30:00" in timestamp:
                    # print(f"{timestamp} : {values['1. open']}")
                    price_4 = float(values['1. open'])
                    price_4_low = float(values['3. low'])
                    price_4_high = float(values['2. high'])
                    price_4_close = float(values['4. close'])
                    time_4 = timestamp

        # testing for price pattern dictionary
        if dates:
            dates.pop(0)
            opens.pop(0)
            highs.pop(0)
            lows.pop(0)
            closes.pop(0)
            emas.pop(0)

        # Create a custom candlestick chart using matplotlib
        fig, ax = plt.subplots()

        try:
            history_csv = pd.read_csv(f'data/history{config_path_extension}/{symbol}.csv')
            history = history_csv.values
            time_set = ['09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00',
                        '14:30', '15:00', '15:30']
            for i in range(len(history)):
                if history[i][0] == selected_date:
                    buy_time = 1
                    minutes_part = history[i][5]
                    if str(history[i][5]) == 'nan':
                        minutes_part = history[i][10]
                    sell_time = 3
                    for j in range(len(time_set)):
                        if time_set[j] in minutes_part:
                            sell_time = j
                            break
                    ax.scatter(buy_time, lows[buy_time] * 0.9995, color='purple', marker='^', s=150, label='Buy Signal',
                               zorder=5)
                    ax.scatter(sell_time, highs[sell_time] * 1.0005, color='purple', marker='v', s=150,
                               label='Sell Signal', zorder=5)
                    break
        except FileNotFoundError:
            pass

        for i in range(len(dates)):
            if opens[i] < closes[i]:
                color = 'green'
            else:
                color = 'red'

            ax.plot([i, i], [lows[i], highs[i]], color='black', linewidth=1)
            ax.plot([i, i], [opens[i], closes[i]], color=color, linewidth=7)

        ax.plot(range(len(dates)), emas, color='blue', label='EMA-10', linewidth=2)

        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels(dates, rotation=45, fontsize=8)
        ax.set_title(f'{symbol} - {selected_date} Candlestick (30mins)')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')

        # Convert the diagram to a QPixmap for display
        buffer = BytesIO()
        plt.savefig(f'data/graph{config_path_extension}/{symbol}_{selected_date}.png')
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.read())
        scaled_pixmap = pixmap.scaled(1200, 800)
        self.label.setPixmap(scaled_pixmap)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setScaledContents(True)

    def update_diagram_15(self, index, symbol, postDate):
        if not index == None:
            row = index.row()
            col = index.column()
            # Get the data for the selected row
            model = index.model()
            selected_date = model.get_data(row, col)
        else:
            selected_date = postDate
        if "202" not in selected_date:  # handle post-analysis data
            symbol = selected_date
            selected_date = postDate
        input_date = datetime.strptime(selected_date, "%Y-%m-%d")
        month_format = input_date.strftime("%Y-%m")
        us_calendar = mcal.get_calendar('NYSE')
        previous_trading_day = input_date - timedelta(days=1)
        while len(us_calendar.valid_days(start_date=previous_trading_day, end_date=previous_trading_day)) <= 0:
            previous_trading_day -= timedelta(days=1)
        yesterday_date = previous_trading_day.strftime('%Y-%m-%d')

        dates = []
        opens = []
        highs = []
        lows = []
        closes = []
        emas = []
        macds = []
        bbhigh =[]
        bbmiddle = []
        bblow = []

        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&outputsize=full&apikey={api_key}&month={month_format}&entitlement=delayed"
        response = requests.get(url)
        url_ema_10 = f"https://www.alphavantage.co/query?function=BBANDS&symbol={symbol}&interval=1min&time_period=20&series_type=close&apikey={api_key}&month={month_format}&entitlement=delayed"
        #url_ema_10 = f"https://www.alphavantage.co/query?function=EMA&symbol={symbol}&month={month_format}&interval=1min&time_period=20&series_type=close&apikey={api_key}&entitlement=delayed"
        response2 = requests.get(url_ema_10)
        if response.status_code == 200 and response2.status_code == 200:
            data_temp = response.json()
            time_series = data_temp['Time Series (1min)']
            data_ema = response2.json()
            #ema_series = data_ema['Technical Analysis: EMA']
            bbands = data_ema['Technical Analysis: BBANDS']
            price_1 = 0.0
            price_1_low = 0.0
            price_1_high = 0.0
            price_1_open = 0.0
            price_3 = 0.0
            price_3_low = 0.0
            price_3_high = 0.0
            price_3_close = 0.0
            price_4 = 0.0
            price_4_low = 0.0
            price_4_high = 0.0
            price_4_close = 0.0
            time_1 = ""
            time_3 = ""
            time_4 = ""
            verify_array = []
            verify_array_format = 32
            num_of_minute = 28
            for i in range(num_of_minute):
                row = [f'09:{str(verify_array_format).zfill(2)}:00', 0.0, '', 0.0, 0.0, 0.0, 0.0, 0.0,
                       0.0, 0.0, 0.0, 0.0,
                       0.0,
                       0.0,0.0,0.0,0.0]  # time, closed, date, low, SMA-5, high, EMA-5, SMA-10, EMA-10, open, macd, rsi, SMA-20, vol, bhigh, bmiddle, blow
                verify_array.append(row)
                verify_array_format = verify_array_format + 1
            verify_array_format = 0
            num_of_minute = 30
            for i in range(num_of_minute):
                row = [f'10:{str(verify_array_format).zfill(2)}:00', 0.0, '', 0.0, 0.0, 0.0, 0.0, 0.0,
                       0.0, 0.0, 0.0, 0.0,
                       0.0,
                       0.0, 0.0, 0.0,
                       0.0]  # time, closed, date, low, SMA-5, high, EMA-5, SMA-10, EMA-10, open, macd, rsi, SMA-20, vol, bhigh, bmiddle, blow
                verify_array.append(row)
                verify_array_format = verify_array_format + 1
            for timestamp, values in time_series.items():
                if f"{selected_date} 09:00:00" in timestamp:
                    price_1 = float(values['4. close'])
                    price_1_low = float(values['3. low'])
                    price_1_high = float(values['2. high'])
                    price_1_open = float(values['1. open'])
                    time_1 = timestamp
                    if price_4 != 0.0 and price_3 != 0.0 and verify_array[56][1] != 0.0 and price_1 != 0.0:
                        bh_values_1 = 0.0
                        bm1 = 0.0
                        bl1 =0.0
                        bh_values_3 = 0.0
                        bm3 = 0.0
                        bl3 = 0.0
                        bh_values_4 = 0.0
                        bm4 = 0.0
                        bl4 = 0.0
                        for timestamp_ema, values_ema in bbands.items():
                            if timestamp_ema in time_1:
                                bh_values_1 = float(values_ema['Real Upper Band'])
                                bm1 = float(values_ema['Real Middle Band'])
                                bl1 = float(values_ema['Real Lower Band'])
                            if timestamp_ema in time_4:
                                bh_values_4 = float(values_ema['Real Upper Band'])
                                bm4 = float(values_ema['Real Middle Band'])
                                bl4 = float(values_ema['Real Lower Band'])
                            if timestamp_ema in time_3:
                                bh_values_3 = float(values_ema['Real Upper Band'])
                                bm3 = float(values_ema['Real Middle Band'])
                                bl3 = float(values_ema['Real Lower Band'])
                            for verify in verify_array:
                                if timestamp_ema in verify[2]:
                                    verify[14] = float(values_ema['Real Upper Band'])
                                    verify[15] = float(values_ema['Real Middle Band'])
                                    verify[16] = float(values_ema['Real Lower Band'])
                            if bh_values_1 != 0.0 and bh_values_3 != 0.0 and verify_array[2][
                                6] != 0.0 and bh_values_4 != 0.0:
                                break
                        for m in range(len(verify_array)):
                            if m > 0:
                                this_min_date = verify_array[m][2][:10]
                                before_min_date = verify_array[m - 1][2][:10]
                                if this_min_date != before_min_date:
                                    verify_array[m][1] = verify_array[m - 1][9]
                                    datetime_obj = datetime.strptime(verify_array[m - 1][2], '%Y-%m-%d %H:%M:%S')
                                    next_minute = datetime_obj + timedelta(minutes=1)
                                    next_minute_str = next_minute.strftime('%Y-%m-%d %H:%M:%S')
                                    verify_array[m][2] = next_minute_str
                                    verify_array[m][3] = verify_array[m - 1][9]
                                    verify_array[m][5] = verify_array[m - 1][9]
                                    verify_array[m][9] = verify_array[m - 1][9]
                                    verify_array[m][6] = verify_array[m - 1][6]
                        dates.append("16:00:00")
                        opens.append(price_1_open)
                        highs.append(price_1_high)
                        lows.append(price_1_low)
                        closes.append(price_1)
                        dates.append("09:30:00")
                        opens.append(price_4)
                        highs.append(price_4_high)
                        lows.append(price_4_low)
                        closes.append(price_4_close)
                        dates.append("09:31:00")
                        opens.append(price_3)
                        highs.append(price_3_high)
                        lows.append(price_3_low)
                        closes.append(price_3_close)
                        for verify in verify_array:
                            dates.append(verify[0])
                            opens.append(verify[1])
                            highs.append(verify[5])
                            lows.append(verify[3])
                            closes.append(verify[9])
                        bbhigh.append(bh_values_1)
                        bbmiddle.append(bm1)
                        bblow.append(bl1)
                        bbhigh.append(bh_values_4)
                        bbmiddle.append(bm4)
                        bblow.append(bl4)
                        bbhigh.append(bh_values_3)
                        bbmiddle.append(bm3)
                        bblow.append(bl3)
                        for verify in verify_array:
                            bbhigh.append(verify[14])
                            bbmiddle.append(verify[15])
                            bblow.append(verify[16])
                        break
                for verify in verify_array:
                    if verify[0] in timestamp:
                        verify[1] = float(values['1. open'])
                        verify[2] = timestamp
                        verify[3] = float(values['3. low'])
                        verify[5] = float(values['2. high'])
                        verify[9] = float(values['4. close'])
                if f"{selected_date} 09:31:00" in timestamp:
                    # print(f"{timestamp} : {values['1. open']}")
                    price_3 = float(values['1. open'])
                    price_3_low = float(values['3. low'])
                    price_3_high = float(values['2. high'])
                    price_3_close = float(values['4. close'])
                    time_3 = timestamp
                if f"{selected_date} 09:30:00" in timestamp:
                    # print(f"{timestamp} : {values['1. open']}")
                    price_4 = float(values['1. open'])
                    price_4_low = float(values['3. low'])
                    price_4_high = float(values['2. high'])
                    price_4_close = float(values['4. close'])
                    time_4 = timestamp

        # testing for price pattern dictionary
        if dates:
            dates.pop(0)
            opens.pop(0)
            highs.pop(0)
            lows.pop(0)
            closes.pop(0)
            bbhigh.pop(0)
            bbmiddle.pop(0)
            bblow.pop(0)

        # Create a custom candlestick chart using matplotlib
        fig, ax = plt.subplots(figsize=(10, 5))

        for i in range(len(dates)):
            if opens[i] < closes[i]:
                color = 'green'
            else:
                color = 'red'

            ax.plot([i, i], [lows[i], highs[i]], color='black', linewidth=1)
            ax.plot([i, i], [opens[i], closes[i]], color=color, linewidth=7)

        ax.plot(range(len(dates)), bbhigh, color='yellow', label='BH', linewidth=2)
        ax.plot(range(len(dates)), bbmiddle, color='pink', label='BM', linewidth=2)
        ax.plot(range(len(dates)), bblow, color='blue', label='BL', linewidth=2)

        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels(dates, rotation=45, fontsize=8)
        ax.set_title(f'{symbol} - {selected_date} Candlestick (1min)')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')

        # Convert the diagram to a QPixmap for display
        buffer = BytesIO()
        plt.savefig(f'data/graph{config_path_extension}/{symbol}_{selected_date}.png')
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.read())
        scaled_pixmap = pixmap.scaled(1200, 800)
        self.label.setPixmap(scaled_pixmap)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setScaledContents(True)

    def futu_diagram(self, index, symbol, postDate):
        if not index == None:
            row = index.row()
            col = index.column()
            # Get the data for the selected row
            model = index.model()
            selected_date = model.get_data(row, col)
        else:
            selected_date = postDate
        if "202" not in selected_date:  # handle post-analysis data
            symbol = selected_date
            selected_date = postDate
        input_date = datetime.strptime(selected_date, "%Y-%m-%d")
        month_format = input_date.strftime("%Y-%m")
        us_calendar = mcal.get_calendar('NYSE')
        previous_trading_day = input_date - timedelta(days=1)
        while len(us_calendar.valid_days(start_date=previous_trading_day, end_date=previous_trading_day)) <= 0:
            previous_trading_day -= timedelta(days=1)
        yesterday_date = previous_trading_day.strftime('%Y-%m-%d')

        dates = []
        opens = []
        highs = []
        lows = []
        closes = []
        ema_10s = []

        ret_sub, err_message = quote_ctx.subscribe([f'US.{symbol}'], [SubType.K_30M], subscribe_push=False)

        if ret_sub == RET_OK:

            ret, data = quote_ctx.get_cur_kline(f'US.{symbol}', 13, SubType.K_30M, AuType.QFQ)

            if ret == RET_OK:
                price_series = pd.Series(data['close'])
                ema_10 = price_series.ewm(span=5, adjust=False).mean()

                dates = data['time_key']
                opens = data['open']
                highs = data['high']
                lows = data['low']
                closes = data['close']
                ema_10s = ema_10

        current_time = data['time_key'][12]

        # Create a custom candlestick chart using matplotlib
        fig, ax = plt.subplots()

        for i in range(len(dates)):
            if opens[i] < closes[i]:
                color = 'green'
            else:
                color = 'red'

            ax.plot([i, i], [lows[i], highs[i]], color='black', linewidth=1)
            ax.plot([i, i], [opens[i], closes[i]], color=color, linewidth=7)

        ax.plot(range(len(dates)), ema_10s, color='blue', label='EMA-10', linewidth=2)

        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels(dates, rotation=45, fontsize=8)
        ax.set_title(f'{symbol} - {current_time} Real-time Candlestick')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')

        # Convert the diagram to a QPixmap for display
        buffer = BytesIO()
        plt.savefig(f'data/futu/{symbol}_{selected_date}.png')
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.read())
        scaled_pixmap = pixmap.scaled(1100, 700)
        self.label.setPixmap(scaled_pixmap)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setScaledContents(True)

    def predict_full_diagram(self, index, symbol, postDate):
        if not index == None:
            row = index.row()
            col = index.column()
            # Get the data for the selected row
            model = index.model()
            selected_date = model.get_data(row, col)
        else:
            selected_date = postDate
        if "202" not in selected_date:  # handle post-analysis data
            symbol = selected_date
            selected_date = postDate
        input_date = datetime.strptime(selected_date, "%Y-%m-%d")
        month_format = input_date.strftime("%Y-%m")
        us_calendar = mcal.get_calendar('NYSE')
        previous_trading_day = input_date - timedelta(days=1)
        while len(us_calendar.valid_days(start_date=previous_trading_day, end_date=previous_trading_day)) <= 0:
            previous_trading_day -= timedelta(days=1)
        yesterday_date = previous_trading_day.strftime('%Y-%m-%d')

        dates = []
        opens = []
        highs = []
        lows = []
        closes = []
        ema_10s = []

        ret_sub, err_message = quote_ctx.subscribe([f'US.{symbol}'], [SubType.K_30M], subscribe_push=False)

        if ret_sub == RET_OK:

            ret, data = quote_ctx.get_cur_kline(f'US.{symbol}', 13, SubType.K_30M, AuType.QFQ)

            if ret == RET_OK:

                price_series = pd.Series(data['close'])
                ema_10 = price_series.ewm(span=5, adjust=False).mean()
                # ema_10 = price_series.ewm(span=10, adjust=False).mean()

                dates = data['time_key']
                opens = data['open']
                highs = data['high']
                lows = data['low']
                closes = data['close']
                ema_10s = ema_10
                current_time = ''

                df = pd.read_csv(f'data/train{config_path_extension}/{symbol}.csv')
                npp_array = df.iloc[1:].values
                num_2 = 53
                minute = "00"
                start_minute = "00"
                mining = 11

                num = 0
                pos1600 = 0
                for i in range(10):
                    if int(start_minute) == 60:
                        start_minute = "00"
                        mining = mining + 1
                    current_time = f"{mining}{start_minute}"
                    if f"{mining}{start_minute}" in data['time_key'][len(data) - 1]:
                        num = 13 + (i * 4)
                        remainingMin = 10 - i
                        pos1600 = 3 + i
                        break
                    start_minute = int(start_minute) + 30
                if num != 0:
                    np_array_input = npp_array[:, 1:num]
                    np_array_verify = npp_array[:, num:num_2]
                    np_array_input_float = np.empty_like(np_array_input, dtype=float)
                    np_array_input_float[:] = np_array_input.astype(float)
                    np_array_verify_float = np.empty_like(np_array_verify, dtype=float)
                    np_array_verify_float[:] = np_array_verify.astype(float)

                    features = np_array_input_float
                    target = np_array_verify_float

                    # Split the data into training and testing sets
                    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2,
                                                                        random_state=42)

                    # Create a linear regression model
                    model = LinearRegression()

                    # Train the model using the training data
                    model.fit(X_train, y_train)

                    # Make predictions on the test data
                    predictions = model.predict(X_test)

                    # Evaluate the model's performance
                    score = model.score(X_test, y_test)
                    print(f"Model R^2 score: {score}")

                    cols = []
                    for i in range(pos1600):  # 1000,1030,1100
                        cols.append(data['open'][len(data) - pos1600 + i])
                        cols.append(data['low'][len(data) - pos1600 + i])
                        cols.append(data['high'][len(data) - pos1600 + i])
                        cols.append(data['close'][len(data) - pos1600 + i])

                    start_minute = "00"
                    mining = 11
                    predicted_data = pd.DataFrame()
                    for i in range(10):
                        if int(start_minute) == 60:
                            start_minute = "00"
                            mining = mining + 1
                        if f"{mining}{start_minute}" in data['time_key'][len(data) - 1]:
                            predicted_data = pd.DataFrame([cols])
                            break
                        start_minute = int(start_minute) + 30

                    # Make a prediction on new data
                    new_data = pd.DataFrame(predicted_data)
                    prediction = model.predict(new_data)
                    print(f"Prediction at {mining}:{minute}: {prediction}")

                    # Create a custom candlestick chart using matplotlib
                    fig, ax = plt.subplots()

                    j = 0
                    for i in range(len(dates)):
                        if opens[i] < closes[i]:
                            color = 'green'
                        else:
                            color = 'red'

                        ax.plot([j, j], [lows[i], highs[i]], color='black', linewidth=1)
                        ax.plot([j, j], [opens[i], closes[i]], color=color, linewidth=7)
                        j = j + 1

                    c = 3
                    l = 1
                    h = 2
                    o = 0
                    for i in range(remainingMin):
                        if prediction[0][o] < prediction[0][c]:
                            color = 'green'
                        else:
                            color = 'red'

                        ax.plot([j, j], [prediction[0][l], prediction[0][h]], color='black', linewidth=1)
                        ax.plot([j, j], [prediction[0][o], prediction[0][c]], color=color, linewidth=7)
                        j = j + 1
                        c = c + 4
                        l = l + 4
                        h = h + 4
                        o = o + 4

                    ax.set_xticks(range(len(dates)))
                    ax.set_xticklabels(dates, rotation=45, fontsize=8)
                    ax.set_title(f'{symbol} - {current_time} Predicted 16:00:00 Candlestick')
                    ax.set_xlabel('Date')
                    ax.set_ylabel('Price')

                    # Convert the diagram to a QPixmap for display
                    buffer = BytesIO()
                    plt.savefig(f'data/predicted_full{config_path_extension}/{symbol}_{selected_date}.png')
                    plt.savefig(buffer, format='png')
                    buffer.seek(0)
                    pixmap = QPixmap()
                    pixmap.loadFromData(buffer.read())
                    scaled_pixmap = pixmap.scaled(1100, 700)
                    self.label.setPixmap(scaled_pixmap)
                    self.label.setAlignment(Qt.AlignCenter)
                    self.label.setScaledContents(True)

                    file_path = f'data/predicted_full{config_path_extension}/{symbol}_{selected_date}.csv'
                    np.savetxt(file_path, prediction, delimiter=',', fmt='%s')
                    print(f"Array exported to {file_path} successfully.")
                else:
                    print(f"Time is Not Ready.")


def monitorFUTU(symbol, type, model):
    ret_sub, err_message = quote_ctx.subscribe([f'US.{symbol}'], [SubType.K_30M], subscribe_push=False)

    if ret_sub == RET_OK:

        is_buy = True

        while (is_buy):

            ret, data = quote_ctx.get_cur_kline(f'US.{symbol}', 10, SubType.K_30M, AuType.QFQ)

            if ret == RET_OK:

                # ema_10 = np.convolve(data['close'], np.ones(10) / 10, mode='valid')
                price_series = pd.Series(data['close'])
                ema_10 = price_series.ewm(span=5, adjust=False).mean()

                latest_time = data['time_key'][9]
                lastest_ema = ema_10[9]

                if type == "CALL":
                    lastest_price = data['low'][9]
                    print(f"{symbol} - {latest_time} : {lastest_price} with EMA {lastest_ema}")
                    model.add_output(f"{symbol} - {latest_time} : {lastest_price} with EMA {lastest_ema}")
                    if lastest_ema > data['close'][9] and data['open'][9] > data['close'][9]:
                        print(f"{symbol}: Sell CALL!")
                        model.add_output(f"{symbol}: Sell CALL!")
                        telegram_instant_sell.put(f"{symbol}賣出觸發!\n{latest_time}\n現價:{lastest_price}")
                        is_buy = False
                else:
                    lastest_price = data['high'][9]
                    print(f"{symbol} - {latest_time} : {lastest_price} with EMA {lastest_ema}")
                    model.add_output(f"{symbol} - {latest_time} : {lastest_price} with EMA {lastest_ema}")
                    if lastest_ema < data['close'][9] and data['open'][9] < data['close'][9]:
                        print(f"{symbol}: Sell PUT!")
                        model.add_output(f"{symbol}: Sell PUT!")
                        telegram_instant_sell.put(f"{symbol}賣出觸發!\n{latest_time}\n現價:{lastest_price}")
                        is_buy = False
                timemodule.sleep(60)
            else:
                print(f"Stock Code Not Found!")
                model.add_output(f"Stock Code Not Found!")
                telegram_instant_sell.put(f"找不到股票代碼.")


def handleDataList(given_date,name_symbol):
    global one_chance
    global zero_chance
    global call_chance
    global put_chance
    global sell_loss_chancePA
    global sell_win_chancePA
    global sell_loss_chanceEMA
    global sell_win_chanceEMA
    global sell_loss_chanceH
    global sell_win_chanceH
    global total_record

    rawHistoricalData = pd.read_csv(f'{folder_path}/{name_symbol}.csv')
    historicalData = rawHistoricalData[rawHistoricalData['Date'] < given_date]
    total_record = historicalData.shape[0]
    one_chance = historicalData[historicalData.iloc[:, 9] == 1].shape[0] / total_record
    zero_chance = historicalData[historicalData.iloc[:, 9] == 0].shape[0] / total_record
    sell_loss_chancePA = historicalData[historicalData.iloc[:, 5] == '10:30:00'].shape[0] / total_record
    sell_win_chancePA = historicalData[historicalData.iloc[:, 5] != '10:30:00'].shape[0] / total_record
    sell_loss_chanceEMA = historicalData[historicalData.iloc[:, 10] == '10:30:00'].shape[0] / total_record
    sell_win_chanceEMA = historicalData[historicalData.iloc[:, 10] == '15:30:00'].shape[0] / total_record
    sell_loss_chanceH = historicalData[historicalData.iloc[:, 12] == '10:30:00'].shape[0] / total_record
    sell_win_chanceH = historicalData[historicalData.iloc[:, 12] == '15:30:00'].shape[0] / total_record

def execute_performanceList(input_date, model):
    global symbol
    global performance_csv
    global performance_array
    global date
    global folder_path

    performance_csv = []
    performance_array = []

    for file in os.listdir(f'data/post-analysis5{config_path_extension}/'):
        if os.path.isfile(os.path.join(f'data/post-analysis5{config_path_extension}/', file)):
            dateK = file.split('_')[0]
            pre_date_csv = pd.read_csv(f'data/post-analysis5{config_path_extension}/{dateK}_beforeMarket.csv')
            post_datas = pre_date_csv.values
            selected_array = []
            choice_1 = 'None'
            c1_result = 'None'
            c1_earn = 0.0
            choice_2 = 'None'
            c2_result = 'None'
            c2_earn = 0.0
            overall_earn = 0.0
            bbRatio = ''
            folder_path = f'data/history{config_path_extension}'
            for file in os.listdir(folder_path):
                if os.path.isfile(os.path.join(folder_path, file)):
                    symbol = os.path.splitext(file)[0]
                    pre_data_csv = pd.read_csv(f'{folder_path}/{symbol}.csv')
                    date = pre_data_csv.iloc[:, 0].values
                    chance = pre_data_csv.iloc[:, 9].values
                    earning = pre_data_csv.iloc[:, 11].values
                    earningSell = pre_data_csv.iloc[:, 7].values
                    for j in range(len(date)):
                        if date[j] == dateK:
                            row = [date[j], symbol, chance[j], earning[j], earningSell[j]]
                            selected_array.append(row)
                            break
            # print(selected_array)
            chances_long_red = []
            chances_long_green = []
            trendQQQ = "None"
            trendSPY = "None"
            jumpUpQQQ = "None"
            jumpDownQQQ = "None"
            jumpUpSPY ="None"
            jumpDownSPY = "None"
            overHighQQQ = "None"
            overHighSPY = "None"
            overLowQQQ = "None"
            overLowSPY = "None"
            patternQQQ = "None"
            patternSPY = "None"
            bigPatternQQQ = "None"
            bigPatternSPY = "None"
            lowestChanceLongRed = 0
            lowestSymbolLongRed = "None"
            highestChanceLongGreen = 0
            highestSymbolLongGreen = "None"
            secondHighestSymbolLongGreen = "None"
            secondLowestSymbolLongRed = "None"
            secondLowestChanceLongRed = 0
            secondHighestChanceLongGreen = 0
            filter_symbol = ['NOW','NET','MDB','TEAM']
            for post_data in post_datas:
                if post_data[0] == "SPY" and "Red" in post_data[1]:
                    trendSPY = post_data[8]
                    patternSPY = post_data[1]
                    bigPatternSPY = post_data[3]
                    jumpUpSPY = post_data[13]
                    jumpDownSPY = post_data[14]
                    overHighSPY = post_data[11]
                    overLowSPY = post_data[12]
                if post_data[0] == "QQQ" and "Red" in post_data[1]:
                    trendQQQ = post_data[8]
                    bigPatternQQQ = post_data[3]
                    patternQQQ = post_data[1]
                    jumpUpQQQ = post_data[13]
                    jumpDownQQQ = post_data[14]
                    overHighQQQ = post_data[11]
                    overLowQQQ = post_data[12]
                if post_data[1] == "Long-Red" and "Null" not in post_data[3] and float(post_data[4]) != 0.0:
                    chances_long_red.append(post_data)
                if post_data[0] == "SPY" and "Green" in post_data[1]:
                    trendSPY = post_data[8]
                    patternSPY = post_data[1]
                    bigPatternSPY = post_data[3]
                    jumpUpSPY = post_data[13]
                    jumpDownSPY = post_data[14]
                    overHighSPY = post_data[11]
                    overLowSPY = post_data[12]
                if post_data[0] == "QQQ" and "Green" in post_data[1]:
                    trendQQQ = post_data[8]
                    patternQQQ = post_data[1]
                    bigPatternQQQ = post_data[3]
                    jumpUpQQQ = post_data[13]
                    jumpDownQQQ = post_data[14]
                    overHighQQQ = post_data[11]
                    overLowQQQ = post_data[12]
                if post_data[1] == "Long-Green" and "Null" not in post_data[3] and float(post_data[4]) != 1.0 and not post_data[3].startswith('Bottom'):
                    chances_long_green.append(post_data)
            if chances_long_red and len(chances_long_red) > len(chances_long_green):
                filtered_chances_long_red = [x for x in chances_long_red if  ((x[9] == False and x[10] == False) or configurations[7] == "Deny")]
                if filtered_chances_long_red:
                    lowestChanceLongRed = min(filtered_chances_long_red, key=lambda x: x[4])[4]
                    lowestSymbolLongRed = min(filtered_chances_long_red, key=lambda x: x[4])[0]
                    lowestTrendLongRed = min(filtered_chances_long_red, key=lambda x: x[4])[8]
                    lowestPatternLongRed = min(filtered_chances_long_red, key=lambda x: x[4])[3]
                    unique_numbers = sorted(set(item[4] for item in filtered_chances_long_red))
                    if len(unique_numbers) >= 2:
                        secondLowestChanceLongRed = unique_numbers[1]
                        secondLowestSymbolLongRed = [item[0] for item in filtered_chances_long_red if item[4] == secondLowestChanceLongRed]
            if chances_long_green and len(chances_long_red) < len(chances_long_green):
                filtered_chances_long_green = [x for x in chances_long_green if  ((x[9] == False and x[10] == False) or configurations[7] == "Deny")]
                if filtered_chances_long_green:
                    highestChanceLongGreen = max(filtered_chances_long_green, key=lambda x: x[4])[4]
                    highestSymbolLongGreen = max(filtered_chances_long_green, key=lambda x: x[4])[0]
                    highestTrendLongGreen = max(filtered_chances_long_green, key=lambda x: x[4])[8]
                    highestPatternLongGreen = max(filtered_chances_long_green, key=lambda x: x[4])[3]
                    unique_numbers2 = sorted(set(item[4] for item in filtered_chances_long_green))
                    if len(unique_numbers2) >= 2:
                        secondHighestChanceLongGreen = unique_numbers2[-2]
                        secondHighestSymbolLongGreen = [item[0] for item in filtered_chances_long_green if item[4] == secondHighestChanceLongGreen]
            positive_count = (pre_date_csv.iloc[:, 26] >= 2).sum()
            negative_count = (pre_date_csv.iloc[:, 26] < 2).sum()
            countWinLong = 0
            for selected in selected_array:
                if len(chances_long_red) < len(chances_long_green):
                    for row in chances_long_green:
                        if selected[1] == row[0]:
                            if selected[4] > 0 :
                                countWinLong = countWinLong + 1
                    if selected[1] == highestSymbolLongGreen:
                        choice_1 = highestSymbolLongGreen
                        if selected[2] == 1:
                            c1_result = "Win"
                        else:
                            c1_result = "Lost"
                        c1_earn = selected[4] * 1
                    if secondHighestSymbolLongGreen and selected[1] == secondHighestSymbolLongGreen[0]:
                        choice_2 = secondHighestSymbolLongGreen[0]
                        if selected[2] == 0:
                            c2_result = "Lost"
                        else:
                            c2_result = "Win"
                        c2_earn = selected[4] * 1
                if len(chances_long_red) > len(chances_long_green):
                    for row in chances_long_red:
                        if selected[1] == row[0]:
                            if selected[4] < 0 :
                                countWinLong = countWinLong + 1
                    if selected[1] == lowestSymbolLongRed:
                        choice_1 = lowestSymbolLongRed
                        if selected[2] == 0:
                            c1_result = "Win"
                        else:
                            c1_result = "Lost"
                        c1_earn = selected[4] * -1
                    if secondLowestSymbolLongRed and selected[1] == secondLowestSymbolLongRed[0]:
                        choice_2 = secondLowestSymbolLongRed[0]
                        if selected[2] == 1:
                            c2_result = "Lost"
                        else:
                            c2_result = "Win"
                        c2_earn = selected[4] * -1

            isCondition = 0
            if len(chances_long_red) > len(chances_long_green): #put condition
                if ("Sideway" in trendSPY and "Sideway" in trendQQQ):
                    if overLowSPY and overLowQQQ and jumpDownSPY and not jumpDownQQQ:
                        isCondition = 1
                    if patternSPY == patternQQQ and 'Short' not in patternQQQ:
                        if 'Long-Long-Red-Red' in bigPatternSPY and 'Long-Long-Red-Red' in bigPatternQQQ:
                            isCondition = 1
                        if jumpUpSPY and jumpUpQQQ:
                            isCondition = 1
                if ("Upward" in trendSPY and "Downward" in trendQQQ):
                    if "Long-Red" in patternQQQ and patternQQQ == patternSPY:
                        isCondition = 1
                if ("Sideway" in trendSPY and "Downward" in trendQQQ) or ("Downward" in trendSPY and "Sideway" in trendQQQ):
                    if patternQQQ == patternSPY:
                        if ("Short-Red" in patternQQQ or "Short-Green" in patternQQQ) and jumpDownSPY:
                            isCondition = 1
                        if "Long-Red" in patternQQQ:
                            if not overLowSPY and overLowQQQ and jumpDownSPY and jumpDownQQQ:
                                isCondition = 1
                            if overLowSPY and overLowQQQ and not jumpDownSPY and jumpDownQQQ:
                                isCondition = 1
                            if overLowSPY and not overLowQQQ and jumpDownSPY and jumpDownQQQ:
                                isCondition = 1
                    if "Upper-Red" in patternSPY and "Long-Red" in patternQQQ:
                        isCondition = 1
                if ("Sideway" in trendSPY and "Upward" in trendQQQ) or ("Upward" in trendSPY and "Sideway" in trendQQQ):
                    if "Long-Red" in patternSPY and "Bottom-Red" in patternQQQ:
                        isCondition = 1
                    if "Bottom-Red" in patternSPY and "Long-Red" in patternQQQ:
                        isCondition = 1
                    if "Short-Red" in patternSPY and ("Upper-Red" in patternQQQ or "Bottom-Green" in patternQQQ):
                        isCondition = 1
                if ("Downward" in trendSPY and "Downward" in trendQQQ):
                    if not jumpUpQQQ and not jumpUpSPY and not jumpDownQQQ and not jumpDownSPY:
                        if 'Short' not in patternQQQ and 'Short' not in patternSPY and 'Bottom' not in patternQQQ and 'Bottom' not in patternSPY:
                            if overLowSPY and overLowQQQ:
                                isCondition = 1
                    if not overLowQQQ and not overLowSPY and not overHighQQQ and not overHighSPY:
                        if jumpUpQQQ and jumpUpSPY and patternQQQ == patternSPY and 'Red' in patternSPY and 'Bottom' not in patternSPY:
                            isCondition = 1
                        if jumpUpSPY and not jumpUpQQQ:
                            isCondition = 1
                    if overLowQQQ and overLowSPY and jumpDownQQQ:
                        if jumpDownSPY and patternSPY == patternQQQ and ('Long-Short' in bigPatternSPY and 'Long-Short' in bigPatternQQQ or 'Long-Upper' in bigPatternSPY and 'Long-Upper' in bigPatternQQQ):
                            isCondition = 1
                        if not jumpDownSPY:
                            isCondition = 1
                    if overLowQQQ and jumpUpSPY and patternQQQ == patternSPY:
                            isCondition = 1
                    if overHighQQQ and jumpDownSPY:
                        isCondition = 1
                    if overHighSPY and not overHighQQQ and jumpUpQQQ and jumpUpSPY and 'Long-Green' not in patternSPY:
                        isCondition = 1
                    if overHighSPY and overHighQQQ and jumpUpQQQ and jumpUpSPY:
                        isCondition = 1
                    if overLowQQQ and not overLowSPY and jumpDownQQQ and not jumpDownSPY and patternQQQ == patternSPY:
                        isCondition = 1
                    if not overHighSPY and overHighQQQ and jumpDownSPY:
                        isCondition = 1
                    if jumpUpSPY and not jumpUpQQQ and not overHighSPY:
                        isCondition = 1
                    if not jumpUpSPY and jumpUpQQQ and (bigPatternQQQ.startswith("Long") or bigPatternSPY.startswith("Long")):
                        isCondition = 1
                    if jumpDownSPY and not jumpDownQQQ and patternQQQ == patternSPY:
                        isCondition = 1
                if ("Upward" in trendSPY and "Upward" in trendQQQ):
                    if jumpUpQQQ and jumpUpSPY and not (overLowSPY or overHighQQQ) and 'Red' in patternQQQ and 'Red' in patternSPY and 'Upper-Short' not in bigPatternQQQ:
                        isCondition = 1
                    if overLowQQQ and jumpUpSPY and not overHighSPY and not (jumpUpQQQ and overLowSPY):
                        isCondition = 1
                    if overLowQQQ and not overLowSPY and jumpDownQQQ and not jumpDownSPY and 'Short' not in patternQQQ and 'Short' not in patternSPY:
                        isCondition = 1
                    if overLowQQQ and overLowSPY and jumpDownQQQ and jumpDownSPY:
                        if not bigPatternQQQ.startswith('Long-Short') and not bigPatternSPY.startswith('Long-Short') and not bigPatternSPY.startswith('Bottom') and not (bigPatternQQQ.startswith('Upper') and bigPatternSPY.startswith('Upper')) and 'Bottom' not in patternSPY:
                            isCondition = 1
                    if overHighSPY and not overHighQQQ and not jumpUpQQQ and not jumpUpSPY and patternQQQ == patternSPY:
                        isCondition = 1
                    if overHighQQQ and not (overHighSPY and jumpUpQQQ and jumpUpSPY) and (overLowQQQ or overLowSPY):
                        isCondition = 1
                    if overLowSPY and not overLowQQQ and "Bottom" not in patternQQQ and "Bottom" not in patternSPY and "Long-Long-Green-Red" not in bigPatternQQQ:
                        isCondition = 1


            if len(chances_long_red) < len(chances_long_green): #call condition
                if ("Sideway" in trendSPY and "Sideway" in trendQQQ):
                    if not bigPatternSPY.startswith('Bottom') and not bigPatternQQQ.startswith('Bottom') and 'Short' not in patternSPY and patternQQQ == patternSPY:
                        if overHighQQQ and overHighSPY and not jumpUpQQQ:
                            isCondition = 1
                        if not overHighQQQ and not overHighSPY and jumpUpQQQ and jumpUpSPY:
                            isCondition = 1
                        if overHighQQQ and overHighSPY and jumpUpQQQ and jumpUpSPY and bigPatternQQQ == bigPatternSPY:
                            isCondition = 1
                if ("Upward" in trendSPY and "Downward" in trendQQQ):
                    if "Long-Green" in patternQQQ and patternQQQ == patternSPY:
                        isCondition = 1
                if ("Sideway" in trendSPY and "Upward" in trendQQQ) or ("Upward" in trendSPY and "Sideway" in trendQQQ):
                    if patternQQQ == patternSPY:
                        if jumpDownQQQ and jumpDownSPY and not bigPatternSPY.startswith("Bottom") and not bigPatternSPY.startswith("Upper"):
                            isCondition = 1
                        if overHighSPY and not overHighQQQ and jumpUpSPY and jumpUpQQQ:
                            isCondition = 1
                        if overHighSPY and overHighQQQ and jumpUpSPY and jumpUpQQQ and bigPatternQQQ.startswith("Short"):
                            isCondition = 1
                if ("Sideway" in trendSPY and "Downward" in trendQQQ) or ("Downward" in trendSPY and "Sideway" in trendQQQ):
                    if (jumpDownQQQ or jumpDownSPY) and not overHighSPY and not overLowQQQ:
                        isCondition = 1
                    if not overHighQQQ and overLowQQQ and not jumpDownSPY:
                        isCondition = 1
                    if overLowSPY and overLowQQQ:
                        isCondition = 1
                    if overLowSPY and overHighQQQ and jumpUpQQQ:
                        isCondition = 1
                    if not jumpUpQQQ and not jumpUpSPY and not jumpDownQQQ and not jumpDownSPY:
                        if "Red" not in patternQQQ and "Red" not in patternSPY and "Bottom" not in patternQQQ and "Bottom" not in patternSPY and not bigPatternSPY.startswith('Upper') and not bigPatternSPY.startswith('Short'):
                            isCondition = 1
                if ("Downward" in trendSPY and "Downward" in trendQQQ):
                    if overHighSPY and overHighQQQ and jumpUpQQQ and jumpUpSPY:
                        if not bigPatternQQQ.startswith("Bottom") and not bigPatternSPY.startswith("Bottom") and not bigPatternQQQ.startswith("Upper-Long") and not bigPatternSPY.startswith("Upper-Long"):
                            isCondition = 1
                    if overHighSPY and overHighQQQ and jumpDownQQQ and jumpDownSPY and patternQQQ == patternSPY:
                        isCondition = 1
                    if overHighSPY and not overHighQQQ and not jumpUpSPY and not jumpDownSPY:
                        isCondition = 1
                    if not overHighSPY and overHighQQQ and not (jumpDownQQQ and jumpDownSPY) and (jumpDownQQQ or overLowSPY):
                        isCondition = 1
                    if jumpDownQQQ and jumpDownSPY and not overHighSPY and not overHighQQQ and not overLowSPY and not overLowQQQ and "Green" in patternQQQ and "Green" in patternSPY and not ("Short" in patternQQQ and "Short" in patternSPY):
                        isCondition = 1
                    if overLowSPY and overLowQQQ and patternQQQ == patternSPY and not overHighSPY:
                        isCondition = 1
                    if jumpUpSPY and not jumpUpQQQ  and patternQQQ == patternSPY:
                        isCondition = 1
                    if not jumpUpSPY and jumpUpQQQ and overHighSPY and overHighQQQ:
                        isCondition = 1
                    if overLowSPY and not overLowQQQ and overHighQQQ and jumpUpSPY:
                        isCondition = 1
                    if not overLowSPY and overLowQQQ and not jumpDownSPY:
                        isCondition = 1
                    if not jumpDownSPY and jumpDownQQQ and not overLowQQQ and 'Green' in patternSPY and 'Green' in patternQQQ:
                        isCondition = 1
                if ("Upward" in trendSPY and "Upward" in trendQQQ):
                    if overHighSPY and overHighQQQ and jumpUpQQQ and jumpUpSPY and patternQQQ == patternSPY and not ('Long-Long' in bigPatternSPY and 'Long-Long' in bigPatternQQQ):
                        isCondition = 1
                    if not overHighSPY and not overHighQQQ and not overLowSPY and not jumpDownSPY and not jumpDownQQQ and 'Red' not in patternQQQ and 'Red' not in patternSPY:
                        isCondition = 1
                    if not overHighSPY and overHighQQQ and not jumpUpQQQ and not (jumpDownSPY and jumpDownQQQ) and not jumpUpSPY:
                        isCondition = 1
                    if not overHighQQQ and overHighSPY and patternQQQ == patternSPY and "Upper-Green" not in patternSPY and 'Long-Long' not in bigPatternSPY:
                        isCondition = 1
                    if jumpUpQQQ and jumpUpSPY and overHighSPY and not overHighQQQ:
                        if "Short-Short" not in bigPatternSPY and "Short-Short" not in bigPatternQQQ and "Upper-Green" not in patternSPY and "Upper-Green" not in patternQQQ:
                            isCondition = 1
                    if not jumpDownSPY and jumpDownQQQ and patternQQQ == patternSPY and "Long-Green" in patternSPY:
                        isCondition = 1
                    if jumpDownSPY and not jumpDownQQQ and patternQQQ == patternSPY and "Short-Green" not in patternSPY:
                        isCondition = 1

            if len(chances_long_red) > len(chances_long_green) and (isCondition == 1  or configurations[8] == "Deny") and ('QQQ' not in lowestSymbolLongRed and 'SPY' not in lowestSymbolLongRed) and ((patternSPY == patternQQQ and 'Green' not in patternSPY and 'Short' not in patternSPY and 'Upper' not in patternSPY and 'None' not in patternSPY) or configurations[5] == "Deny") and (lowestChanceLongRed < 0.4 or configurations[6] == "Deny"):
                overall_earn = c1_earn + c2_earn
                performance_array.append(
                [dateK, f'{positive_count}:{negative_count}',"PUT", lowestSymbolLongRed, c1_result, c1_earn, lowestChanceLongRed,lowestPatternLongRed,
                 trendSPY, trendQQQ,lowestTrendLongRed,overHighSPY,overLowSPY,overHighQQQ,overLowQQQ,jumpUpSPY,jumpDownSPY,jumpUpQQQ,jumpDownQQQ,f'{countWinLong/len(chances_long_red):.2g}',f'{len(chances_long_green)}:{len(chances_long_red)}',patternSPY,patternQQQ,bigPatternSPY,bigPatternQQQ])
                model.add_output(
                    f'{dateK},{positive_count}:{negative_count},{choice_1},{c1_result},{c1_earn},{choice_2},{c2_result},{c2_earn},{overall_earn}')
                print(
                    f'{dateK},{positive_count}:{negative_count},{choice_1},{c1_result},{c1_earn},{choice_2},{c2_result},{c2_earn},{overall_earn}')
            if len(chances_long_red) < len(chances_long_green) and (isCondition == 1  or configurations[8] == "Deny") and ('QQQ' not in highestSymbolLongGreen and 'SPY' not in highestSymbolLongGreen) and ((patternSPY == patternQQQ and 'Red' not in patternSPY and 'Short' not in patternSPY and 'Bottom' not in patternSPY  and 'None' not in patternSPY) or configurations[5] == "Deny")  and (highestChanceLongGreen > 0.63 or configurations[6] == "Deny"):
                overall_earn = c1_earn + c2_earn
                performance_array.append(
                [dateK, f'{positive_count}:{negative_count}',"CALL", highestSymbolLongGreen, c1_result, c1_earn,highestChanceLongGreen,highestPatternLongGreen, trendSPY, trendQQQ,highestTrendLongGreen,overHighSPY,overLowSPY,overHighQQQ,overLowQQQ,jumpUpSPY,jumpDownSPY,jumpUpQQQ,jumpDownQQQ,f'{countWinLong/len(chances_long_green):.2g}',f'{len(chances_long_green)}:{len(chances_long_red)}',patternSPY,patternQQQ,bigPatternSPY,bigPatternQQQ])
                model.add_output(
                    f'{dateK},{positive_count}:{negative_count},{choice_1},{c1_result},{c1_earn},{choice_2},{c2_result},{c2_earn},{overall_earn}')
                print(
                    f'{dateK},{positive_count}:{negative_count},{choice_1},{c1_result},{c1_earn},{choice_2},{c2_result},{c2_earn},{overall_earn}')

    countFirstCALLWin = sum(1 for record in performance_array if 'Win' in record[4] and 'CALL' in record[2])
    countFirstPUTWin = sum(1 for record in performance_array if 'Win' in record[4] and 'PUT' in record[2])
    countFirstWin = countFirstCALLWin + countFirstPUTWin
    countFirstCALLLost = sum(1 for record in performance_array if 'Lost' in record[4] and 'CALL' in record[2])
    countFirstPUTLost = sum(1 for record in performance_array if 'Lost' in record[4] and 'PUT' in record[2])
    countFirstLost = countFirstCALLLost + countFirstPUTLost
    countFirstNull = sum(1 for record in performance_array if 'None' in record[4])
    countFirstCALLRecord = countFirstCALLWin + countFirstCALLLost
    countFirstPUTRecord = countFirstPUTWin + countFirstPUTLost
    countFirstRecord = countFirstCALLRecord + countFirstPUTRecord
    countFirstWin = countFirstCALLWin + countFirstPUTWin
    countFirstLost = countFirstCALLLost + countFirstPUTLost

    if len(performance_array) != 0:
        file_path = f'data/performance{config_path_extension}/{input_date}_performance.csv'
        header = ['Date', 'BB Ratio','Type', 'Choice', 'Result', 'Earning', 'Chance', 'Pattern',
                  'SPY Trend', 'QQQ Trend', 'Symbol Trend','High(SPY)','Low(SPY)','High(QQQ)','Low(QQQ)','Up(SPY)','Down(SPY)','Up(QQQ)','Down(QQQ)','Beta Rate','GR Ratio','SPY (30)','QQQ (30)','SPY (15)','QQQ (15)']
        performance_csv = np.vstack([header, performance_array])
        np.savetxt(file_path, performance_csv, delimiter=',', fmt='%s')
        print(f"Array exported to {file_path} successfully.")
        model.add_output(f"Array exported to {file_path} successfully.")
        #model.add_output( f"First Only - Win: {countFirstWin}, Lost: {countFirstLost}, Record: {countFirstRecord}, Win Rate: {countFirstWin / countFirstRecord}, #CALL: {countFirstCALLRecord}, #PUT: {countFirstPUTRecord}")
        #model.add_output(f"CALL Only - Win: {countFirstCALLWin}, Lost: {countFirstCALLLost}, Record: {countFirstCALLRecord}, Win Rate: {(countFirstCALLWin) / countFirstCALLRecord}")
        #model.add_output(f"PUT Only - Win: {countFirstPUTWin}, Lost: {countFirstPUTLost}, Record: {countFirstPUTRecord}, Win Rate: {(countFirstPUTWin)/countFirstPUTRecord}")
    else:
        print(f"No Data Updated.")
        model.add_output(f"No Data Updated.")

def execute_maxList(input_date, model):
    global symbol
    global overall_csv
    global max_array
    global date
    global folder_path

    overall_csv = []
    max_array = []

    for file in os.listdir(f'data/verify{config_path_extension}/'):
        try:
            if os.path.isfile(os.path.join(f'data/verify{config_path_extension}/', file)):
                dateK = file.split('_')[0]
                pre_date_csv = pd.read_csv(f'data/verify{config_path_extension}/{dateK}_actual.csv')
                post_datas = pre_date_csv.values
                for post_data in post_datas:
                    row = [dateK, post_data[0], post_data[1], post_data[2], post_data[3], post_data[4], post_data[5],
                           post_data[6],
                           post_data[7], post_data[8], post_data[9], post_data[10], post_data[11], post_data[12],
                           post_data[13], post_data[14], post_data[15]]
                    overall_csv.append(row)

            # row_max = [dateK,post_datas[0][0],post_datas[0][1],post_datas[0][2],post_datas[0][3],post_datas[0][4],post_datas[0][5],post_datas[0][6],post_datas[0][7],post_datas[0][8],post_datas[0][9],post_datas[0][10],post_datas[0][11]]
            # overall_csv.append(row_max)
            # tail = len(post_datas) - 1
            # row_min = [dateK,post_datas[tail][0],post_datas[tail][1],post_datas[tail][2],post_datas[tail][3],post_datas[tail][4],post_datas[tail][5],post_datas[tail][6],post_datas[tail][7],post_datas[tail][8],post_datas[tail][9],post_datas[tail][10],post_datas[tail][11]]
            # overall_csv.append(row_min)
        except:
            pass

    if len(overall_csv) != 0:
        file_path = f'data/performance{config_path_extension}/{input_date}_max.csv'
        header = ['Date', 'Symbol', 'BUY Pattern(30)', 'BUY Pattern(15)', 'Trend', '1st Band', '2nd Band',
                  'Jump Up', 'Jump Down', 'Type', 'Earning', 'RF', 'SVC', 'DT', 'LR', 'Actual','Result']
        max_array = np.vstack([header, overall_csv])
        np.savetxt(file_path, max_array, delimiter=',', fmt='%s')
        print(f"Array exported to {file_path} successfully.")
        model.add_output(f"Array exported to {file_path} successfully.")
    else:
        print(f"No Data Updated.")
        model.add_output(f"No Data Updated.")

def execute_earning(input_date, model):
    global symbol
    global overall_csv
    global e_array
    global date
    global folder_path

    overall_csv = []
    e_array = []

    pre_date_csv = pd.read_csv(f'data/pre-analysis{config_path_extension}/{input_date}_afterMarket.csv')
    post_datas = pre_date_csv.values
    selected_array = []
    folder_path = f'data/history{config_path_extension}'
    for file in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file)):
            symbol = os.path.splitext(file)[0]
            pre_data_csv = pd.read_csv(f'{folder_path}/{symbol}.csv')
            date = [x[0] for x in pre_data_csv.values if x[0] == input_date]
            buy_price = [x[2] for x in pre_data_csv.values if x[0] == input_date]
            earning = [x[7] for x in pre_data_csv.values if x[0] == input_date]
            sell_price = [x[6] for x in pre_data_csv.values if x[0] == input_date]
            pattern_30 = [x[3] for x in pre_data_csv.values if x[0] == input_date]
            pattern_15 = [x[4] for x in pre_data_csv.values if x[0] == input_date]
            sell_pattern = [x[8] for x in pre_data_csv.values if x[0] == input_date]
            for post_data in post_datas:
                if symbol == post_data[0] and date and buy_price and earning and sell_price and pattern_30 and pattern_15 and sell_pattern:
                    row = [symbol, buy_price[0], sell_price[0], pattern_30[0], pattern_15[0],post_data[10],post_data[11],post_data[9],post_data[14],post_data[15], sell_pattern[0], earning[0]]
                    overall_csv.append(row)
                    model.add_output(f'{symbol}...')
                    print(f'{symbol}...')
                    break

    if len(overall_csv) != 0:
        rearranged_array = sorted(overall_csv, key=lambda x: x[11], reverse=True)
        file_path = f'data/earning{config_path_extension}/{input_date}_earning.csv'
        header = ['Symbol', 'Buy Price','Sell Price', 'BUY Pattern(30)', 'BUY Pattern(15)', '1st Band', '2nd Band', 'Trend',
                  'Jump Up', 'Jump Down', 'SELL Pattern','Earning']
        e_array = np.vstack([header, rearranged_array])
        np.savetxt(file_path, e_array, delimiter=',', fmt='%s')
        print(f"Array exported to {file_path} successfully.")
        model.add_output(f"Array exported to {file_path} successfully.")
    else:
        print(f"No Data Updated.")
        model.add_output(f"No Data Updated.")

def execute_verifyEarning(input_date, model):
    global symbol
    global overall_csv
    global ve_array
    global date
    global folder_path

    overall_csv = []
    ve_array = []

    pre_date_csv = pd.read_csv(f'data/earning{config_path_extension}/{input_date}_earning.csv')
    post_datas = pre_date_csv.values
    verify_date_csv = pd.read_csv(f'data/predict{config_path_extension}/{input_date}_prediction.csv')
    verify_datas = verify_date_csv.values
    for verify_data in verify_datas:
        for post_data in post_datas:
            if verify_data[0] == post_data[0]:
                result = "None"
                if verify_data[8] == "CALL":
                    if float(post_data[11]) > 0:
                        result = "Win"
                    else:
                        result = "Lost"
                if verify_data[8] == "PUT":
                    if float(post_data[11]) < 0:
                        result = "Win"
                    else:
                        result = "Lost"

                row = [verify_data[0],verify_data[1],verify_data[2],verify_data[3],verify_data[4],verify_data[5],
                       verify_data[6],verify_data[7],verify_data[8],post_data[11],verify_data[9],verify_data[10],verify_data[11],
                       verify_data[12],post_data[10],result]
                overall_csv.append(row)


    if len(overall_csv) != 0:
        rearranged_array = sorted(overall_csv, key=lambda x: float(x[9]), reverse=True)
        file_path = f'data/verify{config_path_extension}/{input_date}_actual.csv'
        header = ['Symbol', 'BUY Pattern(30)', 'BUY Pattern(15)', 'Trend', '1st Band', '2nd Band',
                  'Jump Up', 'Jump Down','Type','Earning','Predict(RF)',"Predict(SVC)","Predict(DT)","Predict(LR)","Actual","Result"]
        ve_array = np.vstack([header, rearranged_array])
        np.savetxt(file_path, ve_array, delimiter=',', fmt='%s')
        print(f"Array exported to {file_path} successfully.")
        model.add_output(f"Array exported to {file_path} successfully.")
    else:
        print(f"No Data Updated.")
        model.add_output(f"No Data Updated.")


def execute_rankList(input_date, model):
    global symbol
    global rank_csv
    global rank_array
    global date
    global folder_path

    folder_path = f'data/history{config_path_extension}'
    symbols = [os.path.splitext(f)[0] for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    # symbols = ['AVGO','TSLA','AMZN','INTC','IBM','META']
    # the date after market
    date = input_date

    rank_csv = []

    for symbol in symbols:
        model.add_output(f"Caclulating for {symbol}...")
        handleData(input_date,symbol)
        handleDataList(input_date,symbol)
        row = [symbol, f"{one_chance:.5g}", f"{zero_chance:.5g}", f"{earning_probability:.5g}",
               f"{earning_probability_pa:.5g}",
               f"{sell_loss_chancePA:.5g}", f"{sell_win_chancePA:.5g}",
               f"{sell_loss_chanceEMA:.5g}", f"{sell_win_chanceEMA:.5g}", f"{sell_loss_chanceH:.5g}",
               f"{sell_win_chanceH:.5g}", f"{total_record:.5g}"]
        telegram_instant_array.append(row)
        for chance in chance_values:
            row.append(f"{chance:.2g}")
        for chance in chance_values_2:
            row.append(f"{chance:.2g}")
        sell_set = [sellLostPA_set, sellWinPA_set, sellLostEMA_set, sellWinEMA_set, sellLostH_set, sellWinH_set,
                    numPattern_set,
                    sellLostPA_set_2, sellWinPA_set_2, sellLostEMA_set_2, sellWinEMA_set_2, sellLostH_set_2,
                    sellWinH_set_2, numPattern_set_2]
        for bigSell in sell_set:
            for sell in bigSell:
                row.append(sell)
        rank_csv.append(row)

    if len(rank_csv) != 0:
        rearranged_array = sorted(rank_csv, key=lambda x: x[0], reverse=False)
        file_path = f'data/ranking{config_path_extension}/{input_date}_list.csv'
        header = ['Symbol', 'CALL Chance', 'PUT Chance', 'Earning (EMA)', 'Earning (PA)',
                  'Sell Lost (PA)', 'Sell Win (PA)', 'Sell Lost (EMA)', 'Sell Win (EMA)', 'Lowest Chance',
                  'Highest Chance', 'Total Record']
        header_loop = ['SLT-PA', 'SWT-PA', 'SLT-EMA', 'SWT-EMA', 'SLT-H', 'SWT-H', 'NUM']
        for price_action in chance_set:
            abstracted_string = ''.join(word[0] for word in price_action.split('-'))
            header.append(abstracted_string)
        for price_action in chance_set_2:
            abstracted_string = ''.join(word[0] for word in price_action.split('-'))
            header.append(abstracted_string)
        for text in header_loop:
            for price_action in chance_set:
                abstracted_string = ''.join(word[0] for word in price_action.split('-'))
                header.append(f'{text}-{abstracted_string}')
        for text in header_loop:
            for price_action in chance_set_2:
                abstracted_string = ''.join(word[0] for word in price_action.split('-'))
                header.append(f'{text}-{abstracted_string}')
        rank_array = np.vstack([header, rearranged_array])
        np.savetxt(file_path, rank_array, delimiter=',', fmt='%s')
        print(f"Array exported to {file_path} successfully.")
        model.add_output(f"Array exported to {file_path} successfully.")
    else:
        print(f"No Data Updated.")
        model.add_output(f"No Data Updated.")


def trainData(month, model):
    global array_overall

    with lock:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&month={month}&symbol={symbol}&interval=30min&outputsize=full&apikey={api_key}&entitlement=delayed"
        response = session.get(url)

        if response.status_code == 200:
            data = response.json()
            time_series = data['Time Series (30min)']

            verify_array = []
            verify_array_format = "00"
            num_of_minute = 12
            row = [f'09:30:00', 0.0, '', 0.0, 0.0, 0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0,
                   0.0]
            verify_array.append(row)
            hours = 10
            for i in range(num_of_minute):
                if int(verify_array_format) == 60:
                    hours = hours + 1
                    verify_array_format = "00"
                row = [f'{hours}:{verify_array_format}:00', 0.0, '', 0.0, 0.0, 0.0, 0.0, 0.0,
                       0.0, 0.0, 0.0, 0.0,
                       0.0]  # time, closed, date, low, SMA-5, high, EMA-5, SMA-10, EMA-10, open, macd, rsi, SMA-20
                verify_array.append(row)
                verify_array_format = int(verify_array_format) + 30
            time_1 = ""
            total_earn = 0
            total_lost = 0
            array_csv = []

            for timestamp, values in time_series.items():
                if "09:00:00" in timestamp:
                    # print(f"{timestamp} : {values['4. close']}")
                    if verify_array[11][2] != '':
                        for m in range(len(verify_array)):
                            if m > 0:
                                this_min_date = verify_array[m][2][:10]
                                before_min_date = verify_array[m - 1][2][:10]
                                if this_min_date != before_min_date:
                                    verify_array[m][1] = verify_array[m - 1][9]
                                    datetime_obj = datetime.strptime(verify_array[m - 1][2], '%Y-%m-%d %H:%M:%S')
                                    next_minute = datetime_obj + timedelta(minutes=1)
                                    next_minute_str = next_minute.strftime('%Y-%m-%d %H:%M:%S')
                                    verify_array[m][2] = next_minute_str
                                    verify_array[m][3] = verify_array[m - 1][9]
                                    verify_array[m][5] = verify_array[m - 1][9]
                                    verify_array[m][9] = verify_array[m - 1][9]
                                    verify_array[m][4] = verify_array[m - 1][4]
                        row = [verify_array[8][2].split(' ')[0]]
                        for m in range(len(verify_array)):
                            row.append(verify_array[m][1])
                            row.append(verify_array[m][3])
                            row.append(verify_array[m][5])
                            row.append(verify_array[m][9])
                        array_csv.append(row)
                        print(f"{verify_array[10][2]} : Capturing Data...")
                        model.add_output(f"{verify_array[10][2]} : Capturing Data...")
                        print("--------------")
                        model.add_output("--------------")
                for verify in verify_array:
                    if verify[0] in timestamp:
                        verify[1] = float(values['1. open'])
                        verify[2] = timestamp
                        verify[3] = float(values['3. low'])
                        verify[5] = float(values['2. high'])
                        verify[9] = float(values['4. close'])
                        verify[12] = float(values['5. volume'])
                        break
            array_overall = array_overall + array_csv
        else:
            print(f"Error: {response.status_code} - {response.text}")
            model.add_output(f"Error: {response.status_code} - {response.text}")


def execute_trainData(input_symbol, model):
    global lock
    global symbol
    global array_overall
    global array_month
    global session
    global td_array

    symbol = input_symbol

    current_date = QDate.currentDate().toString("yyyy-MM-dd")
    current_date_obj = QDate.fromString(current_date, 'yyyy-MM-dd')
    array_month = []
    for i in range(60):
        month = current_date_obj.addMonths(-i)
        month_str = month.toString('yyyy-MM')
        array_month.append(month_str)

    array_month.reverse()

    array_overall = []

    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504]
    )

    adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=retry_strategy)

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    lock = threading.Lock()

    threads = []
    for month in array_month:
        thread = threading.Thread(target=trainData, args=(month, model))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    status = ['open', 'low', 'high', 'close']
    header_series = []
    verify_array_format = "00"
    num_of_minute = 12
    header_series.append(f"0930{status[0][0]}")
    header_series.append(f"0930{status[1][0]}")
    header_series.append(f"0930{status[2][0]}")
    header_series.append(f"0930{status[3][0]}")
    hours = 10
    for i in range(12):
        if int(verify_array_format) == 60:
            hours = hours + 1
            verify_array_format = "00"
        minutes = 30 + i
        header_series.append(f"{hours}{verify_array_format}{status[0][0]}")
        header_series.append(f"{hours}{verify_array_format}{status[1][0]}")
        header_series.append(f"{hours}{verify_array_format}{status[2][0]}")
        header_series.append(f"{hours}{verify_array_format}{status[3][0]}")
        verify_array_format = int(verify_array_format) + 30
    if len(array_overall) != 0:
        file_path = f'data/train{config_path_extension}/{symbol}.csv'
        header = ['Date']
        for i in header_series:
            header.append(i)
        td_array = np.vstack([header, array_overall])
        np.savetxt(file_path, td_array, delimiter=',', fmt='%s')
        print(f"Array exported to {file_path} successfully.")
        model.add_output(f"Array exported to {file_path} successfully.")
    else:
        print(f"No Data Updated.")
        model.add_output(f"No Data Updated.")


async def startTG(update, context):
    user = update.message.from_user
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"歡迎{user.first_name}! 準備好財自未?")


async def helpTG(update, context):
    user = update.message.from_user
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"/start - 開始\n/instant - 即時分析\n/rank - 即日排行\n/setup - 配置預備\n/prelist - 盤前數據\n/postlist - 盤前核實\n/detail (stock) - 深度分析\n/pattern (s) (a) - 方式調查\n/backtest (stock) - 回測股票\n/plot (stock) (date) - 歷史繪圖\n/subplot - 歷史繪圖(1分K)\n/real (stock) - 實時繪圖\n/monitor (stock) (type) - 實時監察\n/get (stock) - 存取數據\n/update - 更新數據庫\n/train (stock) - 數據訓練\n/predict (stock)  - 實時預測\n/restart - 重啟程式\n/schedule - 自動執行")


async def monitor_stock(update, context):
    global telegram_instant_array

    if context.args:
        symbol = context.args[0]
        type = context.args[1]
    else:
        symbol = "AVGO"
        type = "CALL"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"現準備為{symbol}提供實時的賣出訊號, 期間請不要輸入任何指令...")

    chat_id = update.message.chat_id
    bt_model = OutputListModel()
    monitorFUTU(symbol, type, bt_model)
    TGthreads = []
    for tg_instant in telegram_instant_array:
        thread = threading.Thread(target=monitorFUTU, args=(symbol, type, bt_model))
        thread.start()
        TGthreads.append(thread)
    while any(thread.is_alive() for thread in TGthreads) or not telegram_instant_sell.empty():
        try:
            result = telegram_instant_sell.get(timeout=1)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=result)
        except queue.Empty:
            pass
    for thread in TGthreads:
        thread.join()


async def send_detail(update, context):
    global telegram_instant_array

    telegram_instant_array = []

    if context.args:
        symbol = context.args[0]
    else:
        symbol = "AVGO"
    date = QDate.currentDate().toString("yyyy-MM-dd")
    chat_id = update.message.chat_id
    bt_model = OutputListModel()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等, 正在準備為{symbol}進行深度分析...")
    execute_rankList(date, bt_model)
    for instant in telegram_instant_array:
        if instant[0] == symbol:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"代碼: {instant[0]}\n機會: {instant[1]}\n方式: {instant[2]}\n利潤: {instant[3]}%\nCALL: {instant[4]}\nPUT: {instant[5]}\n最早機會: {instant[6]}\n最遲機會: {instant[7]}\n最高機會: {instant[8]}\n紀錄: {instant[9]}")


async def send_pattern(update, context):
    global telegram_pattern_array
    global folder_path

    telegram_pattern_array = []

    if context.args:
        symbol = context.args[0]
        pattern = context.args[1]
    else:
        symbol = "AVGO"
        pattern = "LLGG"
    date = QDate.currentDate().toString("yyyy-MM-dd")
    chat_id = update.message.chat_id
    bt_model = OutputListModel()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等, 正在準備為{symbol}的{pattern}進行調查...")
    folder_path = f"data/history{config_path_extension}"
    handleData(date,symbol)
    main_string = ""
    for instant in telegram_pattern_array:
        strings = f"{instant[0]}"
        abstracted_string = ''.join(word[0] for word in strings.split('-'))
        if abstracted_string == pattern:
            main_string = f"代碼: {symbol}\n方式名稱: {instant[0]}\n方式機會: {instant[1]}"
            break
    telegram_pattern_array = []
    if len(pattern) == 2:
        handlePattern(symbol, pattern,date)
        main_string = main_string + f"\n最早止損次數(PA): {numSellLostTimePA}\n最遲止賺次數(PA): {numSellWinTimePA}\n最早止損次數(EMA): {numSellLostTimeEMA}\n最遲止賺次數(EMA): {numSellWinTimeEMA}\n最早止損次數(H): {numSellLostTimeH}\n最遲止賺次數(H): {numSellWinTimeH}\n觸發次數:{numPattern}\n總紀錄:{numRecord}"
    else:
        handlePatternMini(symbol, pattern,date)
        main_string = main_string + f"\n最早止損次數(PA): {numSellLostTimePAMini}\n最遲止賺次數(PA): {numSellWinTimePAMini}\n最早止損次數(EMA): {numSellLostTimeEMAMini}\n最遲止賺次數(EMA): {numSellWinTimeEMAMini}\n最早止損次數(H): {numSellLostTimeHMini}\n最遲止賺次數(H): {numSellWinTimeHMini}\n觸發次數:{numPatternMini}\n總紀錄:{numRecordMini}"
    total_string = ""
    for instant in telegram_pattern_array:
        if "2023" in instant[0]:
            total_string = total_string + f"日期: {instant[0]}\n機會: {instant[1]}\n離場(PA): {instant[2]}\n利潤(PA): {instant[3]}%\n離場(EMA): {instant[4]}\n利潤(EMA): {instant[5]}%\n離場(H): {instant[6]}\n利潤(H): {instant[7]}%\n------------\n"
    main_string = main_string
    total_string = total_string + main_string
    await context.bot.send_message(chat_id=update.effective_chat.id, text=total_string)


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.job_queue.run_daily(instantSimpleTG,time=time(hour=6, minute=59, second=14, tzinfo=pytz.timezone('Canada/Pacific')))
    context.job_queue.run_daily(auto_prepostList,time=time(hour=8, minute=0, second=0, tzinfo=pytz.timezone('Canada/Pacific')))
    context.job_queue.run_daily(auto_setupUpdate,time=time(hour=15, minute=0, second=0, tzinfo=pytz.timezone('Canada/Pacific')))
    context.job_queue.run_daily(instantNewsTG,time=time(hour=22, minute=00, second=0, tzinfo=pytz.timezone('Canada/Pacific')))
    context.job_queue.run_daily(auto_rankList,time=time(hour=1, minute=0, second=0, tzinfo=pytz.timezone('Canada/Pacific')))
    text = "所有功能將會按時自動執行.\n-------------\n工作天(7AM): 即時分析\n工作天(8AM): 盤前數據核實\n工作天(3PM): 配置及數據更新\n工作天(10PM): 每日新聞焦點\n工作天(1AM): 刷新每日排行\n星期六(0AM): 所有數據庫回測\n星期日(0AM): 整理預測數據庫"
    await update.effective_message.reply_text(text)

async def instantNewsTG(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = '-4095879826'
    now = datetime.now(pytz.timezone('Canada/Pacific'))  # Get current time in Pacific timezone
    if now.weekday() in [5, 6]:  # Saturday = 5, Sunday = 6
        await context.bot.send_message(chat_id=chat_id, text="星期六和星期日的即時新聞已取消.")
        return

    global telegram_instant_array

    telegram_instant_array = []
    date = QDate.currentDate().toString("yyyy-MM-dd")
    bt_model = OutputListModel()
    await context.bot.send_message(chat_id=chat_id, text=f"請稍等...\n 正在準備為你分析{date}的所有新聞內容.")
    execute_newsanalysis(date, bt_model)
    try:
        for tg_instant in telegram_instant_array:
            await context.bot.send_message(chat_id=chat_id,text=f"股票: {tg_instant[0]}\n新聞:{tg_instant[4]}\n時間:{tg_instant[3]}\n市場情緒:{tg_instant[1]}\n相關性:{tg_instant[2]}")
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text="今天沒有新聞.")

async def instantSimpleTG(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = '-4095879826'
    now = datetime.now(pytz.timezone('Canada/Pacific'))  # Get current time in Pacific timezone
    if now.weekday() in [5, 6]:  # Saturday = 5, Sunday = 6
        await context.bot.send_message(chat_id=chat_id, text="星期六和星期日的即時分析功能已取消.")
        return

    global telegram_instant_array
    global telegram_ai_array

    telegram_instant_array = []
    telegram_ai_array = []
    date = QDate.currentDate().toString("yyyy-MM-dd")
    bt_model = OutputListModel()
    await context.bot.send_message(chat_id=chat_id, text=f"請稍等...\n 正在準備為你分析{date}的實時數據.")
    instantAnalysisFUTU(date, bt_model)
    try:
        for tg_instant in telegram_instant_array:
            await context.bot.send_message(chat_id=chat_id,text=f"{tg_instant[0]} {tg_instant[7]}買入觸發!\n牛熊比例:{tg_instant[19]}\n形式:{tg_instant[2]}\n形式勝率:{tg_instant[1]}\nSPY形式:{tg_instant[3]}\nQQQ形式:{tg_instant[4]}\nSPY(15):{tg_instant[17]}\nQQQ(15):{tg_instant[18]}\nSPY勢向:{tg_instant[5]}\nQQQ勢向:{tg_instant[6]}\n{tg_instant[0]}勢向:{tg_instant[8]}\nSPY過高:{tg_instant[9]}\nSPY過低:{tg_instant[10]}\nQQQ過高:{tg_instant[11]}\nQQQ過低:{tg_instant[12]}\nSPY跳升:{tg_instant[13]}\nSPY跳跌:{tg_instant[14]}\nQQQ跳升:{tg_instant[15]}\nQQQ跳跌:{tg_instant[16]}")
            await context.bot.send_message(chat_id=chat_id,text=f"策略A已觸發.\n(2021-2023年: 88% CALL勝率和95% PUT勝率")
            for tg_ai in telegram_ai_array:
                await context.bot.send_message(chat_id=chat_id, text=f"AI分析員({tg_ai[0]}):\n認為是次交易將會是{tg_ai[1]}")
            diagram_widget = DiagramWidget()
            diagram_widget.futu_diagram(None, tg_instant[0], date)
            path_to_image = f'data/futu/{tg_instant[0]}_{date}.png'
            with open(path_to_image, 'rb') as img:
                await context.bot.send_photo(chat_id, img)
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text="今天沒有適合的股票作交易.")
    document = open(f'data/post-analysis(futu){config_path_extension}/{date}_beforeMarket.csv', 'rb')
    await context.bot.send_document(chat_id, document)
    chat_id = '243423219'
    telegram_ai_array = []
    try:
        await context.bot.send_message(chat_id=chat_id, text=f"請稍等...\n 正在準備為你預測並提供{date}的買入訊號.")
        execute_predictAnalysisFUTU(date, bt_model)
        for tg_ai in telegram_ai_array:
            await context.bot.send_message(chat_id=chat_id,
                                           text=f"{tg_ai[10]}策略觸發!\n{tg_ai[0]} {tg_ai[10]} 買入訊號\n形式(30):{tg_ai[1]}\n形式(15):{tg_ai[2]}\nAI-RF:{tg_ai[3]}\nAI-SVC:{tg_ai[4]}\nAI-DT:{tg_ai[5]}\nAI-LR:{tg_ai[6]}\n總紀錄:{tg_ai[7]}\nCALL機會:{tg_ai[8]}\nPUT機會:{tg_ai[9]}")
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text="今天沒有AA的策略.")
    document = open(f'data/predict{config_path_extension}/{date}_prediction.csv', 'rb')
    await context.bot.send_document(chat_id, document)

async def auto_prepostList(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = '-4095879826'
    now = datetime.now(pytz.timezone('Canada/Pacific'))  # Get current time in Pacific timezone
    if now.weekday() in [5, 6]:  # Saturday = 5, Sunday = 6
        await context.bot.send_message(chat_id=chat_id, text="星期六和星期日的盤前數據核實功能已取消.")
        return
    date = QDate.currentDate()
    bt_model = OutputListModel()
    current_date = date.toString("yyyy-MM-dd")
    await context.bot.send_message(chat_id=chat_id, text=f"請稍等, {current_date}的盤後結果準備中...")
    execute_preanalysis(current_date, bt_model)
    await context.bot.send_message(chat_id=chat_id, text=f"請稍等, {current_date}的盤前核對結果準備中...")
    execute_postanalysis(current_date, current_date, bt_model)
    document = open(f'data/post-analysis{config_path_extension}/{current_date}_beforeMarket.csv', 'rb')
    await context.bot.send_document(chat_id, document)

async def auto_setupUpdate(context: ContextTypes.DEFAULT_TYPE) -> None:
    global telegram_instant_array
    global telegram_pattern_array
    telegram_instant_array = []
    telegram_pattern_array = []
    date = QDate.currentDate().toString("yyyy-MM-dd")
    chat_id = '-4095879826'
    now = datetime.now(pytz.timezone('Canada/Pacific'))  # Get current time in Pacific timezone
    if now.weekday() in [5, 6]:  # Saturday = 5, Sunday = 6
        await context.bot.send_message(chat_id=chat_id, text="星期六和星期日的配置及數據更新功能已取消.")
        return
    bt_model = OutputListModel()
    await context.bot.send_message(chat_id=chat_id, text=f"請稍等, {date}的配置準備中...")
    execute_setup(date, bt_model)
    document = open(f'data/setup{config_path_extension}/{date}_setup.csv', 'rb')
    await context.bot.send_document(chat_id, document)

    await context.bot.send_message(chat_id=chat_id, text=f"請稍等, 準備更新{date}的數據庫...")
    updateData(date, bt_model)
    sorted_data = sorted(telegram_pattern_array, key=lambda x: float(x[3]))
    end_index = len(sorted_data) - 1
    if sorted_data:
        await context.bot.send_message(chat_id=chat_id,
                                       text=f"是次PUT最大利潤的股票為{sorted_data[0][0]}\n利潤:{sorted_data[0][3]}\n形式:{sorted_data[0][1]}\n形式(15):{sorted_data[0][2]}")
        await context.bot.send_message(chat_id=chat_id,
                                       text=f"是次CALL最大利潤的股票為{sorted_data[end_index][0]}\n利潤:{sorted_data[end_index][3]}\n形式:{sorted_data[end_index][1]}\n形式(15):{sorted_data[end_index][2]}")
    for instant in telegram_instant_array:
        await context.bot.send_message(chat_id=chat_id, text=instant)
    await context.bot.send_message(chat_id=chat_id, text="更新已完成.\n注:請勿一天執行多過一次.")

async def auto_rankList(context: ContextTypes.DEFAULT_TYPE) -> None:
    date = QDate.currentDate().toString("yyyy-MM-dd")
    chat_id = '-4095879826'
    now = datetime.now(pytz.timezone('Canada/Pacific'))  # Get current time in Pacific timezone
    if now.weekday() in [5, 6]:  # Saturday = 5, Sunday = 6
        await context.bot.send_message(chat_id=chat_id, text="星期六和星期日的刷新每日排行功能已取消.")
        return
    bt_model = OutputListModel()
    await context.bot.send_message(chat_id=chat_id, text=f"請稍等, {date}的排行準備中...")
    execute_rankList(date, bt_model)
    document = open(f'data/ranking{config_path_extension}/{date}_list.csv', 'rb')
    await context.bot.send_document(chat_id, document)


async def instantTG(update, context):
    global telegram_instant_array
    global telegram_ai_array

    telegram_instant_array = []
    telegram_ai_array = []
    date = QDate.currentDate().toString("yyyy-MM-dd")
    bt_model = OutputListModel()
    chat_id = update.message.chat_id
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等...\n 正在準備為你分析{date}的實時數據.")
    instantAnalysisFUTU(date, bt_model)
    for tg_instant in telegram_instant_array:
        await context.bot.send_message(chat_id=chat_id,
                                       text=f"{tg_instant[0]} {tg_instant[7]}買入觸發!\n牛熊比例:{tg_instant[19]}\n形式:{tg_instant[2]}\n形式勝率:{tg_instant[1]}\nSPY形式:{tg_instant[3]}\nQQQ形式:{tg_instant[4]}\nSPY(15):{tg_instant[17]}\nQQQ(15):{tg_instant[18]}\nSPY勢向:{tg_instant[5]}\nQQQ勢向:{tg_instant[6]}\n{tg_instant[0]}勢向:{tg_instant[8]}\nSPY過高:{tg_instant[9]}\nSPY過低:{tg_instant[10]}\nQQQ過高:{tg_instant[11]}\nQQQ過低:{tg_instant[12]}\nSPY跳升:{tg_instant[13]}\nSPY跳跌:{tg_instant[14]}\nQQQ跳升:{tg_instant[15]}\nQQQ跳跌:{tg_instant[16]}")
        await context.bot.send_message(chat_id=chat_id, text=f"策略A已觸發.\n(2021-2023年: 88% CALL勝率和95% PUT勝率")
        for tg_ai in telegram_ai_array:
            await context.bot.send_message(chat_id=chat_id, text=f"AI分析員({tg_ai[0]}):\n認為是次交易將會是{tg_ai[1]}")
        diagram_widget = DiagramWidget()
        diagram_widget.futu_diagram(None, tg_instant[0], date)
        path_to_image = f'data/futu/{tg_instant[0]}_{date}.png'
        with open(path_to_image, 'rb') as img:
            await context.bot.send_photo(chat_id, img)
    document = open(f'data/post-analysis(futu){config_path_extension}/{date}_beforeMarket.csv', 'rb')
    await context.bot.send_document(chat_id, document)
    chat_id = '243423219'
    telegram_ai_array = []
    try:
        await context.bot.send_message(chat_id=chat_id, text=f"請稍等...\n 正在準備為你預測並提供{date}的買入訊號.")
        execute_predictAnalysisFUTU(date, bt_model)
        for tg_ai in telegram_ai_array:
            await context.bot.send_message(chat_id=chat_id,
                                           text=f"{tg_ai[10]}策略觸發!\n{tg_ai[0]} {tg_ai[10]} 買入訊號\n形式(30):{tg_ai[1]}\n形式(15):{tg_ai[2]}\nAI-RF:{tg_ai[3]}\nAI-SVC:{tg_ai[4]}\nAI-DT:{tg_ai[5]}\nAI-LR:{tg_ai[6]}\n總紀錄:{tg_ai[7]}\nCALL機會:{tg_ai[8]}\nPUT機會:{tg_ai[9]}")
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text="今天沒有AA的策略.")
    document = open(f'data/predict{config_path_extension}/{date}_prediction.csv', 'rb')
    await context.bot.send_document(chat_id, document)


def TGprocess_finished(worker):
    worker.quit()
    worker.wait()


async def send_rankList(update, context):
    isAll = False
    if context.args:
        if "all" != context.args[0]:
            date = QDate.fromString(context.args[0], 'yyyy-MM-dd')
            isAll = False
        else:
            isAll = True
    else:
        date = QDate.currentDate()
        isAll = False
    bt_model = OutputListModel()
    if isAll == True:
        start_date = datetime(2021, 1, 2)
        end_date = datetime(2021, 12, 30)
        us_calendar = mcal.get_calendar('NYSE')
        next_trading_day = start_date
        while next_trading_day <= end_date:
            formatted_date = next_trading_day.strftime('%Y-%m-%d')
            current = QDate.fromString(formatted_date, 'yyyy-MM-dd')
            formatted = current.toString("yyyy-MM-dd")
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等, {formatted}的排行準備中...")
            try:
                execute_rankList(formatted, bt_model)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{formatted}的排行成功.")
            except Exception as e:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{formatted}的排行失敗.")
            next_trading_day += timedelta(days=1)
            while len(us_calendar.valid_days(start_date=next_trading_day, end_date=next_trading_day)) <= 0:
                next_trading_day += timedelta(days=1)
    else:
        chat_id = update.message.chat_id
        current_date = date.toString("yyyy-MM-dd")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等, {current_date}的排行準備中...")
        execute_rankList(current_date, bt_model)
        document = open(f'data/ranking{config_path_extension}/{current_date}_list.csv', 'rb')
        await context.bot.send_document(chat_id, document)

async def send_setupList(update, context):
    if context.args:
        date = context.args[0]
    else:
        date = QDate.currentDate().toString("yyyy-MM-dd")
    chat_id = update.message.chat_id
    bt_model = OutputListModel()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等, {date}的配置準備中...")
    execute_setup(date, bt_model)
    document = open(f'data/setup{config_path_extension}/{date}_setup.csv', 'rb')
    await context.bot.send_document(chat_id, document)

async def send_preList(update, context):
    isAll = False
    if context.args:
        if "all" != context.args[0]:
            date = QDate.fromString(context.args[0], 'yyyy-MM-dd')
            isAll = False
        else:
            isAll = True
    else:
        date = QDate.currentDate()
        isAll = False
    bt_model = OutputListModel()
    if isAll == True:
        start_date = datetime(2022, 1, 2)
        end_date = datetime(2022, 12, 31)
        us_calendar = mcal.get_calendar('NYSE')
        next_trading_day = start_date
        while next_trading_day <= end_date:
            formatted_date = next_trading_day.strftime('%Y-%m-%d')
            current = QDate.fromString(formatted_date, 'yyyy-MM-dd')
            formatted = current.toString("yyyy-MM-dd")
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等, {formatted}的盤後結果準備中...")
            try:
                execute_preanalysis(formatted, bt_model)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{formatted}的盤後結果成功.")
            except Exception as e:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{formatted}的盤後結果失敗.")
            next_trading_day += timedelta(days=1)
            while len(us_calendar.valid_days(start_date=next_trading_day, end_date=next_trading_day)) <= 0:
                next_trading_day += timedelta(days=1)
    else:
        chat_id = update.message.chat_id
        current_date = date.toString("yyyy-MM-dd")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等, {current_date}的盤後結果準備中...")
        execute_preanalysis(current_date, bt_model)
        document = open(f'data/pre-analysis{config_path_extension}/{current_date}_afterMarket.csv', 'rb')
        await context.bot.send_document(chat_id, document)


async def send_postList(update, context):
    isAll = False
    if context.args:
        if "all" != context.args[0]:
            date = QDate.fromString(context.args[0], 'yyyy-MM-dd')
            isAll = False
        else:
            isAll = True
    else:
        date = QDate.currentDate()
        isAll = False
    bt_model = OutputListModel()
    if isAll == True:
        start_date = datetime(2022, 1, 2)
        end_date = datetime(2022, 12, 30)
        current_date = start_date
        yDate = "2023-01-01"
        us_calendar = mcal.get_calendar('NYSE')
        next_trading_day = start_date
        while next_trading_day <= end_date:
            formatted_date = next_trading_day.strftime('%Y-%m-%d')
            current = QDate.fromString(formatted_date, 'yyyy-MM-dd')
            formatted = current.toString("yyyy-MM-dd")
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等, {formatted}的盤前核對結果準備中...")
            try:
                execute_postanalysis(yDate, formatted, bt_model)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{formatted}的盤前核對結果成功.")
            except Exception as e:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{formatted}的盤前核對結果失敗.")
            next_trading_day += timedelta(days=1)
            while len(us_calendar.valid_days(start_date=next_trading_day, end_date=next_trading_day)) <= 0:
                next_trading_day += timedelta(days=1)
    else:
        chat_id = update.message.chat_id
        current_date = date.toString("yyyy-MM-dd")
        input_date = datetime.strptime(current_date, "%Y-%m-%d")
        us_calendar = mcal.get_calendar('NYSE')
        previous_trading_day = input_date - timedelta(days=1)
        while len(us_calendar.valid_days(start_date=previous_trading_day, end_date=previous_trading_day)) <= 0:
            previous_trading_day -= timedelta(days=1)
        yesterday_day = previous_trading_day.strftime('%Y-%m-%d')
        yesterday = QDate.fromString(yesterday_day, 'yyyy-MM-dd')
        yDate = yesterday.toString("yyyy-MM-dd")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等, {current_date}的盤前核對結果準備中...")
        execute_postanalysis(yDate, current_date, bt_model)
        document = open(f'data/post-analysis{config_path_extension}/{current_date}_beforeMarket.csv', 'rb')
        await context.bot.send_document(chat_id, document)


async def send_graph(update, context):
    if context.args:
        symbol = context.args[0]
        date = context.args[1]
    else:
        symbol = "AVGO"
        date = QDate.currentDate().toString("yyyy-MM-dd")
    chat_id = update.message.chat_id
    bt_model = OutputListModel()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等, 正在為{date}的{symbol}繪圖...")
    diagram_widget = DiagramWidget()
    diagram_widget.update_diagram(None, symbol, date)
    path_to_image = f'data/graph{config_path_extension}/{symbol}_{date}.png'
    with open(path_to_image, 'rb') as img:
        await context.bot.send_photo(chat_id, img)

async def send_graph_sub(update, context):
    if context.args:
        symbol = context.args[0]
        date = context.args[1]
    else:
        symbol = "AVGO"
        date = QDate.currentDate().toString("yyyy-MM-dd")
    chat_id = update.message.chat_id
    bt_model = OutputListModel()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等, 正在為{date}的{symbol}繪圖...")
    diagram_widget = DiagramWidget()
    diagram_widget.update_diagram_15(None, symbol, date)
    path_to_image = f'data/graph{config_path_extension}/{symbol}_{date}.png'
    with open(path_to_image, 'rb') as img:
        await context.bot.send_photo(chat_id, img)

async def send_prediction_graph(update, context):
    if context.args:
        symbol = context.args[0]
    else:
        symbol = "AVGO"
    date = QDate.currentDate().toString("yyyy-MM-dd")
    chat_id = update.message.chat_id
    bt_model = OutputListModel()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等, 正在為{date}的{symbol}進行即時預測...")
    diagram_widget = DiagramWidget()
    diagram_widget.predict_full_diagram(None, symbol, date)
    path_to_image = f'data/predicted_full{config_path_extension}/{symbol}_{date}.png'
    with open(path_to_image, 'rb') as img:
        await context.bot.send_photo(chat_id, img)


async def send_futu(update, context):
    if context.args:
        symbol = context.args[0]
    else:
        symbol = "AVGO"
    date = QDate.currentDate().toString("yyyy-MM-dd")
    chat_id = update.message.chat_id
    bt_model = OutputListModel()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等, 正在為{symbol}製作實時繪圖...")
    diagram_widget = DiagramWidget()
    diagram_widget.futu_diagram(None, symbol, date)
    path_to_image = f'data/futu/{symbol}_{date}.png'
    with open(path_to_image, 'rb') as img:
        await context.bot.send_photo(chat_id, img)


async def send_dailyUpdate(update, context):
    global telegram_instant_array
    global telegram_pattern_array

    telegram_instant_array = []
    telegram_pattern_array = []
    if context.args:
        date = context.args[0]
    else:
        date = QDate.currentDate().toString("yyyy-MM-dd")
    chat_id = update.message.chat_id
    bt_model = OutputListModel()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等, 準備更新{date}的數據庫...")
    updateData(date, bt_model)
    sorted_data = sorted(telegram_pattern_array, key=lambda x: float(x[3]))
    end_index = len(sorted_data) - 1
    if sorted_data:
        await context.bot.send_message(chat_id=chat_id,
                                       text=f"是次PUT最大利潤的股票為{sorted_data[0][0]}\n利潤:{sorted_data[0][3]}\n形式:{sorted_data[0][1]}\n形式(15):{sorted_data[0][2]}")
        await context.bot.send_message(chat_id=chat_id,
                                       text=f"是次CALL最大利潤的股票為{sorted_data[end_index][0]}\n利潤:{sorted_data[end_index][3]}\n形式:{sorted_data[end_index][1]}\n形式(15):{sorted_data[end_index][2]}")
    for instant in telegram_instant_array:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=instant)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="更新已完成.\n注:請勿一天執行多過一次.")

async def get_backtestList(update, context):
    if context.args:
        symbol = context.args[0]
        chat_id = update.message.chat_id
        bt_model = OutputListModel()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"正在存取{symbol}的回測數據...")
        document = open(f'data/history{config_path_extension}/{symbol}.csv', 'rb')
        await context.bot.send_document(chat_id, document)


async def send_backtestList(update, context):
    if context.args:
        symbol = context.args[0]
        chat_id = update.message.chat_id
        bt_model = OutputListModel()
        if symbol == "all":
            folder_path = f'data/history{config_path_extension}'
            symbols = [os.path.splitext(f)[0] for f in os.listdir(folder_path) if
                       os.path.isfile(os.path.join(folder_path, f))]
            for input in symbols:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等, 準備為{input}進行回測...")
                execute_backtest(input, bt_model)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{input}回測完成.")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等, 準備為{symbol}進行回測...")
            execute_backtest(symbol, bt_model)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{symbol}回測完成.")
            document = open(f'data/history{config_path_extension}/{symbol}.csv', 'rb')
            await context.bot.send_document(chat_id, document)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請輸入股票代碼.")


async def send_trainData(update, context):
    if context.args:
        symbol = context.args[0]
        chat_id = update.message.chat_id
        bt_model = OutputListModel()
        if symbol == "all":
            folder_path = f'data/history{config_path_extension}'
            symbols = [os.path.splitext(f)[0] for f in os.listdir(folder_path) if
                       os.path.isfile(os.path.join(folder_path, f))]
            for input in symbols:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等, 準備為{input}訓練數據...")
                execute_trainData(input, bt_model)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{input}訓練數據完成.")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等, 準備為{symbol}進行訓練數據...")
            execute_trainData(symbol, bt_model)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{symbol}訓練數據完成.")
            document = open(f'data/train{config_path_extension}/{symbol}.csv', 'rb')
            await context.bot.send_document(chat_id, document)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請輸入股票代碼.")


async def restart_program(update, context):
    update.message.reply_text('Restarting the program...')
    subprocess.Popen(["python", "GUI.py"])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"程式已重新啟動.")


def startTelegramBot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    application = ApplicationBuilder().token('6512259248:AAE-cXHkSigC6K_Q4gKxrlAkv82t82cABBw').build()

    start_handler = CommandHandler('start', startTG)
    application.add_handler(start_handler)
    instant_handler = CommandHandler('instant', instantTG)
    application.add_handler(instant_handler)
    application.add_handler(CommandHandler("rank", send_rankList))
    application.add_handler(CommandHandler("prelist", send_preList))
    application.add_handler(CommandHandler("postlist", send_postList))
    application.add_handler(CommandHandler("update", send_dailyUpdate))
    application.add_handler(CommandHandler("backtest", send_backtestList))
    application.add_handler(CommandHandler("restart", restart_program))
    application.add_handler(CommandHandler("help", helpTG))
    application.add_handler(CommandHandler("plot", send_graph))
    application.add_handler(CommandHandler("subplot", send_graph_sub))
    application.add_handler(CommandHandler("real", send_futu))
    application.add_handler(CommandHandler("train", send_trainData))
    application.add_handler(CommandHandler("predict", send_prediction_graph))
    application.add_handler(CommandHandler("monitor", monitor_stock))
    application.add_handler(CommandHandler("detail", send_detail))
    application.add_handler(CommandHandler("get", get_backtestList))
    application.add_handler(CommandHandler("pattern", send_pattern))
    application.add_handler(CommandHandler("setup", send_setupList))
    application.add_handler(CommandHandler("schedule", set_timer))

    loop.run_until_complete(application.run_polling())



def monitorOrder(bt_model, text):
    trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US, host='127.0.0.1', port=11111,
                                  security_firm=SecurityFirm.FUTUSECURITIES)
    ret, data = trd_ctx.order_list_query(order_id=text)
    if ret == RET_OK:
        while data['order_status'][0] == "SUBMITTING" or data['order_status'][0] == "SUBMITTED":
            ret, data = trd_ctx.order_list_query(order_id=text)
            print(data['order_id'][0])
            print(data['order_id'].values.tolist())
            bt_model.add_output("Currently You still have the below opening order:")
            bt_model.add_output(f"Order ID: {data['order_id'][0]}")
            bt_model.add_output(
                f"Stock Name: {data['stock_name'][0]} AND Price: {data['price'][0]} AND QTY: {data['qty'][0]}")
            timemodule.sleep(2)
        bt_model.add_output("Now You have no any opening orders.")
    else:
        print('order_list_query error: ', data)
        bt_model.add_output("order_list_query")


def autoTrade(bt_model):
    global telegram_instant_array
    telegram_instant_array = []

    bt_model.add_output("Auto Trading is started...")
    bt_model.add_output("Ready to wait the time for 'BUY' signal...")
    today_date = QDate.currentDate().toString("yyyy-MM-dd")
    # Run Instant Analysis for Buy Signal
    instantAnalysisFUTU(today_date, bt_model)
    if len(overall_csv) != 0:
        for stock in overall_csv:
            # Filter Chance with lower than 0.6
            if float(stock[5]) > 0.6:
                bt_model.add_output(f"Getting Stock Price for {stock[0]}...")
                # Ger Price
                ret_sub, err_message = quote_ctx.subscribe([f"US.{stock[0]}"], [SubType.QUOTE], subscribe_push=False)
                if ret_sub == RET_OK:
                    ABret, Adata = quote_ctx.get_stock_quote(f"US.{stock[0]}")
                    if ABret == RET_OK:
                        # Get Targe Price
                        current_stock_price = float(Adata["last_price"][0])
                        bt_model.add_output(f"The Current Stock Price is {current_stock_price}")
                        type = ""
                        if stock[4] == "CALL":
                            type = "C"
                            if float(current_stock_price) < 100:
                                target_stock_price = (float(current_stock_price) // 2) * 2
                            else:
                                target_stock_price = (float(current_stock_price) // 5) * 5
                        else:
                            type = "P"
                            if float(current_stock_price) < 100:
                                target_stock_price = (float(current_stock_price) + 1) // 2 * 2
                            else:
                                target_stock_price = (float(current_stock_price) + 4) // 5 * 5
                        current_date = datetime.now()
                        days_ahead = (4 - current_date.weekday()) % 7
                        next_friday = current_date + timedelta(days=days_ahead)
                        next_friday_date = next_friday.strftime('%y%m%d')
                        price = int(float(target_stock_price))
                        # View Option Price
                        bt_model.add_output(f"Viewing Option Price for {stock[0]}...")
                        Aret_sub, err_message = quote_ctx.subscribe(
                            [f"US.{stock[0]}{next_friday_date}{type}{price}000"],
                            [SubType.QUOTE],
                            subscribe_push=False)
                        Aret_subb = \
                            quote_ctx.subscribe([f"US.{stock[0]}{next_friday_date}{type}{price}000"],
                                                [SubType.ORDER_BOOK],
                                                subscribe_push=False)[0]
                        if Aret_sub == RET_OK and Aret_subb == RET_OK:  # Successfully subscribed
                            Aret, dataB = quote_ctx.get_stock_quote(
                                f"US.{stock[0]}{next_friday_date}{type}{price}000")  # Get the latest 2 candlestick data of HK.00700
                            Arett, data2B = quote_ctx.get_order_book(f"US.{stock[0]}{next_friday_date}{type}{price}000",
                                                                     num=1)
                            if Aret == RET_OK and Arett == RET_OK:
                                option_name = dataB["code"][0]
                                option_price = dataB["last_price"][0]
                                bt_model.add_output(
                                    f"Found the Option Name: {option_name} with current Option Price: {option_price}")
                                middle_number = (Decimal(data2B["Ask"][0][0]) + Decimal(data2B["Bid"][0][0])) / Decimal(
                                    '2')
                                rounded_middle_number = round(middle_number, 2)
                                qty = int(500 / (rounded_middle_number * 100))
                                if qty == 0:
                                    qty = 1
                                amount = qty * rounded_middle_number * 100
                                market_price = rounded_middle_number
                                # Order Option Price
                                pwd_unlock = '147852'
                                trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US, host='127.0.0.1',
                                                              port=11111,
                                                              security_firm=SecurityFirm.FUTUSECURITIES)
                                ret, data = trd_ctx.unlock_trade(pwd_unlock)
                                if ret == RET_OK:
                                    trd_sidee = TrdSide.BUY
                                    ret, data = trd_ctx.place_order(price=float(market_price), qty=int(qty),
                                                                    code=option_name,
                                                                    trd_side=trd_sidee, trd_env=TrdEnv.REAL)
                                    if ret == RET_OK:
                                        bt_model.add_output(f'The order for {option_name} has been made successfully!')
                                        bt_model.add_output(f'Market Price: {market_price}, Quantity: {qty}')
                                        order_id = data['order_id'][0]
                                        # Monitor and Modify Order Until Deals
                                        trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US, host='127.0.0.1',
                                                                      port=11111,
                                                                      security_firm=SecurityFirm.FUTUSECURITIES)
                                        ret, data = trd_ctx.order_list_query(order_id=order_id)
                                        if ret == RET_OK:
                                            while data['order_status'][0] == "SUBMITTING" or data['order_status'][
                                                0] == "SUBMITTED":
                                                ret, data = trd_ctx.order_list_query(order_id=order_id)
                                                print(data['order_id'][0])
                                                print(data['order_id'].values.tolist())
                                                bt_model.add_output("Currently You still have the below opening order:")
                                                bt_model.add_output(f"Order ID: {data['order_id'][0]}")
                                                bt_model.add_output(
                                                    f"Stock Name: {data['stock_name'][0]} AND Price: {data['price'][0]} AND QTY: {data['qty'][0]}")
                                                timemodule.sleep(2)
                                            bt_model.add_output("Now You have no any opening orders.")
                                        else:
                                            print('order_list_query error: ', data)
                                            bt_model.add_output("order_list_query")
                                    else:
                                        bt_model.add_output('place_order error ')
                                        print('place_order error: ', data)
                                else:
                                    bt_model.add_output('unlock_trade failed ')
                                    print('unlock_trade failed: ', data)
                                trd_ctx.close()
                            else:
                                bt_model.add_output('error')
                        else:
                            bt_model.add_output('subscription failed')
                    else:
                        bt_model.add_output('error')
                else:
                    bt_model.add_output('subscription failed', err_message)


class CSVTableModel(QAbstractTableModel):
    def __init__(self, data=[], parent=None):
        super().__init__(parent)
        self.header = data[0] if data else []
        self.data = data[1:] if data else []

    def rowCount(self, parent=None):
        return len(self.data)

    def columnCount(self, parent=None):
        return len(self.header)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            return str(self.data[row][column])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return str(self.header[section])
        return None

    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()
        self.data.sort(key=lambda x: x[column], reverse=order == Qt.DescendingOrder)
        self.layoutChanged.emit()

    def get_data(self, row, col):
        # Access the data for the specified row and column
        return self.data[row][col]


class WorkerThread(QThread):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.bt_model = None
        self.table_view = None
        self.diagram = None
        self.text = ""
        self.text_2 = ""
        self.tab = ""

    def set_data(self, bt_model, table_view, diagram, text, text_2, tab):
        self.bt_model = bt_model
        self.table_view = table_view
        self.diagram = diagram
        self.text = text
        self.text_2 = text_2
        self.tab = tab

    def run(self):
        # Perform the task with the provided data
        if self.tab == "backtest":
            self.generate_list(self.bt_model, self.table_view, self.text)
        elif self.tab == "preanalysis":
            self.generate_prelist(self.bt_model, self.table_view, self.text)
        elif self.tab == "postanalysis":
            self.generate_postlist(self.bt_model, self.table_view, self.text, self.text_2)
        elif self.tab == "update":
            self.update_list(self.bt_model, self.text)
        elif self.tab == "monitorAV":
            self.monitor_dataAV(self.bt_model, self.text, self.text_2)
        elif self.tab == "newsanalysis":
            self.generate_newslist(self.bt_model, self.table_view, self.text)
        elif self.tab == "analysisFUTU":
            self.generate_futulist(self.bt_model, self.table_view, self.text)
        elif self.tab == "monitorFUTU":
            self.monitor_dataFUTU(self.bt_model, self.text, self.text_2)
        elif self.tab == "rankingList":
            self.generate_rankList(self.bt_model, self.table_view, self.text)
        elif self.tab == "performanceList":
            self.generate_performanceList(self.bt_model, self.table_view, self.text)
        elif self.tab == "maxList":
            self.generate_maxList(self.bt_model, self.table_view, self.text)
        elif self.tab == "fullList":
            self.generate_fullList(self.bt_model, self.table_view, self.text)
        elif self.tab == "predictAnalysis":
            self.generate_predictAnalysis(self.bt_model, self.table_view, self.text)
        elif self.tab == "rankingChange":
            self.change_ranking(self.table_view, self.text)
        elif self.tab == "startBot":
            self.start_bot()
        elif self.tab == "monitorOrder":
            self.monitor_order(self.bt_model, self.text)
        elif self.tab == "startAutoTrade":
            self.start_autoTrade(self.bt_model)
        elif self.tab == "predictionReal":
            self.conduct_predictionReal(self.bt_model, self.diagram, self.text, self.text_2)
        elif self.tab == "predictionFull":
            self.conduct_predictionFull(self.bt_model, self.diagram, self.text, self.text_2)
        elif self.tab == "trainData":
            self.train_data(self.bt_model, self.table_view, self.text)
        elif self.tab == "setup":
            self.generate_setuplist(self.bt_model, self.table_view, self.text)
        elif self.tab == "earning":
            self.generate_earninglist(self.bt_model, self.table_view, self.text)
        elif self.tab == "verify":
            self.generate_verifylist(self.bt_model, self.table_view, self.text)
        # Emit the finished signal
        self.finished.emit()

    def generate_list(self, bt_model, table_view, text):

        execute_backtest(text, bt_model)

        if len(array_overall) != 0:
            data = bt_array.tolist()

            model = CSVTableModel(data)
            table_view.setModel(model)

        self.finished.emit()

    def generate_prelist(self, bt_model, table_view, text):

        execute_preanalysis(text, bt_model)

        if len(overall_csv) != 0:
            data = pa_array.tolist()

            model = CSVTableModel(data)
            table_view.setModel(model)

        self.finished.emit()

    def generate_postlist(self, bt_model, table_view, text, text_2):

        execute_postanalysis(text, text_2, bt_model)

        if len(overall_csv) != 0:
            data = pta_array.tolist()

            model = CSVTableModel(data)
            table_view.setModel(model)

        self.finished.emit()

    def update_list(self, bt_model, text):

        updateData(text, bt_model)

        self.finished.emit()

    def generate_setuplist(self, bt_model, table_view, text):

        execute_setup(text, bt_model)

        if len(overall_csv) != 0:
            data = s_array.tolist()

            model = CSVTableModel(data)
            table_view.setModel(model)

        self.finished.emit()

    def generate_maxList(self, bt_model, table_view, text):

        execute_maxList(text, bt_model)

        if len(max_array) != 0:
            data = max_array.tolist()

            model = CSVTableModel(data)
            table_view.setModel(model)

        self.finished.emit()

    def generate_predictAnalysis(self, bt_model, table_view, text):

        execute_predictAnalysis(text, bt_model)

        if len(full_array) != 0:
            data = full_array.tolist()

            model = CSVTableModel(data)
            table_view.setModel(model)

        self.finished.emit()

    def generate_fullList(self, bt_model, table_view, text):

        execute_fullList(text, bt_model)

        if len(full_array) != 0:
            data = full_array.tolist()

            model = CSVTableModel(data)
            table_view.setModel(model)

        self.finished.emit()

    def generate_earninglist(self, bt_model, table_view, text):

        execute_earning(text, bt_model)

        if len(overall_csv) != 0:
            data = e_array.tolist()

            model = CSVTableModel(data)
            table_view.setModel(model)

        self.finished.emit()

    def generate_newslist(self, bt_model, table_view, text):

        execute_newsanalysis(text, bt_model)

        if len(overall_csv) != 0:
            data = news_array.tolist()

            model = CSVTableModel(data)
            table_view.setModel(model)

        self.finished.emit()

    def generate_verifylist(self, bt_model, table_view, text):

        execute_verifyEarning(text, bt_model)

        if len(overall_csv) != 0:
            data = ve_array.tolist()

            model = CSVTableModel(data)
            table_view.setModel(model)

        self.finished.emit()

    def monitor_dataAV(self, bt_model, text, text_2):

        monitorAV(text, text_2, bt_model)

        self.finished.emit()

    def generate_futulist(self, bt_model, table_view, text):
        global telegram_instant_array
        telegram_instant_array = []

        instantAnalysisFUTU(text, bt_model)

        if len(overall_csv) != 0:
            data = futu_array.tolist()

            model = CSVTableModel(data)
            table_view.setModel(model)

        self.finished.emit()

    def monitor_dataFUTU(self, bt_model, text, text_2):

        monitorFUTU(text, text_2, bt_model)

        self.finished.emit()

    def generate_rankList(self, bt_model, table_view, text):

        execute_rankList(text, bt_model)

        if len(rank_csv) != 0:
            data = rank_array.tolist()

            model = CSVTableModel(data)
            table_view.setModel(model)

        self.finished.emit()

    def generate_performanceList(self, bt_model, table_view, text):

        execute_performanceList(text, bt_model)

        if len(performance_csv) != 0:
            data = performance_csv.tolist()

            model = CSVTableModel(data)
            table_view.setModel(model)

        self.finished.emit()

    def change_ranking(self, table_view, text):
        if len(rank_csv) != 0:
            data = rank_array.tolist()
            df = pd.DataFrame(data)
            first_row = df.iloc[:1]
            data_to_sort = df.iloc[1:]
            sorted_df_by_index = data_to_sort.sort_values(by=text, ascending=False)
            sorted_data_with_first_row = pd.concat([first_row, sorted_df_by_index])
            sorted_data_by_index = sorted_data_with_first_row.values.tolist()
            model = CSVTableModel(sorted_data_by_index)
            table_view.setModel(model)

        self.finished.emit()

    def start_bot(self):
        startTelegramBot()
        self.finished.emit()

    def monitor_order(self, bt_model, text):
        monitorOrder(bt_model, text)
        self.finished.emit()

    def start_autoTrade(self, bt_model):
        autoTrade(bt_model)
        self.finished.emit()

    def conduct_predictionReal(self, bt_model, diagram, text, text2):
        refresh_seconds = 10
        for i in range(180):
            diagram.futu_diagram(None, text, text2)
            bt_model.add_output(f"Refresh Real Graphs... {i} (Every {refresh_seconds} seconds)")
            timemodule.sleep(refresh_seconds)
        self.finished.emit()

    def conduct_predictionFull(self, bt_model, diagram, text, text2):
        refresh_secondss = 18
        for i in range(180):
            diagram.predict_full_diagram(None, text, text2)
            bt_model.add_output(f"Refresh Predicted Full Graphs... {i} (Every {refresh_secondss} seconds)")
            timemodule.sleep(refresh_secondss)
        self.finished.emit()

    def train_data(self, bt_model, table_view, text):

        execute_trainData(text, bt_model)

        if len(array_overall) != 0:
            data = td_array.tolist()

            model = CSVTableModel(data)
            table_view.setModel(model)

        self.finished.emit()


class CustomDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)

        if index.column() == 9 and (index.data() == "1" or index.data() == "1.0"):
            option.backgroundBrush = QColor("green")
        elif index.column() == 9 and (index.data() == "0" or index.data() == "0.0"):
            option.backgroundBrush = QColor("red")


class OutputListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.output_data = []

    def rowCount(self, parent=None):
        return len(self.output_data)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self.output_data[index.row()])

    def add_output(self, output):
        self.beginInsertRows(self.index(self.rowCount(), 0), self.rowCount(), self.rowCount())
        self.output_data.append(output)
        self.endInsertRows()

        # Emit the dataChanged signal for the affected model indexes
        first_index = self.index(self.rowCount() - 1, 0)
        last_index = self.index(self.rowCount() - 1, 0)
        self.dataChanged.emit(first_index, last_index)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Neverland v4.8 Public")
        self.setGeometry(200, 200, 2400, 1600)
        self.setWindowIcon(QIcon('logo.png'))

        # Create a central widget and layout
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        # Create the tab widget
        self.tab_widget = QTabWidget(self)
        layout.addWidget(self.tab_widget)

        # Set the central widget
        self.setCentralWidget(central_widget)

        # Add tabs to the tab widget
        self.add_tabs()

        self.set_blue_theme()
        self.selected_postDate = ""
        self.selected_symbol = ""
        self.worker_threads = []

        self.priceRadio = 0.2

    def add_tabs(self):
        # Create tabs
        tab1 = QWidget()
        tab2 = QWidget()
        tab3 = QWidget()
        tab4 = QWidget()
        tab5 = QWidget()
        tab6 = QWidget()
        tab7 = QWidget()
        tab8 = QWidget()
        tab9 = QWidget()
        tab10 = QWidget()
        tab11 = QWidget()
        tab12 = QWidget()
        tab13 = QWidget()
        tab14 = QWidget()
        tab15 = QWidget()

        # Add tabs to the tab widget
        self.tab_widget.addTab(tab1, "Backtesting")
        self.tab_widget.addTab(tab2, "Pre-Analysis")
        self.tab_widget.addTab(tab3, "Post-Analysis")
        self.tab_widget.addTab(tab4, "Daily Update")
        # self.tab_widget.addTab(tab5, "Monitoring (AV)")
        self.tab_widget.addTab(tab5, "Setup")
        self.tab_widget.addTab(tab6, "Instant Analysis")
        self.tab_widget.addTab(tab7, "Monitoring")
        self.tab_widget.addTab(tab14, "News Analysis")
        self.tab_widget.addTab(tab12, "Training")
        self.tab_widget.addTab(tab11, "Prediction")
        self.tab_widget.addTab(tab8, "Trading")
        self.tab_widget.addTab(tab9, "Ranking")
        self.tab_widget.addTab(tab15, "Earning")
        self.tab_widget.addTab(tab13, "Performance")
        self.tab_widget.addTab(tab10, "Configuration")

        # Add content to the tabs
        self.add_content_to_backtesting(tab1)
        self.add_content_to_preanalysis(tab2)
        self.add_content_to_postanalysis(tab3)
        self.add_content_to_updateData(tab4)
        self.add_content_to_setup(tab5)
        # self.add_content_to_monitoringAV(tab5)
        self.add_content_to_analysisFUTU(tab6)
        self.add_content_to_monitoringFUTU(tab7)
        self.add_content_to_trading(tab8)
        self.add_content_to_rankingList(tab9)
        self.add_content_to_configuration(tab10)
        self.add_content_to_prediction(tab11)
        self.add_content_to_training(tab12)
        self.add_content_to_performanceList(tab13)
        self.add_content_to_newsanalysis(tab14)
        self.add_content_to_earning(tab15)

    def set_blue_theme(self):
        # Set the palette for the blue theme
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(230, 241, 246))
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.Base, QColor(230, 241, 246))
        palette.setColor(QPalette.AlternateBase, QColor(230, 241, 246))
        palette.setColor(QPalette.Button, QColor(0, 0, 255))
        palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        self.setPalette(palette)

    def add_content_to_backtesting(self, tab):

        # Create a layout for the tab
        layout = QVBoxLayout(tab)
        H_layout = QHBoxLayout()
        H2_layout = QHBoxLayout()

        label = QLabel("Stock Code:", tab)
        input_box = QLineEdit(tab)
        button = QPushButton("Generate", tab)
        button2 = QPushButton("Browse", tab)
        list_view = QListView(tab)
        table_view = QTableView(tab)
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table_view.setSelectionBehavior(QTableView.SelectRows)
        delegate = CustomDelegate()
        table_view.setItemDelegate(delegate)
        diagram_widget = DiagramWidget()

        H_layout.addWidget(label)
        H_layout.addWidget(input_box)
        H_layout.addWidget(button)
        H_layout.addWidget(button2)
        H2_layout.addWidget(list_view)
        H2_layout.addWidget(diagram_widget)
        H2_layout.setStretchFactor(list_view, 1)
        H2_layout.setStretchFactor(diagram_widget, 1)
        layout.addLayout(H_layout)
        layout.addLayout(H2_layout)
        layout.addWidget(table_view)

        bt_model = OutputListModel(self)
        list_view.setModel(bt_model)

        table_model = QStandardItemModel(self)
        table_model.setHorizontalHeaderLabels(
            ['Date', '16:00', 'Jump Distance', 'Type', 'Trigger Buy Time', 'Trigger Buy Price', 'BUY Time',
             'BUY Price', 'BUY Pattern',
             'Num of Chance', 'EMA-10 Sell Time', 'EMA-10 Earning(%)', 'Highest Sell Time', 'Highest Earning(%)'])

        # Set the table model to the table view
        table_view.setModel(table_model)
        table_view.setSortingEnabled(True)

        # Connect the button click event to the add_to_list function
        button.clicked.connect(lambda: self.start_backtesting(button, bt_model, table_view, input_box.text()))
        button2.clicked.connect(lambda: self.browse_history(table_view))
        table_view.clicked.connect(lambda: self.show_backtest_plot(table_view.currentIndex(), diagram_widget))
        bt_model.rowsInserted.connect(lambda: self.scroll_to_bottom(list_view))
        table_view.horizontalHeader().sectionClicked.connect(
            lambda column: self.sort_by_column(column, table_view, bt_model))

    def sort_by_column(self, column, table_view, bt_model):
        order = table_view.horizontalHeader().sortIndicatorOrder()
        bt_model.sort(column, order)

    def start_backtesting(self, button, bt_model, table_view, text):
        # Disable the button
        button.setEnabled(False)
        bt_model.add_output("Please Wait... Executing......")
        self.selected_symbol = text
        # Create a worker thread
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.process_finished(button))
        self.worker.set_data(bt_model, table_view, None, text, "", "backtest")

        # Start the worker thread
        self.worker_threads.append(self.worker)
        self.worker.start()

    def browse_history(self, table_view):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV", f"data/history{config_path_extension}",
                                                   "CSV Files (*.csv)")
        if file_path:
            self.load_data(file_path, table_view)
            self.selected_symbol = os.path.splitext(os.path.basename(file_path))[0]

    def browse_earning(self, table_view):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV", f"data/earning{config_path_extension}",
                                                   "CSV Files (*.csv)")

        if file_path:
            self.load_data(file_path, table_view)
            self.selected_postDate = os.path.splitext(os.path.basename(file_path))[0][:10]

    def browse_newsanalysis(self, table_view):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV", f"data/news-analysis{config_path_extension}",
                                                   "CSV Files (*.csv)")
        if file_path:
            self.load_data(file_path, table_view)

    def browse_train(self, table_view):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV", f"data/train{config_path_extension}",
                                                   "CSV Files (*.csv)")
        if file_path:
            self.load_data(file_path, table_view)
            self.selected_symbol = os.path.splitext(os.path.basename(file_path))[0]

    def browse_preanalysis(self, table_view):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV", f"data/pre-analysis{config_path_extension}",
                                                   "CSV Files (*.csv)")

        if file_path:
            self.load_data(file_path, table_view)

    def browse_setup(self, table_view):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV", f"data/setup{config_path_extension}",
                                                   "CSV Files (*.csv)")

        if file_path:
            self.load_data(file_path, table_view)

    def browse_postanalysis(self, table_view):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV", f"data/post-analysis{config_path_extension}",
                                                   "CSV Files (*.csv)")

        if file_path:
            self.load_data(file_path, table_view)
            self.selected_postDate = os.path.splitext(os.path.basename(file_path))[0][:10]

    def browse_analysisFUTU(self, table_view):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV", f"data/post-analysis(futu){config_path_extension}",
                                                   "CSV Files (*.csv)")

        if file_path:
            self.load_data(file_path, table_view)
            self.selected_postDate = os.path.splitext(os.path.basename(file_path))[0][:10]

    def browse_performancelist(self, combo_box, table_view):
        global rank_csv
        global rank_array
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV", f"data/performance{config_path_extension}",
                                                   "CSV Files (*.csv)")

        if file_path:
            self.load_data(file_path, table_view)
            combo_box.setDisabled(False)
            rank_csv = pd.read_csv(file_path)
            rank_array = np.vstack([rank_csv.columns, rank_csv.values])

    def browse_ranklist(self, combo_box, table_view):
        global rank_csv
        global rank_array
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV", f"data/ranking{config_path_extension}",
                                                   "CSV Files (*.csv)")

        if file_path:
            self.load_data(file_path, table_view)
            combo_box.setDisabled(False)
            rank_csv = pd.read_csv(file_path)
            rank_array = np.vstack([rank_csv.columns, rank_csv.values])

    def load_data(self, file_path, table_view):
        with open(file_path, "r") as file:
            reader = csv.reader(file)
            data = list(reader)

        model = CSVTableModel(data)
        table_view.setModel(model)

    def process_finished(self, button):
        # Enable the button
        button.setEnabled(True)
        # Clean up the worker thread
        self.worker.quit()
        self.worker.wait()
        QSound.play('sound/finish.wav')

    def all_process_finished(self, button, button3, button6, checkBox10, button9a):
        button.setEnabled(True)
        button3.setEnabled(True)
        button6.setEnabled(True)
        checkBox10.setEnabled(True)
        button9a.setEnabled(True)
        self.worker.quit()
        self.worker.wait()
        QSound.play('sound/finish.wav')

    def order_process_finished(self, order_box):
        order_box.clear()
        self.worker.quit()
        self.worker.wait()
        QSound.play('sound/finish.wav')

    def add_content_to_preanalysis(self, tab):

        # Create a layout for the tab
        layout = QVBoxLayout(tab)
        H_layout = QHBoxLayout()

        label = QLabel("Date:", tab)
        input_box = QDateEdit(tab)
        input_box.setCalendarPopup(True)
        input_box.setDate(QDate.currentDate())
        button = QPushButton("Generate", tab)
        button2 = QPushButton("Browse", tab)
        table_view = QTableView(tab)
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        list_view = QListView(tab)

        H_layout.addWidget(label)
        H_layout.addWidget(input_box)
        H_layout.addWidget(button)
        H_layout.addWidget(button2)
        layout.addLayout(H_layout)
        layout.addWidget(list_view)
        layout.addWidget(table_view)

        bt_model = OutputListModel(self)
        list_view.setModel(bt_model)

        table_model = QStandardItemModel(self)
        table_model.setHorizontalHeaderLabels(
            ['Symbol', 'Pattern Chance', 'BUY Pattern', 'Pattern Chance 2', 'BUY Pattern 2', 'Total Chance',
             'Recommended Sell', 'Earning Probability', 'Total Record'])

        # Set the table model to the table view
        table_view.setModel(table_model)
        table_view.setSortingEnabled(True)

        # Connect the button click event to the add_to_list function
        button.clicked.connect(
            lambda: self.start_preanalysis(button, bt_model, table_view, input_box.date().toString("yyyy-MM-dd")))
        button2.clicked.connect(lambda: self.browse_preanalysis(table_view))
        bt_model.rowsInserted.connect(lambda: self.scroll_to_bottom(list_view))
        table_view.horizontalHeader().sectionClicked.connect(
            lambda column: self.sort_by_column(column, table_view, bt_model))

    def start_preanalysis(self, button, bt_model, table_view, text):
        # Disable the button
        button.setEnabled(False)
        bt_model.add_output("Please Wait... Executing......")

        # Create a worker thread
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.process_finished(button))
        self.worker.set_data(bt_model, table_view, None, text, "", "preanalysis")

        # Start the worker thread
        self.worker_threads.append(self.worker)
        self.worker.start()

    def add_content_to_postanalysis(self, tab):

        # Create a layout for the tab
        layout = QVBoxLayout(tab)
        H_layout = QHBoxLayout()
        H2_layout = QHBoxLayout()

        current_date = QDate.currentDate()
        yesterday = current_date.addDays(-1)
        while yesterday.dayOfWeek() in (Qt.Saturday, Qt.Sunday):
            yesterday = yesterday.addDays(-1)

        label = QLabel("Last & Today Date:", tab)
        input_box_1 = QDateEdit(tab)
        input_box_1.setCalendarPopup(True)
        input_box_1.setDate(yesterday)
        input_box_2 = QDateEdit(tab)
        input_box_2.setCalendarPopup(True)
        input_box_2.setDate(current_date)
        button = QPushButton("Generate", tab)
        button3 = QPushButton("Predict", tab)
        button2 = QPushButton("Browse", tab)
        table_view = QTableView(tab)
        table_view.setSelectionBehavior(QTableView.SelectRows)
        delegate = CustomDelegate()
        table_view.setItemDelegate(delegate)
        diagram_widget = DiagramWidget()
        diagram_widget_2 = DiagramWidget()
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        list_view = QListView(tab)

        H_layout.addWidget(label)
        H_layout.addWidget(input_box_1)
        H_layout.addWidget(input_box_2)
        H_layout.addWidget(button)
        H_layout.addWidget(button3)
        H_layout.addWidget(button2)
        H2_layout.addWidget(list_view, 1)
        H2_layout.addWidget(diagram_widget, 2)
        H2_layout.addWidget(diagram_widget_2, 2)
        layout.addLayout(H_layout)
        layout.addLayout(H2_layout)
        layout.addWidget(table_view)

        bt_model = OutputListModel(self)
        list_view.setModel(bt_model)

        table_model = QStandardItemModel(self)
        table_model.setHorizontalHeaderLabels(
            ['Symbol', '16:00', 'Trigger Buy Time', 'Trigger Buy Price', 'Buy Pattern', 'Pattern Chance', 'Signal',
             'Total Chance', 'Recommended Sell', 'Earning Probability'])

        # Set the table model to the table view
        table_view.setModel(table_model)
        table_view.setSortingEnabled(True)

        # Connect the button click event to the add_to_list function
        button.clicked.connect(
            lambda: self.start_postanalysis(button, bt_model, table_view, input_box_1.date().toString("yyyy-MM-dd"),
                                            input_box_2.date().toString("yyyy-MM-dd")))
        button3.clicked.connect(
            lambda: self.start_predictAnalysis(button3, bt_model, table_view,
                                               input_box_2.date().toString("yyyy-MM-dd")))
        button2.clicked.connect(lambda: self.browse_postanalysis(table_view))
        table_view.clicked.connect(lambda: self.show_backtest_plot(table_view.currentIndex(), diagram_widget))
        table_view.clicked.connect(lambda: self.show_backtest_plot_2(table_view.currentIndex(), diagram_widget_2))
        bt_model.rowsInserted.connect(lambda: self.scroll_to_bottom(list_view))
        table_view.horizontalHeader().sectionClicked.connect(
            lambda column: self.sort_by_column(column, table_view, bt_model))

    def start_postanalysis(self, button, bt_model, table_view, text, text_2):
        # Disable the button
        button.setEnabled(False)
        bt_model.add_output("Please Wait... Executing......")
        self.selected_postDate = text_2
        # Create a worker thread
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.process_finished(button))
        self.worker.set_data(bt_model, table_view, None, text, text_2, "postanalysis")

        # Start the worker thread
        self.worker_threads.append(self.worker)
        self.worker.start()

    def start_predictAnalysis(self, button, bt_model, table_view, text):
        # Disable the button
        button.setEnabled(False)
        bt_model.add_output("Please Wait... Executing......")
        # Create a worker thread
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.process_finished(button))
        self.worker.set_data(bt_model, table_view, None, text, None, "predictAnalysis")

        # Start the worker thread
        self.worker_threads.append(self.worker)
        self.worker.start()

    def add_content_to_updateData(self, tab):

        # Create a layout for the tab
        layout = QVBoxLayout(tab)
        H_layout = QHBoxLayout()

        label = QLabel("Date:", tab)
        input_box = QDateEdit(tab)
        input_box.setCalendarPopup(True)
        input_box.setDate(QDate.currentDate())
        button = QPushButton("Generate", tab)
        list_view = QListView(tab)

        H_layout.addWidget(label)
        H_layout.addWidget(input_box)
        H_layout.addWidget(button)
        layout.addLayout(H_layout)
        layout.addWidget(list_view)

        bt_model = OutputListModel(self)
        list_view.setModel(bt_model)

        # Connect the button click event to the add_to_list function
        button.clicked.connect(lambda: self.start_updateData(button, bt_model, input_box.date().toString("yyyy-MM-dd")))
        bt_model.rowsInserted.connect(lambda: self.scroll_to_bottom(list_view))

    def start_updateData(self, button, bt_model, text):
        # Disable the button
        button.setEnabled(False)
        bt_model.add_output("Please Wait... Executing......")

        # Create a worker thread
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.process_finished(button))
        self.worker.set_data(bt_model, None, None, text, "", "update")

        # Start the worker thread
        self.worker_threads.append(self.worker)
        self.worker.start()

    def add_content_to_setup(self, tab):

        # Create a layout for the tab
        layout = QVBoxLayout(tab)
        H_layout = QHBoxLayout()

        label = QLabel("Date:", tab)
        input_box = QDateEdit(tab)
        input_box.setCalendarPopup(True)
        input_box.setDate(QDate.currentDate())
        button = QPushButton("Generate", tab)
        button2 = QPushButton("Browse", tab)
        table_view = QTableView(tab)
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        list_view = QListView(tab)

        H_layout.addWidget(label)
        H_layout.addWidget(input_box)
        H_layout.addWidget(button)
        H_layout.addWidget(button2)
        layout.addLayout(H_layout)
        layout.addWidget(list_view)
        layout.addWidget(table_view)

        bt_model = OutputListModel(self)
        list_view.setModel(bt_model)

        table_model = QStandardItemModel(self)
        table_model.setHorizontalHeaderLabels(
            ['Symbol', 'Pattern Chance', 'BUY Pattern', 'Pattern Chance 2', 'BUY Pattern 2', 'Total Chance',
             'Recommended Sell', 'Earning Probability', 'Total Record','Trend','Signal'])

        # Set the table model to the table view
        table_view.setModel(table_model)
        table_view.setSortingEnabled(True)

        # Connect the button click event to the add_to_list function
        button.clicked.connect(
            lambda: self.start_setup(button, bt_model, table_view, input_box.date().toString("yyyy-MM-dd")))
        button2.clicked.connect(lambda: self.browse_setup(table_view))
        bt_model.rowsInserted.connect(lambda: self.scroll_to_bottom(list_view))
        table_view.horizontalHeader().sectionClicked.connect(
            lambda column: self.sort_by_column(column, table_view, bt_model))

    def start_setup(self, button, bt_model, table_view, text):
        # Disable the button
        button.setEnabled(False)
        bt_model.add_output("Please Wait... Executing......")

        # Create a worker thread
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.process_finished(button))
        self.worker.set_data(bt_model, table_view, None, text, "", "setup")

        # Start the worker thread
        self.worker_threads.append(self.worker)
        self.worker.start()

    def add_content_to_newsanalysis(self, tab):

        # Create a layout for the tab
        layout = QVBoxLayout(tab)
        H_layout = QHBoxLayout()

        label = QLabel("Date:", tab)
        input_box = QDateEdit(tab)
        input_box.setCalendarPopup(True)
        input_box.setDate(QDate.currentDate())
        button = QPushButton("Generate", tab)
        button2 = QPushButton("Browse", tab)
        table_view = QTableView(tab)
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        list_view = QListView(tab)

        H_layout.addWidget(label)
        H_layout.addWidget(input_box)
        H_layout.addWidget(button)
        H_layout.addWidget(button2)
        layout.addLayout(H_layout)
        layout.addWidget(list_view)
        layout.addWidget(table_view)

        bt_model = OutputListModel(self)
        list_view.setModel(bt_model)

        table_model = QStandardItemModel(self)
        table_model.setHorizontalHeaderLabels(
            ['Symbol', 'Sentiment Score', 'Relevance Score', 'Published Time', 'News Title'])

        # Set the table model to the table view
        table_view.setModel(table_model)
        table_view.setSortingEnabled(True)

        # Connect the button click event to the add_to_list function
        button.clicked.connect(
            lambda: self.start_newsanalysis(button, bt_model, table_view, input_box.date().toString("yyyy-MM-dd")))
        button2.clicked.connect(lambda: self.browse_newsanalysis(table_view))
        bt_model.rowsInserted.connect(lambda: self.scroll_to_bottom(list_view))
        table_view.horizontalHeader().sectionClicked.connect(
            lambda column: self.sort_by_column(column, table_view, bt_model))

    def start_newsanalysis(self, button, bt_model, table_view, text):
        # Disable the button
        button.setEnabled(False)
        bt_model.add_output("Please Wait... Executing......")

        # Create a worker thread
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.process_finished(button))
        self.worker.set_data(bt_model, table_view, None, text, "", "newsanalysis")

        # Start the worker thread
        self.worker_threads.append(self.worker)
        self.worker.start()

    def add_content_to_monitoringAV(self, tab):
        # Create a layout for the tab
        layout = QVBoxLayout(tab)
        H_layout1 = QHBoxLayout()
        H_layout2 = QHBoxLayout()
        H_layout3a = QHBoxLayout()
        H_layout4 = QHBoxLayout()
        H_layout5 = QHBoxLayout()
        H_layout6b = QHBoxLayout()
        V_layout1 = QVBoxLayout()
        V_layout2 = QVBoxLayout()
        V_layout3 = QVBoxLayout()
        V_layout4 = QVBoxLayout()

        label = QLabel("Stock Code:", tab)
        input_box = QLineEdit(tab)
        button = QPushButton("Start", tab)
        buttonb = QPushButton("Stop", tab)
        list_view = QListView(tab)

        label2 = QLabel("Stock Code:", tab)
        input_box2 = QLineEdit(tab)
        button2 = QPushButton("Start", tab)
        button2b = QPushButton("Stop", tab)
        list_view2 = QListView(tab)

        label3 = QLabel("Stock Code:", tab)
        input_box3 = QLineEdit(tab)
        button3 = QPushButton("Start", tab)
        button3b = QPushButton("Stop", tab)
        list_view3 = QListView(tab)

        label4 = QLabel("Stock Code:", tab)
        input_box4 = QLineEdit(tab)
        button4 = QPushButton("Start", tab)
        button4b = QPushButton("Stop", tab)
        list_view4 = QListView(tab)

        H_layout1.addWidget(label)
        H_layout1.addWidget(input_box)
        H_layout1.addWidget(button)
        H_layout1.addWidget(buttonb)
        V_layout1.addLayout(H_layout1)
        V_layout1.addWidget(list_view)

        H_layout2.addWidget(label2)
        H_layout2.addWidget(input_box2)
        H_layout2.addWidget(button2)
        H_layout2.addWidget(button2b)
        V_layout2.addLayout(H_layout2)
        V_layout2.addWidget(list_view2)

        H_layout4.addWidget(label3)
        H_layout4.addWidget(input_box3)
        H_layout4.addWidget(button3)
        H_layout4.addWidget(button3b)
        V_layout3.addLayout(H_layout4)
        V_layout3.addWidget(list_view3)

        H_layout5.addWidget(label4)
        H_layout5.addWidget(input_box4)
        H_layout5.addWidget(button4)
        H_layout5.addWidget(button4b)
        V_layout4.addLayout(H_layout5)
        V_layout4.addWidget(list_view4)

        H_layout3a.addLayout(V_layout1)
        H_layout3a.addLayout(V_layout2)
        H_layout6b.addLayout(V_layout3)
        H_layout6b.addLayout(V_layout4)

        layout.addLayout(H_layout3a)
        layout.addLayout(H_layout6b)

        bt_model = OutputListModel(self)
        list_view.setModel(bt_model)
        bt_model2 = OutputListModel(self)
        list_view2.setModel(bt_model2)
        bt_model3 = OutputListModel(self)
        list_view3.setModel(bt_model3)
        bt_model4 = OutputListModel(self)
        list_view4.setModel(bt_model4)

        today_date = QDate.currentDate().toString("yyyy-MM-dd")

        # Connect the button click event to the add_to_list function
        button.clicked.connect(lambda: self.start_monitorAV(button, bt_model, input_box.text(), today_date))
        button2.clicked.connect(lambda: self.start_monitorAV(button2, bt_model2, input_box2.text(), today_date))
        button3.clicked.connect(lambda: self.start_monitorAV(button3, bt_model3, input_box3.text(), today_date))
        button4.clicked.connect(lambda: self.start_monitorAV(button4, bt_model4, input_box4.text(), today_date))
        buttonb.clicked.connect(lambda: self.stop_threads_monitor(button, bt_model, input_box.text()))
        button2b.clicked.connect(lambda: self.stop_threads_monitor(button2, bt_model2, input_box2.text()))
        button3b.clicked.connect(lambda: self.stop_threads_monitor(button3, bt_model3, input_box3.text()))
        button4b.clicked.connect(lambda: self.stop_threads_monitor(button4, bt_model4, input_box4.text()))
        bt_model.rowsInserted.connect(lambda: self.scroll_to_bottom(list_view))
        bt_model2.rowsInserted.connect(lambda: self.scroll_to_bottom(list_view2))
        bt_model3.rowsInserted.connect(lambda: self.scroll_to_bottom(list_view3))
        bt_model4.rowsInserted.connect(lambda: self.scroll_to_bottom(list_view4))

    def stop_threads_monitor(self, button, bt_model, text):
        for worker in self.worker_threads:
            if worker.text == text:
                button.setEnabled(True)
                worker.terminate()
                worker.wait()
                bt_model.add_output("Terminated Already!")

    def start_monitorAV(self, button, bt_model, text, date):
        # Disable the button
        button.setEnabled(False)
        bt_model.add_output("Please Wait... Executing......")

        # Create a worker thread
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.process_finished(button))
        self.worker.set_data(bt_model, None, None, text, date, "monitorAV")

        # Start the worker thread
        self.worker_threads.append(self.worker)
        self.worker.start()

    def add_content_to_analysisFUTU(self, tab):
        layout = QVBoxLayout(tab)
        H_layout = QHBoxLayout()
        H2_layout = QHBoxLayout()

        current_date = QDate.currentDate()

        label = QLabel("Date:", tab)
        input_box = QDateEdit(tab)
        input_box.setCalendarPopup(True)
        input_box.setDate(current_date)
        button = QPushButton("Start", tab)
        buttonb = QPushButton("Stop", tab)
        button2 = QPushButton("Browse", tab)
        table_view = QTableView(tab)
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table_view.setSelectionBehavior(QTableView.SelectRows)
        delegate = CustomDelegate()
        table_view.setItemDelegate(delegate)
        diagram_widget = DiagramWidget()
        list_view = QListView(tab)

        H_layout.addWidget(label)
        H_layout.addWidget(input_box)
        H_layout.addWidget(button)
        H_layout.addWidget(buttonb)
        H_layout.addWidget(button2)
        H2_layout.addWidget(list_view)
        H2_layout.addWidget(diagram_widget)
        H2_layout.setStretchFactor(list_view, 1)
        H2_layout.setStretchFactor(diagram_widget, 1)
        layout.addLayout(H_layout)
        layout.addLayout(H2_layout)
        layout.addWidget(table_view)

        bt_model = OutputListModel(self)
        list_view.setModel(bt_model)
        table_view.setSortingEnabled(True)

        table_model = QStandardItemModel(self)
        table_model.setHorizontalHeaderLabels(
            ['Symbol', '16:00', 'Trigger Buy Time', 'Trigger Buy Price', 'Buy Pattern', 'Pattern Chance', 'Signal',
             'Total Chance', 'Recommended Sell', 'Earning Probability'])

        # Set the table model to the table view
        table_view.setModel(table_model)

        # Connect the button click event to the add_to_list function
        button.clicked.connect(
            lambda: self.start_analysisFUTU(button, bt_model, table_view, input_box.date().toString("yyyy-MM-dd")))
        button2.clicked.connect(lambda: self.browse_analysisFUTU(table_view))
        buttonb.clicked.connect(
            lambda: self.stop_threads_monitor(button, bt_model, input_box.date().toString("yyyy-MM-dd")))
        bt_model.rowsInserted.connect(lambda: self.scroll_to_bottom(list_view))
        table_view.horizontalHeader().sectionClicked.connect(
            lambda column: self.sort_by_column(column, table_view, bt_model))
        table_view.clicked.connect(lambda: self.show_futu_plot(table_view.currentIndex(), diagram_widget))

    def start_analysisFUTU(self, button, bt_model, table_view, text):
        # Disable the button
        button.setEnabled(False)
        bt_model.add_output("Please Wait... Executing......")

        # Create a worker thread
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.process_finished(button))
        self.worker.set_data(bt_model, table_view, None, text, "", "analysisFUTU")

        # Start the worker thread
        self.worker_threads.append(self.worker)
        self.worker.start()

    def show_backtest_plot(self, index, diagram_widget):
        row = index.row()
        model = index.model()
        postDate = model.get_data(row, 0)
        if '202' not in postDate:
            symbol = model.get_data(row, 0)
            postDate = self.selected_postDate
        else:
            symbol = self.selected_symbol
        diagram_widget.update_diagram(None, symbol, postDate)

    def show_backtest_plot_2(self, index, diagram_widget):
        row = index.row()
        model = index.model()
        symbol = model.get_data(row, 0)
        diagram_widget.update_diagram_15(None, symbol, self.selected_postDate)

    def show_backtest_plot_performance(self, index, diagram_widget):
        row = index.row()
        model = index.model()
        postDate = model.get_data(row, 0)
        symbol = model.get_data(row, 3)
        diagram_widget.update_diagram(None, symbol, postDate)

    def show_backtest_plot_performance_2(self, index, diagram_widget):
        row = index.row()
        model = index.model()
        postDate = model.get_data(row, 0)
        symbol = model.get_data(row, 3)
        diagram_widget.update_diagram_15(None, symbol, postDate)

    def show_futu_plot(self, index, diagram_widget):
        diagram_widget.futu_diagram(index, self.selected_symbol, self.selected_postDate)

    def add_content_to_monitoringFUTU(self, tab):
        # Create a layout for the tab
        layout = QVBoxLayout(tab)
        H_layout1 = QHBoxLayout()
        H_layout2 = QHBoxLayout()
        H_layout3a = QHBoxLayout()
        H_layout4 = QHBoxLayout()
        H_layout5 = QHBoxLayout()
        H_layout6b = QHBoxLayout()
        V_layout1 = QVBoxLayout()
        V_layout2 = QVBoxLayout()
        V_layout3 = QVBoxLayout()
        V_layout4 = QVBoxLayout()

        label = QLabel("Stock Code:", tab)
        input_box = QLineEdit(tab)
        yes_button = QRadioButton('CALL', tab)
        yes_button.setChecked(False)
        no_button = QRadioButton('PUT', tab)
        no_button.setChecked(False)
        button = QPushButton("Start", tab)
        buttonb = QPushButton("Stop", tab)
        list_view = QListView(tab)

        label2 = QLabel("Stock Code:", tab)
        input_box2 = QLineEdit(tab)
        yes_button2 = QRadioButton('CALL', tab)
        yes_button2.setChecked(False)
        no_button2 = QRadioButton('PUT', tab)
        no_button2.setChecked(False)
        button2 = QPushButton("Start", tab)
        button2b = QPushButton("Stop", tab)
        list_view2 = QListView(tab)

        label3 = QLabel("Stock Code:", tab)
        input_box3 = QLineEdit(tab)
        yes_button3 = QRadioButton('CALL', tab)
        yes_button3.setChecked(False)
        no_button3 = QRadioButton('PUT', tab)
        no_button3.setChecked(False)
        button3 = QPushButton("Start", tab)
        button3b = QPushButton("Stop", tab)
        list_view3 = QListView(tab)

        label4 = QLabel("Stock Code:", tab)
        input_box4 = QLineEdit(tab)
        yes_button4 = QRadioButton('CALL', tab)
        yes_button4.setChecked(False)
        no_button4 = QRadioButton('PUT', tab)
        no_button4.setChecked(False)
        button4 = QPushButton("Start", tab)
        button4b = QPushButton("Stop", tab)
        list_view4 = QListView(tab)

        H_layout1.addWidget(label)
        H_layout1.addWidget(input_box)
        H_layout1.addWidget(yes_button)
        H_layout1.addWidget(no_button)
        H_layout1.addWidget(button)
        H_layout1.addWidget(buttonb)
        V_layout1.addLayout(H_layout1)
        V_layout1.addWidget(list_view)

        H_layout2.addWidget(label2)
        H_layout2.addWidget(input_box2)
        H_layout2.addWidget(yes_button2)
        H_layout2.addWidget(no_button2)
        H_layout2.addWidget(button2)
        H_layout2.addWidget(button2b)
        V_layout2.addLayout(H_layout2)
        V_layout2.addWidget(list_view2)

        H_layout4.addWidget(label3)
        H_layout4.addWidget(input_box3)
        H_layout4.addWidget(yes_button3)
        H_layout4.addWidget(no_button3)
        H_layout4.addWidget(button3)
        H_layout4.addWidget(button3b)
        V_layout3.addLayout(H_layout4)
        V_layout3.addWidget(list_view3)

        H_layout5.addWidget(label4)
        H_layout5.addWidget(input_box4)
        H_layout5.addWidget(yes_button4)
        H_layout5.addWidget(no_button4)
        H_layout5.addWidget(button4)
        H_layout5.addWidget(button4b)
        V_layout4.addLayout(H_layout5)
        V_layout4.addWidget(list_view4)

        H_layout3a.addLayout(V_layout1)
        H_layout3a.addLayout(V_layout2)
        H_layout6b.addLayout(V_layout3)
        H_layout6b.addLayout(V_layout4)

        layout.addLayout(H_layout3a)
        layout.addLayout(H_layout6b)

        bt_model = OutputListModel(self)
        list_view.setModel(bt_model)
        bt_model2 = OutputListModel(self)
        list_view2.setModel(bt_model2)
        bt_model3 = OutputListModel(self)
        list_view3.setModel(bt_model3)
        bt_model4 = OutputListModel(self)
        list_view4.setModel(bt_model4)

        # Connect the button click event to the add_to_list function
        button.clicked.connect(
            lambda: self.start_monitorFUTU(button, bt_model, input_box.text(), yes_button, no_button))
        button2.clicked.connect(
            lambda: self.start_monitorFUTU(button2, bt_model2, input_box2.text(), yes_button2, no_button2))
        button3.clicked.connect(
            lambda: self.start_monitorFUTU(button3, bt_model3, input_box3.text(), yes_button3, no_button3))
        button4.clicked.connect(
            lambda: self.start_monitorFUTU(button4, bt_model4, input_box4.text(), yes_button4, no_button4))
        buttonb.clicked.connect(lambda: self.stop_threads_monitor(button, bt_model, input_box.text()))
        button2b.clicked.connect(lambda: self.stop_threads_monitor(button2, bt_model2, input_box2.text()))
        button3b.clicked.connect(lambda: self.stop_threads_monitor(button3, bt_model3, input_box3.text()))
        button4b.clicked.connect(lambda: self.stop_threads_monitor(button4, bt_model4, input_box4.text()))
        bt_model.rowsInserted.connect(lambda: self.scroll_to_bottom(list_view))
        bt_model2.rowsInserted.connect(lambda: self.scroll_to_bottom(list_view2))
        bt_model3.rowsInserted.connect(lambda: self.scroll_to_bottom(list_view3))
        bt_model4.rowsInserted.connect(lambda: self.scroll_to_bottom(list_view4))

    def scroll_to_bottom(self, list_view):
        list_view.scrollToBottom()

    def start_monitorFUTU(self, button, bt_model, text, button1, button2):
        # Disable the button
        button.setEnabled(False)
        bt_model.add_output("Please Wait... Executing......")

        if button1.isChecked():
            selected_option = 'CALL'
        elif button2.isChecked():
            selected_option = 'PUT'
        else:
            selected_option = 'None'
        # Create a worker thread
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.process_finished(button))
        self.worker.set_data(bt_model, "", None, text, selected_option, "monitorFUTU")

        # Start the worker thread
        self.worker_threads.append(self.worker)
        self.worker.start()

    def add_content_to_trading(self, tab):
        # Create a layout for the tab
        layout = QVBoxLayout(tab)
        H_layout1 = QHBoxLayout()
        H_layout2 = QHBoxLayout()
        H_layout3 = QHBoxLayout()
        H_layout4 = QHBoxLayout()
        H_layout5 = QHBoxLayout()
        H_layout6 = QHBoxLayout()
        H_layout7 = QHBoxLayout()
        H_layout8 = QHBoxLayout()
        H_layout9 = QHBoxLayout()
        H_layout10 = QHBoxLayout()
        H_layouta = QHBoxLayout()
        H_layoutb = QHBoxLayout()
        H_layoutc = QHBoxLayout()
        H_layoutd = QHBoxLayout()
        H_layoute = QHBoxLayout()

        label = QLabel("Stock Code:", tab)
        input_box = QLineEdit(tab)
        button = QPushButton("Get Price", tab)

        label2 = QLabel("Current Price:", tab)
        input_box2 = QLineEdit(tab)
        input_box2.setDisabled(True)
        label2a = QLabel("Target Price:", tab)
        input_box2a = QLineEdit(tab)
        input_box2a.setDisabled(True)

        label3 = QLabel("Type:", tab)
        yes_button3 = QRadioButton('CALL', tab)
        yes_button3.setChecked(False)
        no_button3 = QRadioButton('PUT', tab)
        no_button3.setChecked(False)
        button_group1 = QButtonGroup(tab)
        button_group1.addButton(yes_button3)
        button_group1.addButton(no_button3)
        button3 = QPushButton("View", tab)

        label4 = QLabel("Option Code:", tab)
        input_box4 = QLineEdit(tab)
        input_box4.setDisabled(True)
        label4a = QLabel("Type:", tab)
        input_box4a = QLineEdit(tab)
        input_box4a.setDisabled(True)
        label4b = QLabel("Expiration:", tab)
        input_box4b = QLineEdit(tab)
        input_box4b.setDisabled(True)

        label5 = QLabel("Option Price:", tab)
        input_box5 = QLineEdit(tab)
        input_box5.setDisabled(True)
        label6a = QLabel("Ask:", tab)
        input_box6a = QLineEdit(tab)
        input_box6a.setDisabled(True)
        label6b = QLabel("Bid:", tab)
        input_box6b = QLineEdit(tab)
        input_box6b.setDisabled(True)
        yes_button5 = QRadioButton('BUY', tab)
        yes_button5.setChecked(True)
        no_button5 = QRadioButton('SELL', tab)
        no_button5.setChecked(False)
        button_group2 = QButtonGroup(tab)
        button_group2.addButton(yes_button5)
        button_group2.addButton(no_button5)

        label6 = QLabel("Option Quantity:", tab)
        input_box6 = QLineEdit(tab)
        input_box6.setText("1")
        label5a = QLabel("Market Price:", tab)
        input_box5a = QLineEdit(tab)
        button6 = QPushButton("Order", tab)
        button6.setDisabled(True)
        label11 = QLabel("Total Amount:", tab)
        input_box11 = QLineEdit(tab)
        input_box11.setDisabled(True)

        list_view = QListView(tab)

        label7 = QLabel("Order ID:", tab)
        input_box7 = QLineEdit(tab)
        input_box7.setDisabled(True)

        button7a = QPushButton("Modify Order", tab)
        button7a.setDisabled(True)
        button8 = QPushButton("Cancel Order", tab)
        button8.setDisabled(True)

        label9 = QLabel("Automatic Trading:", tab)
        button9a = QPushButton("Start", tab)
        button9b = QPushButton("Stop", tab)

        checkBox10 = QCheckBox("Filtering with Lower Chance", tab)

        H_layout1.addWidget(label)
        H_layout1.addWidget(input_box)
        H_layout1.addWidget(button)

        H_layout2.addWidget(label2)
        H_layout2.addWidget(input_box2)
        H_layout2.addWidget(label2a)
        H_layout2.addWidget(input_box2a)

        H_layout3.addWidget(label3)
        H_layout3.addWidget(yes_button3)
        H_layout3.addWidget(no_button3)
        H_layout3.addWidget(button3)

        H_layout4.addWidget(label4)
        H_layout4.addWidget(input_box4)
        H_layout4.addWidget(label4a)
        H_layout4.addWidget(input_box4a)
        H_layout4.addWidget(label4b)
        H_layout4.addWidget(input_box4b)

        H_layout5.addWidget(label5)
        H_layout5.addWidget(input_box5)
        H_layout5.addWidget(label6a)
        H_layout5.addWidget(input_box6a)
        H_layout5.addWidget(label6b)
        H_layout5.addWidget(input_box6b)
        H_layout5.addWidget(yes_button5)
        H_layout5.addWidget(no_button5)

        H_layout6.addWidget(label6)
        H_layout6.addWidget(input_box6)
        H_layout6.addWidget(label5a)
        H_layout6.addWidget(input_box5a)
        H_layout6.addWidget(label11)
        H_layout6.addWidget(input_box11)
        H_layout6.addWidget(button6)

        H_layout7.addWidget(label7)
        H_layout7.addWidget(input_box7)

        H_layout9.addWidget(label9)
        H_layout9.addWidget(button9a)
        H_layout9.addWidget(button9b)

        H_layoutd.addLayout(H_layout9, 1)
        H_layoutd.addLayout(H_layout7, 1)

        H_layout8.addWidget(button7a)
        H_layout8.addWidget(button8)

        H_layout10.addWidget(checkBox10)

        H_layoute.addLayout(H_layout10, 1)
        H_layoute.addLayout(H_layout8, 1)

        H_layouta.addLayout(H_layout1, 1)
        H_layouta.addLayout(H_layout4, 1)

        H_layoutb.addLayout(H_layout2, 1)
        H_layoutb.addLayout(H_layout5, 1)

        H_layoutc.addLayout(H_layout3, 1)
        H_layoutc.addLayout(H_layout6, 1)

        layout.addLayout(H_layouta)
        layout.addLayout(H_layoutb)
        layout.addLayout(H_layoutc)
        layout.addWidget(list_view)
        layout.addLayout(H_layoutd)
        layout.addLayout(H_layoute)

        bt_model = OutputListModel(self)
        list_view.setModel(bt_model)

        button.clicked.connect(
            lambda: self.get_stock_price(input_box2, bt_model, input_box.text(), input_box2a))
        yes_button3.clicked.connect(lambda: self.calculate_call_price(input_box2, input_box2a))
        no_button3.clicked.connect(lambda: self.calculate_put_price(input_box2, input_box2a))
        button3.clicked.connect(
            lambda: self.view_option_price(input_box4, input_box4a, input_box4b, input_box5,
                                           input_box5a, input_box6a, input_box6b,
                                           input_box6, input_box11,
                                           input_box.text(), yes_button3, no_button3, input_box2a.text(), bt_model,
                                           button6))
        input_box6.textChanged.connect(lambda: self.calculate_amount(input_box11, input_box6, input_box5a))
        input_box5a.textChanged.connect(lambda: self.calculate_amount(input_box11, input_box6, input_box5a))
        button6.clicked.connect(
            lambda: self.order_option(bt_model, input_box4.text(), input_box5a.text(), input_box6.text(), yes_button5,
                                      no_button5, input_box7, button7a, button8, button6))
        button7a.clicked.connect(
            lambda: self.change_order(bt_model, input_box4.text(), input_box6a.text(), input_box6b.text(),
                                      input_box6.text(), input_box7))
        button8.clicked.connect(lambda: self.cancel_order(bt_model, input_box4.text(), input_box7, button7a, button8))
        bt_model.rowsInserted.connect(lambda: self.scroll_to_bottom(list_view))
        button9a.clicked.connect(
            lambda: self.start_autoTrade(bt_model, checkBox10, button, button3, button6, button7a, button8, button9a))

    def add_content_to_performanceList(self, tab):

        # Create a layout for the tab
        layout = QVBoxLayout(tab)
        H_layout = QHBoxLayout()
        H_layout2 = QHBoxLayout()
        V_layout = QVBoxLayout()
        diagram_widget = DiagramWidget()
        diagram_widget_2 = DiagramWidget()

        label = QLabel("Date:", tab)
        input_box = QDateEdit(tab)
        input_box.setCalendarPopup(True)
        input_box.setDate(QDate.currentDate())
        button = QPushButton("Generate", tab)
        button3 = QPushButton("Maximize", tab)
        button4 = QPushButton("Full", tab)
        button2 = QPushButton("Browse", tab)
        label2 = QLabel("Order By:", tab)
        combo_box = QComboBox(tab)
        combo_box.setDisabled(True)
        table_view = QTableView(tab)
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table_view.setSelectionBehavior(QTableView.SelectRows)
        list_view = QListView(tab)

        header = ['Date', 'BB Ratio', 'Choice 1', 'Choice 2', 'C1 Result', 'C2 Result',
                  'C1 Earning', 'C2 Earning',
                  'Overall Earning']

        for head in header:
            combo_box.addItem(head)

        combo_box.setCurrentIndex(1)

        H_layout.addWidget(label, 1)
        H_layout.addWidget(input_box, 4)
        H_layout.addWidget(button, 2)
        H_layout.addWidget(button3, 2)
        H_layout.addWidget(button4, 2)
        H_layout.addWidget(button2, 2)
        H_layout.addWidget(label2, 1)
        H_layout.addWidget(combo_box, 3)
        H_layout2.addWidget(table_view, 2)
        H_layout2.addLayout(V_layout, 1)
        V_layout.addWidget(diagram_widget, 1)
        V_layout.addWidget(diagram_widget_2, 1)
        layout.addLayout(H_layout, 1)
        layout.addWidget(list_view, 1)
        layout.addLayout(H_layout2, 8)

        bt_model = OutputListModel(self)
        list_view.setModel(bt_model)

        table_model = QStandardItemModel(self)
        table_model.setHorizontalHeaderLabels(header)

        # Set the table model to the table view
        table_view.setModel(table_model)
        table_view.setSortingEnabled(True)

        # Connect the button click event to the add_to_list function
        button.clicked.connect(
            lambda: self.start_performanceList(combo_box, button, bt_model, table_view,
                                               input_box.date().toString("yyyy-MM-dd")))
        button3.clicked.connect(
            lambda: self.start_maxList(combo_box, button3, bt_model, table_view,
                                       input_box.date().toString("yyyy-MM-dd")))
        button4.clicked.connect(
            lambda: self.start_fullList(combo_box, button4, bt_model, table_view,
                                        input_box.date().toString("yyyy-MM-dd")))
        button2.clicked.connect(lambda: self.browse_performancelist(combo_box, table_view))
        combo_box.currentIndexChanged.connect(
            lambda: self.sort_and_order_columns(combo_box, table_view, combo_box.currentIndex()))
        bt_model.rowsInserted.connect(lambda: self.scroll_to_bottom(list_view))
        table_view.horizontalHeader().sectionClicked.connect(
            lambda column: self.sort_by_column(column, table_view, bt_model))
        table_view.clicked.connect(lambda: self.show_backtest_plot_performance(table_view.currentIndex(), diagram_widget))
        table_view.clicked.connect(lambda: self.show_backtest_plot_performance_2(table_view.currentIndex(), diagram_widget_2))

    def start_maxList(self, combo_box, button, bt_model, table_view, text):
        # Disable the button
        button.setEnabled(False)
        bt_model.add_output("Please Wait... Executing......")
        combo_box.setDisabled(False)

        # Create a worker thread
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.process_finished(button))
        self.worker.set_data(bt_model, table_view, None, text, "", "maxList")

        # Start the worker thread
        self.worker_threads.append(self.worker)
        self.worker.start()

    def start_fullList(self, combo_box, button, bt_model, table_view, text):
        # Disable the button
        button.setEnabled(False)
        bt_model.add_output("Please Wait... Executing......")
        combo_box.setDisabled(False)

        # Create a worker thread
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.process_finished(button))
        self.worker.set_data(bt_model, table_view, None, text, "", "fullList")

        # Start the worker thread
        self.worker_threads.append(self.worker)
        self.worker.start()

    def start_performanceList(self, combo_box, button, bt_model, table_view, text):
        # Disable the button
        button.setEnabled(False)
        bt_model.add_output("Please Wait... Executing......")
        combo_box.setDisabled(False)

        # Create a worker thread
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.process_finished(button))
        self.worker.set_data(bt_model, table_view, None, text, "", "performanceList")

        # Start the worker thread
        self.worker_threads.append(self.worker)
        self.worker.start()

    def add_content_to_rankingList(self, tab):

        # Create a layout for the tab
        layout = QVBoxLayout(tab)
        H_layout = QHBoxLayout()

        label = QLabel("Date:", tab)
        input_box = QDateEdit(tab)
        input_box.setCalendarPopup(True)
        input_box.setDate(QDate.currentDate())
        button = QPushButton("Generate", tab)
        button2 = QPushButton("Browse", tab)
        label2 = QLabel("Order By:", tab)
        combo_box = QComboBox(tab)
        combo_box.setDisabled(True)
        table_view = QTableView(tab)
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        list_view = QListView(tab)

        header = ['Symbol', 'Chance', 'Recommended Sell', 'Earning Probability', 'One Chance', 'Zero Chance',
                  'CALL Chance', 'PUT Chance',
                  '09:35 Sell Chance', '09:58 Highest Chance', 'Total Record']

        for head in header:
            combo_box.addItem(head)

        combo_box.setCurrentIndex(1)

        H_layout.addWidget(label, 1)
        H_layout.addWidget(input_box, 4)
        H_layout.addWidget(button, 2)
        H_layout.addWidget(button2, 2)
        H_layout.addWidget(label2, 1)
        H_layout.addWidget(combo_box, 3)
        layout.addLayout(H_layout, 1)
        layout.addWidget(list_view, 1)
        layout.addWidget(table_view, 8)

        bt_model = OutputListModel(self)
        list_view.setModel(bt_model)

        table_model = QStandardItemModel(self)
        table_model.setHorizontalHeaderLabels(header)

        # Set the table model to the table view
        table_view.setModel(table_model)
        table_view.setSortingEnabled(True)

        # Connect the button click event to the add_to_list function
        button.clicked.connect(
            lambda: self.start_rankingList(combo_box, button, bt_model, table_view,
                                           input_box.date().toString("yyyy-MM-dd")))
        button2.clicked.connect(lambda: self.browse_ranklist(combo_box, table_view))
        combo_box.currentIndexChanged.connect(
            lambda: self.sort_and_order_columns(combo_box, table_view, combo_box.currentIndex()))
        bt_model.rowsInserted.connect(lambda: self.scroll_to_bottom(list_view))
        table_view.horizontalHeader().sectionClicked.connect(
            lambda column: self.sort_by_column(column, table_view, bt_model))

    def sort_and_order_columns(self, combo_box, table_view, index):
        # Create a worker thread
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.process_finished(combo_box))
        self.worker.set_data("", table_view, None, index, "", "rankingChange")

        # Start the worker thread
        self.worker_threads.append(self.worker)
        self.worker.start()

    def start_rankingList(self, combo_box, button, bt_model, table_view, text):
        # Disable the button
        button.setEnabled(False)
        bt_model.add_output("Please Wait... Executing......")
        combo_box.setDisabled(False)

        # Create a worker thread
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.process_finished(button))
        self.worker.set_data(bt_model, table_view, None, text, "", "rankingList")

        # Start the worker thread
        self.worker_threads.append(self.worker)
        self.worker.start()

    def add_content_to_prediction(self, tab):
        layout = QVBoxLayout(tab)
        H_layout = QHBoxLayout()
        H2_layout = QHBoxLayout()
        H3_layout = QHBoxLayout()

        label = QLabel("Stock:", tab)
        input_box = QLineEdit(tab)
        button = QPushButton("Start", tab)
        buttonb = QPushButton("Stop", tab)
        diagram_widget = DiagramWidget()
        diagram_widget2 = DiagramWidget()
        diagram_widget3 = DiagramWidget()
        list_view = QListView(tab)

        H_layout.addWidget(label)
        H_layout.addWidget(input_box)
        H_layout.addWidget(button)
        H_layout.addWidget(buttonb)
        H2_layout.addWidget(list_view, 1)
        H2_layout.addWidget(diagram_widget, 1)
        H3_layout.addWidget(diagram_widget2, 1)
        H3_layout.addWidget(diagram_widget3, 1)
        layout.addLayout(H_layout, 1)
        layout.addLayout(H2_layout, 5)
        layout.addLayout(H3_layout, 5)

        bt_model = OutputListModel(self)
        list_view.setModel(bt_model)

        # Connect the button click event to the add_to_list function
        button.clicked.connect(
            lambda: self.start_prediction(button, bt_model, input_box.text(), diagram_widget))
        button.clicked.connect(
            lambda: self.start_predictionFull(button, bt_model, input_box.text(), diagram_widget3))
        buttonb.clicked.connect(
            lambda: self.stop_threads_monitor(button, bt_model, input_box.text()))
        bt_model.rowsInserted.connect(lambda: self.scroll_to_bottom(list_view))

    def start_prediction(self, button, bt_model, text, diagram_widget):
        button.setEnabled(False)
        # Create a worker thread
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.process_finished(button))
        self.worker.set_data(bt_model, "", diagram_widget, text, QDate.currentDate().toString("yyyy-MM-dd"),
                             "predictionReal")
        self.worker_threads.append(self.worker)
        self.worker.start()

    def start_predictionFull(self, button, bt_model, text, diagram_widget):
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.process_finished(button))
        self.worker.set_data(bt_model, "", diagram_widget, text, QDate.currentDate().toString("yyyy-MM-dd"),
                             "predictionFull")
        self.worker_threads.append(self.worker)
        self.worker.start()

    def add_content_to_training(self, tab):

        # Create a layout for the tab
        layout = QVBoxLayout(tab)
        H_layout = QHBoxLayout()
        H2_layout = QHBoxLayout()

        label = QLabel("Stock Code:", tab)
        input_box = QLineEdit(tab)
        button = QPushButton("Generate", tab)
        button2 = QPushButton("Browse", tab)
        list_view = QListView(tab)
        table_view = QTableView(tab)
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table_view.setSelectionBehavior(QTableView.SelectRows)
        delegate = CustomDelegate()
        table_view.setItemDelegate(delegate)
        diagram_widget = DiagramWidget()

        H_layout.addWidget(label)
        H_layout.addWidget(input_box)
        H_layout.addWidget(button)
        H_layout.addWidget(button2)
        H2_layout.addWidget(list_view)
        H2_layout.addWidget(diagram_widget)
        H2_layout.setStretchFactor(list_view, 1)
        H2_layout.setStretchFactor(diagram_widget, 1)
        layout.addLayout(H_layout)
        layout.addLayout(H2_layout)
        layout.addWidget(table_view)

        bt_model = OutputListModel(self)
        list_view.setModel(bt_model)

        table_model = QStandardItemModel(self)
        header = ['Date']
        status = ['open', 'low', 'high', 'close']
        header_series = []
        for i in range(30):
            minutes = 30 + i
            header_series.append(f"09{minutes}{status[0][0]}")
            header_series.append(f"09{minutes}{status[1][0]}")
            header_series.append(f"09{minutes}{status[2][0]}")
            header_series.append(f"09{minutes}{status[3][0]}")
        for i in header_series:
            header.append(i)
        table_model.setHorizontalHeaderLabels(header)

        # Set the table model to the table view
        table_view.setModel(table_model)
        table_view.setSortingEnabled(True)

        # Connect the button click event to the add_to_list function
        button.clicked.connect(lambda: self.start_training(button, bt_model, table_view, input_box.text()))
        button2.clicked.connect(lambda: self.browse_train(table_view))
        table_view.clicked.connect(lambda: self.show_backtest_plot(table_view.currentIndex(), diagram_widget))
        bt_model.rowsInserted.connect(lambda: self.scroll_to_bottom(list_view))
        table_view.horizontalHeader().sectionClicked.connect(
            lambda column: self.sort_by_column(column, table_view, bt_model))

    def start_training(self, button, bt_model, table_view, text):
        # Disable the button
        button.setEnabled(False)
        bt_model.add_output("Please Wait... Executing......")
        self.selected_symbol = text
        # Create a worker thread
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.process_finished(button))
        self.worker.set_data(bt_model, table_view, None, text, "", "trainData")

        # Start the worker thread
        self.worker_threads.append(self.worker)
        self.worker.start()

    def add_content_to_configuration(self, tab):

        # Create a layout for the tab
        layout = QVBoxLayout(tab)
        Hlayout = QHBoxLayout()
        section1 = QGroupBox("Others")
        section_layout1 = QVBoxLayout()

        H_layout = QHBoxLayout()
        config1 = QLabel("Exponential Moving Average (EMA): ")
        radio_button1 = QRadioButton("Allow")
        radio_button2 = QRadioButton("Deny")
        button_group1 = QButtonGroup(tab)
        button_group1.addButton(radio_button1)
        button_group1.addButton(radio_button2)
        if configurations[0] == "Allow":
            radio_button1.setChecked(True)
        else:
            radio_button2.setChecked(True)
        H_layout.addWidget(config1, 2)
        H_layout.addWidget(radio_button1, 1)
        H_layout.addWidget(radio_button2, 1)

        H_layout2 = QHBoxLayout()
        config2 = QLabel("Moving Average Convergence/Divergence (MACD): ")
        radio_button3 = QRadioButton("Allow")
        radio_button4 = QRadioButton("Deny")
        button_group2 = QButtonGroup(tab)
        button_group2.addButton(radio_button3)
        button_group2.addButton(radio_button4)
        if configurations[1] == "Allow":
            radio_button3.setChecked(True)
        else:
            radio_button4.setChecked(True)
        H_layout2.addWidget(config2, 2)
        H_layout2.addWidget(radio_button3, 1)
        H_layout2.addWidget(radio_button4, 1)

        H_layout3 = QHBoxLayout()
        config3 = QLabel("Relative Strength Index (RSI): ")
        radio_button5 = QRadioButton("Allow")
        radio_button6 = QRadioButton("Deny")
        button_group3 = QButtonGroup(tab)
        button_group3.addButton(radio_button5)
        button_group3.addButton(radio_button6)
        if configurations[2] == "Allow":
            radio_button5.setChecked(True)
        else:
            radio_button6.setChecked(True)
        H_layout3.addWidget(config3, 2)
        H_layout3.addWidget(radio_button5, 1)
        H_layout3.addWidget(radio_button6, 1)

        H_layout4 = QHBoxLayout()
        config4 = QLabel("Bearish and Bullish Ratio (BB Ratio): ")
        radio_button7 = QRadioButton("Allow")
        radio_button8 = QRadioButton("Deny")
        button_group4 = QButtonGroup(tab)
        button_group4.addButton(radio_button7)
        button_group4.addButton(radio_button8)
        if configurations[3] == "Allow":
            radio_button7.setChecked(True)
        else:
            radio_button8.setChecked(True)
        H_layout4.addWidget(config4, 2)
        H_layout4.addWidget(radio_button7, 1)
        H_layout4.addWidget(radio_button8, 1)

        H_layout5 = QHBoxLayout()
        config5 = QLabel("Caculated Chance (CC): ")
        radio_button9 = QRadioButton("Allow")
        radio_button10 = QRadioButton("Deny")
        button_group5 = QButtonGroup(tab)
        button_group5.addButton(radio_button9)
        button_group5.addButton(radio_button10)
        if configurations[4] == "Allow":
            radio_button9.setChecked(True)
        else:
            radio_button10.setChecked(True)
        H_layout5.addWidget(config5, 2)
        H_layout5.addWidget(radio_button9, 1)
        H_layout5.addWidget(radio_button10, 1)

        section_layout1.addLayout(H_layout)
        section_layout1.addLayout(H_layout2)
        section_layout1.addLayout(H_layout3)
        section_layout1.addLayout(H_layout4)
        section_layout1.addLayout(H_layout5)

        section1.setLayout(section_layout1)

        section2 = QGroupBox("Performance Filters")
        section_layout2 = QVBoxLayout()

        H_layoutb = QHBoxLayout()
        config1b = QLabel("QQQ/SPY Pattern (30): ")
        radio_button1b = QRadioButton("Allow")
        radio_button2b = QRadioButton("Deny")
        button_group1b = QButtonGroup(tab)
        button_group1b.addButton(radio_button1b)
        button_group1b.addButton(radio_button2b)
        if configurations[5] == "Allow":
            radio_button1b.setChecked(True)
        else:
            radio_button2b.setChecked(True)
        H_layoutb.addWidget(config1b, 2)
        H_layoutb.addWidget(radio_button1b, 1)
        H_layoutb.addWidget(radio_button2b, 1)

        H_layout2b = QHBoxLayout()
        config2b = QLabel("Pattern Chance (15): ")
        radio_button3b = QRadioButton("Allow")
        radio_button4b = QRadioButton("Deny")
        button_group2b = QButtonGroup(tab)
        button_group2b.addButton(radio_button3b)
        button_group2b.addButton(radio_button4b)
        if configurations[6] == "Allow":
            radio_button3b.setChecked(True)
        else:
            radio_button4b.setChecked(True)
        H_layout2b.addWidget(config2b, 2)
        H_layout2b.addWidget(radio_button3b, 1)
        H_layout2b.addWidget(radio_button4b, 1)

        H_layout3b = QHBoxLayout()
        config3b = QLabel("Bollinger Bands (BB Bands): ")
        radio_button5b = QRadioButton("Allow")
        radio_button6b = QRadioButton("Deny")
        button_group3b = QButtonGroup(tab)
        button_group3b.addButton(radio_button5b)
        button_group3b.addButton(radio_button6b)
        if configurations[7] == "Allow":
            radio_button5b.setChecked(True)
        else:
            radio_button6b.setChecked(True)
        H_layout3b.addWidget(config3b, 2)
        H_layout3b.addWidget(radio_button5b, 1)
        H_layout3b.addWidget(radio_button6b, 1)

        H_layout4b = QHBoxLayout()
        config4b = QLabel("Volume-Weighted Average Price (VWAP): ")
        radio_button7b = QRadioButton("Allow")
        radio_button8b = QRadioButton("Deny")
        button_group4b = QButtonGroup(tab)
        button_group4b.addButton(radio_button7b)
        button_group4b.addButton(radio_button8b)
        if configurations[8] == "Allow":
            radio_button7b.setChecked(True)
        else:
            radio_button8b.setChecked(True)
        H_layout4b.addWidget(config4b, 2)
        H_layout4b.addWidget(radio_button7b, 1)
        H_layout4b.addWidget(radio_button8b, 1)

        section_layout2.addLayout(H_layoutb)
        section_layout2.addLayout(H_layout2b)
        section_layout2.addLayout(H_layout3b)
        section_layout2.addLayout(H_layout4b)

        section1.setLayout(section_layout1)
        section2.setLayout(section_layout2)

        Hlayout.addWidget(section1)
        Hlayout.addWidget(section2)

        apply_button = QPushButton("Apply")
        bot_button = QPushButton("Start Telegram Bot")

        layout.addLayout(Hlayout)
        layout.addWidget(apply_button)
        layout.addWidget(bot_button)

        apply_button.clicked.connect(
            lambda: self.apply_configuration(button_group1, button_group2, button_group3, button_group4, button_group5,
                                             button_group1b, button_group2b, button_group3b, button_group4b))
        bot_button.clicked.connect(lambda: self.start_telegramBot(bot_button))

    def start_telegramBot(self, button):

        button.setEnabled(False)
        # Create a worker thread
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.process_finished(button))
        self.worker.set_data(None, None, None, "", "", "startBot")

        # Start the worker thread
        self.worker_threads.append(self.worker)
        self.worker.start()

    def apply_configuration(self, button_group1, button_group2, button_group3, button_group4, button_group5,
                            button_group1b, button_group2b, button_group3b, button_group4b):

        configurations[0] = button_group1.checkedButton().text()
        configurations[1] = button_group2.checkedButton().text()
        configurations[2] = button_group3.checkedButton().text()
        configurations[3] = button_group4.checkedButton().text()
        configurations[4] = button_group5.checkedButton().text()
        configurations[5] = button_group1b.checkedButton().text()
        configurations[6] = button_group2b.checkedButton().text()
        configurations[7] = button_group3b.checkedButton().text()
        configurations[8] = button_group4b.checkedButton().text()

        with open("configuration.txt", "w") as file:
            for configuration in configurations:
                file.write(str(configuration) + "\n")

    def get_stock_price(self, price_box, bt_model, text, input_box2a):
        bt_model.add_output(f"Getting Stock Price for {text}...")
        ret_sub, err_message = quote_ctx.subscribe([f"US.{text}"], [SubType.QUOTE], subscribe_push=False)
        if ret_sub == RET_OK:  # Successfully subscribed
            ret, data = quote_ctx.get_stock_quote(f"US.{text}")  # Get Time Frame data once
            if ret == RET_OK:
                print(data)
                current_stock_price = float(data["last_price"][0])
                bt_model.add_output(f"The Current Stock Price is {current_stock_price}")
                price_box.setText(str(current_stock_price))
                input_box2a.clear()
            else:
                bt_model.add_output('error:', data)
        else:
            bt_model.add_output('subscription failed', err_message)

    def calculate_call_price(self, input_box2, input_box2a):
        if input_box2.text():
            if float(input_box2.text()) < 100:
                target_stock_price = (float(input_box2.text()) // 2) * 2
            else:
                target_stock_price = (float(input_box2.text()) // 5) * 5
            input_box2a.setText(str(target_stock_price))

    def calculate_put_price(self, input_box2, input_box2a):
        if input_box2.text():
            if float(input_box2.text()) < 100:
                target_stock_price = (float(input_box2.text()) + 1) // 2 * 2
            else:
                target_stock_price = (float(input_box2.text()) + 4) // 5 * 5
            input_box2a.setText(str(target_stock_price))

    def view_option_price(self, option_name_box, type_box, expiration_box, option_price_box, market_price_box, ask_box,
                          bid_box, quantity_box, amount_box, text1, yes_button3, no_button3, text2, bt_model, button6):
        type = ""
        if yes_button3.isChecked():
            type = "C"
        elif no_button3.isChecked():
            type = "P"

        current_date = datetime.now()
        days_ahead = (4 - current_date.weekday()) % 7
        next_friday = current_date + timedelta(days=days_ahead)
        next_friday_date = next_friday.strftime('%y%m%d')

        price = int(float(text2))

        bt_model.add_output(f"Viewing Option Price for {text1}...")
        ret_sub, err_message = quote_ctx.subscribe([f"US.{text1}{next_friday_date}{type}{price}000"], [SubType.QUOTE],
                                                   subscribe_push=False)
        ret_subb = quote_ctx.subscribe([f"US.{text1}{next_friday_date}{type}{price}000"], [SubType.ORDER_BOOK],
                                       subscribe_push=False)[0]
        if ret_sub == RET_OK and ret_subb == RET_OK:  # Successfully subscribed
            ret, data = quote_ctx.get_stock_quote(
                f"US.{text1}{next_friday_date}{type}{price}000")  # Get the latest 2 candlestick data of HK.00700
            rett, data2 = quote_ctx.get_order_book(f"US.{text1}{next_friday_date}{type}{price}000", num=1)
            if ret == RET_OK and rett == RET_OK:
                option_name = data["code"][0]
                option_price = data["last_price"][0]
                bt_model.add_output(f"Found the Option Name: {option_name} with current Option Price: {option_price}")
                option_name_box.setText(str(option_name))
                type_box.setText(str(type))
                expiration_box.setText(str(next_friday_date))
                option_price_box.setText(str(option_price))
                ask_box.setText(str(data2["Ask"][0][0]))
                bid_box.setText(str(data2["Bid"][0][0]))
                # middle_number = (Decimal(data2["Ask"][0][0]) + Decimal(data2["Bid"][0][0])) / Decimal('2')
                # rounded_middle_number = round(middle_number, 2)
                self.priceRadio = 0.4
                if data2["Ask"][0][0] > data2["Bid"][0][0]:
                    distance = data2["Ask"][0][0] - data2["Bid"][0][0]
                    middle_number = distance * self.priceRadio + data2["Bid"][0][0]
                else:
                    distance = data2["Bid"][0][0] - data2["Ask"][0][0]
                    middle_number = distance * self.priceRadio + data2["Ask"][0][0]
                rounded_middle_number = round(middle_number, 2)
                market_price_box.setText(str(rounded_middle_number))
                quantity = int(1000 / (rounded_middle_number * 100))
                if quantity < 1:
                    quantity = 1
                quantity_box.setText(str(quantity))
                amount_box.setText(str(quantity * rounded_middle_number * 100))
                button6.setDisabled(False)
            else:
                bt_model.add_output('error')
        else:
            bt_model.add_output('subscription failed')

    def calculate_amount(self, amount_box, quantity_box, market_price_box):
        amount_box.setText(str(Decimal(quantity_box.text()) * Decimal(market_price_box.text()) * 100))

    def order_option(self, bt_model, option_code, market_price, quantity, yes_button5, no_button5, order_id_box,
                     button7a, button8, button6):
        pwd_unlock = '147852'
        trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US, host='127.0.0.1', port=11111,
                                      security_firm=SecurityFirm.FUTUSECURITIES)
        ret, data = trd_ctx.unlock_trade(pwd_unlock)
        if ret == RET_OK:
            trd_sidee = ""
            if yes_button5.isChecked():
                trd_sidee = TrdSide.BUY
            elif no_button5.isChecked():
                trd_sidee = TrdSide.SELL
            ret, data = trd_ctx.place_order(price=float(market_price), qty=int(quantity), code=option_code,
                                            trd_side=trd_sidee, trd_env=TrdEnv.REAL)
            if ret == RET_OK:
                bt_model.add_output(f'The order for {option_code} has been made successfully!')
                bt_model.add_output(f'Market Price: {market_price}, Quantity: {quantity}')
                order_id_box.setText(str(data['order_id'][0]))
                button7a.setDisabled(False)
                button8.setDisabled(False)
                button6.setDisabled(True)
                self.start_monitorOrder(bt_model, order_id_box, data['order_id'][0])
            else:
                bt_model.add_output('place_order error ')
                print('place_order error: ', data)
        else:
            bt_model.add_output('unlock_trade failed ')
            print('unlock_trade failed: ', data)
        trd_ctx.close()

    def start_monitorOrder(self, bt_model, order_id_box, order_id):

        # Create a worker thread
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.order_process_finished(order_id_box))
        self.worker.set_data(bt_model, None, None, order_id, "", "monitorOrder")

        # Start the worker thread
        self.worker_threads.append(self.worker)
        self.worker.start()

    def change_order(self, bt_model, option_code, ask_price, bid_price, quantity, order_id_box):
        pwd_unlock = '147852'
        trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US, host='127.0.0.1', port=11111,
                                      security_firm=SecurityFirm.FUTUSECURITIES)
        ret, data = trd_ctx.unlock_trade(pwd_unlock)
        if ret == RET_OK:
            order_id = order_id_box.text()
            if order_id:
                # middle_number = (Decimal(ask_price) + Decimal(bid_price)) / Decimal('2')
                # rounded_middle_number = round(middle_number, 2)
                self.priceRadio = self.priceRadio + 0.05
                if ask_price > bid_price:
                    distance = ask_price - bid_price
                    middle_number = distance * self.priceRadio + bid_price
                else:
                    distance = bid_price - ask_price
                    middle_number = distance * self.priceRadio + ask_price
                rounded_middle_number = round(middle_number, 2)
                ret, data = trd_ctx.modify_order(ModifyOrderOp.NORMAL, order_id, int(quantity), rounded_middle_number)
                if ret == RET_OK:
                    bt_model.add_output(f'The order for {option_code} has been modified and adjusted successfully!')
                    bt_model.add_output(f'Market Price: {rounded_middle_number}, Quantity: {quantity}')
                else:
                    bt_model.add_output('modify_order error ')
                    print('modify_order error: ', data)
        else:
            bt_model.add_output('unlock_trade failed ')
            print('unlock_trade failed: ', data)
        trd_ctx.close()

    def cancel_order(self, bt_model, option_code, order_id_box, button7a, button8):
        pwd_unlock = '147852'
        trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US, host='127.0.0.1', port=11111,
                                      security_firm=SecurityFirm.FUTUSECURITIES)
        ret, data = trd_ctx.unlock_trade(pwd_unlock)
        if ret == RET_OK:
            order_id = order_id_box.text()
            if order_id:
                ret, data = trd_ctx.modify_order(ModifyOrderOp.CANCEL, order_id, 0, 0)
                if ret == RET_OK:
                    bt_model.add_output(f'The order for {option_code} has been cancelled successfully!')
                    order_id_box.clear()
                    button7a.setDisabled(True)
                    button8.setDisabled(True)
                else:
                    bt_model.add_output('cancel_order error ')
                    print('cancel_order error: ', data)
        else:
            bt_model.add_output('unlock_trade failed ')
            print('unlock_trade failed: ', data)
        trd_ctx.close()

    def start_autoTrade(self, bt_model, checkBox10, button, button3, button6, button7a, button8, button9a):
        button.setEnabled(False)
        button3.setEnabled(False)
        button6.setEnabled(False)
        button7a.setEnabled(False)
        button8.setEnabled(False)
        button9a.setEnabled(False)
        checkBox10.setEnabled(False)
        # Create a worker thread
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.all_process_finished(button, button3, button6, checkBox10, button9a))
        self.worker.set_data(bt_model, None, None, "", "", "startAutoTrade")

        # Start the worker thread
        self.worker_threads.append(self.worker)
        self.worker.start()

    def add_content_to_earning(self, tab):

        # Create a layout for the tab
        layout = QVBoxLayout(tab)
        H_layout = QHBoxLayout()
        H2_layout = QHBoxLayout()

        current_date = QDate.currentDate()

        label = QLabel("Date:", tab)
        input_box_2 = QDateEdit(tab)
        input_box_2.setCalendarPopup(True)
        input_box_2.setDate(current_date)
        button = QPushButton("Generate", tab)
        button3 = QPushButton("Verify", tab)
        button2 = QPushButton("Browse", tab)
        table_view = QTableView(tab)
        table_view.setSelectionBehavior(QTableView.SelectRows)
        delegate = CustomDelegate()
        table_view.setItemDelegate(delegate)
        diagram_widget = DiagramWidget()
        diagram_widget_2 = DiagramWidget()
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        list_view = QListView(tab)

        H_layout.addWidget(label)
        H_layout.addWidget(input_box_2)
        H_layout.addWidget(button)
        H_layout.addWidget(button3)
        H_layout.addWidget(button2)
        H2_layout.addWidget(list_view, 1)
        H2_layout.addWidget(diagram_widget, 2)
        H2_layout.addWidget(diagram_widget_2, 2)
        layout.addLayout(H_layout)
        layout.addLayout(H2_layout)
        layout.addWidget(table_view)

        bt_model = OutputListModel(self)
        list_view.setModel(bt_model)

        table_model = QStandardItemModel(self)
        table_model.setHorizontalHeaderLabels(
            ['Symbol', 'Buy Price', 'Sell Price', 'Pattern (30)', 'Pattern (15)', '1st Band', '2st Band',
             'Trend', 'Pattern Chance (15)', 'Jump Up', 'Jump Down', 'Earning'])

        # Set the table model to the table view
        table_view.setModel(table_model)
        table_view.setSortingEnabled(True)

        # Connect the button click event to the add_to_list function
        button.clicked.connect(
            lambda: self.start_earning(button, bt_model, table_view, input_box_2.date().toString("yyyy-MM-dd")))
        button2.clicked.connect(lambda: self.browse_earning(table_view))
        button3.clicked.connect(
            lambda: self.start_verify(button3, bt_model, table_view, input_box_2.date().toString("yyyy-MM-dd")))
        table_view.clicked.connect(lambda: self.show_backtest_plot(table_view.currentIndex(), diagram_widget))
        table_view.clicked.connect(lambda: self.show_backtest_plot_2(table_view.currentIndex(), diagram_widget_2))
        bt_model.rowsInserted.connect(lambda: self.scroll_to_bottom(list_view))
        table_view.horizontalHeader().sectionClicked.connect(
            lambda column: self.sort_by_column(column, table_view, bt_model))

    def start_earning(self, button, bt_model, table_view, text):
        # Disable the button
        button.setEnabled(False)
        bt_model.add_output("Please Wait... Executing......")

        # Create a worker thread
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.process_finished(button))
        self.worker.set_data(bt_model, table_view, None, text, "", "earning")

        # Start the worker thread
        self.worker_threads.append(self.worker)
        self.worker.start()

    def start_verify(self, button, bt_model, table_view, text):
        # Disable the button
        button.setEnabled(False)
        bt_model.add_output("Please Wait... Executing......")

        # Create a worker thread
        self.worker = None
        self.worker = WorkerThread()
        self.worker.finished.connect(lambda: self.process_finished(button))
        self.worker.set_data(bt_model, table_view, None, text, "", "verify")

        # Start the worker thread
        self.worker_threads.append(self.worker)
        self.worker.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('logo.png'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
