from __future__ import division

#utils / libraries
import time
import ipdb

class TraverseObject(object):
  pass
def o():
  return  TraverseObject()

def getProperty(obj, address):
  if isinstance(obj, dict):
    return obj[address]
  else:
    return getattr(obj, address)
def hasProperty(obj, address):
  if isinstance(obj, dict):
    return address in obj
  else:
    return hasattr(obj, address)
def setProperty(obj, address, value):
  if isinstance(obj, dict):
    obj[address] = value
  else:
    setattr(obj, address, value)

#implements a "does this exist, if not create it" paradigm, using "some.tree.of.attributes" notation
#  default values may be supplied. 
#  Works with dictionaries or objects
def traverse(obj, address, defaultValueList=None):

  addressCounter  = 0
  addressList     = address.split(".")

  current = obj
  for addressItem in addressList:
    if not hasProperty(current, addressItem):
      if defaultValueList is None:
        value = o()
      else:
        value = defaultValueList[addressCounter]
        addressCounter +=1
      setProperty(current, addressItem, value )
    current = getProperty(current, addressItem)


  return current


#implements a simple dependency.
#  dependent functions must take no arguments
#  values from dependent functions are memoised and the memoised version is served
#  memoised values are automatically updated when any dependency is changed
class depends(object):
  dependencyID = 0
  dependencies = {}

  def __init__(self, *config):
    #ipdb.set_trace()

    #store the parameters given to the decorator
    self.config         = config
    
  def __call__(self, underlyingFunction):
    #ipdb.set_trace()

    decoratorInstance   = self
    localName           = underlyingFunction.__name__

    def wrapped(*args, **kwargs):
      #ipdb.set_trace()

      #self for the object the function is bound to
      obj                   = args[0]
      #to identify this instance of the decorator we need the object the function is bound to and the name of the function
      #  here we store all the context related to this instantiation of the decorator on the object itself, hiding it somewhat (_context)
      #  this gives us an easy way to diferentiate and to access a persistent context for this decoration
      context = traverse( obj, "_context.decorators.depends.%s" % (localName, ) )

      #until the method is first actually run, we dont know what the object it is bound to is. 
      #  once it has been run, we can define a context on the object for this specific decorator instantiation
      #    (specific to this function bound to this object)
      if traverse( context, "firstRun", defaultValueList=[ True ] ) == True:
        context.firstRun     = False

        context.decoratorInstance   = decoratorInstance
        context.obj                 = obj
        context.localName           = localName
        context.underlyingFunction  = underlyingFunction
        def call(): { getattr(obj, localName)() }
        context.call = call
        
        #we need to wrap the function upon which this function's value depends
        if decoratorInstance.config[0] == None:
          #basic memoise of answer
          pass
        elif len(decoratorInstance.config) == 1 and isinstance(decoratorInstance.config[0], basestring):
          #should be a string naming a function in the same class / object
          context.emitterAttrName = context.decoratorInstance.config[0]
          setattr( obj, context.emitterAttrName, emitter( obj, context.emitterAttrName, context) )
        elif len(decoratorInstance.config) == 2:
          #install a tool over the named property
          pass
        
        
      #the dependency graph allows us to memoise values in the knowledge that they cannot have changed
      if traverse( context, "updateMemoise", defaultValueList=[ True ]) == True:
        context.updateMemoise = False
        #memoizeCurrentValue
        context.currentValue  = underlyingFunction(*args, **kwargs)
      
      #the currently memoised value, either defined on the firstRun or still here since no dependency has changed
      return context.currentValue

    return wrapped

    def call(self):
      #ipdb.set_trace()

      self.underlyingFunction(self.obj)

