#!/usr/bin/env python3

import config as conf

from sqlitedict import SqliteDict
import numpy as np

# TODO:
# [ ] challenge definer
# [ ] run algo
# [ ] data analyser (opt)


class Pmatch:
    def __init__(self):
        self.db = SqliteDict(conf.DB_PATH)

    def add_challenge(self, sName, aOriginalImages, aComparativeImages, aTargetDecisions, dicMetadata={}):
        """ adds a challenge under the given name to the database """

        # catch wrong parameters
        if (not sName) or (not aOriginalImages) or (not aComparativeImages) or (not aTargetDecisions):
            raise Exception("Parameters can not be None.")
        if not(len(aOriginalImages) == len(aComparativeImages) == len(aTargetDecisions)):
            raise Exception(
                "Image sets and target decisions have to have the same amount of entries.")
        if not (all(isinstance(x, str) for x in aOriginalImages) and all(isinstance(x, str) for x in aComparativeImages)):
            raise Exception(
                "All images have to be defined as path given as string.")
        if not all(isinstance(x, bool) for x in aTargetDecisions):
            raise Exception("The target decisions have to be boolean only.")

        # get current challenges from database
        aChallenges = self.db.get(conf.DB_CHALLENGES_KEY, [])

        # test whether name was used before
        aChallengesSameName = [ch for ch in aChallenges if ch["name"] == sName]
        if len(aChallengesSameName) != 0:
            raise Exception(
                "Challenge name %s is already in use. Define an other one. Aborting." % sName)

        # append new challenge
        dicChallenge = {"name": sName, "originalImages": aOriginalImages,
                        "comparativeImages": aComparativeImages, "targetDecisions": aTargetDecisions}
        # adding additional information if given
        if dicMetadata:
            dicChallenge = {**dicMetadata, **dicChallenge}
        aChallenges.append(dicChallenge)
        self.db[conf.DB_CHALLENGES_KEY] = aChallenges
        self.db.commit()

    def del_challenge(self, sName):
        """ deletes an existing challenge """

        # get current challenges from database
        aChallenges = self.db.get(conf.DB_CHALLENGES_KEY, [])
        aMatches = [ch for ch in aChallenges if ch["name"] == sName]
        if len(aMatches) == 0:
            raise Exception("No challenge named %s found." % sName)

        # remove element
        aChallenges.remove(aMatches[0])

        # save new db
        self.db[conf.DB_CHALLENGES_KEY] = aChallenges
        self.db.commit()

    def get_challenges(self):
        """ getting array of defined challenges """
        return self.db.get(conf.DB_CHALLENGES_KEY, [])

    def get_challenge(self, sChallengeName):
        """ getting a single challenge object """
        aChallenges = self.db.get(conf.DB_CHALLENGES_KEY, [])
        aMatches = [ch for ch in aChallenges if ch["name"] == sChallengeName]
        if len(aMatches) == 0:
            raise Exception("No challenge with name %s found." %
                            sChallengeName)
        return aMatches[0]

    def clear_challenges(self):
        """ clears all challenge entries """
        self.db[conf.DB_CHALLENGES_KEY] = []
        self.db.commit()

    def run_test(self, sChallengeName, fnCallback, dicCallbackParameters={}):
        """ run single challenge as test using given callback function and optional params"""
        if not(sChallengeName) or not(fnCallback):
            raise Exception("Parameters are not allowed to be None.")

        dicChallenge = self.get_challenge(sChallengeName)
        sChallengeName = dicChallenge["name"]
        aOriginalImages = dicChallenge["originalImages"]
        aComparativeImages = dicChallenge["comparativeImages"]
        aTargetDecisions = dicChallenge["targetDecisions"]

        # run challenge
        aDecisions, dicAdditionalInformation = fnCallback(
            aOriginalImages, aComparativeImages, **dicCallbackParameters)

        # check if site of decisions is right
        if len(aDecisions) != len(aTargetDecisions):
            raise Exception(
                "Array of Decisions is not the same size as given set of images. Aborting.")

        # calculate errorate
        lTestsetSize = len(aTargetDecisions)
        lErrors = np.count_nonzero(aDecisions != aTargetDecisions)
        dErrorRate = lErrors / lTestsetSize

        # fill test object
        dicTest = dicAdditionalInformation
        dicTest["challenge"] = sChallengeName
        dicTest["errorrate"] = dErrorRate

        # save test in db
        self.__save_test(dicTest)

    def __save_test(self, dicTest):
        """ saves a test object to the database"""
        if not dicTest:
            raise Exception("Test object must not be None.")

        aTests = self.db.get(conf.DB_TESTS_KEY, [])
        aTests.append(dicTest)
        self.db[conf.DB_TESTS_KEY] = aTests
        self.db.commit()

    def get_tests(self):
        """getting all tests"""
        return self.db.get(conf.DB_TESTS_KEY, [])

    def clear_tests(self):
        """ clears all tests """
        self.db[conf.DB_TESTS_KEY] = []
        self.db.commit()


if __name__ == "__main__":
    klaus = Pmatch()

    # define one single challenge
    sName = "printscan_printer1"
    aOriginalImages = ["challenges/print_scan/d1/p1.tiff",
                       "challenges/print_scan/d1/p2.tiff", "challenges/print_scan/d1/p3.tiff"]
    aComparativeImages = ["challenges/print_scan/d1/c1.png",
                          "challenges/print_scan/d1/c2.png", "challenges/print_scan/d1/c3.png"]
    aTargetDecisions = [True, False, True]
    dicMetadata = {"printer": "Epson XL3", "resolution": "200dip"}

    klaus.clear_challenges()

    klaus.add_challenge(sName, aOriginalImages,
                        aComparativeImages, aTargetDecisions)
    print(klaus.get_challenges())

    # def testalgo(a, b, p1="", p2=""):
    #     """ algo mocking a test function """
    #     print("i got p1 as %s | p2 as %s" % (p1, p2))
    # return [True, True, True], {"algo": "ahash", "precision": 12,
    # "threshold": 0.02}

    # klaus.run_test(sName, testalgo, {})
    # klaus.run_test(sName, testalgo, {"p1": 42})
    # klaus.run_test(sName, testalgo, {"p1": 42, "p2": 33})
    # klaus.run_test(sName, testalgo, {"p2": 98})

    # print(klaus.get_tests())
    # klaus.clear_tests()
    # print(klaus.get_tests())
