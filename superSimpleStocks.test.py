from __future__ import division

#required infrastructure
import unittest

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


def tests():
  commonStock     = unittest.TestSuite( map( Case_CommonStock     , [ 'test_getDiviendYield', 'test_getPERatio', ]          ) )
  preferredStock  = unittest.TestSuite( map( Case_PreferredStock  , [ 'test_getDiviendYield', 'test_updateFixedDividendPercentage' ]                             ) )

  return unittest.TestSuite( [commonStock, preferredStock, ] )


if __name__ == '__main__':
  unittest.TextTestRunner(verbosity=2).run( tests() )