#the emitter function is a decorator, more or less, but simply manually installed using the definition supplied
#  as parameter to the @depends decorator
def emitter( obj, emitterAttrName, dependsContext ):
 
  #ipdb.set_trace()

  #the traverse structure neatly deals with our namespace
  context   = traverse( obj,    "_context.decorators.emitter.%s" % (emitterAttrName) )
  #and implicitly only defines things on firstRun
  listeners = traverse(context, "listeners", defaultValueList=[ [] ])

  #add the context of the @depends
  listeners.append(dependsContext)

  #Thats this function, right here
  emittingFunction = getattr(obj, emitterAttrName)
  #wrap_emitter = None

  #"decorate" this function, we can since the dependsContext knows what object the function it depends on is bound to
  #  This doesnt have to be the same obj as the initial @depends, but it does have to be available in scope at runtime... probabaly
  def wrap_emitter(underlyingFunction):
    #replace the function we depend on with a wrapper for it which emits to the @depends decorator that it needs to 
    #  update its memoised value
    def wrapped_emitter(*args, **kwargs):
      #ipdb.set_trace()

      #first thing we need to  get the new value of this function calculated
      toReturn = underlyingFunction(*args, **kwargs)
      #if the value hasnt changed, then we dont need to update through the depenency graph
      if traverse( context, "oldValue", defaultValueList=[None] ) == toReturn:
        return toReturn
      context.oldValue = toReturn

      #this is all very naively implemented, but simply the dependent function will very often *call* the emitting function
      #  to determine the new value. Sometimes this is memoised :)
      traverse( context, "cycle", defaultValueList=[ list(context.listeners) ])
      #putUp and tearDown done at the root of the dependency graph
      traverse( context, "root",  defaultValueList=[ 0 ] )

      context.root += 1
      #emit changed event to all listeners (different verbal paradigm, but serves to describe the dependency graph in a different way
      #  I believe that is called "description" :)
      for listener in context.listeners:
        # if listener in context.cycle:
        #   #the cycle just maintains a list of which listeners have already been fired by the 
        #   #context.cycle.remove(listener)
        listener.updateMemoise = True
        listener.call()

      context.root -= 1
      if context.root == 0:
        delattr(context, "cycle")

      return toReturn


    return wrapped_emitter

  return wrap_emitter(emittingFunction)



class DictionaryDependency(object):
  def __init__(self, object, dictionary, testForObject, targetFunctionName):
    pass


class Stock(object):
  def __init__(self, symbol, lastDividend, parValue):
    self.symbol       = symbol
    self.type         = "abstractType"
    self.lastDividend = lastDividend
    self.parValue     = parValue
    self.currency     = "USD"

    self.tradeHistory               = []
    self.tradeHistory15MinuteSlice  = 0

    self.stockPool    = "infinite"

    self.dividendYield  = None
    self.PERatio        = None


  def getDividendYield(self):
    raise NotImplementedError("I'd like you to Subclass Stock and implement this Method")
  
  @depends("getDividendYield")
  def getPERatio(self):
    try:
      return 1.0 / self.getDividendYield()
    except ZeroDivisionError:
      return 0

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
    
    self.type                 = "Preferred"
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

  @depends("updateFixedDividendPercentage")
  def getDividendYield(self):
    return  (   ( (self.fixedDividend / 100) * self.parValue ) 
              /   self.getTickerPrice()
            )

class CommonStock(Stock):
  def __init__(self, symbol, lastDividend, parValue):
    super(CommonStock, self).__init__(symbol, lastDividend, parValue)
    self.type = "common"

  @depends(None)
  def getDividendYield(self):
    return self.lastDividend / self.getTickerPrice()



class GBCE(object):
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

  #@depends("stocks", DictionaryDependency( lamda (key, item): isinstance(item, PreferredStock), "getDividendYield" ) )
  def showInfo(self):
    toReturn = ["symbol   type  lastDividend  fixedDividend  parValue  PERatio  dividendYield  price" ]
    for (key, stock) in self.stocks.items():
      toReturn.append ( "s:%s t:%s ld:%s fd:%s pv:%s per:%s dy:%s p:%s" 
                      % ( stock.symbol, 
                          stock.type, 
                          stock.lastDividend, 
                          stock.fixedDividend if hasattr(stock, "fixedDividend") else "  ", 
                          stock.parValue, 
                          stock.getPERatio(), 
                          stock.getDividendYield(), 
                          stock.getTickerPrice()
                        ) 
                      )
    
    return "\n".join(toReturn)

class Trade(object):
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

    self.market           = market
    self.currentTrade     = None

    self.COMMAND          = 0
    self.SYMBOL           = 1
    self.QUANTITY         = 2
    self.POSORALL         = 3
    self.PERCENT          = 2

  def blocking_getUserInput(self):
    print self.market.showInfo()
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
      toReturn = self.market.showInfo()
    

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
      # #ipdb.set_trace()
      self.currentTrade.purchase()
      toReturn = self.currentTrade.trace
    
    
    elif  command == "index":
      toReturn = GBCE.index()
    
    
    elif  command.startswith("updateFixed"):
      commandData = command.split(" ")
      stock       = self.market.stocks[ commandData[self.SYMBOL] ]
      toReturn    = stock.updateFixedDividendPercentage( float(commandData[self.PERCENT]) )


      #self.solveDependencyGraph(commandData)


    return toReturn

  def solveDependencyGraph(commandData):
    pass







if __name__ == "__main__":
    #ipdb.set_trace()
    CommandProcessor(GBCE()).blocking_getUserInput()