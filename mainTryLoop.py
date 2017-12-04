from functions import *
import time, datetime

while True:
    try:
        myfxbookEmail=""
        myfxbookPassword=""
        liveOrPractice="practice"
        accessToken=""
        account_id=""
        mfxbSession = myfxbLogin(myfxbookEmail,myfxbookPassword)
        oanda = oandapy.API(environment=liveOrPractice, access_token=accessToken)

        percentPerTrade = 10 # (unleveraged percentage of balance)
        upperSellThreshold = 100 
        lowerSellThreshold = 90
        upperBuyThreshold = 10
        lowerBuyThreshold = 0
        upperCloseThreshold = 90
        lowerCloseThreshold = 10

        maxLeverage = 8
        gbpDiffThresh = 23438797  # Require sentiment to be at least this extreme to trade (in GBP terms)
        
        while True:
            response = oanda.get_account(account_id)
            unrealizedPl = response['unrealizedPl']
            balance = response['balance']
            NAV = balance+unrealizedPl
            print("NAV "+str(NAV))
            GBPperTrade = NAV * percentPerTrade / 100
            print("GBPperTrade "+str(GBPperTrade))
            
            outlookObj = mfxbComm(mfxbSession)
            noSymbols = len(outlookObj['symbols'])
            print(str(noSymbols))
            
            instruments = oanda.get_instruments(account_id)
            numSymbols = len(instruments['instruments'])
         
            for x in range(0,noSymbols): # loop through myfxbook symbols, change names and initiate variables
                symbol = outlookObj['symbols'][x]['name']
                symbol = symbol[0:3]+"_"+symbol[-3:]
                potentialTrade=""
                bias=""
                stop=""
                profit=""
                today=""
                for y in range(0,numSymbols): # loop through oanda instruments
                    instrument = instruments['instruments'][y]['instrument']
                    if symbol == instrument:
                        print(symbol)
                        shortPercentage = outlookObj['symbols'][x]['shortPercentage']
                        longVolume = outlookObj['symbols'][x]['longVolume']
                        shortVolume = outlookObj['symbols'][x]['shortVolume']
                        absDiffVol = abs(longVolume-shortVolume)
                        gbpDiff = gbpEquivCalc(symbol,absDiffVol,oanda)
                        if lowerSellThreshold <= shortPercentage < upperSellThreshold:
                            potentialTrade = "sell"
                        elif lowerBuyThreshold < shortPercentage <= upperBuyThreshold:
                            potentialTrade = "buy"
                        if shortPercentage > 50:
                            bias = "sell"
                        else:
                            bias = "buy"
                        trades = oanda.get_trades(account_id,instrument=symbol,count=500) # 500 is max oanda will return
                        numTrades = len(trades['trades'])
                        for z in range(0,numTrades): # loop through current trades
                            tradeInstrument = trades['trades'][z]['instrument']
                            if tradeInstrument == symbol: # if symbol matches
                                side = trades['trades'][z]['side']
                                price = oanda.get_prices(instruments=symbol)
                                if side == "buy" and shortPercentage >= upperCloseThreshold:
                                    close = "yes"
                                elif side == "sell" and shortPercentage <= lowerCloseThreshold:
                                    close = "yes"
                                else:
                                    close = ""                    
                                if close == "yes":
                                    tradeId=trades['trades'][z]['id']
                                    print(tradeId)
                                    response = oanda.close_trade(account_id,trade_id=tradeId)
                                    now = datetime.datetime.utcnow()
                                    nowYear = now.year
                                    nowMonth = now.month
                                    nowDay = now.day
                                    print("TRADE CLOSED")
                                    f = open('file.txt', 'a')
                                    f.write(str(nowDay)+"."+str(nowMonth)+"."+str(nowYear)+" "+symbol+" closed. Short percentage "+str(shortPercentage)+"\n")
                                    f.close()
                                else: # elif in loss set stop = "yes"
                                    ask = price['prices'][0]['ask']
                                    bid = price['prices'][0]['bid']
                                    tradePrice = trades['trades'][z]['price']
                                    if side == "buy":
                                        if bid > tradePrice:
                                            profit = "yes"
                                        else:
                                            profit = "no"
                                    else:
                                        if ask < tradePrice:
                                            profit = "yes"
                                        else:
                                            profit = "no"
                                    DateAndTime = trades['trades'][z]['time']
                                    Year = int(DateAndTime[0:4])
                                    Month = int(DateAndTime[5:7])
                                    Day = int(DateAndTime[8:10])
                                    now = datetime.datetime.utcnow()
                                    nowYear = now.year
                                    nowMonth = now.month
                                    nowDay = now.day
                                    if nowYear == Year and nowMonth == Month and nowDay == Day: # elif if done today set stop = "yes"
                                        today = "yes"
                                    else:
                                        today = "no"
                                if profit == "no" or today == "yes":
                                    stop = "yes"

                        overLeveraged = leverageTest(oanda,account_id,maxLeverage)
                       
                        if potentialTrade != "" and stop != "yes" and overLeveraged != "yes" and gbpDiff > gbpDiffThresh: # if potential trade = "sell" or "buy" and stop != "yes and speculators have large positioning"
        
                            tradeSize = sizeCalc(symbol,GBPperTrade,oanda) # calculate trade size and trade
        
                            if tradeSize > 0:
                                response = oanda.create_order(account_id,instrument=symbol,side=potentialTrade,type="market",units=tradeSize)
                                now = datetime.datetime.utcnow()
                                nowYear = now.year
                                nowMonth = now.month
                                nowDay = now.day
                                print("TRADE OPENED")
                                f = open('file.txt', 'a')
                                f.write(str(nowDay)+"."+str(nowMonth)+"."+str(nowYear)+" "+symbol+" "+potentialTrade+". Short percentage "+str(shortPercentage)+". gbpDiff "+str(floor(gbpDiff))+"\n")
                                f.close()
                        time.sleep(0.5)               
            time.sleep(61)    
    except:
        print('exception')
    else:
        print('non exception error')
    time.sleep(7201) #myfxbook used to block for 5 minutes when overloaded (was 301)
