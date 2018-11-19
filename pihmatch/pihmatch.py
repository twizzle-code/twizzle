#!/usr/bin/env python3

import config as conf

from sqlitedict import SqliteDict
import numpy as np


class Pihmatch(object):
    """Perceptual Image Hashing Matching Challenge -- Backbone
    """

    def __init__(self, sDBPath=None):
        """Constructor of the Pihmatch class

        Note:
            Please define the `DB_PATH` in the config.py or pass the path of the SQLite 
            as parameter
        Args:
            sDBPath (str): Path to the SQLite database.
        """
        if sDBPath is None and not hasattr(conf, "DB_PATH"):
            raise Exception("Path to SQL-Database has to be defined")
        sDBPath = sDBPath if sDBPath else conf.DB_PATH
        self._db = SqliteDict(sDBPath)

    def add_challenge(self, sName, aOriginalImages, aComparativeImages, aTargetDecisions, dicMetadata={}):
        """Adds a challenge under the given name to the database

        Note:
            The three lists describe a table of the following format:

            | Original image | Comparative image | target decision |
            |----------------|-------------------|-----------------|
            | Img1.png       | Img1_scaled.png   | True            |
            | Img2.png       | Img2_brighter.png | True            |
            | Img2.png       | Img9.png          | False           |

            In thisexample the tested perceptual image hashing algorithm would generate a hash for Img1.png and
            Img1_scaled.png, compare them based on a deviationfunction and decide for True (is the same image) or
            False (is not the same image).


        Args:
            sName (str): the name of the challenge.
            aOriginalImages (:obj:`list` of :obj:`str`): List of paths of the original images
            aComparativeImages (:obj:`list` of :obj:`str`): List of paths of the images that should be compared to 
                                                            the original image at the same position in the list
            aTargetDecisions (:obj:`list` of :obj:`bool`): List of boolean defining whether the images linked in aOriginalImages
                                                            and aComparativeImagesbeeing at the same position in the list are
                                                            the same (True) or not (False)
            dicMetadata (:obj:): an object defining metadata for the challenge like what printer was used or what kind of attack 
                                using which parameters was performed

        Returns:
            None
        """

        # catch wrong parameters
        if (not sName) or (aOriginalImages is None) or (aComparativeImages is None) or (aTargetDecisions is None):
            raise Exception("Parameters can not be None.")
        if not(len(aOriginalImages) == len(aComparativeImages) == len(aTargetDecisions)):
            raise Exception(
                "Image sets and target decisions have to have the same amount of entries.")
        if not (all(isinstance(x, str) for x in aOriginalImages) and all(isinstance(x, str) for x in aComparativeImages)):
            raise Exception(
                "All images have to be defined as path given as string.")
        if (not all(isinstance(x, bool) for x in aTargetDecisions)) and not isinstance(aTargetDecisions, np.ndarray) and not (aTargetDecisions.dtype == np.dtype("bool")):
            raise Exception("The target decisions have to be boolean only.")

        # get current challenges from database
        aChallenges = self._db.get(conf.DB_CHALLENGES_KEY, [])

        # test whether name was used before
        aChallengesSameName = [
            ch for ch in aChallenges if ch["challenge"] == sName]
        if len(aChallengesSameName) != 0:
            raise Exception(
                "Challenge name %s is already in use. Define an other one. Aborting." % sName)

        # append new challenge
        dicChallenge = {"challenge": sName, "originalImages": aOriginalImages,
                        "comparativeImages": aComparativeImages, "targetDecisions": aTargetDecisions}
        # adding additional information if given
        if dicMetadata:
            dicChallenge = {**dicMetadata, **dicChallenge}
        aChallenges.append(dicChallenge)
        self._db[conf.DB_CHALLENGES_KEY] = aChallenges
        self._db.commit()

    def del_challenge(self, sName):
        """ deletes an existing challenge by its name

        Args:
            sName (str): the name of the challenge to be deleted

        Returns:
            None
        """

        # get current challenges from database
        aChallenges = self._db.get(conf.DB_CHALLENGES_KEY, [])
        aMatches = [ch for ch in aChallenges if ch["challenge"] == sName]
        if len(aMatches) == 0:
            raise Exception("No challenge named %s found." % sName)

        # remove element
        aChallenges.remove(aMatches[0])

        # save new db
        self._db[conf.DB_CHALLENGES_KEY] = aChallenges
        self._db.commit()

    def get_challenges(self):
        """ getting a list of all defined challenges

        Returns:
            :obj:`list` of :obj:: `obj`:  List of all defined challenges
        """
        return self._db.get(conf.DB_CHALLENGES_KEY, [])

    def get_challenge(self, sChallengeName):
        """ getting a single challenge object

        Args:
            sChallengeName (str): the name of the challenge to get

          Returns:
            :obj:: `obj`:  Object defining the challenge having the name sChallengeName
        """
        aChallenges = self._db.get(conf.DB_CHALLENGES_KEY, [])
        aMatches = [ch for ch in aChallenges if ch["challenge"]
                    == sChallengeName]
        if len(aMatches) == 0:
            raise Exception("No challenge with name %s found." %
                            sChallengeName)
        return aMatches[0]

    def clear_challenges(self):
        """ clears all challenge entries from the database """
        self._db[conf.DB_CHALLENGES_KEY] = []
        self._db.commit()

    def run_test(self, sChallengeName, fnCallback, dicCallbackParameters={}):
        """ run single challenge as test using given callback function and optional params

        Note:
            fnCallback has to fullfill following specifications

            Parameters:
            fnCallback(aOriginalImages, aComparativeImages, **dicCallbackParameters)
            - aOriginalImages: list of strings describing paths to original images
            - aComparativeImages: list of strings describing paths to comparative images
            ... arbitrary number of further parameters

            Returns:
            aDecisions, dicAdditionalInformation = fnCallback(...)
            - aDecisions: list of boolean decisions describing wether the algorithm has decided that the original image 
                          and the comparative image are the same (True) or not (False)
            - dicAdditionalInformation: the algorithm can supply additional information that can be used in the evaluation 
                                        later on to compare different settings


        Args:
            sChallengeName (str): the challenge that should be executed
            fnCallback (function): Pointer to wrapper-function that tests a challenge on a specific image hashing algorithm
                                    and makes decisions whether the images are the same or not depending on its decision algorithm
            dicCallbackParameters (:obj:): Dictionary defining parameters for the function in fnCallback

        Returns:
            None
        """
        if not(sChallengeName) or not(fnCallback):
            raise Exception("Parameters are not allowed to be None.")

        dicChallenge = self.get_challenge(sChallengeName)
        sChallengeName = dicChallenge["challenge"]
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
        lErrors = np.count_nonzero(
            np.array(aDecisions) != np.array(aTargetDecisions))
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

        aTests = self._db.get(conf.DB_TESTS_KEY, [])
        aTests.append(dicTest)
        self._db[conf.DB_TESTS_KEY] = aTests
        self._db.commit()

    def get_tests(self):
        """getting all tests

        Returns:
            :obj:`list` of :obj:: `obj`:  List of all tests executed
        """
        return self._db.get(conf.DB_TESTS_KEY, [])

    def clear_tests(self):
        """ delete all tests from the database """
        self._db[conf.DB_TESTS_KEY] = []
        self._db.commit()
