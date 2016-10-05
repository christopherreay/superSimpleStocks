from __future__ import division

#utils / libraries
import time
import ipdb

#and beyond
class Dependency(dict):
  pass

class Stock(object):
  def __init__(self, symbol, lastDividend, parValue):
    self.symbol       = symbol
    self.lastDividend = lastDividend
    self.parValue     = parValue
    self.currency     = "USD"

    self.tradeHistory               = []
    self.tradeHistory15MinuteSlice  = 0

    self.stockPool    = "infinite"

  def getDividendYield(self):
    raise NotImplementedError("I'd like you to Subclass Stock and implement this Method")
  
  def getPERatio(self):
    return 1.0 / self.getDividendYield()

  def getTickerPrice(self):
    #hilarious
    return self.parValue

  def completeTrade(self, trade, context):
    if self.stockPool == "infinite":
      trade.quantity = trade.offerQuantity
      context.update( { "status"  : "success",
                        "message" : "You successfully %s %s of %s at %s %s" % (trade.verb, trade.quantity, self.symbol, trade.price, self.currency)
                      }
                    )
      trade.purchased = True
    elif trade.style == "all" and ( (self.stockPool - trade.quantity) < 0 ) :
      context.update( { "status": "fail",
                        "message": "There are not enough shares in the pool to fulfill your request",
                      }
                    )
      trade.quantity = 0
    else:
      ### TODO code to negotiate purchase over time
      trade.quantity =  min(trade.quantity, self.stockPool)
      self.stockPool -= trade.quantity
      context.update( { "status"  : "success",
                        "message" : "You successfully %s %s of %s at %s %s" % (trade.verb, trade.quantity, self.symbol, trade.price, self.currency)
                      }
                    )
      trade.purchased = True


    
    trade.timestamp = time.time()
    self.tradeHistory.append(trade)

class PreferredStock(Stock):
  def __init__(self, symbol, lastDividend, fixedDividend, parValue):
    super(PreferredStock, self).__init__(symbol, lastDividend, parValue)
    
    self.fixedDividend        = fixedDividend
    
    #This "optimisation" is incorrect, as it is possible for the "fixed dividend" rate to change, e.g. if it is linked to LIBOR
    #self.dividendDollarValue  = self.parValue * fixedDividendAsPercentage / 100.0

  def updateFixedDividendPercentage(self, newPercentage):
    context = {}
    if newPercentage > 100 or newPercentage < 0:
      context = { "status"  : "fail",
                  "message" : "Percentage must be between 0 and 100"
                }
    else:
      context = { "status"  : "success",
                  "message" : "Updating fixed dividend to %s" % ( newPercentage, )
                }
      self.fixedDividend = newPercentage
    return context

  def getDividendYield(self):
    return  (   ( (self.fixedDividend / 100) * self.parValue ) 
              /   self.getTickerPrice()
            )

class CommonStock(Stock):
  def __init__(self, symbol, lastDividend, parValue):
    super(CommonStock, self).__init__(symbol, lastDividend, parValue)

  def getDividendYield(self):
    return self.lastDividend / self.getTickerPrice()


class GBCE():
  def __init__(self):
    self.stocks = \
        { "TEA": CommonStock     ("TEA", 0 ,     100 ),
          "POP": CommonStock     ("POP", 8 ,     100 ),
          "ALE": CommonStock     ("ALE", 23,     60  ),
          "GIN": PreferredStock  ("GIN", 8 , 2,  100 ),
          "JOE": CommonStock     ("JOE", 13,     250 )
        }
  def index(self):
    #calculate geometric mean
    product = 1
    for (symbol, stock) in self.stocks.items():
      product *= stock.getTickerPrice()
    return pow( product, 1 / float(len(self.stocks)) )

class Trade():
  def __init__(self, stock, quantity, asManyAsPossibleOrAll="asManyAsPossible"):
    self.stock                = stock

    self.offerTimestamp       = time.time()
    self.offerQuantity        = quantity
    self.price                = self.stock.getTickerPrice()

    self.timestamp            = None
    self.quantity             = None

    self.style                = asManyAsPossibleOrAll

    self.offerVerb            = "buy"    if self.offerQuantity > 0 else "sell"
    self.verb                 = "bought" if self.offerQuantity > 0 else "sold"

    self.purchased            = False    

    self.trace                = { "offer": "%s %s of %s at %s" % (self.offerVerb, self.offerQuantity, self.stock.symbol, self.price)
                                }


  def purchase(self):
      ipdb.set_trace()
      now = time.time()

      if now - self.offerTimestamp > 5:
        context = { "status"  : "fail",
                    "message" : "Offer timeout is 5 seconds",
                  }
      else:
        context = {}
        self.stock.completeTrade(self, context)

      self.trace.update(context)

      return context

class CommandProcessor(object):
  def __init__(self, market):
    self.dependencyGraph  = {}

    self.market           = market
    self.currentTrade     = None

    self.COMMAND          = 0
    self.SYMBOL           = 1
    self.QUANTITY         = 2
    self.POSORALL         = 3
    self.PERCENT          = 2

  def blocking_getUserInput(self):
    while True:
      try:
        command = raw_input("\n\n? for help>> ")
        result = self.userInputProcessor(command)
      except EOFError as e:
        result = "bye"
      
      print result
      
      if result == "bye":
        break


  def userInputProcessor(self, command):
    toReturn = True

    if    command == "?":
      toReturn = \
"""bye                     to quit
list                    to show curent stock information
buy  symbol quantity [asManyAsPossible | all ] 
                        to request an offer price to buy
sell symbol quantity [asManyAsPossible | all ] 
                        to request an offer price to sell
confirm                 to confirm an offer (actually buy or sell a stock). Timeout is 5 seconds.
index                   to get the current GBCE All Share Price Index
updateFixed symbol percent    
                        to update the Fixed Dividend Percentage of a Preferred Stock
"""

    
    elif  command == "bye":
      toReturn = "bye"
    

    elif  command == "list":
      toReturn = """all the info"""
    

    elif  command.startswith("buy") or command.startswith("sell"):
      commandData = command.split(" ")
      if len(commandData) == 3: 
        commandData.append("asManyAsPossible")
      commandData[self.QUANTITY] = int(commandData[self.QUANTITY])
      if commandData[self.COMMAND] == "sell": 
        commandData[self.QUANTITY] = commandData[self.QUANTITY] * -1

      self.currentTrade = Trade( self.market.stocks[commandData[self.SYMBOL]], commandData[self.QUANTITY], commandData[self.POSORALL] )
      toReturn = self.currentTrade.trace
    
    
    elif  command == "confirm":
      # ipdb.set_trace()
      self.currentTrade.purchase()
      toReturn = self.currentTrade.trace
    
    
    elif  command == "index":
      toReturn = GBCE.index()
    
    
    elif  command.startswith("updateFixed"):
      commandData = command.split(" ")
      stock = self.market[ commandData[self.SYMBOL] ]
      self.solveDependencyGraph(commandData)


    return toReturn

  def solveDependencyGraph(commandData):
    pass


if __name__ == "__main__":
    CommandProcessor(GBCE()).blocking_getUserInput()