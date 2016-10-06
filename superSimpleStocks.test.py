from __future__ import division

#required infrastructure
import unittest

#utilities used in tests
import time

#test module
import superSimpleStocks

class Case_CommonStock(unittest.TestCase):
  def setUp(self):
    self.commonStock1 = superSimpleStocks.CommonStock("abc", 123, 123)
    self.commonStock2 = superSimpleStocks.CommonStock("bcd", 123, 246)

  def test_getDiviendYield(self):
    """common stock, get dividend yield
    """
    self.assertEqual( self.commonStock1.getDividendYield(), 123 / 123)
    self.assertEqual( self.commonStock2.getDividendYield(), 123 / 246)

  def test_getPERatio(self):
    """common / preferred stock get PE Ratio
    """
    self.assertEqual( self.commonStock1.getPERatio()      , 123 / 123)
    self.assertEqual( self.commonStock2.getPERatio()      , 246 / 123)

class Case_PreferredStock(unittest.TestCase):
  def setUp(self):
    self.preferredStock1 = superSimpleStocks.PreferredStock("abc", 123, 1, 123)
    self.preferredStock2 = superSimpleStocks.PreferredStock("bcd", 123, 2, 246)

  def test_getDiviendYield(self):
    """preferred stock, get dividend yield
    """
    self.assertEqual( self.preferredStock1.getDividendYield(), 0.01 * 123 / 123 )
    self.assertEqual( self.preferredStock2.getDividendYield(), 0.02 * 246 / 246 )

  def test_updateFixedDividendPercentage(self):
    """update fixed dividend, get new yield
    """
    self.preferredStock1.updateFixedDividendPercentage(10)
    self.assertEqual( self.preferredStock1.getDividendYield(), 0.1  * 123 / 123 )

class Case_GBCE(unittest.TestCase):
  def setUp(self):
    self.gbce = superSimpleStocks.GBCE()

  def test_init_GBCE(self):
    self.gbce = superSimpleStocks.GBCE()
    self.assertEqual( len(self.gbce.stocks), 5)

  def test_index(self):
    product = 100 * 100 * 60 * 100 * 250
    index   = pow( product, 1 / float(5) ) 
    self.assertEqual( self.gbce.index(), index)

class Case_TradesAndStocks(unittest.TestCase):
  def setUp(self):
    self.gbce = superSimpleStocks.GBCE()

  def test_failPurchase_timeout(self):
    trade = superSimpleStocks.Trade(self.gbce.stocks['TEA'], 100)
    #hack the trade to make it 6 seconds old without waiting 6 seconds in the test
    trade.offerTimestamp = time.time() - 6
    self.assertEqual( trade.purchase()['status'], 'fail' )
    self.assertEqual( trade.purchase()['message'], 'Offer timeout is 5 seconds' )

  def test_purchaseStock(self):
    TEA   = self.gbce.stocks['TEA']
    trade = superSimpleStocks.Trade(TEA, 100)
    self.assertEqual( trade.purchase()['status'], 'success' )
    self.assertEqual( TEA.tradeHistory[0], trade )

  def test_failPurchase_sharesNotAvailable():
    ##not doing this :)
    pass

class Case_CommandProcessor(unittest.TestCase):
  def setUp(self):
    self.commandProcessor = superSimpleStocks.CommandProcessor(superSimpleStocks.GBCE())

  def test_strings(self):
    result = self.commandProcessor.userInputProcessor("?")
    self.assertEqual(result, 
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
                     )
    result = self.commandProcessor.userInputProcessor("bye")
    self.assertEqual(result, "bye")

    result = self.commandProcessor.userInputProcessor("list")
    self.assertEqual(result,
"""symbol   type  lastDividend  fixedDividend  parValue  PERatio  dividendYield  price
s:TEA t:common ld:0 fd:   pv:100 per:0 dy:0.0 p:100
s:ALE t:common ld:23 fd:   pv:60 per:2.60869565217 dy:0.383333333333 p:60
s:JOE t:common ld:13 fd:   pv:250 per:19.2307692308 dy:0.052 p:250
s:POP t:common ld:8 fd:   pv:100 per:12.5 dy:0.08 p:100
s:GIN t:Preferred ld:8 fd:2 pv:100 per:50.0 dy:0.02 p:100""")

  def test_buySell(self):
    result = self.commandProcessor.userInputProcessor("buy TEA 100")

    print result
    self.assertEqual( 'offer' in result, True )
    self.assertEqual( result['offer'], 'buy 100 of TEA at 100')

    result = self.commandProcessor.userInputProcessor("sell TEA 100")
    print result

    self.assertEqual( 'offer' in result, True )
    self.assertEqual( result['offer'], "sell -100 of TEA at 100")
    self.assertEqual( self.commandProcessor.currentTrade.quantity < 0, True )

  def test_confirmTooSlow(self):
    result = self.commandProcessor.userInputProcessor("buy TEA 100")

    self.commandProcessor.currentTrade.offerTimestamp = time.time() - 6

    confirmResult = self.commandProcessor.userInputProcessor("confirm")
    self.assertEqual( 'status' in confirmResult, True)
    self.assertEqual( confirmResult['status'] == 'fail', True)

  def test_confirmPurchaseSell(self):
    result = self.commandProcessor.userInputProcessor("sell TEA 100")

    confirmResult = self.commandProcessor.userInputProcessor("confirm")
    self.assertEqual( 'status' in confirmResult, True)
    self.assertEqual( confirmResult['status'] == 'success', True)
    self.assertEqual( self.commandProcessor.currentTrade.purchased, True)
    self.assertEqual( self.commandProcessor.currentTrade.stock.tradeHistory[0], self.commandProcessor.currentTrade )


def tests():
  commonStock       = unittest.TestSuite( map( Case_CommonStock     , [ 'test_getDiviendYield', 'test_getPERatio', ]                    ) )
  preferredStock    = unittest.TestSuite( map( Case_PreferredStock  , [ 'test_getDiviendYield', 'test_updateFixedDividendPercentage' ]  ) )
  gbce              = unittest.TestSuite( map( Case_GBCE            , [ 'test_index']                                                   ) )
  tradesAndStocks   = unittest.TestSuite( map( Case_TradesAndStocks , [ 'test_purchaseStock', 'test_failPurchase_timeout' ]             ) )
  commandProcessor  = unittest.TestSuite( map( Case_CommandProcessor, [ 'test_strings', 'test_buySell', 'test_confirmTooSlow', 'test_confirmPurchaseSell' ]             ) )
  
  return unittest.TestSuite( [commonStock, preferredStock, gbce, tradesAndStocks, commandProcessor] )


if __name__ == '__main__':
  unittest.TextTestRunner(verbosity=2).run( tests() )