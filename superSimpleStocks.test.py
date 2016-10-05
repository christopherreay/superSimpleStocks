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
    trade.offerTimestamp = time.time() - 6000
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


def tests():
  commonStock     = unittest.TestSuite( map( Case_CommonStock     , [ 'test_getDiviendYield', 'test_getPERatio', ]                    ) )
  preferredStock  = unittest.TestSuite( map( Case_PreferredStock  , [ 'test_getDiviendYield', 'test_updateFixedDividendPercentage' ]  ) )
  gbce            = unittest.TestSuite( map( Case_GBCE            , [ 'test_index']                                                   ) )
  tradesAndStocks = unittest.TestSuite( map( Case_TradesAndStocks , [ 'test_purchaseStock', 'test_failPurchase_timeout' ]             ) )
  
  return unittest.TestSuite( [commonStock, preferredStock, gbce, tradesAndStocks] )


if __name__ == '__main__':
  unittest.TextTestRunner(verbosity=2).run( tests() )