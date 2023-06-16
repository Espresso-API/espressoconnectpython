# # websocket Programming Testing

from espressoApi.espressoApiWebsocket import EspressoWebSocket
api_key = "Your Api-key"
access_token = 'Your Access Token'
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