from __future__ import division

#utils / libraries
import time


#and beyond
class Dependency(dict):
  pass

class Stock(object):
  def __init__(self, symbol, lastDividend, parValue):
    self.symbol       = symbol
    self.lastDividend = lastDividend
    self.parValue     = parValue
    self.currency     = "USD"

    self.tradeHistory = []

    self.stockPool = "infinite"

  def getDividendYield(self):
    pass
  
  def getPERatio(self):
    return 1.0 / self.getDividendYield()

  def getTickerPrice(self):
    #hilarious
    return self.parValue

  def completeTrade(self, trade, context):
    if self.stockPool == "infinite":
      trade.quantity = trade.offerQuantity
      context.update( { "status"  : "success",
                        "message" : "You successfully %s of %s at %s %s" % (trade.verb, self.symbol, trade.price, self.currency)
                      }
                    )
    elif trade.style == "all" and ( (self.stockPool - trade.quantity) < 0 ) :
      context.update( { "status": "fail",
                        "message": "There are not enough shares in the pool to fulfill your request",
                      }
                    )
      trade.quantity = 0
      ### TODO code to negotiate purchase over time
    else:
      trade.quantity =  min(trade.quantity, self.stockPool)
      self.stockPool -= trade.quantity

    
    trade.timestamp           = time.time()
    self.tradeHistory         .append(trade)

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

    self.verb                 = "bought" if self.quantity > 0 else "sold"

  def purchase(self):
      now = time.time()

      if now - self.offerTimestamp > 5000:
        context = { "status"  : "fail",
                    "message" : "Offer timeout is 5 seconds",
                  }
      else:
        context = {}
        self.stock.completeTrade(self, context)

      return context

#Question: Is the trade price calculated over the last 15 minutes the same as the trade price cumulatively over the entire trading history?
#Answer: No, because the 15 minute version is something like a sliding average.