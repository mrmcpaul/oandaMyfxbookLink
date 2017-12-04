from urllib.request import Request, urlopen
import requests
from math import *
import json, oandapy


def myfxbLogin(myfxbookEmail,myfxbookPassword):
    
    response=requests.get('https://www.myfxbook.com/api/login.json?email='+myfxbookEmail+'&password='+myfxbookPassword',verify=False)

    print(response)
    loginResponse=json.loads(response.text)

    mfxbSession = loginResponse['session']
    return mfxbSession

def mfxbComm(mfxbSession):
    outlookUrl = 'http://www.myfxbook.com/api/get-community-outlook.json?session='+mfxbSession

    response = requests.get(outlookUrl,verify=False)
    print(response)
    outlookObj=json.loads(response.text)
    return outlookObj

def leverageTest(oanda,account_id,maxLeverage):
    response=oanda.get_account(account_id)
    marginUsed=response['marginUsed']
    marginRate=response['marginRate']
    balance=response['balance']    
    positionValue=marginUsed/marginRate
    leverage = positionValue / balance
    if leverage>maxLeverage:
        overLeveraged="yes"
        print("Over leveraged")
    else:
        overLeveraged="no"
    return overLeveraged

def calcAveragePrice(instrument,oanda):
    price = oanda.get_prices(instruments=instrument)
    ask = price['prices'][0]['ask']
    bid = price['prices'][0]['bid']
    avPrice = (ask + bid) / 2
    return avPrice

def gbpEquivCalc(instrument,absDiffVol,oanda):
    firstPartInst = instrument[0:3]
    if firstPartInst == "EUR":
        eurGbp = calcAveragePrice("EUR_GBP",oanda)
        gbpEquiv = 100000 * absDiffVol * eurGbp
    elif firstPartInst == "GBP":
        gbpEquiv = 100000 * absDiffVol
    elif firstPartInst == "USD":
        gbpUsd = calcAveragePrice("GBP_USD",oanda)
        gbpEquiv = 100000 * absDiffVol / gbpUsd
    elif firstPartInst == "HKD":
        gbpHkd = calcAveragePrice("GBP_HKD",oanda)
        gbpEquiv = 100000 * absDiffVol / gbpHkd
    elif firstPartInst == "AUD":
        gbpAud = calcAveragePrice("GBP_AUD",oanda)
        gbpEquiv = 100000 * absDiffVol / gbpAud
    elif firstPartInst == "CAD":
        gbpCad = calcAveragePrice("GBP_CAD",oanda)
        gbpEquiv = 100000 * absDiffVol / gbpCad
    elif firstPartInst == "NZD":
        gbpNzd = calcAveragePrice("GBP_NZD",oanda)
        gbpEquiv = 100000 * absDiffVol / gbpNzd
    elif firstPartInst == "CHF":
        gbpChf = calcAveragePrice("GBP_CHF",oanda)
        gbpEquiv = 100000 * absDiffVol / gbpChf
    elif firstPartInst == "ZAR":
        gbpZar = calcAveragePrice("GBP_ZAR",oanda)
        gbpEquiv = 100000 * absDiffVol / gbpZar
    elif firstPartInst == "XAG":
        xagGbp = calcAveragePrice("XAG_GBP",oanda)
        gbpEquiv = 5000 * absDiffVol * xagGbp
    elif firstPartInst == "XAU":
        xauGbp = calcAveragePrice("XAU_GBP",oanda)
        gbpEquiv = 100 * absDiffVol * xauGbp
    elif firstPartInst == "SGD":
        gbpSgd = calcAveragePrice("GBP_SGD",oanda)
        gbpEquiv = 100000 * absDiffVol / gbpSgd
    elif firstPartInst == "XPT":
        xptGbp = calcAveragePrice("XPT_GBP",oanda)
        gbpEquiv = 50 * absDiffVol * xptGbp
    elif firstPartInst == "XPD":
        xpdGbp = calcAveragePrice("XPD_GBP",oanda)
        gbpEquiv = 100 * absDiffVol * xpdGbp
    return gbpEquiv


def sizeCalc(instrument,GBPperTrade,oanda):
    firstPartInst = instrument[0:3]
    if firstPartInst == "EUR":
        eurGbp = calcAveragePrice("EUR_GBP",oanda)
        tradeSize = floor(GBPperTrade/eurGbp)
        print("units "+str(tradeSize))
    elif firstPartInst == "GBP":
        tradeSize = floor(GBPperTrade)
        print("units "+str(tradeSize))
    elif firstPartInst == "USD":
        gbpUsd = calcAveragePrice("GBP_USD",oanda)
        tradeSize = floor(GBPperTrade*gbpUsd)
        print("units "+str(tradeSize))
    elif firstPartInst == "AUD":
        gbpAud = calcAveragePrice("GBP_AUD",oanda)
        tradeSize = floor(GBPperTrade*gbpAud)
        print("units "+str(tradeSize))
    elif firstPartInst == "CAD":
        gbpCad = calcAveragePrice("GBP_CAD",oanda)
        tradeSize = floor(GBPperTrade*gbpCad)
        print("units "+str(tradeSize))
    elif firstPartInst == "NZD":
        gbpNzd = calcAveragePrice("GBP_NZD",oanda)
        tradeSize = floor(GBPperTrade*gbpNzd)
        print("units "+str(tradeSize))
    elif firstPartInst == "CHF":
        gbpChf = calcAveragePrice("GBP_CHF",oanda)
        tradeSize = floor(GBPperTrade*gbpChf)
        print("units "+str(tradeSize))
    elif firstPartInst == "ZAR":
        gbpZar = calcAveragePrice("GBP_ZAR",oanda)
        tradeSize = floor(GBPperTrade*gbpZar)
        print("units "+str(tradeSize))
    elif firstPartInst == "XAG":
        xagGbp = calcAveragePrice("XAG_GBP",oanda)
        tradeSize = floor(GBPperTrade/xagGbp)
        print("units "+str(tradeSize))
    elif firstPartInst == "XAU":
        xauGbp = calcAveragePrice("XAU_GBP",oanda)
        tradeSize = floor(GBPperTrade/xauGbp)
        print("units "+str(tradeSize))
    elif firstPartInst == "SGD":
        gbpSgd = calcAveragePrice("GBP_SGD",oanda)
        tradeSize = floor(GBPperTrade*gbpSgd)
        print("units "+str(tradeSize))
    elif firstPartInst == "XPT":
        xptGbp = calcAveragePrice("XPT_GBP",oanda)
        tradeSize = floor(GBPperTrade/xptGbp)
        print("units "+str(tradeSize))
    elif firstPartInst == "XPD":
        xpdGbp = calcAveragePrice("XPD_GBP",oanda)
        tradeSize = floor(GBPperTrade/xpdGbp)
        print("units "+str(tradeSize))
    return tradeSize

