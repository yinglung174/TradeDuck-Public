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

import numpy as np
import asyncio
import matplotlib.pyplot as plt
from io import BytesIO
import pandas_market_calendars as mcal
from futu import *
import time
import random
from datetime import datetime, timedelta
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

import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, Updater

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

api_key = 'Q4HS1CE7298ANN7M'

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

configurations = []

telegram_instant_sell = queue.Queue()
futu_instant_buy = queue.Queue()

# Open the file in read mode
with open("configuration.txt", "r") as file:
    for line in file:
        configurations.append(line.strip())
    if not configurations:
        for i in range(9):
            configurations.append("Allow")


def initializeIndicator():
    global sma_values_1
    global sma_values_10_1
    global sma_values_20_1
    global sma_values_daily_yesterstday
    global sma_values_daily_previousday
    global sma_values_daily_10_yesterstday
    global sma_values_daily_10_previousday
    global sma_values_daily_20_yesterstday
    global daily_values_open_yestersday
    global daily_values_close_yestersday
    global ema_values_1
    global ema_values_10_1

    sma_values_1 = 0.0
    for timestamp_sma, values_sma in sma.items():
        if timestamp_sma in time_1:
            sma_values_1 = float(values_sma['SMA'])
        for verify in verify_array:
            if timestamp_sma in verify[2]:
                verify[4] = float(values_sma['SMA'])
        if sma_values_1 != 0.0 and verify_array[28][4] != 0.0:
            break
    sma_values_10_1 = 0.0
    for timestamp_sma, values_sma in sma_10.items():
        if timestamp_sma in time_1:
            sma_values_10_1 = float(values_sma['SMA'])
        for verify in verify_array:
            if timestamp_sma in verify[2]:
                verify[7] = float(values_sma['SMA'])
        if sma_values_10_1 != 0.0 and verify_array[28][7] != 0.0:
            break
    sma_values_20_1 = 0.0
    for timestamp_sma, values_sma in sma_20.items():
        if timestamp_sma in time_1:
            sma_values_20_1 = float(values_sma['SMA'])
        for verify in verify_array:
            if timestamp_sma in verify[2]:
                verify[12] = float(values_sma['SMA'])
        if sma_values_20_1 != 0.0 and verify_array[28][12] != 0.0:
            break
    sma_values_daily_yesterstday = 0.0
    sma_values_daily_previousday = 0.0
    sma_found_previousday = False
    for timestamp_sma, values_sma in sma_daily.items():
        if sma_found_previousday:
            sma_values_daily_previousday = float(values_sma['SMA'])
            break
        if timestamp_sma in time_1:
            sma_values_daily_yesterstday = float(values_sma['SMA'])
            sma_found_previousday = True
    sma_values_daily_10_yesterstday = 0.0
    sma_values_daily_10_previousday = 0.0
    sma_10_found_previousday = False
    for timestamp_sma, values_sma in sma_daily_10.items():
        if sma_10_found_previousday:
            sma_values_daily_10_previousday = float(values_sma['SMA'])
            break
        if timestamp_sma in time_1:
            sma_values_daily_10_yesterstday = float(values_sma['SMA'])
            sma_10_found_previousday = True
    sma_values_daily_20_yesterstday = 0.0
    for timestamp_sma, values_sma in sma_daily_20.items():
        if timestamp_sma in time_1:
            sma_values_daily_20_yesterstday = float(values_sma['SMA'])
            break
    daily_values_open_yestersday = 0.0
    daily_values_close_yestersday = 0.0
    for timestamp, values in time_series_daily.items():
        if timestamp in time_1:
            daily_values_open_yestersday = float(values['1. open'])
            daily_values_close_yestersday = float(values['4. close'])
            break
    ema_values_1 = 0.0
    for timestamp_ema, values_ema in ema.items():
        if timestamp_ema in time_1:
            ema_values_1 = float(values_ema['EMA'])
        for verify in verify_array:
            if timestamp_ema in verify[2]:
                verify[6] = float(values_ema['EMA'])
        if ema_values_1 != 0.0 and verify_array[28][6] != 0.0:
            break
    ema_values_10_1 = 0.0
    for timestamp_ema, values_ema in ema_10.items():
        if timestamp_ema in time_1:
            ema_values_10_1 = float(values_ema['EMA'])
        for verify in verify_array:
            if timestamp_ema in verify[2]:
                verify[8] = float(values_ema['EMA'])
        if ema_values_10_1 != 0.0 and verify_array[28][8] != 0.0:
            break
def defineCandleSticksFUTU(data):
    global isLastGreen
    global isLastRed
    global isLast2Green
    global isLast2Red
    global isLast3Green
    global isLast3Red
    global isLast4Green
    global isLast4Red
    global lastUpperDistance
    global lastLowerDistance
    global last2UpperDistance
    global last2LowerDistance
    global last3UpperDistance
    global last3LowerDistance
    global last4UpperDistance
    global last4LowerDistance
    global lastOpen
    global lastClose
    global lastHigh
    global lastLow
    global last2Open
    global last2Close
    global last2High
    global last2Low
    global last3Open
    global last3Close
    global last3High
    global last3Low
    global last4Open
    global last4Close
    global last4High
    global last4Low
    global lastTime
    global lastEMA10
    global lastLargestDistance
    global last2LargestDistance
    global last3LargestDistance
    global last4LargestDistance
    global lastMiddleDistance
    global last2MiddleDistance
    global last3MiddleDistance
    global last4MiddleDistance
    ema_10 = data['close'].ewm(span=10, adjust=False).mean()
    isLastGreen = False
    isLastRed = False
    isLast2Green = False
    isLast2Red = False
    isLast3Green = False
    isLast3Red = False
    isLast4Green = False
    isLast4Red = False
    lastUpperDistance = 0
    lastLowerDistance = 0
    last2UpperDistance = 0
    last2LowerDistance = 0
    last3UpperDistance = 0
    last3LowerDistance = 0
    last4UpperDistance = 0
    last4LowerDistance = 0
    lastOpen = 0
    lastClose = 0
    lastHigh = 0
    lastLow = 0
    last2Open = 0
    last2Close = 0
    last2High = 0
    last2Low = 0
    last3Open = 0
    last3Close = 0
    last3High = 0
    last3Low = 0
    last4Open = 0
    last4Close = 0
    last4High = 0
    last4Low = 0
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
    if "09:31:00" not in data['time_key'][len(data) - 2]:
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
    if "09:31:00" not in data['time_key'][len(data) - 2] and "09:32:00" not in data['time_key'][len(data) - 2]:
        last3Open = data['open'][len(data) - 4]
        last3Close = data['close'][len(data) - 4]
        last3High = data['high'][len(data) - 4]
        last3Low = data['low'][len(data) - 4]
        last3LargestDistance = lastHigh - lastLow
        if (last3Open < last3Close):
            isLast3Green = True
            last3MiddleDistance = last3Close - last3Open
            last3UpperDistance = last3High - last3Close
            last3LowerDistance = last3Open - last3Low
        else:
            isLast3Red = True
            last3MiddleDistance = last3Open - last3Close
            last3UpperDistance = last3High - last3Open
            last3LowerDistance = last3Close - last3Low
    if "09:31:00" not in data['time_key'][len(data) - 2] and "09:32:00" not in data['time_key'][
        len(data) - 2] and "09:33:00" not in data['time_key'][len(data) - 2]:
        last4Open = data['open'][len(data) - 5]
        last4Close = data['close'][len(data) - 5]
        last4High = data['high'][len(data) - 5]
        last4Low = data['low'][len(data) - 5]
        last4LargestDistance = lastHigh - lastLow
        if (last4Open < last4Close):
            isLast4Green = True
            last4MiddleDistance = last4Close - last4Open
            last4UpperDistance = last4High - last4Close
            last4LowerDistance = last4Open - last4Low
        else:
            isLast4Red = True
            last4MiddleDistance = last4Open - last4Close
            last4UpperDistance = last4High - last4Open
            last4LowerDistance = last4Close - last4Low

def callBuyConditionFUTU(data):
    global isBuySignal
    global buyPattern
    # price pattern (color > self distance > compare)
    if "09:31:00" not in data['time_key'][len(data) - 2] and "09:32:00" not in data['time_key'][
        len(data) - 2] and "09:33:00" not in data['time_key'][len(data) - 2]:
        if  False:
            isBuySignal = True
            buyPattern = "Bullish Belt Hold"
        if isLastGreen and isLast2Green and isLast3Green and isLast4Red and \
            last2MiddleDistance < last3MiddleDistance * 2.5 and \
            lastMiddleDistance < last2MiddleDistance * 2.5 and \
            last2UpperDistance < last2MiddleDistance and \
            lastUpperDistance < lastMiddleDistance and \
            last3UpperDistance < last3MiddleDistance and \
            lastHigh > lastEMA10 and isBuySignal == False:
            isBuySignal = True
            buyPattern = "Three Strong Soldiers"
    if "09:31:00" not in data['time_key'][len(data) - 2] and "09:32:00" not in data['time_key'][len(data) - 2]:
        if False:
            isBuySignal = True
            buyPattern = "Three star in south"
        if False:
            isBuySignal = True
            buyPattern = "Upside Tasuki gap"
        if isLastGreen and isLast2Green and isLast3Red and \
            lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
            last3LowerDistance > last3UpperDistance and last3MiddleDistance > last3UpperDistance and \
            lastHigh > lastEMA10 and isBuySignal == False:
            isBuySignal = True
            buyPattern = "Half Doji Star"
        if isLastGreen and isLast2Red and isLast3Green and \
            last2MiddleDistance + last2LowerDistance > last2UpperDistance and \
            lastMiddleDistance > lastUpperDistance and lastLowerDistance > lastUpperDistance and \
            lastClose * 1.000125 > lastHigh and isBuySignal == False:
            isBuySignal = True
            buyPattern = "Upfront Tweezer Top"
    if "09:31:00" not in data['time_key'][len(data) - 2]:
        if False:
            isBuySignal = True
            buyPattern = "Bullish Piercing"
        if False:
            isBuySignal = True
            buyPattern = "Rising Window"
        if False:
            isBuySignal = True
            buyPattern = "Bullish kicker"
        if False:
            isBuySignal = True
            buyPattern = "Matching low candlestick"
        if isLastGreen and isLast2Green and "09:32" in lastTime and \
            last2Open == last2Low and \
            lastOpen == lastLow  and \
            last2MiddleDistance < lastMiddleDistance * 3 and isBuySignal == False :
            isBuySignal = True
            buyPattern = "First Shot"

def putBuyConditionFUTU(data):
    global isBuySignal
    global buyPattern
    # price pattern (color > self distance > compare)
    if "09:31:00" not in data['time_key'][len(data) - 2] and "09:32:00" not in data['time_key'][
        len(data) - 2] and "09:33:00" not in data['time_key'][len(data) - 2]:
        if False:
            isBuySignal = True
            buyPattern = "Bearish belt hold"  # changed
        if isLastRed and isLast2Red and isLast3Red and isLast4Green and \
                last2MiddleDistance < last3MiddleDistance * 2.5 and \
                lastMiddleDistance < last2MiddleDistance * 2.5 and \
                last2LowerDistance < last2MiddleDistance and \
                lastLowerDistance < lastMiddleDistance and \
                last3LowerDistance < last3MiddleDistance and \
                lastLow < lastEMA10 and isBuySignal == False:
            isBuySignal = True
            buyPattern = "Three Weak Soldiers"
    if "09:31:00" not in data['time_key'][len(data) - 2] and "09:32:00" not in data['time_key'][len(data) - 2]:
        if False:
            isBuySignal = True
            buyPattern = "Advance block"  # changed
        if False:
            isBuySignal = True
            buyPattern = "Deliberation"  # changed
        if False:
            isBuySignal = True
            buyPattern = "Downside tasuki gap"  # changed
        if isLastRed and isLast2Red and isLast3Green and \
                lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                last3LowerDistance < last3UpperDistance and last3MiddleDistance > last3LowerDistance and \
                lastLow < lastEMA10 and isBuySignal == False:
            isBuySignal = True
            buyPattern = "Reversed Doji Star"
        if isLastRed and isLast2Green and isLast3Red and \
                last2MiddleDistance + last2UpperDistance > last2LowerDistance and \
                lastMiddleDistance > last2LowerDistance and lastLowerDistance < lastUpperDistance and \
                lastClose <= lastLow * 1.000125 and isBuySignal == False:
            isBuySignal = True
            buyPattern = "Upfront Tweezer Down"
    if "09:31:00" not in data['time_key'][len(data) - 2]:
        if False:
            isBuySignal = True
            buyPattern = "Falling Window"  # changed
        if False:
            isBuySignal = True
            buyPattern = "Bear Kicking"  # changed
        if False:
            isBuySignal = True
            buyPattern = "On neck candlestick"  # changed
        if False:
            isBuySignal = True
            buyPattern = "Matching high"  # changed
        if False:
            isBuySignal = True
            buyPattern = "Bearish Piercing"  # changed
        if isLastRed and isLast2Red and "09:32" in lastTime and \
                last2Open == last2High and \
                lastOpen == lastHigh and \
                last2MiddleDistance < lastMiddleDistance * 3 and isBuySignal == False:
            isBuySignal = True
            buyPattern = "First Kill"

