import urllib
import urllib2
import json
import time
import hmac
import hashlib
import ccxt

def createTimeStamp(datestr, format="%Y-%m-%d %H:%M:%S"):
    return time.mktime(time.strptime(datestr, format))


class poloniex:
    def __init__(self, APIKey, Secret):
        self.APIKey = APIKey
        self.Secret = Secret

    def post_process(self, before):
        after = before

        # Add timestamps if there isnt one but is a datetime
        if('return' in after):
            if(isinstance(after['return'], list)):
                for x in xrange(0, len(after['return'])):
                    if(isinstance(after['return'][x], dict)):
                        if('datetime' in after['return'][x] and 'timestamp' not in after['return'][x]):
                            after['return'][x]['timestamp'] = float(createTimeStamp(after['return'][x]['datetime']))

        return after

    def api_query(self, command, req={}):
        exchange=ccxt.cobinhood()
        exchange.apiKey='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGlfdG9rZW5faWQiOiIxYjZiYzYwMC02Mjk5LTRjYjktYjk3MC02NDcwZjBkNzc5NTQiLCJzY29wZSI6WyJzY29wZV9leGNoYW5nZV90cmFkZV9yZWFkIiwic2NvcGVfZXhjaGFuZ2VfdHJhZGVfd3JpdGUiLCJzY29wZV9leGNoYW5nZV9sZWRnZXJfcmVhZCJdLCJ1c2VyX2lkIjoiM2U1OGU2NzItZDk0My00Y2I1LTkyMzMtOWZkMGYyODFmMGRkIn0.IpuC_7GuJPp4D1LyqX43ILzDcqpga8xxaFG39_26Nv4.V2:36199575115e65a66690f1b692b9ba5ed96ba9ace53c25f28601d6bcd5d323ba'
        if(command == "returnTicker" or command == "return24Volume"):
            tickers = {}    
        # load all markets from the exchange
            markets = exchange.load_markets()

            # output all symbols

            delay = int(exchange.rateLimit / 1000)  # delay in between requests

            for symbol in exchange.symbols:
                try:
                    # suffix '.d' means 'darkpool' on some exchanges
                    if symbol.find('.d') < 0:

                        # sleep to remain under the rateLimit
                        time.sleep(delay)

                        # fetch and print ticker
                        ##print_ticker(exchange, symbol)
                        ticker = exchange.fetch_ticker(symbol.upper())
                        tickers[symbol.upper()]=    (ticker)
                        print (ticker)
                except Exception as e:
                    print(e)    
            #ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + command))
            return (tickers)
        elif(command == "returnOrderBook"):
            ret = exchange.fetch_order_book(str(req['currencyPair']))
            
            return ret
        elif(command == "returnMarketTradeHistory"):
            ret = exchange.fetch_trades(str(req['currencyPair']))
            
            return ret
        elif (command=="returnCompleteBalances"):
            ret = exchange.fetchBalance()
            
            return ret
        elif (command == "returnOpenOrders"):
            ret = exchage.fetchOpenOrders(str(req['currencyPair']))
            return ret
        elif (command == "returnTradeHistory"):

            ret = exchnage.fetchMyTrades(str(req['currencyPair']))
            return ret
        elif (command == "buy"):
            ret = exchange.createOrder (str(req['currencyPair']), 'limit', 'buy', req['amount'],req['rate'])
            return ret
        elif (command == "sell"):
            ret = exchange.createOrder (str(req['currencyPair']), 'limit', 'sell', req['amount'],req['rate'])
            return ret
        elif (command == "cancel"):
            ret = exchange.cancelOrder(req['orderNumber'])
            return ret
        else:        
            req['command'] = command
            req['nonce'] = int(time.time()*1000)
            post_data = urllib.urlencode(req)

            sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
            headers = {
                'Sign': sign,
                'Key': self.APIKey
            }

            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/tradingApi', post_data, headers))
            jsonRet = json.loads(ret.read())
            return self.post_process(jsonRet)

    def returnTicker(self):
        return self.api_query("returnTicker")

    def return24Volume(self):
        return self.api_query("return24Volume")

    def returnOrderBook(self, currencyPair):
        return self.api_query("returnOrderBook", {'currencyPair': currencyPair})

    def returnMarketTradeHistory(self, currencyPair):
        return self.api_query("returnMarketTradeHistory", {'currencyPair': currencyPair})

    # Returns all of your balances.
    # Outputs:
    # {"BTC":"0.59098578","LTC":"3.31117268", ... }
    def returnBalances(self):
        return self.api_query('returnCompleteBalances')

    # Returns your open orders for a given market, specified by the "currencyPair" POST parameter, e.g. "BTC_XCP"
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs:
    # orderNumber   The order number
    # type          sell or buy
    # rate          Price the order is selling or buying at
    # Amount        Quantity of order
    # total         Total value of order (price * quantity)
    def returnOpenOrders(self, currencyPair):
        return self.api_query('returnOpenOrders', {"currencyPair": currencyPair})

    # Returns your trade history for a given market, specified by the "currencyPair" POST parameter
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs:
    # date          Date in the form: "2014-02-19 03:44:59"
    # rate          Price the order is selling or buying at
    # amount        Quantity of order
    # total         Total value of order (price * quantity)
    # type          sell or buy
    def returnTradeHistory(self, currencyPair):
        return self.api_query('returnTradeHistory', {"currencyPair": currencyPair})

    # Places a buy order in a given market. Required POST parameters are "currencyPair", "rate", and "amount".
    # If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is buying at
    # amount        Amount of coins to buy
    # Outputs:
    # orderNumber   The order number
    def buy(self, currencyPair, rate, amount):
        return self.api_query('buy', {"currencyPair": currencyPair, "rate": rate, "amount": amount})

    # Places a sell order in a given market. Required POST parameters are "currencyPair", "rate", and "amount".
    # If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is selling at
    # amount        Amount of coins to sell
    # Outputs:
    # orderNumber   The order number
    def sell(self, currencyPair, rate, amount):
        return self.api_query('sell', {"currencyPair": currencyPair, "rate": rate, "amount": amount})

    # Cancels an order you have placed in a given market. Required POST parameters are "currencyPair" and "orderNumber".
    # Inputs:
    # currencyPair  The curreny pair
    # orderNumber   The order number to cancel
    # Outputs:
    # succes        1 or 0
    def cancel(self, currencyPair, orderNumber):
        return self.api_query('cancelOrder', {"currencyPair": currencyPair, "orderNumber": orderNumber})

    # Immediately places a withdrawal for a given currency, with no email confirmation.
    # In order to use this method, the withdrawal privilege must be enabled for your API key.
    # Required POST parameters are "currency", "amount", and "address". Sample output: {"response":"Withdrew 2398 NXT."}
    # Inputs:
    # currency      The currency to withdraw
    # amount        The amount of this coin to withdraw
    # address       The withdrawal address
    # Outputs:
    # response      Text containing message about the withdrawal
    def withdraw(self, currency, amount, address):
        return self.api_query('withdraw', {"currency": currency, "amount": amount, "address": address})

    def returnDepositHistory(self, start, end):
        return self.api_query('returnDepositsWithdrawals', {"start": start, "end": end})
