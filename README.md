# Espresso-API-Pyhton
    Espresso-API-Python is a Python library that provides a simple interface for accessing the Espresso API,which is a RESTful API for real-time streaming of financial market data.
    With Espresso-API-Python, developers and traders can easily retrieve real-time market data such as stock prices, market trends, historical data, stream live market data (WebSockets), and more. 
    

# Installation 
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install espressoconnectpython
```bash    
    pip install espressoconnect
    pip install websocket
```
# Usage
```python

    # package import statement
    from espressoApi.espressoConnect import EspressoConnect
    
    # Make a object call
    
    api_key = "Your API KEY"
    """ vendor_key="Vendor Key" """
    espressoApi = EspressoConnect(api_key=api_key)
    
    # Print the login url
    
    """ Pass vendor_key if it is needed """
    
    print(espressoApi.login_url())
    
    # Pass the required parameters for decryption and encryption
    
    """ After Successfully Login You will receive the request token value
        then you have to decrypt the token value by using secret key and 
        then swap the request token which is a combination of RequestId and CustomerId
        Then after that decrypt the request token value   """
    
    request_token="Your request token"
    secret_key="Your secret key"
    
    """Use generate session method for decrypt and re-encrypt the request token value """
    session = espressoApi.generate_session(request_token,secret_key)
    
    """Use get_access_token for generating access token """
    access_token=espressoApi.get_access_token(api_key,session,vendor_key,state)
    print(access_token)
    
    access_token = 'Your access token value'
    espressoApi = EspressoConnect(api_key=api_key,access_token=access_token)
    print(espressoApi.requestHeaders())         # for printing request headers
    
    # place order history
    
    orderparams={
      "customerId": XXXXXX,
      "scripCode": 2475,
      "tradingSymbol": "ONGC",    -->  (Allowed parameters NC/BC/NF/RN/MX)
      "exchange": "NC",
      "transactionType": "B",      --> (Allowed parameters (B, S, BM, SM, SAM))
      "quantity": 1,
      "disclosedQty": 0,
      "price": "145.85",
      "triggerPrice": "0",
      "rmsCode": "ANY",
      "afterHour": "N",
      "orderType": "NORMAL",
      "channelUser": "XXXXXX",  --> (Use LoginId as ChannelUser)
      "validity": "GFD",       --> (Validity of an order (GFD/MyGTD/IOC))
      "requestType": "NEW",
      "productType": "CNC"
    """Note: For Equity Exchange – CNC (Normal), For F&O – CNF(Normal), MIS or MIS+)"""
    "instrumentType": "FUTCUR",       --> ((Future Stocks(FS)/ Future Index(FI)/ Option Index(OI)/ Option Stocks(OS)/ Future Currency(FUTCUR)/ Option Currency(OPTCUR)))
    "strikePrice":"-1",
    """For optiontype"""
    "optionType": "XX",
    "expiry": "31/03/2023"
    }

    order=espressoApi.placeOrder(orderparams)
    print("PlaceOrder: {}".format(order))

    # modify order

    orderparams={
        "orderId": "XXXXXXX",
        "customerId": XXXXXX,
      "scripCode": 2475,
      "tradingSymbol": "ONGC",    -->  (Allowed parameters NC/BC/NF/RN/MX)
      "exchange": "NC",
      "transactionType": "B",      --> (Allowed parameters (B, S, BM, SM, SAM))
      "quantity": 1,
      "disclosedQty": 0,
      "price": "145.85",
      "triggerPrice": "0",
      "rmsCode": "ANY",
      "afterHour": "N",
      "orderType": "NORMAL",
      "channelUser": "XXXXXX",  --> (Use LoginId as ChannelUser)
      "validity": "GFD",       --> (Validity of an order (GFD/MyGTD/IOC))
      "requestType": "MODIFY",    -->(requestType should be MODIFY for modifying the order)
      "productType": "CNC"
    """Note: For Equity Exchange – CNC (Normal), For F&O – CNF(Normal), MIS or MIS+)"""
    "instrumentType": "FUTCUR",       --> ((Future Stocks(FS)/ Future Index(FI)/ Option Index(OI)/ Option Stocks(OS)/ Future Currency(FUTCUR)/ Option Currency(OPTCUR)))
    "strikePrice":"-1",
    """For optiontype"""
    "optionType": "XX",
    "expiry": "31/03/2023"
    }
    
    order=espressoApi.modifyOrder(orderparams)
    print("ModifyOrder: {}".format(order))
    
    # cancel order
    orderparams={
         "orderId": "XXXXXX",
        "customerId": XXXXXX,
      "scripCode": 2475,
      "tradingSymbol": "ONGC",    -->  (Allowed parameters NC/BC/NF/RN/MX)
      "exchange": "NC",
      "transactionType": "B",      --> (Allowed parameters (B, S, BM, SM, SAM))
      "quantity": 1,
      "disclosedQty": 0,
      "price": "145.85",
      "triggerPrice": "0",
      "rmsCode": "ANY",
      "afterHour": "N",
      "orderType": "NORMAL",
      "channelUser": "XXXXXX",  --> (Use LoginId as ChannelUser)
      "validity": "GFD",       --> (Validity of an order (GFD/MyGTD/IOC))
      "requestType": "CANCEL",   --> (requestType should be CANCEL for cancel the order)
      "productType": "CNC"
    """Note: For Equity Exchange – CNC (Normal), For F&O – CNF(Normal), MIS or MIS+)"""
    "instrumentType": "FUTCUR",       --> ((Future Stocks(FS)/ Future Index(FI)/ Option Index(OI)/ Option Stocks(OS)/ Future Currency(FUTCUR)/ Option Currency(OPTCUR)))
    "strikePrice":"-1",
    """For optiontype"""
    "optionType": "XX",
    "expiry": "31/03/2023"
      }

    order=espressoApi.cancelOrder(orderparams)
    print("CancelOrder: {}".format(order))
    
    # Retrieves all positions
    
    customerId="customerId < int data type>"
    order=espressoApi.trades(customerId)
    print("Retrieves All Position: {}".format(order))
    
    # Retrieve history of an given order
    
    exchange="exchange value <string>"
    customerId="customerId <int data type>"
    orderId="orderId <int data type>"
    order=espressoApi.exchange(exchange, customerId, orderId)
    print("History of an give order: {}".format(order))
    
    # Retrieves the trade  generated by an order
    
    exchange="exchange value <string>"
    customerId="customerId <int data type>"
    orderId="orderId <int data type>"
    order=espressoApi.exchangetrades(exchange, customerId, orderId)
    print("Trade Generated By an Order : {}".format(order))
    
    # services Holdings
    
    customerId="customerId <int data type>"
    order=espressoApi.holdings(customerId)
    print("Holdings : {}".format(order))
    
    # Script Master
    
    exchange="exchange value <string>"
    order=espressoApi.master(exchange)
    print("Script Master : {}".format(order))
    
    # Scrip Master data by CSV-Without Access-Token
    
    exchange="exchange value <string>"
    order=espressoApi.mastercsv(exchange)
    print("Script Master CSV : {}".format(order))
    
    # Historical Data
    
    exchange="exchange value <string>"
    scripcode="Unique scripcode provided by the broker <int>"
    interval="Available Intervals <string>"
    order=espressoApi.historicaldata(exchange, scripcode, interval)
    print("Holdings Data: {}".format(order))
```

 # websocket Programming Testing
```python

     from espressoApi.espressoApiWebsocket import EspressoWebSocket
    params={
        "access_token": access_token,
        "api_key": api_key
    }
    
    token_list = {"action": "subscribe", "key": ["feed"], "value": [""]}
    feed = {"action": "feed", "key": ["depth"], "value": ["MX250715"]}
    unsubscribefeed = {"action":"unsubscribe","key":["feed"],"value":["NC22,NF37833,NF37834,MX253461,RN7719"]}
    
    sws = EspressoWebSocket(access_token,api_key)
    def on_data(wsapp, message):
        print("Ticks: {}".format(message))

    def on_open(wsapp):
        print("on open")
        sws.subscribe(token_list)
        sws.fetchData(feed)
        # sws.unsubscribe(feed)
        # sws.close_connection()
    
    def on_error(wsapp, error):
        print(error)
    
    def on_close(wsapp):
        print("Close")
    
    # Assign the callbacks.
    sws.on_open = on_open
    sws.on_data = on_data
    sws.on_error = on_error
    sws.on_close = on_close
    
    sws.connect()
```