def defineCandleSticks(i):
    global isLastGreen
    global isLastRed
    global isLast2Green
    global isLast2Red
    global isLast3Green
    global isLast3Red
    global isLast4Green
    global isLast4Red
    global lastUpperDistance
    global lastLowerDistance
    global last2UpperDistance
    global last2LowerDistance
    global last3UpperDistance
    global last3LowerDistance
    global last4UpperDistance
    global last4LowerDistance
    global lastOpen
    global lastClose
    global lastHigh
    global lastLow
    global last2Open
    global last2Close
    global last2High
    global last2Low
    global last3Open
    global last3Close
    global last3High
    global last3Low
    global last4Open
    global last4Close
    global last4High
    global last4Low
    global lastTime
    global lastEMA10
    global lastLargestDistance
    global last2LargestDistance
    global last3LargestDistance
    global last4LargestDistance
    global lastMiddleDistance
    global last2MiddleDistance
    global last3MiddleDistance
    global last4MiddleDistance

    isLastGreen = False
    isLastRed = False
    isLast2Green = False
    isLast2Red = False
    isLast3Green = False
    isLast3Red = False
    isLast4Green = False
    isLast4Red = False
    lastUpperDistance = 0
    lastLowerDistance = 0
    last2UpperDistance = 0
    last2LowerDistance = 0
    last3UpperDistance = 0
    last3LowerDistance = 0
    last4UpperDistance = 0
    last4LowerDistance = 0
    lastOpen = 0
    lastClose = 0
    lastHigh = 0
    lastLow = 0
    last2Open = 0
    last2Close = 0
    last2High = 0
    last2Low = 0
    last3Open = 0
    last3Close = 0
    last3High = 0
    last3Low = 0
    last4Open = 0
    last4Close = 0
    last4High = 0
    last4Low = 0
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
    if i - 2 >= 0:
        last3Open = float(verify_array[i - 2][9])
        last3Close = float(verify_array[i - 2][1])
        last3High = float(verify_array[i - 2][5])
        last3Low = float(verify_array[i - 2][3])
        last3LargestDistance = lastHigh - lastLow
        if (float(verify_array[i - 2][9]) < float(verify_array[i - 2][1])):
            isLast3Green = True
            last3MiddleDistance = float(verify_array[i - 2][1]) - float(
                verify_array[i - 2][9])
            last3UpperDistance = float(verify_array[i - 2][5]) - float(
                verify_array[i - 2][1])
            last3LowerDistance = float(verify_array[i - 2][9]) - float(
                verify_array[i - 2][3])
        else:
            isLast3Red = True
            last3MiddleDistance = float(verify_array[i - 2][9]) - float(
                verify_array[i - 2][1])
            last3UpperDistance = float(verify_array[i - 2][5]) - float(
                verify_array[i - 2][9])
            last3LowerDistance = float(verify_array[i - 2][1]) - float(
                verify_array[i - 2][3])
    if i - 3 >= 0:
        last4Open = float(verify_array[i - 3][9])
        last4Close = float(verify_array[i - 3][1])
        last4High = float(verify_array[i - 3][5])
        last4Low = float(verify_array[i - 3][3])
        last4LargestDistance = lastHigh - lastLow
        if (float(verify_array[i - 3][9]) < float(verify_array[i - 3][1])):
            isLast4Green = True
            last4MiddleDistance = float(verify_array[i - 3][1]) - float(
                verify_array[i - 3][9])
            last4UpperDistance = float(verify_array[i - 3][5]) - float(
                verify_array[i - 3][1])
            last4LowerDistance = float(verify_array[i - 3][9]) - float(
                verify_array[i - 3][3])
        else:
            isLast4Red = True
            last4MiddleDistance = float(verify_array[i - 3][9]) - float(
                verify_array[i - 3][1])
            last4UpperDistance = float(verify_array[i - 3][5]) - float(
                verify_array[i - 3][9])
            last4LowerDistance = float(verify_array[i - 3][1]) - float(
                verify_array[i - 3][3])


def callBuyCondition(i):
    global isBuySignal
    global buyPattern
    # price pattern (color > self distance > compare)
    if i - 3 >= 0:
        if  False:
            isBuySignal = True
            buyPattern = "Bullish Belt Hold"
        if isLastGreen and isLast2Green and isLast3Green and isLast4Red and \
            last2MiddleDistance < last3MiddleDistance * 2.5 and \
            lastMiddleDistance < last2MiddleDistance * 2.5 and \
            last2UpperDistance < last2MiddleDistance and \
            lastUpperDistance < lastMiddleDistance and \
            last3UpperDistance < last3MiddleDistance and \
            lastHigh > lastEMA10 and isBuySignal == False:
            isBuySignal = True
            buyPattern = "Three Strong Soldiers"
    if i - 2 >= 0:
        if False:
            isBuySignal = True
            buyPattern = "Three star in south"
        if False:
            isBuySignal = True
            buyPattern = "Upside Tasuki gap"
        if isLastGreen and isLast2Green and isLast3Red and \
            lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
            last3LowerDistance > last3UpperDistance and last3MiddleDistance > last3UpperDistance and \
            lastHigh > lastEMA10 and isBuySignal == False:
            isBuySignal = True
            buyPattern = "Half Doji Star"
        if isLastGreen and isLast2Red and isLast3Green and \
            last2MiddleDistance + last2LowerDistance > last2UpperDistance and \
            lastMiddleDistance > lastUpperDistance and lastLowerDistance > lastUpperDistance and \
            lastClose * 1.000125 > lastHigh and isBuySignal == False:
            isBuySignal = True
            buyPattern = "Upfront Tweezer Top"
    if i - 1 >= 0:
        if False:
            isBuySignal = True
            buyPattern = "Bullish Piercing"
        if False:
            isBuySignal = True
            buyPattern = "Rising Window"
        if False:
            isBuySignal = True
            buyPattern = "Bullish kicker"
        if False:
            isBuySignal = True
            buyPattern = "Matching low candlestick"
        if isLastGreen and isLast2Green and "09:31" in lastTime and \
            last2Open == last2Low and \
            lastOpen == lastLow  and \
            last2MiddleDistance < lastMiddleDistance * 3 and isBuySignal == False :
            isBuySignal = True
            buyPattern = "First Shot"

def putBuyCondition(i):
    global isBuySignal
    global buyPattern
    # price pattern (color > self distance > compare)
    if i - 3 >= 0:
        if False:
            isBuySignal = True
            buyPattern = "Bearish belt hold"  # changed
        if isLastRed and isLast2Red and isLast3Red and isLast4Green and \
                last2MiddleDistance < last3MiddleDistance * 2.5 and \
                lastMiddleDistance < last2MiddleDistance * 2.5 and \
                last2LowerDistance < last2MiddleDistance and \
                lastLowerDistance < lastMiddleDistance and \
                last3LowerDistance < last3MiddleDistance and \
                lastLow < lastEMA10 and isBuySignal == False:
            isBuySignal = True
            buyPattern = "Three Weak Soldiers"
    if i - 2 >= 0:
        if False:
            isBuySignal = True
            buyPattern = "Advance block"  # changed
        if False:
            isBuySignal = True
            buyPattern = "Deliberation"  # changed
        if False:
            isBuySignal = True
            buyPattern = "Downside tasuki gap"  # changed
        if isLastRed and isLast2Red and isLast3Green and \
                lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                last3LowerDistance < last3UpperDistance and last3MiddleDistance > last3LowerDistance and \
                lastLow < lastEMA10 and isBuySignal == False:
            isBuySignal = True
            buyPattern = "Reversed Doji Star"
        if isLastRed and isLast2Green and isLast3Red and \
                last2MiddleDistance + last2UpperDistance > last2LowerDistance and \
                lastMiddleDistance > last2LowerDistance and lastLowerDistance < lastUpperDistance and \
                lastClose <= lastLow * 1.000125 and isBuySignal == False:
            isBuySignal = True
            buyPattern = "Upfront Tweezer Down"
    if i - 1 >= 0:
        if False:
            isBuySignal = True
            buyPattern = "Falling Window"  # changed
        if False:
            isBuySignal = True
            buyPattern = "Bear Kicking"  # changed
        if False:
            isBuySignal = True
            buyPattern = "On neck candlestick"  # changed
        if False:
            isBuySignal = True
            buyPattern = "Matching high"  # changed
        if False:
            isBuySignal = True
            buyPattern = "Bearish Piercing"  # changed
        if isLastRed and isLast2Red and "09:31" in lastTime and \
                last2Open == last2High and \
                lastOpen == lastHigh and \
                last2MiddleDistance < lastMiddleDistance * 3 and isBuySignal == False:
            isBuySignal = True
            buyPattern = "First Kill"

