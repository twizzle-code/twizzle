from pihmatch import Pihmatch
from multiprocessing.pool import ThreadPool


class TestRunner(object):
    def __init__(self, sDBPath=None, lNrOfThreads=2):
        self.pm = Pihmatch(sDBPath)
        self.oPool = ThreadPool(processes=lNrOfThreads)
        self.aTaskPoolThreads = []

    def run_test_async(self, sChallengeName, fnCallback, dicCallbackParameters={}):
        pThread = self.oPool.apply_async(
            self.pm.run_test, (sChallengeName, fnCallback, dicCallbackParameters))
        self.aTaskPoolThreads.append(pThread)

    def wait_till_tests_finished(self):
        # catch threads ready
        for pThread in self.aTaskPoolThreads:
            pThread.get()

    def get_tests(self):
        return self.pm.get_tests()
