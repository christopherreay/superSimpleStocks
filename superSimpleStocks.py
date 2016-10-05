from __future__ import division


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

  def requestBuy(self, quantity):
    return Trade(self, quantity)

  def requestSell(self, quantity):
    return Trade(self, quantity * -1)

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



class Trade():
  def __init__(self, market, symbol, quantity, asManyAsPossibleOrAll="asManyAsPossible"):
    self.__init__(market.stocks[symbol], quantity, asManyAsPossible)

  def __init__(self, stock, quantity, asManyAsPossibleOrAll="asManyAsPossible"):
    self.stock                = stock

    self.offerTimestamp       = time.time()
    self.offerQuantity        = quantity
    self.price                = self.stock.getTickerPrice()

    self.timestamp            = None
    self.quantity             = None

    self.style                = asManyAsPossibleOrAll

    self.verb                 = "bought" if self.quantity > 0 else "sold"


#Question: Is the trade price calculated over the last 15 minutes the same as the trade price cumulatively over the entire trading history?
#Answer: No, because the 15 minute version is something like a sliding average.