def backtestData(month, model):
    global sma
    global sma_10
    global sma_20
    global ema
    global ema_10
    global sma_daily
    global sma_daily_10
    global sma_daily_20
    global time_series_daily
    global time_1
    global verify_array
    global array_overall
    global isBuySignal
    global buyPattern

    with lock:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&month={month}&symbol={symbol}&interval=1min&outputsize=full&apikey={api_key}&entitlement=delayed"
        response = session.get(url)

        url_sma = f"https://www.alphavantage.co/query?function=SMA&symbol={symbol}&month={month}&interval=1min&time_period=5&series_type=close&apikey={api_key}&entitlement=delayed"
        response_2 = session.get(url_sma)

        url_sma_10 = f"https://www.alphavantage.co/query?function=SMA&symbol={symbol}&month={month}&interval=1min&time_period=10&series_type=close&apikey={api_key}&entitlement=delayed"
        response_3 = session.get(url_sma_10)

        url_ema = f"https://www.alphavantage.co/query?function=EMA&symbol={symbol}&month={month}&interval=1min&time_period=5&series_type=close&apikey={api_key}&entitlement=delayed"
        response_4 = session.get(url_ema)

        url_ema_10 = f"https://www.alphavantage.co/query?function=EMA&symbol={symbol}&month={month}&interval=1min&time_period=10&series_type=close&apikey={api_key}&entitlement=delayed"
        response_5 = session.get(url_ema_10)

        url_sma_20 = f"https://www.alphavantage.co/query?function=SMA&symbol={symbol}&month={month}&interval=1min&time_period=20&series_type=close&apikey={api_key}&entitlement=delayed"
        response_3a = session.get(url_sma_20)

        if response.status_code == 200:
            data = response.json()
            data_sma = response_2.json()
            data_sma_10 = response_3.json()
            data_sma_20 = response_3a.json()
            data_ema = response_4.json()
            data_ema_10 = response_5.json()
            data_sma_daily = response_6a.json()
            data_sma_daily_10 = response_6b.json()
            data_sma_daily_20 = response_6c.json()
            data_daily = response_9.json()
            time_series = data['Time Series (1min)']
            sma = data_sma['Technical Analysis: SMA']
            sma_10 = data_sma_10['Technical Analysis: SMA']
            sma_20 = data_sma_20['Technical Analysis: SMA']
            ema = data_ema['Technical Analysis: EMA']
            ema_10 = data_ema_10['Technical Analysis: EMA']
            sma_daily = data_sma_daily['Technical Analysis: SMA']
            sma_daily_10 = data_sma_daily_10['Technical Analysis: SMA']
            sma_daily_20 = data_sma_daily_20['Technical Analysis: SMA']
            time_series_daily = data_daily['Time Series (Daily)']

            price_1 = 0.0
            price_1_low = 0.0
            price_1_high = 0.0
            is3DailySMATrend = False
            isVersionTwo = False
            time_1 = ""
            verify_array = []
            verify_array_format = 30
            num_of_minute = 30
            for i in range(num_of_minute):
                row = [f'09:{verify_array_format}:00', 0.0, '', 0.0, 0.0, 0.0, 0.0, 0.0,
                       0.0, 0.0, 0.0, 0.0,
                       0.0]  # time, closed, date, low, SMA-5, high, EMA-5, SMA-10, EMA-10, open, macd, rsi, SMA-20
                verify_array.append(row)
                verify_array_format = verify_array_format + 1
            total_chance = 0
            total_bingo_chance = 0
            array_csv = []

            for timestamp, values in time_series.items():
                if "16:00:00" in timestamp:
                    # print(f"{timestamp} : {values['4. close']}")
                    price_1 = float(values['4. close'])
                    price_1_low = float(values['3. low'])
                    price_1_high = float(values['2. high'])
                    time_1 = timestamp
                    if verify_array[28][1] != 0.0 and price_1 != 0.0:
                        initializeIndicator()
                        if verify_array[0][3] > price_1_high:  # condition 1
                        #if False:
                            jumpDistance = (verify_array[0][3] - price_1_high) / verify_array[0][3]
                            isBuySignal = False
                            isSellSignal = False
                            buyAlready = False
                            buyPattern = ""
                            sellPattern = ""
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
                                        verify_array[m][6] = verify_array[m - 1][6]
                                        verify_array[m][7] = verify_array[m - 1][7]
                                        verify_array[m][8] = verify_array[m - 1][8]
                                        verify_array[m][12] = verify_array[m - 1][12]

                            for i in range(len(verify_array) - 1):  # start adding buy condition
                                defineCandleSticks(i)
                                callBuyCondition(i)
                                if isBuySignal == True and buyAlready == False and "09:3" in lastTime:
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
                                    k = 2
                                    chance_bingo = 0
                                    chance_bingo_correct = 0
                                    buyAlready = True
                                    for j in range(len(verify_array) - 3 - i):
                                        print(f"{verify_array[k + i][2]} : {verify_array[k + i][3]}")
                                        model.add_output(f"{verify_array[k + i][2]} : {verify_array[k + i][3]}")
                                        defineCandleSticks(k+i)
                                            # price pattern (color > self distance > compare)
                                        if k + i - 3 > 0:
                                            if isLastRed and isLast2Green and isLast3Green and isLast4Green and \
                                                    lastLargestDistance > last2LargestDistance and lastLargestDistance > last3LargestDistance and lastLargestDistance > last4LargestDistance and \
                                                    lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                                                    last4Close < last3Close and last3Close < last2Close and last2Close < lastOpen and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Bearish belt hold"  # changed
                                        if k + i - 2 > 0:
                                            if isLastRed and isLast2Red and isLast3Green and \
                                                    last2MiddleDistance > last3MiddleDistance and \
                                                    last2Open > last3Close and last2Close < last3Open and \
                                                    lastClose < last2Low and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Three outside down"  # changed
                                            if isLastRed and isLast3Green and \
                                                    lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                                                    last3MiddleDistance > last3UpperDistance + last3LowerDistance and \
                                                    last2MiddleDistance < last2LargestDistance * 0.1 and \
                                                    last2High > last3Close and last2High > lastOpen and last2Low > last3Low and last2Low > lastLow and \
                                                    lastClose < last3MiddleDistance / 2 and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Evening doji star"  # changed
                                            if isLastRed and isLast3Green and \
                                                    lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                                                    last3MiddleDistance > last3UpperDistance + last3LowerDistance and \
                                                    last2MiddleDistance < last2LargestDistance * 0.1 and \
                                                    last2Low > last3High and last2Low > lastHigh and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Bearish abandoned baby"  # chaged
                                            if isLastRed and isLast2Red and isLast3Red and \
                                                    lastClose < last2Close and last2Close < last3Close and \
                                                    lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                                                    last3MiddleDistance > last3UpperDistance + last3LowerDistance and \
                                                    last2MiddleDistance < last2LargestDistance + last2LowerDistance and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Three black crows"  # changed
                                            if isLastGreen and isLast2Green and isLast3Green and \
                                                    last2Open > last3Open and last2Close > last3Close and \
                                                    lastClose > last2Close and lastOpen > lastOpen and lastUpperDistance > lastMiddleDistance and \
                                                    last2MiddleDistance / 2 > lastMiddleDistance and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Advance block"  # changed
                                            if isLastGreen and isLast2Green and isLast3Green and \
                                                    last2Open > last3Open and last2Close > last3Close and \
                                                    lastClose > last2Close and last2MiddleDistance / 2 > lastMiddleDistance and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Deliberation"  # changed
                                            if isLastGreen and isLast2Red and isLast3Red and \
                                                    lastClose > last2Open and last2Open < last3Close and lastClose < last3Close and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Downside tasuki gap"  # changed
                                        if k + i - 1 > 0:
                                            if isLastRed and isLast2Red and \
                                                    lastHigh > last2Low and \
                                                    lastMiddleDistance > lastUpperDistance + lastLowerDistance and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Falling Window"  # changed
                                            if isLastRed and isLast2Green and \
                                                    lastHigh == lastOpen and last2High == last2Close and \
                                                    lastClose > last2Open and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Tweezer Top"  # changed
                                            if isLastRed and isLast2Green and \
                                                    lastOpen == lastHigh and lastLow == lastClose and \
                                                    last2Open == lastLow and last2Close == lastHigh and \
                                                    lastHigh < last2Low and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Bear Kicking"  # changed
                                            if isLastGreen and isLast2Red and \
                                                    lastMiddleDistance < last2MiddleDistance and \
                                                    last2Close > lastHigh and lastLow > last2Low and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "On neck candlestick"  # changed
                                            if isLastGreen and isLast2Green and \
                                                    lastHigh == lastClose and last2High == last2Close and \
                                                    lastOpen > last2Open and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Matching high"  # changed
                                            if isLastRed and isLast2Green and \
                                                    lastClose < last2MiddleDistance / 2 and \
                                                    lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                                                    last2MiddleDistance > last2UpperDistance + last2LowerDistance and \
                                                    last2Close < lastOpen and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Bearish Piercing"  # changed
                                        if float(verify_array[i + k][3]) > float(
                                                verify_array[i + 1][3]):
                                            chance_bingo_correct = chance_bingo_correct + 1
                                        if isSellSignal == True and buyAlready == True:
                                            # print(f"SELL BUY Signal, Pattern: {sellPattern}")
                                            # model.add_output(f"SELL BUY Signal, Pattern: {sellPattern}")
                                            trigger_sell_time = verify_array[i + k][0]
                                            trigger_sell_price = verify_array[i + k][3]
                                            sell_time = verify_array[i + k + 1][0]
                                            sell_price = verify_array[i + k + 1][3]
                                            price_action_earn = (verify_array[i + k + 1][3] - verify_array[i + 1][3]) / \
                                                                verify_array[i + k + 1][3] * 100
                                            # buyAlready = False
                                        if float(verify_array[i + k][7]) > float(verify_array[i + k][9]) and float(
                                                verify_array[i + k][1]) > float(
                                                verify_array[i + k][9]) and is_sell_ema_10 == 0 and buyAlready == True:
                                            print(f"Sell CALL! (EMA-10 Method)")  # sell method 3
                                            model.add_output(f"Sell CALL! (EMA-10 Method)")
                                            ema_10_time = verify_array[i + k][0]
                                            ema_10_earn = (verify_array[i + k][3] - verify_array[i + 1][3]) / \
                                                          verify_array[i + k][3] * 100
                                            is_sell_ema_10 = 1
                                            buyAlready = False
                                        if (highest_sell_earn < float(verify_array[i + k][3]) - float(
                                                verify_array[i + 1][3])):
                                            highest_sell_time = verify_array[i + k][0]
                                            highest_sell_earn = (verify_array[i + k][3] - verify_array[i + 1][3]) / \
                                                                verify_array[i + k][3] * 100
                                        chance_bingo = chance_bingo + 1
                                        k = k + 1
                                    if is_sell_ema_10 == 0:
                                        ema_10_time = verify_array[len(verify_array) - 1][0]
                                        ema_10_earn = (verify_array[len(verify_array) - 1][3] - verify_array[i + 1][
                                            3]) / verify_array[len(verify_array) - 1][3] * 100
                                    print("Increasing Direction")
                                    print("Total Chance of Trigger Bingo Rise:")
                                    model.add_output("Increasing Direction")
                                    model.add_output("Total Chance of Trigger Bingo Rise:")
                                    if chance_bingo != 0:
                                        every_trade_chance = chance_bingo_correct / chance_bingo
                                    else:
                                        every_trade_chance = 0
                                    print(every_trade_chance)
                                    model.add_output(every_trade_chance)
                                    total_bingo_chance = total_bingo_chance + chance_bingo_correct
                                    total_chance = total_chance + chance_bingo
                                    row = [verify_array[i][2].split(' ')[0], price_1_low, f"{jumpDistance:.5g}", "CALL",
                                           verify_array[i][0], verify_array[i][3], verify_array[i + 1][0],
                                           verify_array[i + 1][3], buyPattern,
                                           f"{every_trade_chance:.5g}", ema_10_time,
                                           f"{ema_10_earn:.5g}", highest_sell_time,
                                           f"{highest_sell_earn:.5g}"]
                                    array_csv.append(row)
                                    print("--------------")
                                    model.add_output("--------------")
                                    break
                        if verify_array[0][5] < price_1_low:  # condition 1
                        #if False:
                            jumpDistance = (verify_array[0][5] - price_1_low) / verify_array[0][5]
                            isBuySignal = False
                            buyAlready = False
                            buyPattern = ""
                            isSellSignal = False
                            sellPattern = ""
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
                                        verify_array[m][6] = verify_array[m - 1][6]
                                        verify_array[m][7] = verify_array[m - 1][7]
                                        verify_array[m][8] = verify_array[m - 1][8]
                                        verify_array[m][12] = verify_array[m - 1][12]
                            for i in range(len(verify_array) - 1):  # start adding buy condition
                                defineCandleSticks(i)
                                putBuyCondition(i)
                                if isBuySignal == True and (float(verify_array[i][7]) >= lastClose or float(
                                        verify_array[i][7]) >= lastOpen) and buyAlready == False and "09:3" in \
                                        verify_array[i][0]:
                                    print(f"{time_1} : {price_1_high}")
                                    print(f"{verify_array[i][2]} : {lastClose} - PUT BUY Signal, Pattern: {buyPattern}")
                                    model.add_output(
                                        f"{verify_array[i][2]} : {lastClose} - PUT BUY Signal, Pattern: {buyPattern}")
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
                                    k = 2
                                    chance_bingo = 0
                                    chance_bingo_correct = 0
                                    buyAlready = True
                                    for j in range(len(verify_array) - 3 - i):
                                        print(f"{verify_array[k + i][2]} : {verify_array[k + i][5]}")
                                        model.add_output(f"{verify_array[k + i][2]} : {verify_array[k + i][5]}")
                                        defineCandleSticks(k+i)
                                            # price pattern (color > self distance > compare)
                                        if k + i - 3 > 0:
                                            if isLastGreen and isLast2Red and isLast3Red and isLast4Red and \
                                                    lastLargestDistance > last2LargestDistance and lastLargestDistance > last3LargestDistance and lastLargestDistance > last4LargestDistance and \
                                                    lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                                                    last4Close > last3Close and last3Close > last2Close and last2Close > lastOpen and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Bullish Belt Hold"
                                        if k + i - 2 > 0:
                                            if isLastGreen and isLast3Red and \
                                                    lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                                                    last3MiddleDistance > last3UpperDistance + last3LowerDistance and \
                                                    last2MiddleDistance < last2LargestDistance * 0.1 and \
                                                    last2High < last3Open and last2High < lastClose and last2Low < last3Low and last2Low < lastLow and \
                                                    lastClose > last3MiddleDistance / 2 and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Morning doji star"
                                            if isLastGreen and isLast3Red and \
                                                    lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                                                    last3MiddleDistance > last3UpperDistance + last3LowerDistance and \
                                                    last2MiddleDistance < last2LargestDistance * 0.1 and \
                                                    last2High < last3Low and last2High < lastLow and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Bullish abandoned baby"
                                            if isLastGreen and isLast2Green and isLast3Green and \
                                                    lastClose > last2Close and last2Close > last3Close and \
                                                    lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                                                    last3MiddleDistance > last3UpperDistance + last3LowerDistance and \
                                                    last2MiddleDistance < last2LargestDistance + last2LowerDistance and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Three white soldiers"
                                            if isLastRed and isLast2Red and isLast3Red and \
                                                    last2Low > last3Low and last2Close < last3Close and last2Open < last3Open and \
                                                    lastClose < last2Close and lastClose == lastHigh and lastOpen == lastLow and \
                                                    last2MiddleDistance > lastMiddleDistance and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Three star in south"
                                            if isLastRed and isLast2Green and isLast3Green and \
                                                    lastOpen < last2Close and last2Open > last3Close and lastClose > last3Close and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Upside Tasuki gap"
                                        if k + i - 1 > 0:
                                            if isLastGreen and isLast2Red and \
                                                    lastClose > last2MiddleDistance / 2 and \
                                                    lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                                                    last2MiddleDistance > last2UpperDistance + last2LowerDistance and \
                                                    last2Close > lastOpen and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Bullish Piercing"
                                            if isLastGreen and isLast2Green and \
                                                    lastLow > last2High and \
                                                    lastMiddleDistance > lastUpperDistance + lastLowerDistance and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Rising Window"
                                            if isLastGreen and isLast2Red and \
                                                    lastLow == lastOpen and last2Low == last2Close and \
                                                    lastClose > last2Open and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Tweezer Bottom"
                                            if isLastGreen and isLast2Red and \
                                                    lastOpen < last2Open and lastClose > last2Open and \
                                                    lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                                                    last2MiddleDistance > last2UpperDistance + last2LowerDistance and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Bullish kicker"
                                            if isLastRed and isLast2Red and \
                                                    lastLow == lastOpen and last2Low == last2Open and \
                                                    lastClose < last2Close and isSellSignal == False:
                                                isSellSignal = True
                                                sellPattern = "Matching low candlestick"
                                        if lastMiddleDistance < lastLargestDistance * 0.1 and \
                                                (
                                                        lastClose == lastHigh or lastOpen == lastHigh) and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Dragonfly doji"
                                        if float(verify_array[i + k][5]) < float(
                                                verify_array[i + 1][5]):
                                            chance_bingo_correct = chance_bingo_correct + 1
                                        if isSellSignal == True and buyAlready == True:
                                            # print(f"SELL BUY Signal, Pattern: {sellPattern}")
                                            # model.add_output(f"SELL BUY Signal, Pattern: {sellPattern}")
                                            trigger_sell_time = verify_array[i + k][0]
                                            trigger_sell_price = verify_array[i + k][5]
                                            sell_time = verify_array[i + k + 1][0]
                                            sell_price = verify_array[i + k + 1][5]
                                            price_action_earn = (verify_array[i + 1][5] - verify_array[i + k + 1][5]) / \
                                                                verify_array[i + 1][5] * 100
                                            # buyAlready = False
                                        if float(verify_array[i + k][8]) < float(verify_array[i + k][9]) and float(
                                                verify_array[i + k][1]) < float(
                                                verify_array[i + k][9]) and is_sell_ema_10 == 0 and buyAlready == True:
                                            print(f"Sell PUT! (EMA-10 Method)")  # sell method 3
                                            model.add_output(f"Sell PUT! (EMA-10 Method)")
                                            ema_10_time = verify_array[i + k][0]
                                            ema_10_earn = (verify_array[i + 1][5] - verify_array[i + k][5]) / \
                                                          verify_array[i + 1][5] * 100
                                            is_sell_ema_10 = 1
                                            buyAlready = False
                                        if (highest_sell_earn < float(verify_array[i + 1][5]) - float(
                                                verify_array[i + k][5])):
                                            highest_sell_time = verify_array[i + k][0]
                                            highest_sell_earn = (verify_array[i + 1][5] - verify_array[i + k][5]) / \
                                                                verify_array[i + 1][5] * 100
                                        chance_bingo = chance_bingo + 1
                                        k = k + 1
                                    if is_sell_ema_10 == 0:
                                        ema_10_time = verify_array[len(verify_array) - 1][0]
                                        ema_10_earn = (verify_array[i + 1][5] - verify_array[len(verify_array) - 1][
                                            5]) / verify_array[i + 1][5] * 100
                                    print("Decreasing Direction")
                                    print("Total Chance of Trigger Bingo Drop:")
                                    model.add_output("Decreasing Direction")
                                    model.add_output("Total Chance of Trigger Bingo Drop:")
                                    every_trade_chance = 0
                                    if chance_bingo != 0:
                                        every_trade_chance = chance_bingo_correct / chance_bingo
                                    print(every_trade_chance)
                                    model.add_output(every_trade_chance)
                                    total_bingo_chance = total_bingo_chance + chance_bingo_correct
                                    total_chance = total_chance + chance_bingo
                                    row = [verify_array[i][2].split(' ')[0], price_1_high, f"{jumpDistance:.5g}", "PUT",
                                           verify_array[i][0], verify_array[i][5], verify_array[i + 1][0],
                                           verify_array[i + 1][5], buyPattern,
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
    global response_6a
    global response_6b
    global response_6c
    global response_9
    global bt_array

    symbol = input_symbol

    current_date = QDate.currentDate().toString("yyyy-MM-dd")
    current_date_obj = QDate.fromString(current_date, 'yyyy-MM-dd')
    array_month = []
    for i in range(12):
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

    url_sma_daily = f"https://www.alphavantage.co/query?function=SMA&symbol={symbol}&interval=daily&time_period=5&series_type=close&apikey={api_key}&entitlement=delayed"
    response_6a = session.get(url_sma_daily)

    url_sma_daily_10 = f"https://www.alphavantage.co/query?function=SMA&symbol={symbol}&interval=daily&time_period=10&series_type=close&apikey={api_key}&entitlement=delayed"
    response_6b = session.get(url_sma_daily_10)

    url_sma_daily_20 = f"https://www.alphavantage.co/query?function=SMA&symbol={symbol}&interval=daily&time_period=20&series_type=close&apikey={api_key}&entitlement=delayed"
    response_6c = session.get(url_sma_daily_20)

    url_daily = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={api_key}&entitlement=delayed"
    response_9 = session.get(url_daily)

    threads = []
    for month in array_month:
        thread = threading.Thread(target=backtestData, args=(month, model))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    if len(array_overall) != 0:
        file_path = f'data/history/{symbol}.csv'
        header = ['Date', '16:00', 'Jump Distance', 'Type', 'Trigger Buy Time', 'Trigger Buy Price', 'BUY Time',
                  'BUY Price', 'BUY Pattern',
                  'Num of Chance', 'EMA-10 Sell Time', 'EMA-10 Earning(%)', 'Highest Sell Time', 'Highest Earning(%)']
        bt_array = np.vstack([header, array_overall])
        np.savetxt(file_path, bt_array, delimiter=',', fmt='%s')
        print(f"Array exported to {file_path} successfully.")
        model.add_output(f"Array exported to {file_path} successfully.")
    else:
        print(f"No Data Updated.")
        model.add_output(f"No Data Updated.")


def handleData(name_symbol):
    global highest_method
    global average_chance
    global earning_probability
    global chance_half_doji_star
    global chance_HDS
    global chance_TSS
    global chance_UTT
    global chance_FS
    global chance_RDS
    global chance_TWS
    global chance_UTD
    global chance_FK

    historicalData = pd.read_csv(f'{folder_path}/{name_symbol}.csv')
    average_chance = historicalData.iloc[:, 9].mean()
    sum_of_sma = historicalData.iloc[:, 11].sum()
    sum_of_sma_10 = historicalData.iloc[:, 11].sum()
    sum_of_ema = historicalData.iloc[:, 11].sum()
    sum_of_ema_10 = historicalData.iloc[:, 11].sum()
    sum_of_macd = historicalData.iloc[:, 11].sum()
    highest_number = max(sum_of_sma, sum_of_sma_10, sum_of_ema, sum_of_ema_10, sum_of_macd)
    highest_method = ''
    total = len(historicalData)
    if highest_number == sum_of_sma:
        highest_method = 'EMA-10'
        count = len(historicalData[historicalData['EMA-10 Earning(%)'] < 0])
    elif highest_method == sum_of_sma_10:
        highest_variable = 'EMA-10'
        count = len(historicalData[historicalData['EMA-10 Earning(%)'] < 0])
    elif highest_number == sum_of_ema:
        highest_method = 'EMA-10'
        count = len(historicalData[historicalData['EMA-10 Earning(%)'] < 0])
    elif highest_number == sum_of_ema_10:
        highest_method = 'EMA-10'
        count = len(historicalData[historicalData['EMA-10 Earning(%)'] < 0])
    else:
        highest_method = 'EMA-10'
        count = len(historicalData[historicalData['EMA-10 Earning(%)'] < 0])
    earning_probability = count / total
    chances_price_actions = defaultdict(list)
    for i in range(len(historicalData)-1):
        chance = historicalData.iloc[:, 9][i]
        type_val = historicalData.iloc[:, 8][i]
        chances_price_actions[type_val].append(chance)
    average_chances_price_actions = {}
    for type_val, chances in chances_price_actions.items():
        if chances:
            average_chances_price_actions[type_val] = sum(chances) / len(chances)
        else:
            average_chances_price_actions[type_val] = 0
    chance_HDS = average_chances_price_actions.get('Half Doji Star', 0)
    chance_TSS = average_chances_price_actions.get('Three Strong Soldiers', 0)
    chance_UTT = average_chances_price_actions.get('Upfront Tweezer Top', 0)
    chance_FS = average_chances_price_actions.get('First Shot', 0)
    chance_RDS = average_chances_price_actions.get('Reversed Doji Star', 0)
    chance_TWS = average_chances_price_actions.get('Three Weak Soldiers', 0)
    chance_UTD = average_chances_price_actions.get('Upfront Tweezer Down', 0)
    chance_FK = average_chances_price_actions.get('First Kill', 0)

def predictData(symbol, model):
    # for symbol in symbols:
    global overall_csv

    with lock:
        month = QDate.fromString(date, 'yyyy-MM-dd').toString('yyyy-MM')
        url_sma_daily = f"https://www.alphavantage.co/query?function=SMA&symbol={symbol}&interval=daily&time_period=5&series_type=close&apikey={api_key}&entitlement=delayed&month={month}"
        response_6a = session.get(url_sma_daily)
        url_sma_daily_10 = f"https://www.alphavantage.co/query?function=SMA&symbol={symbol}&interval=daily&time_period=10&series_type=close&apikey={api_key}&entitlement=delayed&month={month}"
        response_6b = session.get(url_sma_daily_10)
        url_sma_daily_20 = f"https://www.alphavantage.co/query?function=SMA&symbol={symbol}&interval=daily&time_period=20&series_type=close&apikey={api_key}&entitlement=delayed&month={month}"
        response_6c = session.get(url_sma_daily_20)

        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&outputsize=full&apikey={api_key}&entitlement=delayed&month={month}"
        response = session.get(url)

        url_sma = f"https://www.alphavantage.co/query?function=SMA&symbol={symbol}&interval=1min&time_period=5&series_type=close&apikey={api_key}&entitlement=delayed&month={month}"
        response_2 = session.get(url_sma)

        url_sma_10 = f"https://www.alphavantage.co/query?function=SMA&symbol={symbol}&interval=1min&time_period=10&series_type=close&apikey={api_key}&entitlement=delayed&month={month}"
        response_3 = session.get(url_sma_10)

        url_sma_20 = f"https://www.alphavantage.co/query?function=SMA&symbol={symbol}&interval=1min&time_period=20&series_type=close&apikey={api_key}&entitlement=delayed&month={month}"
        response_4 = session.get(url_sma_20)

        url_daily = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={api_key}&entitlement=delayed&month={month}"
        response_9 = session.get(url_daily)

        if response.status_code == 200 and response_2.status_code == 200:
            data = response.json()
            data_sma = response_2.json()
            data_sma_10 = response_3.json()
            data_sma_20 = response_4.json()
            data_sma_daily = response_6a.json()
            data_sma_daily_10 = response_6b.json()
            data_sma_daily_20 = response_6c.json()
            data_daily = response_9.json()
            time_series = data['Time Series (1min)']
            sma = data_sma['Technical Analysis: SMA']
            sma_10 = data_sma_10['Technical Analysis: SMA']
            sma_20 = data_sma_20['Technical Analysis: SMA']
            sma_daily = data_sma_daily['Technical Analysis: SMA']
            sma_daily_10 = data_sma_daily_10['Technical Analysis: SMA']
            sma_daily_20 = data_sma_daily_20['Technical Analysis: SMA']
            time_series_daily = data_daily['Time Series (Daily)']

            price_1 = 0.0
            price_1_low = 0.0
            price_1_high = 0.0
            time_1 = ""
            array_csv = []
            isSMATrend = False
            isVersionTwo = False
            isVersionNonJump = False

            for timestamp, values in time_series.items():
                if f"{date} 16:00:00" in timestamp:
                    # get data
                    price_1 = float(values['4. close'])
                    price_1_low = float(values['3. low'])
                    price_1_high = float(values['2. high'])
                    time_1 = timestamp
                    sma_values_1 = 0.0
                    for timestamp_sma, values_sma in sma.items():
                        if timestamp_sma in time_1:
                            sma_values_1 = float(values_sma['SMA'])
                        if sma_values_1 != 0.0:
                            break
                    sma_10_values_1 = 0.0
                    for timestamp_sma, values_sma in sma_10.items():
                        if timestamp_sma in time_1:
                            sma_10_values_1 = float(values_sma['SMA'])
                        if sma_10_values_1 != 0.0:
                            break
                    sma_20_values_1 = 0.0
                    for timestamp_sma, values_sma in sma_20.items():
                        if timestamp_sma in time_1:
                            sma_20_values_1 = float(values_sma['SMA'])
                        if sma_20_values_1 != 0.0:
                            break
                    sma_values_daily_yesterstday = 0.0
                    sma_values_daily_previousday = 0.0
                    sma_found_previousday = False
                    for timestamp_sma, values_sma in sma_daily.items():
                        if sma_found_previousday:
                            sma_values_daily_previousday = float(values_sma['SMA'])
                            break
                        if timestamp_sma in time_1:
                            sma_values_daily_yesterstday = float(values_sma['SMA'])
                            sma_found_previousday = True
                    sma_values_daily_10_yesterstday = 0.0
                    sma_values_daily_10_previousday = 0.0
                    sma_10_found_previousday = False
                    for timestamp_sma, values_sma in sma_daily_10.items():
                        if sma_10_found_previousday:
                            sma_values_daily_10_previousday = float(values_sma['SMA'])
                            break
                        if timestamp_sma in time_1:
                            sma_values_daily_10_yesterstday = float(values_sma['SMA'])
                            sma_10_found_previousday = True
                    sma_values_daily_20_yesterstday = 0.0
                    for timestamp_sma, values_sma in sma_daily_20.items():
                        if timestamp_sma in time_1:
                            sma_values_daily_20_yesterstday = float(values_sma['SMA'])
                            break
                    daily_values_open_yestersday = 0.0
                    daily_values_close_yestersday = 0.0
                    for timestamp, values in time_series_daily.items():
                        if timestamp in time_1:
                            daily_values_open_yestersday = float(values['1. open'])
                            daily_values_close_yestersday = float(values['4. close'])
                            break
                    # condition
                    #if daily_values_open_yestersday < daily_values_close_yestersday:
                    if True:
                        yestersdayDistance = (
                                                         daily_values_close_yestersday - daily_values_open_yestersday) / daily_values_close_yestersday
                        if sma_values_daily_previousday < sma_values_daily_yesterstday and sma_values_daily_10_previousday < sma_values_daily_10_yesterstday \
                                and sma_values_1 > price_1_low and sma_10_values_1 > price_1_low and sma_20_values_1 > price_1_low:
                            isVersionTwo = True
                        else:
                            isVersionTwo = False
                        if (
                                daily_values_open_yestersday < daily_values_close_yestersday and daily_values_open_yestersday > sma_values_daily_yesterstday \
                                and daily_values_open_yestersday > sma_values_daily_10_yesterstday and daily_values_open_yestersday > sma_values_daily_20_yesterstday) \
                                or (
                                daily_values_open_yestersday > daily_values_close_yestersday and daily_values_close_yestersday > sma_values_daily_yesterstday \
                                and daily_values_close_yestersday > sma_values_daily_10_yesterstday and daily_values_close_yestersday > sma_values_daily_20_yesterstday):
                            isVersionNonJump = True
                        else:
                            isVersionNonJump = False
                        if True:
                            if sma_20_values_1 > sma_10_values_1 > sma_values_1:
                                isSMATrend = True
                            else:
                                isSMATrend = False
                            if (True):
                                handleData(symbol)
                                print(
                                    f"{symbol} - {time_1} : {price_1_high} and {price_1_low} : Recommended: {highest_method}), Chance: {average_chance} with Earning {earning_probability}")
                                model.add_output(
                                    f"{symbol} - {time_1} : {price_1_high} and {price_1_low} : Recommended: {highest_method}), Chance: {average_chance} with Earning {earning_probability}")
                                row = [symbol, price_1_high, price_1_low, f"{average_chance:.5g}", highest_method,
                                       f"{earning_probability:.5g}",f"{chance_HDS:.5g}",f"{chance_TSS:.5g}",f"{chance_UTT:.5g}",
                                f"{chance_FS:.5g}",f"{chance_RDS:.5g}",f"{chance_TWS:.5g}",f"{chance_UTD:.5g}",f"{chance_FK:.5g}"]
                                array_csv.append(row)
                                print("--------------")
                                model.add_output("--------------")
                    #if daily_values_open_yestersday > daily_values_close_yestersday:
                    if False:
                        yestersdayDistance = (
                                                     daily_values_open_yestersday - daily_values_close_yestersday) / daily_values_open_yestersday
                        if sma_values_daily_previousday > sma_values_daily_yesterstday and sma_values_daily_10_previousday > sma_values_daily_10_yesterstday \
                                and sma_values_1 < price_1_high and sma_10_values_1 < price_1_high and sma_20_values_1 < price_1_high:
                            isVersionTwo = True
                        else:
                            isVersionTwo = False
                        if (
                                daily_values_open_yestersday < daily_values_close_yestersday and daily_values_close_yestersday < sma_values_daily_yesterstday \
                                and daily_values_close_yestersday < sma_values_daily_10_yesterstday and daily_values_close_yestersday < sma_values_daily_20_yesterstday) \
                                or (
                                daily_values_open_yestersday > daily_values_close_yestersday and daily_values_open_yestersday < sma_values_daily_yesterstday \
                                and daily_values_open_yestersday < sma_values_daily_10_yesterstday and daily_values_open_yestersday < sma_values_daily_20_yesterstday):
                            isVersionNonJump = True
                        else:
                            isVersionNonJump = False
                        if True:
                            if sma_20_values_1 < sma_10_values_1 < sma_values_1:
                                isSMATrend = True
                            else:
                                isSMATrend = False
                            if (True):
                                handleData(symbol)
                                print(
                                    f"{symbol} - {time_1} : {price_1_low} : Ready to PUT (Recommended: {highest_method}), Chance: {average_chance} with Earning {earning_probability}")
                                model.add_output(
                                    f"{symbol} - {time_1} : {price_1_low} : Ready to PUT (Recommended: {highest_method}), Chance: {average_chance} with Earning {earning_probability}")
                                row = [symbol, price_1_low, sma_values_1, sma_values_daily_previousday,
                                       sma_values_daily_yesterstday, sma_values_daily_10_previousday,
                                       sma_values_daily_10_yesterstday, "PUT", f"{average_chance:.5g}", highest_method,
                                       f"{earning_probability:.5g}", isSMATrend, yestersdayDistance, isVersionTwo,
                                       isVersionNonJump]
                                array_csv.append(row)
                                print("--------------")
                                model.add_output("--------------")
                    break
            overall_csv = overall_csv + array_csv
        else:
            print(f"Error: {response.status_code} - {response.text}")
            model.add_output(f"Error: {response.status_code} - {response.text}")


def execute_preanalysis(input_date, model):
    global lock
    global symbol
    global overall_csv
    global session
    global pa_array
    global date
    global folder_path

    folder_path = 'data/history'
    symbols = [os.path.splitext(f)[0] for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    date = input_date

    overall_csv = []

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
    for symbol in symbols:
        thread = threading.Thread(target=predictData, args=(symbol, model))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    if len(overall_csv) != 0:
        rearranged_array = sorted(overall_csv, key=lambda x: x[8], reverse=True)
        file_path = f'data/pre-analysis/{date}_afterMarket.csv'
        header = ['Symbol', '16:00 High', '16:00 Low', 'Total Chance', 'Recommended Sell', 'Earning Probability',
                  'CALL-HDS','CALL-TSS','CALL-UTT','CALL-FS','PUT-RDS','PUT-TWS','PUT-UTD','PUT-FK']
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
    global ema_10


    month = QDate.fromString(date_2, 'yyyy-MM-dd').toString('yyyy-MM')

    try:
        pre_data_csv = pd.read_csv(f'data/pre-analysis/{date}_afterMarket.csv')

        pre_datas = pre_data_csv.values

        overall_csv = []

        for pre_data in pre_datas:

            model.add_output(f"Checking condition for {pre_data[0]} ......")

            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={pre_data[0]}&interval=1min&outputsize=full&apikey={api_key}&month={month}&entitlement=delayed"
            response = requests.get(url)

            url_ema_10 = f"https://www.alphavantage.co/query?function=EMA&symbol={pre_data[0]}&month={month}&interval=1min&time_period=10&series_type=close&apikey={api_key}&entitlement=delayed"
            response_5 = requests.get(url_ema_10)

            if response.status_code == 200:
                data = response.json()
                time_series = data['Time Series (1min)']
                data_ema_10 = response_5.json()
                ema_10 = data_ema_10['Technical Analysis: EMA']
                price_1_high = pre_data[1]
                price_1_low = pre_data[2]
                array_csv = []

                verify_array = []
                verify_array_format = 30
                num_of_minute = 30
                for i in range(num_of_minute):
                    row = [f'09:{verify_array_format}:00', 0.0, '', 0.0, 0.0, 0.0, 0.0, 0.0,
                           0.0, 0.0, 0.0, 0.0,
                           0.0]  # time, closed, date, low, SMA-5, high, EMA-5, SMA-10, EMA-10, open, macd, rsi, SMA-20
                    verify_array.append(row)
                    verify_array_format = verify_array_format + 1

                for timestamp, values in time_series.items():
                    if verify_array[0][1] != 0.0 and verify_array[28][1] != 0.0:
                        break
                    for verify in verify_array:
                        if f"{date_2} {verify[0]}" in timestamp:
                            verify[9] = float(values['1. open'])
                            verify[2] = timestamp
                            verify[3] = float(values['3. low'])
                            verify[5] = float(values['2. high'])
                            verify[1] = float(values['4. close'])
                for timestamp_ema, values_ema in ema_10.items():
                    for verify in verify_array:
                        if timestamp_ema in verify[2]:
                            verify[8] = float(values_ema['EMA'])
                for m in range(len(verify_array) - 1):
                    if date_2 not in verify_array[m][2]:
                        verify_array[m][1] = verify_array[m - 1][9]
                        datetime_obj = datetime.strptime(verify_array[m - 1][2], '%Y-%m-%d %H:%M:%S')
                        next_minute = datetime_obj + timedelta(minutes=1)
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
                if verify_array[0][3] > price_1_high:  # condition 1
                    isBuySignal = False
                    buyAlready = False
                    buyPattern = ""
                    for i in range(len(verify_array) - 1):  # start adding buy condition
                        defineCandleSticks(i)
                        callBuyCondition(i)
                        if isBuySignal == True and buyAlready == False and "09:3" in lastTime:
                            if buyPattern == 'Half Doji Star':
                                buy_chance = pre_data[6]
                            elif buyPattern == 'Upfront Tweezer Top':
                                buy_chance = pre_data[8]
                            elif buyPattern == 'Three Strong Soldiers':
                                buy_chance = pre_data[7]
                            elif buyPattern == 'First Shot':
                                buy_chance = pre_data[9]
                            else:
                                buyPattern = "Null"
                                buy_chance = 0
                            print(
                                f"{verify_array[i][2]} : {lastClose} - Ready to CALL, Pattern: {buyPattern} ({buy_chance}), (Recommended: {pre_data[4]}), Chance: {pre_data[3]} with Earning {pre_data[5]}")
                            model.add_output(
                                f"{verify_array[i][2]} : {lastClose} - Ready to CALL, Pattern: {buyPattern} ({buy_chance}), (Recommended: {pre_data[4]}), Chance: {pre_data[3]} with Earning {pre_data[5]}")
                            row = [pre_data[0], price_1_high, verify_array[i][0], lastClose, buyPattern,buy_chance, 'CALL',
                                   pre_data[3],pre_data[4], pre_data[5]]
                            array_csv.append(row)
                            print("--------------")
                            model.add_output("--------------")
                            buyAlready = True
                            break
                if verify_array[0][5] < price_1_low:  # condition 1
                    isBuySignal = False
                    buyAlready = False
                    buyPattern = ""
                    for i in range(len(verify_array) - 1):  # start adding buy condition
                        defineCandleSticks(i)
                        putBuyCondition(i)
                        if isBuySignal == True and buyAlready == False and "09:3" in lastTime:
                            if buyPattern == 'Reversed Doji Star':
                                buy_chance = pre_data[10]
                            elif buyPattern == 'Upfront Tweezer Down':
                                buy_chance = pre_data[12]
                            elif buyPattern == 'Three Weak Soldiers':
                                buy_chance = pre_data[11]
                            elif buyPattern == 'First Kill':
                                buy_chance = pre_data[13]
                            else:
                                buyPattern = "Null"
                                buy_chance = 0
                            print(
                                f"{verify_array[i][2]} : {lastClose} - Ready to PUT, Pattern: {buyPattern} ({buy_chance}), (Recommended: {pre_data[4]}), Chance: {pre_data[3]} with Earning {pre_data[5]}")
                            model.add_output(
                                f"{verify_array[i][2]} : {lastClose} - Ready to PUT, Pattern: {buyPattern} ({buy_chance}), (Recommended: {pre_data[4]}), Chance: {pre_data[3]} with Earning {pre_data[5]}")
                            row = [pre_data[0], price_1_low, verify_array[i][0], lastClose, buyPattern, buy_chance,
                                   'PUT',pre_data[3], pre_data[4], pre_data[5]]
                            array_csv.append(row)
                            print("--------------")
                            model.add_output("--------------")
                            buyAlready = True
                            break
                overall_csv = overall_csv + array_csv

            else:
                print(f"Error: {response.status_code} - {response.text}")
                model.add_output(f"Error: {response.status_code} - {response.text}")
    except FileNotFoundError:
        model.add_output(f"The file '{date}_afterMarket.csv' does not exist.")

    if len(overall_csv) != 0:
        rearranged_array = sorted(overall_csv, key=lambda x: x[5], reverse=True)
        file_path = f'data/post-analysis/{date_2}_beforeMarket.csv'
        header = ['Symbol', '16:00', 'Trigger Buy Time', 'Trigger Buy Price','Buy Pattern','Pattern Chance', 'Signal', 'Total Chance', 'Recommended Sell', 'Earning Probability']
        pta_array = np.vstack([header, rearranged_array])
        np.savetxt(file_path, pta_array, delimiter=',', fmt='%s')
        print(f"Array exported to {file_path} successfully.")
        model.add_output(f"Array exported to {file_path} successfully.")
    else:
        print(f"No Data Updated.")
        model.add_output(f"No Data Updated.")


def backtestDailyData(symbol, date, model):
    # for month in array_month:
    global sma
    global sma_10
    global sma_20
    global ema
    global ema_10
    global macd
    global rsi
    global sma_daily
    global sma_daily_10
    global sma_daily_20
    global time_1
    global time_3
    global time_4
    global time_5
    global verify_array
    global array_overall
    global time_series_daily
    global isBuySignal
    global buyPattern

    model.add_output(f"Checking condition for {symbol} ......")

    # Make the API request to retrieve the current price for AAPL in the US market
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&outputsize=full&apikey={api_key}&entitlement=delayed"
    response = session.get(url)

    url_sma = f"https://www.alphavantage.co/query?function=SMA&symbol={symbol}&interval=1min&time_period=5&series_type=close&apikey={api_key}&entitlement=delayed"
    response_2 = session.get(url_sma)

    url_sma_10 = f"https://www.alphavantage.co/query?function=SMA&symbol={symbol}&interval=1min&time_period=10&series_type=close&apikey={api_key}&entitlement=delayed"
    response_3 = session.get(url_sma_10)

    url_ema = f"https://www.alphavantage.co/query?function=EMA&symbol={symbol}&interval=1min&time_period=5&series_type=close&apikey={api_key}&entitlement=delayed"
    response_4 = session.get(url_ema)

    url_ema_10 = f"https://www.alphavantage.co/query?function=EMA&symbol={symbol}&interval=1min&time_period=10&series_type=close&apikey={api_key}&entitlement=delayed"
    response_5 = session.get(url_ema_10)

    url_sma_20 = f"https://www.alphavantage.co/query?function=SMA&symbol={symbol}&interval=1min&time_period=20&series_type=close&apikey={api_key}"
    response_3a = session.get(url_sma_20)

    url_macd = f"https://www.alphavantage.co/query?function=MACD&symbol={symbol}&interval=1min&series_type=close&apikey={api_key}&entitlement=delayed"
    response_7 = session.get(url_macd)

    url_rsi = f"https://www.alphavantage.co/query?function=RSI&symbol={symbol}&interval=1min&time_period=10&series_type=close&apikey={api_key}&&entitlement=delayed"
    response_8 = session.get(url_rsi)

    if response.status_code == 200 and response_2.status_code == 200:
        data = response.json()
        data_sma = response_2.json()
        data_sma_10 = response_3.json()
        data_sma_20 = response_3a.json()
        data_ema = response_4.json()
        data_ema_10 = response_5.json()
        data_sma_daily = response_6a.json()
        data_sma_daily_10 = response_6b.json()
        data_sma_daily_20 = response_6c.json()
        data_macd = response_7.json()
        data_rsi = response_8.json()
        data_daily = response_9.json()
        time_series = data['Time Series (1min)']
        sma = data_sma['Technical Analysis: SMA']
        sma_10 = data_sma_10['Technical Analysis: SMA']
        sma_20 = data_sma_20['Technical Analysis: SMA']
        ema = data_ema['Technical Analysis: EMA']
        ema_10 = data_ema_10['Technical Analysis: EMA']
        sma_daily = data_sma_daily['Technical Analysis: SMA']
        sma_daily_10 = data_sma_daily_10['Technical Analysis: SMA']
        sma_daily_20 = data_sma_daily_20['Technical Analysis: SMA']
        macd = data_macd['Technical Analysis: MACD']
        rsi = data_rsi['Technical Analysis: RSI']
        time_series_daily = data_daily['Time Series (Daily)']

        price_1 = 0.0
        price_1_low = 0.0
        price_1_high = 0.0
        is3DailySMATrend = False
        isVersionTwo = False
        time_1 = ""
        verify_array = []
        verify_array_format = 30
        num_of_minute = 30
        for i in range(num_of_minute):
            row = [f'09:{verify_array_format}:00', 0.0, '', 0.0, 0.0, 0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0,
                   0.0]  # time, closed, date, low, SMA-5, high, EMA-5, SMA-10, EMA-10, open, macd, rsi, SMA-20
            verify_array.append(row)
            verify_array_format = verify_array_format + 1
        total_chance = 0
        total_bingo_chance = 0
        array_csv = []

        for timestamp, values in time_series.items():
            if "16:00:00" in timestamp:
                # print(f"{timestamp} : {values['4. close']}")
                price_1 = float(values['4. close'])
                price_1_low = float(values['3. low'])
                price_1_high = float(values['2. high'])
                time_1 = timestamp
                if verify_array[28][1] != 0.0 and price_1 != 0.0:
                    initializeIndicator()
                    if verify_array[0][3] > price_1_high:  # condition 1
                        # if False:
                        jumpDistance = (verify_array[0][3] - price_1_high) / verify_array[0][3]
                        isBuySignal = False
                        isSellSignal = False
                        buyAlready = False
                        buyPattern = ""
                        sellPattern = ""
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
                                    verify_array[m][6] = verify_array[m - 1][6]
                                    verify_array[m][7] = verify_array[m - 1][7]
                                    verify_array[m][8] = verify_array[m - 1][8]
                                    verify_array[m][12] = verify_array[m - 1][12]

                        for i in range(len(verify_array) - 1):  # start adding buy condition
                            defineCandleSticks(i)
                            callBuyCondition(i)
                            if isBuySignal == True and buyAlready == False and "09:3" in lastTime:
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
                                k = 2
                                chance_bingo = 0
                                chance_bingo_correct = 0
                                buyAlready = True
                                for j in range(len(verify_array) - 3 - i):
                                    print(f"{verify_array[k + i][2]} : {verify_array[k + i][3]}")
                                    model.add_output(f"{verify_array[k + i][2]} : {verify_array[k + i][3]}")
                                    defineCandleSticks(k + i)
                                    # price pattern (color > self distance > compare)
                                    if k + i - 3 > 0:
                                        if isLastRed and isLast2Green and isLast3Green and isLast4Green and \
                                                lastLargestDistance > last2LargestDistance and lastLargestDistance > last3LargestDistance and lastLargestDistance > last4LargestDistance and \
                                                lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                                                last4Close < last3Close and last3Close < last2Close and last2Close < lastOpen and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Bearish belt hold"  # changed
                                    if k + i - 2 > 0:
                                        if isLastRed and isLast2Red and isLast3Green and \
                                                last2MiddleDistance > last3MiddleDistance and \
                                                last2Open > last3Close and last2Close < last3Open and \
                                                lastClose < last2Low and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Three outside down"  # changed
                                        if isLastRed and isLast3Green and \
                                                lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                                                last3MiddleDistance > last3UpperDistance + last3LowerDistance and \
                                                last2MiddleDistance < last2LargestDistance * 0.1 and \
                                                last2High > last3Close and last2High > lastOpen and last2Low > last3Low and last2Low > lastLow and \
                                                lastClose < last3MiddleDistance / 2 and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Evening doji star"  # changed
                                        if isLastRed and isLast3Green and \
                                                lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                                                last3MiddleDistance > last3UpperDistance + last3LowerDistance and \
                                                last2MiddleDistance < last2LargestDistance * 0.1 and \
                                                last2Low > last3High and last2Low > lastHigh and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Bearish abandoned baby"  # chaged
                                        if isLastRed and isLast2Red and isLast3Red and \
                                                lastClose < last2Close and last2Close < last3Close and \
                                                lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                                                last3MiddleDistance > last3UpperDistance + last3LowerDistance and \
                                                last2MiddleDistance < last2LargestDistance + last2LowerDistance and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Three black crows"  # changed
                                        if isLastGreen and isLast2Green and isLast3Green and \
                                                last2Open > last3Open and last2Close > last3Close and \
                                                lastClose > last2Close and lastOpen > lastOpen and lastUpperDistance > lastMiddleDistance and \
                                                last2MiddleDistance / 2 > lastMiddleDistance and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Advance block"  # changed
                                        if isLastGreen and isLast2Green and isLast3Green and \
                                                last2Open > last3Open and last2Close > last3Close and \
                                                lastClose > last2Close and last2MiddleDistance / 2 > lastMiddleDistance and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Deliberation"  # changed
                                        if isLastGreen and isLast2Red and isLast3Red and \
                                                lastClose > last2Open and last2Open < last3Close and lastClose < last3Close and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Downside tasuki gap"  # changed
                                    if k + i - 1 > 0:
                                        if isLastRed and isLast2Red and \
                                                lastHigh > last2Low and \
                                                lastMiddleDistance > lastUpperDistance + lastLowerDistance and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Falling Window"  # changed
                                        if isLastRed and isLast2Green and \
                                                lastHigh == lastOpen and last2High == last2Close and \
                                                lastClose > last2Open and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Tweezer Top"  # changed
                                        if isLastRed and isLast2Green and \
                                                lastOpen == lastHigh and lastLow == lastClose and \
                                                last2Open == lastLow and last2Close == lastHigh and \
                                                lastHigh < last2Low and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Bear Kicking"  # changed
                                        if isLastGreen and isLast2Red and \
                                                lastMiddleDistance < last2MiddleDistance and \
                                                last2Close > lastHigh and lastLow > last2Low and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "On neck candlestick"  # changed
                                        if isLastGreen and isLast2Green and \
                                                lastHigh == lastClose and last2High == last2Close and \
                                                lastOpen > last2Open and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Matching high"  # changed
                                        if isLastRed and isLast2Green and \
                                                lastClose < last2MiddleDistance / 2 and \
                                                lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                                                last2MiddleDistance > last2UpperDistance + last2LowerDistance and \
                                                last2Close < lastOpen and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Bearish Piercing"  # changed
                                    if float(verify_array[i + k][3]) > float(
                                            verify_array[i + 1][3]):
                                        chance_bingo_correct = chance_bingo_correct + 1
                                    if isSellSignal == True and buyAlready == True:
                                        # print(f"SELL BUY Signal, Pattern: {sellPattern}")
                                        # model.add_output(f"SELL BUY Signal, Pattern: {sellPattern}")
                                        trigger_sell_time = verify_array[i + k][0]
                                        trigger_sell_price = verify_array[i + k][3]
                                        sell_time = verify_array[i + k + 1][0]
                                        sell_price = verify_array[i + k + 1][3]
                                        price_action_earn = (verify_array[i + k + 1][3] - verify_array[i + 1][3]) / \
                                                            verify_array[i + k + 1][3] * 100
                                        # buyAlready = False
                                    if float(verify_array[i + k][7]) > float(verify_array[i + k][9]) and float(
                                            verify_array[i + k][1]) > float(
                                        verify_array[i + k][9]) and is_sell_ema_10 == 0 and buyAlready == True:
                                        print(f"Sell CALL! (EMA-10 Method)")  # sell method 3
                                        model.add_output(f"Sell CALL! (EMA-10 Method)")
                                        ema_10_time = verify_array[i + k][0]
                                        ema_10_earn = (verify_array[i + k][3] - verify_array[i + 1][3]) / \
                                                      verify_array[i + k][3] * 100
                                        is_sell_ema_10 = 1
                                        buyAlready = False
                                    if (highest_sell_earn < float(verify_array[i + k][3]) - float(
                                            verify_array[i + 1][3])):
                                        highest_sell_time = verify_array[i + k][0]
                                        highest_sell_earn = (verify_array[i + k][3] - verify_array[i + 1][3]) / \
                                                            verify_array[i + k][3] * 100
                                    chance_bingo = chance_bingo + 1
                                    k = k + 1
                                if is_sell_ema_10 == 0:
                                    ema_10_time = verify_array[len(verify_array) - 1][0]
                                    ema_10_earn = (verify_array[len(verify_array) - 1][3] - verify_array[i + 1][
                                        3]) / verify_array[len(verify_array) - 1][3] * 100
                                print("Increasing Direction")
                                print("Total Chance of Trigger Bingo Rise:")
                                model.add_output("Increasing Direction")
                                model.add_output("Total Chance of Trigger Bingo Rise:")
                                if chance_bingo != 0:
                                    every_trade_chance = chance_bingo_correct / chance_bingo
                                else:
                                    every_trade_chance = 0
                                print(every_trade_chance)
                                model.add_output(every_trade_chance)
                                total_bingo_chance = total_bingo_chance + chance_bingo_correct
                                total_chance = total_chance + chance_bingo
                                row = [verify_array[i][2].split(' ')[0], price_1_low, f"{jumpDistance:.5g}", "CALL",
                                       verify_array[i][0], verify_array[i][3], verify_array[i + 1][0],
                                       verify_array[i + 1][3], buyPattern,
                                       f"{every_trade_chance:.5g}", ema_10_time,
                                       f"{ema_10_earn:.5g}", highest_sell_time,
                                       f"{highest_sell_earn:.5g}"]
                                array_csv.append(row)
                                print("--------------")
                                model.add_output("--------------")
                                break
                    if verify_array[0][5] < price_1_low:  # condition 1
                        # if False:
                        jumpDistance = (verify_array[0][5] - price_1_low) / verify_array[0][5]
                        isBuySignal = False
                        buyAlready = False
                        buyPattern = ""
                        isSellSignal = False
                        sellPattern = ""
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
                                    verify_array[m][6] = verify_array[m - 1][6]
                                    verify_array[m][7] = verify_array[m - 1][7]
                                    verify_array[m][8] = verify_array[m - 1][8]
                                    verify_array[m][12] = verify_array[m - 1][12]
                        for i in range(len(verify_array) - 1):  # start adding buy condition
                            defineCandleSticks(i)
                            putBuyCondition(i)
                            if isBuySignal == True and (float(verify_array[i][7]) >= lastClose or float(
                                    verify_array[i][7]) >= lastOpen) and buyAlready == False and "09:3" in \
                                    verify_array[i][0]:
                                print(f"{time_1} : {price_1_high}")
                                print(f"{verify_array[i][2]} : {lastClose} - PUT BUY Signal, Pattern: {buyPattern}")
                                model.add_output(
                                    f"{verify_array[i][2]} : {lastClose} - PUT BUY Signal, Pattern: {buyPattern}")
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
                                k = 2
                                chance_bingo = 0
                                chance_bingo_correct = 0
                                buyAlready = True
                                for j in range(len(verify_array) - 3 - i):
                                    print(f"{verify_array[k + i][2]} : {verify_array[k + i][5]}")
                                    model.add_output(f"{verify_array[k + i][2]} : {verify_array[k + i][5]}")
                                    defineCandleSticks(k + i)
                                    # price pattern (color > self distance > compare)
                                    if k + i - 3 > 0:
                                        if isLastGreen and isLast2Red and isLast3Red and isLast4Red and \
                                                lastLargestDistance > last2LargestDistance and lastLargestDistance > last3LargestDistance and lastLargestDistance > last4LargestDistance and \
                                                lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                                                last4Close > last3Close and last3Close > last2Close and last2Close > lastOpen and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Bullish Belt Hold"
                                    if k + i - 2 > 0:
                                        if isLastGreen and isLast3Red and \
                                                lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                                                last3MiddleDistance > last3UpperDistance + last3LowerDistance and \
                                                last2MiddleDistance < last2LargestDistance * 0.1 and \
                                                last2High < last3Open and last2High < lastClose and last2Low < last3Low and last2Low < lastLow and \
                                                lastClose > last3MiddleDistance / 2 and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Morning doji star"
                                        if isLastGreen and isLast3Red and \
                                                lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                                                last3MiddleDistance > last3UpperDistance + last3LowerDistance and \
                                                last2MiddleDistance < last2LargestDistance * 0.1 and \
                                                last2High < last3Low and last2High < lastLow and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Bullish abandoned baby"
                                        if isLastGreen and isLast2Green and isLast3Green and \
                                                lastClose > last2Close and last2Close > last3Close and \
                                                lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                                                last3MiddleDistance > last3UpperDistance + last3LowerDistance and \
                                                last2MiddleDistance < last2LargestDistance + last2LowerDistance and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Three white soldiers"
                                        if isLastRed and isLast2Red and isLast3Red and \
                                                last2Low > last3Low and last2Close < last3Close and last2Open < last3Open and \
                                                lastClose < last2Close and lastClose == lastHigh and lastOpen == lastLow and \
                                                last2MiddleDistance > lastMiddleDistance and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Three star in south"
                                        if isLastRed and isLast2Green and isLast3Green and \
                                                lastOpen < last2Close and last2Open > last3Close and lastClose > last3Close and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Upside Tasuki gap"
                                    if k + i - 1 > 0:
                                        if isLastGreen and isLast2Red and \
                                                lastClose > last2MiddleDistance / 2 and \
                                                lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                                                last2MiddleDistance > last2UpperDistance + last2LowerDistance and \
                                                last2Close > lastOpen and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Bullish Piercing"
                                        if isLastGreen and isLast2Green and \
                                                lastLow > last2High and \
                                                lastMiddleDistance > lastUpperDistance + lastLowerDistance and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Rising Window"
                                        if isLastGreen and isLast2Red and \
                                                lastLow == lastOpen and last2Low == last2Close and \
                                                lastClose > last2Open and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Tweezer Bottom"
                                        if isLastGreen and isLast2Red and \
                                                lastOpen < last2Open and lastClose > last2Open and \
                                                lastMiddleDistance > lastUpperDistance + lastLowerDistance and \
                                                last2MiddleDistance > last2UpperDistance + last2LowerDistance and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Bullish kicker"
                                        if isLastRed and isLast2Red and \
                                                lastLow == lastOpen and last2Low == last2Open and \
                                                lastClose < last2Close and isSellSignal == False:
                                            isSellSignal = True
                                            sellPattern = "Matching low candlestick"
                                    if lastMiddleDistance < lastLargestDistance * 0.1 and \
                                            (
                                                    lastClose == lastHigh or lastOpen == lastHigh) and isSellSignal == False:
                                        isSellSignal = True
                                        sellPattern = "Dragonfly doji"
                                    if float(verify_array[i + k][5]) < float(
                                            verify_array[i + 1][5]):
                                        chance_bingo_correct = chance_bingo_correct + 1
                                    if isSellSignal == True and buyAlready == True:
                                        # print(f"SELL BUY Signal, Pattern: {sellPattern}")
                                        # model.add_output(f"SELL BUY Signal, Pattern: {sellPattern}")
                                        trigger_sell_time = verify_array[i + k][0]
                                        trigger_sell_price = verify_array[i + k][5]
                                        sell_time = verify_array[i + k + 1][0]
                                        sell_price = verify_array[i + k + 1][5]
                                        price_action_earn = (verify_array[i + 1][5] - verify_array[i + k + 1][5]) / \
                                                            verify_array[i + 1][5] * 100
                                        # buyAlready = False
                                    if float(verify_array[i + k][8]) < float(verify_array[i + k][9]) and float(
                                            verify_array[i + k][1]) < float(
                                        verify_array[i + k][9]) and is_sell_ema_10 == 0 and buyAlready == True:
                                        print(f"Sell PUT! (EMA-10 Method)")  # sell method 3
                                        model.add_output(f"Sell PUT! (EMA-10 Method)")
                                        ema_10_time = verify_array[i + k][0]
                                        ema_10_earn = (verify_array[i + 1][5] - verify_array[i + k][5]) / \
                                                      verify_array[i + 1][5] * 100
                                        is_sell_ema_10 = 1
                                        buyAlready = False
                                    if (highest_sell_earn < float(verify_array[i + 1][5]) - float(
                                            verify_array[i + k][5])):
                                        highest_sell_time = verify_array[i + k][0]
                                        highest_sell_earn = (verify_array[i + 1][5] - verify_array[i + k][5]) / \
                                                            verify_array[i + 1][5] * 100
                                    chance_bingo = chance_bingo + 1
                                    k = k + 1
                                if is_sell_ema_10 == 0:
                                    ema_10_time = verify_array[len(verify_array) - 1][0]
                                    ema_10_earn = (verify_array[i + 1][5] - verify_array[len(verify_array) - 1][
                                        5]) / verify_array[i + 1][5] * 100
                                print("Decreasing Direction")
                                print("Total Chance of Trigger Bingo Drop:")
                                model.add_output("Decreasing Direction")
                                model.add_output("Total Chance of Trigger Bingo Drop:")
                                every_trade_chance = 0
                                if chance_bingo != 0:
                                    every_trade_chance = chance_bingo_correct / chance_bingo
                                print(every_trade_chance)
                                model.add_output(every_trade_chance)
                                total_bingo_chance = total_bingo_chance + chance_bingo_correct
                                total_chance = total_chance + chance_bingo
                                row = [verify_array[i][2].split(' ')[0], price_1_high, f"{jumpDistance:.5g}", "PUT",
                                       verify_array[i][0], verify_array[i][5], verify_array[i + 1][0],
                                       verify_array[i + 1][5], buyPattern,
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
    global response_6a
    global response_6b
    global response_6c
    global response_9
    global ud_array

    date = input_date

    try:
        pre_data_csv = pd.read_csv(f'data/post-analysis/{date}_beforeMarket.csv')
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

            url_sma_daily = f"https://www.alphavantage.co/query?function=SMA&symbol={symbol}&interval=daily&time_period=5&series_type=close&apikey={api_key}&entitlement=delayed"
            response_6a = session.get(url_sma_daily)

            url_sma_daily_10 = f"https://www.alphavantage.co/query?function=SMA&symbol={symbol}&interval=daily&time_period=10&series_type=close&apikey={api_key}&entitlement=delayed"
            response_6b = session.get(url_sma_daily_10)

            url_sma_daily_20 = f"https://www.alphavantage.co/query?function=SMA&symbol={symbol}&interval=daily&time_period=20&series_type=close&apikey={api_key}&entitlement=delayed"
            response_6c = session.get(url_sma_daily_20)

            url_daily = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={api_key}&entitlement=delayed"
            response_9 = session.get(url_daily)

            backtestDailyData(symbol, date, model)

            file_path = f'data/history/{symbol}.csv'
            # header = ['Date','16:00','09:30','09:31', 'Num of Chance','SMA-5 Sell Time','SMA-5 Earning(%)','SMA-10 Sell Time','SMA-10 Earning(%)','EMA-5 Sell Time','EMA-5 Earning(%)','EMA-10 Sell Time','EMA-10 Earning(%)', 'Best Sell Method', 'Best Sell Time', 'Max Earning(%)', 'Earliest Sell Method', 'Earliest Sell Time', 'Min Earning(%)', 'Highest Sell Time', 'Highest Earning(%)']
            # np_array = np.vstack([header,array_overall])
            if len(array_overall) != 0:
                ud_array = np.array(array_overall)

                with open(file_path, mode='a', newline='') as file:
                    csv_writer = csv.writer(file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                    for row in ud_array:
                        csv_writer.writerow(row.astype(str))

                # np.savetxt(file_path, np_array, delimiter=',', fmt='%s')
                print(f"Array exported to {file_path} successfully.")
                model.add_output(f"Array exported to {file_path} successfully.")
            else:
                print(f"No Data Updated.")
                model.add_output(f"No Data Updated.")
    except FileNotFoundError:
        model.add_output(f"The file '{date}_beforeMarket.csv' does not exist.")


def monitorAV(symbol, date, model):
    global overall_csv
    global np_array

    try:
        pre_data_csv = pd.read_csv(f'data/post-analysis/{date}_beforeMarket.csv')

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


def executeFUTU(symbol, model):
    global isBuySignal
    global buyPattern

    mask = pre_data_csv.iloc[:, 0] == symbol
    sleep_time = random.uniform(0.1,0.2)

    pre_data = pre_data_csv[mask].values.tolist()

    if len(pre_data) != 0:

        pre_data = pre_data[0]

        ret_sub, err_message = quote_ctx.subscribe([f'US.{pre_data[0]}'], [SubType.K_1M], subscribe_push=False)

        if ret_sub == RET_OK:

            is_time = True

            while (is_time):

                ret, data = quote_ctx.get_cur_kline(f'US.{pre_data[0]}', 29, SubType.K_1M, AuType.QFQ)
                # assume data=[[09:31:00,400],[09:32:00,500]]
                if ret == RET_OK:
            
                    price_1_high = pre_data[1]  # 16:00
                    price_1_low = pre_data[2]
                    isBuySignal = False
                    buyPattern = ""
                    buyAlready = False
                    limitedTime = "09:3"

                    if "09:31:00" in data['time_key'][len(data) - 2]:
                    # if True: #testing
                        price_4_high = data['high'][len(data) - 2]
                        price_4_low = data['low'][len(data) - 2]
                        if price_4_low > price_1_high:
                        #if data['low'][len(data) - 2] > data['low'][len(data) - 3]: #testing
                            print(f"{symbol}: Ready to CALL... Please Wait the buy signal...")
                            while buyAlready == False:
                                if ret == RET_OK:
                                    isBuySignal = False
                                    buyPattern = "Null"
                                    buy_chance = 0
                                    defineCandleSticksFUTU(data)
                                    callBuyConditionFUTU(data)
                                    if isBuySignal == True and limitedTime in lastTime:
                                        if buyPattern == 'Half Doji Star':
                                            buy_chance = pre_data[6]
                                        elif buyPattern == 'Upfront Tweezer Top':
                                            buy_chance = pre_data[8]
                                        elif buyPattern == 'Three Strong Soldiers':
                                            buy_chance = pre_data[7]
                                        elif buyPattern == 'First Shot':
                                            buy_chance = pre_data[9]
                                        else:
                                             buyPattern = "Null"
                                             buy_chance = 0
                                        print(f"{symbol} - {data['time_key'][len(data) - 2]} : {lastClose} - CALL!, Pattern: {buyPattern} ({buy_chance}), (Recommended: {pre_data[4]}), Chance: {pre_data[3]} with Earning {pre_data[5]}")
                                        futu_instant_buy.put(f"{symbol} - {data['time_key'][len(data) - 2]} : {lastClose} - CALL!, Pattern: {buyPattern} ({buy_chance}), (Recommended: {pre_data[4]}), Chance: {pre_data[3]} with Earning {pre_data[5]}")
                                        row = [pre_data[0], price_1_high, lastTime, lastClose, buyPattern,
                                               buy_chance, 'CALL',
                                               pre_data[3], pre_data[4], pre_data[5]]
                                        overall_csv.append(row)
                                        telegram_instant_array.append(row)
                                        buyAlready = True
                                        break
                                    elif isBuySignal == False and limitedTime in lastTime:
                                        print(f"{symbol} - Waiting data of next minutes...")
                                        time.sleep(60+sleep_time)
                                        ret, data = quote_ctx.get_cur_kline(f'US.{pre_data[0]}', 29, SubType.K_1M,AuType.QFQ)
                                    else:
                                        print(
                                            f"{symbol} - {data['time_key'][len(data) - 3]} - {data['time_key'][len(data) - 2]} : doesn't meet requirement. (Expired Time)'")
                                        model.add_output(
                                            f"{symbol} - {data['time_key'][len(data) - 3]} - {data['time_key'][len(data) - 2]} : doesn't meet requirement. (Expired Time)'")
                                        buyAlready = True
                                        break
                                    print("--------------")
                                    #model.add_output("--------------")
                        elif price_4_high < price_1_low:
                        #elif data['high'][len(data) - 2] < data['high'][len(data) - 3]: #testing
                            print(f"{symbol}: Ready to PUT... Please Wait the buy signal...")
                            while buyAlready == False:
                                if ret == RET_OK:
                                    isBuySignal = False
                                    buyPattern = "Null"
                                    buy_chance = 0
                                    defineCandleSticksFUTU(data)
                                    putBuyConditionFUTU(data)
                                    if isBuySignal == True and buyAlready == False and limitedTime in lastTime:
                                        if buyPattern == 'Reversed Doji Star':
                                            buy_chance = pre_data[10]
                                        elif buyPattern == 'Upfront Tweezer Down':
                                            buy_chance = pre_data[12]
                                        elif buyPattern == 'Three Weak Soldiers':
                                            buy_chance = pre_data[11]
                                        elif buyPattern == 'First Kill':
                                            buy_chance = pre_data[13]
                                        else:
                                             buyPattern = "Null"
                                             buy_chance = 0
                                        print(
                                            f"{symbol} - {data['time_key'][len(data) - 2]} : {lastClose} - PUT!, Pattern: {buyPattern} ({buy_chance}), (Recommended: {pre_data[4]}), Chance: {pre_data[3]} with Earning {pre_data[5]}")
                                        futu_instant_buy.put(
                                            f"{symbol} - {data['time_key'][len(data) - 2]} : {lastClose} - PUT!, Pattern: {buyPattern} ({buy_chance}), (Recommended: {pre_data[4]}), Chance: {pre_data[3]} with Earning {pre_data[5]}")
                                        row = [pre_data[0], price_1_high, lastTime, lastClose, buyPattern,
                                               buy_chance, 'PUT',
                                               pre_data[3], pre_data[4], pre_data[5]]
                                        overall_csv.append(row)
                                        telegram_instant_array.append(row)
                                        buyAlready = True
                                        break
                                    elif isBuySignal == False and limitedTime in lastTime:
                                        print(f"{symbol} - Waiting data of next minutes...")
                                        time.sleep(60+sleep_time)
                                        ret, data = quote_ctx.get_cur_kline(f'US.{pre_data[0]}', 29, SubType.K_1M, AuType.QFQ)
                                    else:
                                        print(
                                            f"{symbol} - {data['time_key'][len(data) - 3]} - {data['time_key'][len(data) - 2]} : doesn't meet requirement. (Expired Time)'")
                                        model.add_output(
                                            f"{symbol} - {data['time_key'][len(data) - 3]} - {data['time_key'][len(data) - 2]} : doesn't meet requirement. (Expired Time)'")
                                        buyAlready = True
                                        break
                        else:
                            print(
                                f"{symbol} - {data['time_key'][len(data) - 2]} : doesn't meet requirement. (No Jump)'")
                            futu_instant_buy.put(
                                f"{symbol} - {data['time_key'][len(data) - 2]} : doesn't meet requirement. (No Jump)'")
                            break

                        is_time = False

                    else:
                        print(f"Time {data['time_key'][len(data) - 1]} is not ready.")
                        #model.add_output(f"The Time - {data['time_key'][len(data) - 1]} is not ready.")
                        time.sleep(2+sleep_time)

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

    overall_csv = []
    input_date = datetime.strptime(date, "%Y-%m-%d")
    us_calendar = mcal.get_calendar('NYSE')
    previous_trading_day = input_date - timedelta(days=1)
    while len(us_calendar.valid_days(start_date=previous_trading_day, end_date=previous_trading_day)) <= 0:
        previous_trading_day -= timedelta(days=1)
    yesterday_date = previous_trading_day.strftime('%Y-%m-%d')
    try:
        pre_data_csv = pd.read_csv(f'data/pre-analysis/{yesterday_date}_afterMarket.csv')
        symbols = []

        pre_datas = pre_data_csv.values
        for pre_data in pre_datas:
            if pre_data[3] > 0.5:
                symbols.append(pre_data[0])

        threads = []
        for symbol in symbols:
            thread = threading.Thread(target=executeFUTU, args=(symbol, model))
            thread.start()
            threads.append(thread)
            time.sleep(0.05)
        while any(thread.is_alive() for thread in threads) or not futu_instant_buy.empty():
            try:
                result = futu_instant_buy.get(timeout=1)
                model.add_output(result)
            except queue.Empty:
                pass
        for thread in threads:
            thread.join()


        if len(overall_csv) != 0:
            rearranged_array = sorted(overall_csv, key=lambda x: x[5], reverse=True)
            file_path = f'data/post-analysis(futu)/{date}_beforeMarket.csv'
            header = ['Symbol', '16:00', 'Trigger Buy Time', 'Trigger Buy Price','Buy Pattern','Pattern Chance', 'Signal', 'Total Chance', 'Recommended Sell', 'Earning Probability']
            futu_array = np.vstack([header, rearranged_array])
            np.savetxt(file_path, futu_array, delimiter=',', fmt='%s')
            print(f"Array exported to {file_path} successfully.")
            model.add_output(f"Array exported to {file_path} successfully.")
        else:
            print(f"No Data Updated.")
            model.add_output(f"No Data Updated.")
    except FileNotFoundError:
        model.add_output(f"The file '{date}_afterMarket.csv' does not exist.")


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

        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&outputsize=full&apikey={api_key}&month={month_format}&entitlement=delayed"
        response = requests.get(url)
        url_ema_10 = f"https://www.alphavantage.co/query?function=EMA&symbol={symbol}&month={month_format}&interval=1min&time_period=10&series_type=close&apikey={api_key}&entitlement=delayed"
        response2 = requests.get(url_ema_10)
        url_macd = f"https://www.alphavantage.co/query?function=MACD&symbol={symbol}&interval=1min&series_type=close&apikey={api_key}&month={month_format}&entitlement=delayed"
        response_7 = requests.get(url_macd)
        if response.status_code == 200 and response2.status_code == 200:
            data_temp = response.json()
            time_series = data_temp['Time Series (1min)']
            data_ema = response2.json()
            ema_series = data_ema['Technical Analysis: EMA']
            data_macd = response_7.json()
            macd = data_macd['Technical Analysis: MACD']
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
                row = [f'09:{verify_array_format}:00', 0.0, '', 0.0, 0.0, 0.0, 0.0, 0.0,
                       0.0, 0.0, 0.0]  # time, closed, date, low, SMA-5, high, EMA-5, SMA-10, EMA-10, open,MACD
                verify_array.append(row)
                verify_array_format = verify_array_format + 1
            for timestamp, values in time_series.items():
                if f"{yesterday_date} 16:00:00" in timestamp:
                    price_1 = float(values['4. close'])
                    price_1_low = float(values['3. low'])
                    price_1_high = float(values['2. high'])
                    price_1_open = float(values['1. open'])
                    time_1 = timestamp
                    if price_4 != 0.0 and price_3 != 0.0 and verify_array[26][1] != 0.0 and price_1 != 0.0:
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
                            if ema_values_1 != 0.0 and ema_values_3 != 0.0 and verify_array[26][
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
        dates.pop(0)
        opens.pop(0)
        highs.pop(0)
        lows.pop(0)
        closes.pop(0)
        emas.pop(0)

        # Create a custom candlestick chart using matplotlib
        fig, ax = plt.subplots()

        try:
            history_csv = pd.read_csv(f'data/history/{symbol}.csv')
            history = history_csv.values
            for i in range(len(history)):
                if history[i][0] == selected_date:
                    minutes_part = history[i][6].split(":")[1]
                    buy_time = int(minutes_part) - 30
                    minutes_part_2 = history[i][10].split(":")[1]
                    sell_time = int(minutes_part_2) - 30
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
        ax.set_title(f'{symbol} - {selected_date} Candlestick')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')

        # Convert the diagram to a QPixmap for display
        buffer = BytesIO()
        plt.savefig(f'data/graph/{symbol}_{selected_date}.png')
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

        ret_sub, err_message = quote_ctx.subscribe([f'US.{symbol}'], [SubType.K_1M], subscribe_push=False)

        if ret_sub == RET_OK:

            ret, data = quote_ctx.get_cur_kline(f'US.{symbol}', 30, SubType.K_1M, AuType.QFQ)

            if ret == RET_OK:
                price_series = pd.Series(data['close'])
                ema_10 = price_series.ewm(span=10, adjust=False).mean()

                dates = data['time_key']
                opens = data['open']
                highs = data['high']
                lows = data['low']
                closes = data['close']
                ema_10s = ema_10

        current_time = data['time_key'][29]

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

        ret_sub, err_message = quote_ctx.subscribe([f'US.{symbol}'], [SubType.K_1M], subscribe_push=False)

        if ret_sub == RET_OK:

            ret, data = quote_ctx.get_cur_kline(f'US.{symbol}', 30, SubType.K_1M, AuType.QFQ)

            if ret == RET_OK:

                price_series = pd.Series(data['close'])
                ema = price_series.ewm(span=5, adjust=False).mean()
                ema_10 = price_series.ewm(span=10, adjust=False).mean()

                dates = data['time_key']
                opens = data['open']
                highs = data['high']
                lows = data['low']
                closes = data['close']
                ema_10s = ema_10
                current_time = ''

                df = pd.read_csv(f'data/train/{symbol}.csv')
                npp_array = df.iloc[1:].values
                num_2 = 121
                minute = 59
                start_minute = 3

                num = 0
                pos1600 = 0
                for i in range(27):
                    mining = 30 + start_minute
                    current_time = f"09{mining}"
                    if f"09:{mining}" in data['time_key'][len(data) - 1]:
                        num = 13 + (i * 4)
                        remainingMin = 27 - i
                        pos1600 = 3 + i
                        break
                    start_minute = start_minute + 1

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
                    for i in range(pos1600):  # 0931-0933
                        cols.append(data['open'][len(data) - pos1600 + i])
                        cols.append(data['low'][len(data) - pos1600 + i])
                        cols.append(data['high'][len(data) - pos1600 + i])
                        cols.append(data['close'][len(data) - pos1600 + i])

                    start_minute = 3
                    predicted_data = pd.DataFrame()
                    for i in range(27):
                        mining = 30 + start_minute
                        if f"09:{mining}" in data['time_key'][len(data) - 1]:
                            predicted_data = pd.DataFrame([cols])
                            break
                        start_minute = start_minute + 1

                    # Make a prediction on new data
                    new_data = pd.DataFrame(predicted_data)
                    prediction = model.predict(new_data)
                    print(f"Prediction at 09:{minute}: {prediction}")

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
                    ax.set_title(f'{symbol} - {current_time} Predicted 09:59:00 Candlestick')
                    ax.set_xlabel('Date')
                    ax.set_ylabel('Price')

                    # Convert the diagram to a QPixmap for display
                    buffer = BytesIO()
                    plt.savefig(f'data/predicted_full/{symbol}_{selected_date}.png')
                    plt.savefig(buffer, format='png')
                    buffer.seek(0)
                    pixmap = QPixmap()
                    pixmap.loadFromData(buffer.read())
                    scaled_pixmap = pixmap.scaled(1100, 700)
                    self.label.setPixmap(scaled_pixmap)
                    self.label.setAlignment(Qt.AlignCenter)
                    self.label.setScaledContents(True)

                    file_path = f'data/predicted_full/{symbol}_{selected_date}.csv'
                    np.savetxt(file_path, prediction, delimiter=',', fmt='%s')
                    print(f"Array exported to {file_path} successfully.")
                else:
                    print(f"Time is Not Ready.")


def monitorFUTU(symbol, type, model):
    ret_sub, err_message = quote_ctx.subscribe([f'US.{symbol}'], [SubType.K_1M], subscribe_push=False)

    if ret_sub == RET_OK:

        is_buy = True

        while (is_buy):

            ret, data = quote_ctx.get_cur_kline(f'US.{symbol}', 10, SubType.K_1M, AuType.QFQ)

            if ret == RET_OK:

                # ema_10 = np.convolve(data['close'], np.ones(10) / 10, mode='valid')
                price_series = pd.Series(data['close'])
                ema_10 = price_series.ewm(span=10, adjust=False).mean()

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
                time.sleep(2)
            else:
                print(f"Stock Code Not Found!")
                model.add_output(f"Stock Code Not Found!")


def handleDataList(name_symbol):
    global one_chance
    global zero_chance
    global call_chance
    global put_chance
    global sell_loss_chance
    global highest_chance
    global total_record

    historicalData = pd.read_csv(f'{folder_path}/{name_symbol}.csv')
    total_record = historicalData.shape[0]
    one_chance = historicalData[historicalData.iloc[:, 9] == 1].shape[0] / total_record
    zero_chance = historicalData[historicalData.iloc[:, 9] == 0].shape[0] / total_record
    call_chance = historicalData[historicalData.iloc[:, 3] == "CALL"].shape[0] / total_record
    put_chance = historicalData[historicalData.iloc[:, 3] == "PUT"].shape[0] / total_record
    sell_loss_chance = historicalData[historicalData.iloc[:, 10] == '09:35:00'].shape[0] / total_record
    highest_chance = historicalData[historicalData.iloc[:, 12] == '09:58:00'].shape[0] / total_record


def execute_rankList(input_date, model):
    global symbol
    global rank_csv
    global rank_array
    global date
    global folder_path

    folder_path = 'data/history'
    symbols = [os.path.splitext(f)[0] for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    # symbols = ['AVGO','TSLA','AMZN','INTC','IBM','META']
    # the date after market
    date = input_date

    rank_csv = []

    for symbol in symbols:
        handleData(symbol)
        handleDataList(symbol)
        row = [symbol, f"{average_chance:.5g}", highest_method, f"{earning_probability:.5g}", f"{one_chance:.5g}",
               f"{zero_chance:.5g}", f"{call_chance:.5g}", f"{put_chance:.5g}", f"{sell_loss_chance:.5g}",
               f"{highest_chance:.5g}", f"{total_record:.5g}",
               f"{chance_HDS:.5g}",f"{chance_TSS:.5g}",f"{chance_UTT:.5g}",
                f"{chance_FS:.5g}",f"{chance_RDS:.5g}",f"{chance_TWS:.5g}",f"{chance_UTD:.5g}",f"{chance_FK:.5g}"]
        rank_csv.append(row)

    if len(rank_csv) != 0:
        rearranged_array = sorted(rank_csv, key=lambda x: x[1], reverse=True)
        file_path = f'data/ranking/{date}_list.csv'
        header = ['Symbol', 'Chance', 'Recommended Sell', 'Earning Probability', 'One Chance', 'Zero Chance',
                  'CALL Chance', 'PUT Chance',
                  '09:35 Sell Chance', '09:58 Highest Chance', 'Total Record','HSS','TSS','UTT','FS','RDS','TWS','UTD','FK']
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
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&month={month}&symbol={symbol}&interval=1min&outputsize=full&apikey={api_key}&entitlement=delayed"
        response = session.get(url)

        if response.status_code == 200:
            data = response.json()
            time_series = data['Time Series (1min)']

            verify_array = []
            verify_array_format = 30
            num_of_minute = 30
            for i in range(num_of_minute):
                row = [f'09:{verify_array_format}:00', 0.0, '', 0.0, 0.0, 0.0, 0.0, 0.0,
                       0.0, 0.0, 0.0, 0.0, 0.0,
                       0.0]  # time, closed, date, low, SMA-5, high, EMA-5, SMA-10, EMA-10, open, macd, rsi, vol, SMA-20
                verify_array.append(row)
                verify_array_format = verify_array_format + 1
            time_1 = ""
            total_earn = 0
            total_lost = 0
            array_csv = []

            for timestamp, values in time_series.items():
                if "16:00:00" in timestamp:
                    # print(f"{timestamp} : {values['4. close']}")
                    if verify_array[28][2] != '':
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

    status = ['open','low','high','close']
    header_series = []
    for i in range(30):
        minutes = 30 + i
        header_series.append(f"09{minutes}{status[0][0]}")
        header_series.append(f"09{minutes}{status[1][0]}")
        header_series.append(f"09{minutes}{status[2][0]}")
        header_series.append(f"09{minutes}{status[3][0]}")
    if len(array_overall) != 0:
        file_path = f'data/train/{symbol}.csv'
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
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"/start - 開始\n/instant - 即時分析\n/rank - 即日排行\n/prelist - 盤後分析\n/postlist - 盤前核實\n/backtest (stock) - 回測股票\n/plot (stock) (date) - 歷史繪圖\n/real (stock) - 實時繪圖\n/update - 更新數據庫\n/train (stock) - 數據訓練\n/predict (stock)  - 實時預測\n/restart - 重啟程式")


async def instantTG(update, context):
    global telegram_instant_array

    telegram_instant_array = []
    date = QDate.currentDate().toString("yyyy-MM-dd")
    bt_model = OutputListModel()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等...\n 正在準備為你分析{date}的實時數據.")
    instantAnalysisFUTU(date, bt_model)
    for tg_instant in telegram_instant_array:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"{tg_instant[0]}買入觸發!\n請立即{tg_instant[4]}佢老尾!\n現價:{tg_instant[3]}\n勝率:{tg_instant[5]}")
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"現準備為大家提供實時的賣出訊號, Please be ready to the moon!")
    TGthreads = []
    for tg_instant in telegram_instant_array:
        thread = threading.Thread(target=monitorFUTU, args=(tg_instant[0], tg_instant[4], bt_model))
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


def TGprocess_finished(worker):
    worker.quit()
    worker.wait()


async def send_rankList(update, context):
    if context.args:
        date = context.args[0]
    else:
        date = QDate.currentDate().toString("yyyy-MM-dd")
    chat_id = update.message.chat_id
    bt_model = OutputListModel()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等, {date}的排行準備中...")
    execute_rankList(date, bt_model)
    document = open(f'data/ranking/{date}_list.csv', 'rb')
    await context.bot.send_document(chat_id, document)


async def send_preList(update, context):
    if context.args:
        date = context.args[0]
    else:
        date = QDate.currentDate().toString("yyyy-MM-dd")
    chat_id = update.message.chat_id
    bt_model = OutputListModel()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="f請稍等, {date}的盤後結果準備中...")
    execute_preanalysis(date, bt_model)
    document = open(f'data/pre-analysis/{date}_afterMarket.csv', 'rb')
    await context.bot.send_document(chat_id, document)


async def send_postList(update, context):
    if context.args:
        date = QDate.fromString(context.args[0], 'yyyy-MM-dd')
    else:
        date = QDate.currentDate()
    chat_id = update.message.chat_id
    current_date = date.toString("yyyy-MM-dd")
    input_date = datetime.strptime(current_date, "%Y-%m-%d")
    month_format = input_date.strftime("%Y-%m")
    us_calendar = mcal.get_calendar('NYSE')
    previous_trading_day = input_date - timedelta(days=1)
    while len(us_calendar.valid_days(start_date=previous_trading_day, end_date=previous_trading_day)) <= 0:
        previous_trading_day -= timedelta(days=1)
    yesterday_day = previous_trading_day.strftime('%Y-%m-%d')
    yesterday = QDate.fromString(yesterday_day, 'yyyy-MM-dd')
    yDate = yesterday.toString("yyyy-MM-dd")
    bt_model = OutputListModel()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等, {current_date}的盤前核對結果準備中...")
    execute_postanalysis(yDate, current_date, bt_model)
    document = open(f'data/post-analysis/{current_date}_beforeMarket.csv', 'rb')
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
    path_to_image = f'data/graph/{symbol}_{date}.png'
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
    path_to_image = f'data/predicted_full/{symbol}_{date}.png'
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

    if context.args:
        date = context.args[0]
    else:
        date = QDate.currentDate().toString("yyyy-MM-dd")
    chat_id = update.message.chat_id
    bt_model = OutputListModel()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請稍等, 準備更新{date}的數據庫...")
    updateData(date, bt_model)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="更新已完成.\n注:請勿一天執行多過一次.")



async def send_backtestList(update, context):
    if context.args:
        symbol = context.args[0]
        chat_id = update.message.chat_id
        bt_model = OutputListModel()
        if symbol == "all":
            folder_path = 'data/history'
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
            document = open(f'data/history/{symbol}.csv', 'rb')
            await context.bot.send_document(chat_id, document)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"請輸入股票代碼.")


