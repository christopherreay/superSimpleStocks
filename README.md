# superSimpleStocks

Here are the notes for this project: 
 - https://docs.google.com/document/d/1N-ofdZk2hOVOXQskSI74NVhlU0xjPMlDc7SK6lUYEjQ/edit?usp=sharing
 - https://drive.google.com/open?id=0B2ExtwsWVr9DWFhaczY2WlVPZEE
 
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
 - Tests
   - Stock, Market, Trade, UserInteraction
   
 #TODO
 - implement tests for Dependency Code
 - add Dictionary Adapter for the @depends decorator
