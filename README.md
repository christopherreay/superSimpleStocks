# superSimpleStocks

Here are the notes for this project: 
 - Project Specification
   - https://drive.google.com/open?id=0B2ExtwsWVr9DWFhaczY2WlVPZEE
 - My Notes
   - https://docs.google.com/document/d/1N-ofdZk2hOVOXQskSI74NVhlU0xjPMlDc7SK6lUYEjQ/edit?usp=sharing
 
# implementation
 - OO representation of 
   - Stock
     - PreferredStock
     - CommonStock
   - Market (GBCE)
     - should be factored out into Market object
   - Trade
   - UserInteraction
     - blocking with raw_input
   - Dependency / Emitter
     - implemented as a python decorator
 - [Dependency Graph](#Dependency-Graph)
 - Tests
   - Stock, Market, Trade, UserInteraction
   
# Dependency Graph
  - Super simple dependencies between functions, implemented with python decorators
  - PreferredStock.updateFixedDividendPercentage -> PreferredStock.getDividendYield -> Stock.getPERatio
  - Also memoisation of CommonStock.getDividendYield is implemented with the @depends(None) decorator
  - The test for the @depends decorator is test_fixedUpdate_dependencyGraph
  
  - decorator syntax is
    - @depends("dependsOn")
      - depends installs a proxy around dependsOn which emits an event whenever dependsOn is called
      - in response to this event, the decorated method will calculate a new value
      - the current value is memoised by the @depends wrapper, until one of its dependencies is changed
      - calls the original function return the memoised value for speed
    - @depends(None) implements memoisation of the result of the function when first called
 
# usage
  - run the program "python superSimpleStocks.py"
  - follow the prompt
  - offers for purchase or sale last five seconds
     
#TODO
  - add Dictionary Adapter for the @depends decorator
