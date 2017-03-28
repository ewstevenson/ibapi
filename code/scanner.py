#!/usr/bin/python3

# https://interactivebrokers.github.io/tws-api/historical_data.html#hd_request&gsc.tab=0
# https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html#a72fc193c4d50f738b6092a174988f093&gsc.tab=0



from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from threading import Thread
import queue

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

    # begin requests
    def scan(self):
        self.reqScannerSubscription(7001,ScannerSubscriptionSamples.HighOptVolumePCRatioUSIndexes(), [])
    # end requests
    
    # begin returns
    def scannerData(self, reqId: int, rank: int, distance: str, benchmark: str, projection: str, legsStr: str):
        super().scannerData(reqId, rank, contractDetails, distance, benchmark,
                            projection, legsStr)
        print("ScannerData. ", reqId, "Rank:", rank, "Symbol:", contractDetails.summary.symbol,"SecType:", contractDetails.summary.secType, "Currency:", contractDetails.summary.currency,"Distance:", distance, "Benchmark:", benchmark,"Projection:", projection, "Legs String:", legsStr)

    def scannerDataEnd(self, reqId: int):
        super().scannerDataEnd(reqId)
        print("ScannerDataEnd. ", reqId)

    # end returns

# end user added functions
# end TestWrapper

# begin TestClient
class TestClient(EClient):
    """
    The client method

    We don't override native methods, but instead call them from our own wrappers
    """
    def __init__(self, wrapper):
        ## Set up with a wrapper inside
        EClient.__init__(self, wrapper)

# end test client
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

    app = TestApp("127.0.0.1", 4001, 37)
    app.scan()
    #current_time = app.ewsTest()
    #print(current_time)

    app.disconnect()
