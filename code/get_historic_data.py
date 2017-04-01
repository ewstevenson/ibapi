#!/usr/bin/python3

# https://interactivebrokers.github.io/tws-api/historical_data.html#hd_request&gsc.tab=0
# https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html#a72fc193c4d50f738b6092a174988f093&gsc.tab=0

import sys
sys.path.insert(0,"/home/ews/ibapi/dl/twsapi/IBJts/samples/Python/Testbed")

from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.client import *
from ibapi.contract import *
from threading import Thread
import queue
import datetime
from ContractSamples import *

# begin TestWrapper
class TestWrapper(EWrapper):
    """
    The wrapper deals with the action coming back from the IB gateway or TWS instance

    We override methods in EWrapper that will get called when this action happens, like currentTime


    """

    ## error handling code
    def init_error(self):
        error_queue=queue.Queue()
        self._my_errors = error_queue

    def get_error(self, timeout=5):
        if self.is_error():
            try:
                return self._my_errors.get(timeout=timeout)
            except queue.Empty:
                return None
        return None

    def is_error(self):
        an_error_if=not self._my_errors.empty()
        return an_error_if

    def error(self, id, errorCode, errorString):
        ## Overriden method
        errormsg = "IB error id %d errorcode %d string %s" % (id, errorCode, errorString)
        self._my_errors.put(errormsg)
# end error handling 
# begin user add functions

  ######### Send Functions ##########
    def getHistory(self):
        numDays = 5 
        queryTime = (datetime.datetime.today() - datetime.timedelta(days=numDays)).strftime("%Y%m%d %H:%M:%S")
        contract = Contract()
        contract.symbol = "USD"
        contract.secType = "CASH"
        contract.currency = "JPY"
        contract.exchange = "IDEALPRO"
        try:
            earliestDate = self.reqHeadTimeStamp(4103, ContractSamples.USStockAtSmart(), "TRADES", 0, 1)
            print(earliestDate)
            #historicData = self.reqHistoricalData(4101, ContractSamples.USStockAtSmart(), queryTime, "1 M", "1 day", "MIDPOINT", 1, 1, [])
            #historicData = self.reqHistoricalData(4001, ContractSamples.EurGbpFx(), queryTime, "1 M", "1 day", "MIDPOINT", 1, 1, [])
            historicData = self.reqHistoricalData(4001, contract, queryTime, "1 M", "1 day", "MIDPOINT", 1, 1, [])
        except queue.Empty:
            print("Exceeded maimum wait for wrapper to respond")
            current_time =  None
        while self.wrapper.is_error():
            print(self.get_error())
        return historicData


######### Recieve Functions ############
    def historicalData(self, reqId: TickerId, date: str, open: float, high: float,
                       low: float, close: float, volume: int, barCount: int,
                       WAP: float, hasGaps: int):
        super().historicalData(reqId, date, open, high, low, close, volume,
                               barCount, WAP, hasGaps)
        print("HistoricalData. ", reqId, " Date:", date, "Open:", open,
              "High:", high, "Low:", low, "Close:", close, "Volume:", volume,
              "Count:", barCount, "WAP:", WAP, "HasGaps:", hasGaps)
        print("In the historicalData function!")
        return open

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd ", reqId, "from", start, "to", end)
        return end

    def headTimestamp(self, reqId:int, headTimestamp:str):
        print("HeadTimestamp: ", reqId, " ", headTimestamp)
        return headTimestamp


# end user added functions

# begin TestClient
class TestClient(EClient):
    """
    The client method

    We don't override native methods, but instead call them from our own wrappers
    """
    def __init__(self, wrapper):
        ## Set up with a wrapper inside
        EClient.__init__(self, wrapper)

# begin TestApp
class TestApp(TestWrapper, TestClient):
    def __init__(self, ipaddress, portid, clientid):
        TestWrapper.__init__(self)
        TestClient.__init__(self, wrapper=self)

        self.connect(ipaddress, portid, clientid)

        thread = Thread(target = self.run)
        thread.start()

        setattr(self, "_thread", thread)

        self.init_error()
#end TestApp

if __name__ == '__main__':
    ##
    ## Check that the port is the same as on the Gateway
    ## ipaddress is 127.0.0.1 if one same machine, clientid is arbitrary

    app = TestApp("127.0.0.1", 4001, 10)

    historicData = app.getHistory()
    print(historicData)
    #app.disconnect()