async def send_trainData(update, context):
    if context.args:
        symbol = context.args[0]
        chat_id = update.message.chat_id
        bt_model = OutputListModel()
        if symbol == "all":
            folder_path = 'data/history'
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
            document = open(f'data/train/{symbol}.csv', 'rb')
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

    application = ApplicationBuilder().token('6983883431:AAGIgipy7Dl8SMulsXMh01VvaH89JZcJUX0').build()

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
    application.add_handler(CommandHandler("real", send_futu))
    application.add_handler(CommandHandler("train", send_trainData))
    application.add_handler(CommandHandler("predict", send_prediction_graph))

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
            time.sleep(2)
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
                                                time.sleep(2)
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
        if 0 <= row < len(self.data) and 0 <= col < len(self.header):
            return self.data[row][0]
        return None


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
        elif self.tab == "analysisFUTU":
            self.generate_futulist(self.bt_model, self.table_view, self.text)
        elif self.tab == "monitorFUTU":
            self.monitor_dataFUTU(self.bt_model, self.text, self.text_2)
        elif self.tab == "rankingList":
            self.generate_rankList(self.bt_model, self.table_view, self.text)
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
            time.sleep(refresh_seconds)
        self.finished.emit()

    def conduct_predictionFull(self, bt_model, diagram, text, text2):
        refresh_secondss = 18
        for i in range(180):
            diagram.predict_full_diagram(None, text, text2)
            bt_model.add_output(f"Refresh Predicted Full Graphs... {i} (Every {refresh_secondss} seconds)")
            time.sleep(refresh_secondss)
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
        self.setWindowTitle("Neverland v4.4 Beta")
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

        # Add tabs to the tab widget
        self.tab_widget.addTab(tab1, "Backtesting")
        self.tab_widget.addTab(tab2, "Pre-Analysis")
        self.tab_widget.addTab(tab3, "Post-Analysis")
        self.tab_widget.addTab(tab4, "Daily Update")
        self.tab_widget.addTab(tab5, "Monitoring (AV)")
        self.tab_widget.addTab(tab6, "Instant Analysis (FUTU)")
        self.tab_widget.addTab(tab7, "Monitoring (FUTU)")
        self.tab_widget.addTab(tab12, "Training")
        self.tab_widget.addTab(tab11, "Prediction")
        self.tab_widget.addTab(tab8, "Trading")
        self.tab_widget.addTab(tab9, "Ranking List")
        self.tab_widget.addTab(tab10, "Configuration")

        # Add content to the tabs
        self.add_content_to_backtesting(tab1)
        self.add_content_to_preanalysis(tab2)
        self.add_content_to_postanalysis(tab3)
        self.add_content_to_updateData(tab4)
        self.add_content_to_monitoringAV(tab5)
        self.add_content_to_analysisFUTU(tab6)
        self.add_content_to_monitoringFUTU(tab7)
        self.add_content_to_trading(tab8)
        self.add_content_to_rankingList(tab9)
        self.add_content_to_configuration(tab10)
        self.add_content_to_prediction(tab11)
        self.add_content_to_training(tab12)

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
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV", "data/history", "CSV Files (*.csv)")
        if file_path:
            self.load_data(file_path, table_view)
            self.selected_symbol = os.path.splitext(os.path.basename(file_path))[0]

    def browse_train(self, table_view):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV", "data/train", "CSV Files (*.csv)")
        if file_path:
            self.load_data(file_path, table_view)
            self.selected_symbol = os.path.splitext(os.path.basename(file_path))[0]

    def browse_preanalysis(self, table_view):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV", "data/pre-analysis", "CSV Files (*.csv)")

        if file_path:
            self.load_data(file_path, table_view)

    def browse_postanalysis(self, table_view):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV", "data/post-analysis", "CSV Files (*.csv)")

        if file_path:
            self.load_data(file_path, table_view)
            self.selected_postDate = os.path.splitext(os.path.basename(file_path))[0][:10]

    def browse_analysisFUTU(self, table_view):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV", "data/post-analysis(futu)", "CSV Files (*.csv)")

        if file_path:
            self.load_data(file_path, table_view)
            self.selected_postDate = os.path.splitext(os.path.basename(file_path))[0][:10]

    def browse_ranklist(self, combo_box, table_view):
        global rank_csv
        global rank_array
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV", "data/ranking", "CSV Files (*.csv)")

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
            ['Symbol', '16:00 High', '16:00 Low', 'Total Chance', 'Recommended Sell', 'Earning Probability',
                  'CALL-HDS','CALL-TSS','CALL-UTT','CALL-FS','PUT-RDS','PUT-TWS','PUT-UTD','PUT-FK'])

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
        button2 = QPushButton("Browse", tab)
        table_view = QTableView(tab)
        table_view.setSelectionBehavior(QTableView.SelectRows)
        delegate = CustomDelegate()
        table_view.setItemDelegate(delegate)
        diagram_widget = DiagramWidget()
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        list_view = QListView(tab)

        H_layout.addWidget(label)
        H_layout.addWidget(input_box_1)
        H_layout.addWidget(input_box_2)
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
        table_model.setHorizontalHeaderLabels(['Symbol', '16:00', 'Trigger Buy Time', 'Trigger Buy Price','Buy Pattern','Pattern Chance', 'Signal', 'Total Chance', 'Recommended Sell', 'Earning Probability'])

        # Set the table model to the table view
        table_view.setModel(table_model)
        table_view.setSortingEnabled(True)

        # Connect the button click event to the add_to_list function
        button.clicked.connect(
            lambda: self.start_postanalysis(button, bt_model, table_view, input_box_1.date().toString("yyyy-MM-dd"),
                                            input_box_2.date().toString("yyyy-MM-dd")))
        button2.clicked.connect(lambda: self.browse_postanalysis(table_view))
        table_view.clicked.connect(lambda: self.show_backtest_plot(table_view.currentIndex(), diagram_widget))
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
        table_model.setHorizontalHeaderLabels(['Symbol', '16:00', 'Trigger Buy Time', 'Trigger Buy Price','Buy Pattern','Pattern Chance', 'Signal', 'Total Chance', 'Recommended Sell', 'Earning Probability'])

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
        diagram_widget.update_diagram(index, self.selected_symbol, self.selected_postDate)

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
                  '09:35 Sell Chance', '09:58 Highest Chance', 'Total Record','HSS','TSS','UTT','FS','RDS','TWS','UTD','FK']

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
        section1 = QGroupBox("BUY Condition")
        section_layout1 = QVBoxLayout()

        H_layout = QHBoxLayout()
        config1 = QLabel("Daily SMA Comparison: ")
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
        config2 = QLabel("Minute SMA Comparison (5/10/20): ")
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
        config3 = QLabel("Minute K Comparison (0930/0931): ")
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
        config4 = QLabel("Minute K Difference with 0.04 (1600/0930): ")
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
        config5 = QLabel("1600 Comparison (Minute K/SMA-5): ")
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

        section2 = QGroupBox("SELL Condition")
        section_layout2 = QVBoxLayout()

        H_layoutb = QHBoxLayout()
        config1b = QLabel("Current Comparison (High/Low): ")
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
        config2b = QLabel("Current Value with EMA-10: ")
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
        config3b = QLabel("Last 3 Values with Same Colours: ")
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
        config4b = QLabel("Last Value with compared to Current Value: ")
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('logo.png'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
