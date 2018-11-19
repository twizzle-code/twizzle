#!/usr/bin/env python3

import numpy as np
from pihmatch import TestRunner
from pihmatch.utils import load_image
from pihmatch.deviation_presets import hamming_distance

# global config
NR_OF_THREADS = 10


def test_dhash(aOriginalImages, aComparativeImages, lThreshold=0.15, lHashSize=16):
    from pihmatch.hashalgos_preset import dhash

    # create dictionary of metadata
    dicMetadata = {"algorithm": "dhash",
                   "hash_size": lHashSize, "threshold": lThreshold}

    # compare every image
    aDecisions = []
    for i, aOriginalImagePath in enumerate(aOriginalImages):
        aComparativeImagePath = aComparativeImages[i]

        # get images from path
        aOriginalImage = load_image(aOriginalImagePath)
        aComparativeImage = load_image(aComparativeImagePath)

        # calculate hashes
        aHashOriginal = dhash(aOriginalImage, hash_size=lHashSize)
        aHashComparative = dhash(aComparativeImage, hash_size=lHashSize)

        # calculate deviation
        dDeviation = hamming_distance(aHashComparative, aHashOriginal)

        # make decision
        bDecision = False
        if(dDeviation <= lThreshold):
            # images are considered to be the same
            bDecision = True

        # push decision to array of decisions
        aDecisions.append(bDecision)

    # return decision and dictionary of metadata
    return aDecisions, dicMetadata


if __name__ == "__main__":
    oRunner = TestRunner(lNrOfThreads=NR_OF_THREADS)

    # iterate over thresholds
    for lThreshold in np.arange(0.05, 0.5, 0.05):
        # iterate over hash sizes
        for lHashSize in [8, 16, 32]:
            # add test to testrunner
            oRunner.run_test_async("printscan_printer1", test_dhash, {
                                   "lThreshold": lThreshold, "lHashSize": lHashSize})

            # # NOTE: for better understanding, this is what
            # # we do here if we would not use threads
            # pm.run_test("printscan_printer1", test_dhash, {"lThreshold":
            # lThreshold, "lHashSize": lHashSize})

    oRunner.wait_till_tests_finished()
