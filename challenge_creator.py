#!/usr/bin/env python3

# path of original images
# path of attacked images
# name of attacked images has to fit rule (_n.* ... means no-match)

# Reality attacks
# - define name
# - folder of originals
# - folder of targets
# - naming schema
# from terminaltables import AsciiTable
from functools import partial
from tabulate import tabulate
from pmatch import Pmatch
import climenu
import pandas as pd
import numpy as np
import util
import ast
import sys
import re


# adapt cli menu settings
climenu.settings.text['main_menu_title'] = 'PIHMATCHA - Challenge creator\n=============================='
climenu.settings.back_values = ['']


# helper functions
def show_challenges_helper(bShowIndex=False):
    dfChallenges = pd.DataFrame(pm.get_challenges())
    dfChallenges["challenge_set_size"] = dfChallenges.apply(
        lambda row: len(row["targetDecisions"]), axis=1)
    dfChallenges = dfChallenges.drop(
        labels=["originalImages", "comparativeImages", "targetDecisions"],
        axis=1)
    dfChallenges.replace(np.nan, "", inplace=True)
    print(tabulate(dfChallenges, headers='keys',
                   tablefmt='psql', showindex="never" if not bShowIndex else "always"))
    return dfChallenges["challenge"].tolist()


# define menu layout

@climenu.group(title="Add challenge")
def add_challenge_group():
    pass


@climenu.menu(title="Show challenges")
def show_challenges():
    show_challenges_helper(False)


@climenu.menu(title="Remove challenge")
def remove_challenges():
    challengeNameList = show_challenges_helper(True)
    numberOfChallenges = len(challengeNameList)
    print("Which challenge would you like to delete?")
    while True:
        deleteDecision = input("[0-%i, Q]: " % (numberOfChallenges - 1))
        if deleteDecision == "" or deleteDecision.lower() == "q":
            break
        else:
            try:
                deleteDecision = int(deleteDecision)
            except:
                continue
            if (0 <= deleteDecision < numberOfChallenges):
                deleteDecisionChallengeName = challengeNameList[deleteDecision]
                pm.del_challenge(deleteDecisionChallengeName)
                print("Deleted challenge %s ... DONE" %
                      deleteDecisionChallengeName)
                break


@add_challenge_group.menu(title='Add custom challenge')
def add_custom_challenges():
    # Path to original images
    # path to comparative images
    # rule: "<imageName>_[S,D]"
    # add special attributes

    # check list of challenges already defined
    challengeNamesAlreadyDefined = [
        challengeObject["challenge"] for challengeObject in pm.get_challenges()]

    # get name of challenge
    print('\nSpecify a name of the challenge:')
    challengeName = ""
    while True:
        challengeName = input("Challenge name: ")
        if len(challengeName) == 0:
            print("\nName might not be empty")
        elif challengeName in challengeNamesAlreadyDefined:
            print(
                "\n Name %s is already specified in the database. Choose another one." % challengeName)
        else:
            break

    # get path to original images
    print('\nSpecify a path to the original images.')
    while True:
        originalImagesPath = util.escape_home_in_path(
            input("Original Images: "))
        if util.check_if_path_exists(originalImagesPath):
            break
        else:
            print("path %s is not existend" % originalImagesPath)
            correctionDecision = input(
                "would you like to correct it or quit [c/Q]: ")
            print(correctionDecision)
            if not correctionDecision.lower() == "c":
                sys.exit(1)

    # get path to comparative images
    print('\nSpecify a path to the comparative images.')
    while True:
        comparativeImagesPath = util.escape_home_in_path(
            input("Comparative Images: "))
        if util.check_if_path_exists(comparativeImagesPath):
            break
        else:
            print("path %s is not existend" % comparativeImagesPath)
            correctionDecision = input(
                "would you like to correct it or quit [c/Q]: ")
            if not correctionDecision.lower() == "c":
                sys.exit(1)

    # parse all images
    originalImages = util.list_all_images_in_directory(originalImagesPath)
    comparativeImages = util.list_all_images_in_directory(
        comparativeImagesPath)

    # filter originals ans comparatives if they are in the same folder
    regMatcher = r"_[SD]\."
    originalImages = [
        imgPath for imgPath in originalImages if not re.search(regMatcher, imgPath)]
    comparativeImages = [
        imgPath for imgPath in comparativeImages if re.search(regMatcher, imgPath)]

    # sort lists
    originalImages = sorted(originalImages)
    comparativeImages = sorted(comparativeImages)

    # check whether every original has a comparative
    originalImageNamesSet = set([util.get_filename_without_extension(
        imgPath) for imgPath in originalImages])
    comparativeImageNames = [util.get_filename_without_extension(
        imgPath) for imgPath in comparativeImages]
    targetDecisions = [True if name[-1] ==
                       "S" else False for name in comparativeImageNames]
    comparativeImageNamesSet = set([name[:-2]
                                    for name in comparativeImageNames])

    if (originalImageNamesSet ^ comparativeImageNamesSet):
        print("ERROR: We can not match all comparative images with original images.\nPlease check the amount of images and whether\nevery image has its counterpart and vice versa...Exit")
        sys.exit(1)

    while True:
        print(
            '\nSpecify additional metadata in form of a python dictionary {"attribute": "value"}.')
        attributesString = input("Attributes [default {}]: ")
        try:
            if attributesString == "":
                attributesDict = {}
                break
            attributesDict = ast.literal_eval(attributesString)
            if type(attributesDict) is dict:
                break
            print(
                "\nThe input is no python dictionary.\nInsert a dictionary or leave it blank to finish.")
        except:
            print("ERROR: The input is no valid python code.")

    # save challenge object in db
    pm.add_challenge(challengeName, originalImages,
                     comparativeImages, targetDecisions, attributesDict)

    print("Challenge %s was added ..." % challengeName)


@add_challenge_group.group(title="Add attack challenge")
def attack_challenge_group():
    pass

# TODO: take set of images


@attack_challenge_group.menu(title="Rotation (cropped)")
def attack_rotation_cropped():
    print("I am cropped rotation")


@attack_challenge_group.menu(title="Rotation (fitted)")
def attack_rotation_fitted():
    print("I am fitted rotation")


@attack_challenge_group.menu(title="Crop (uniform)")
def attack_crop_uniform():
    print("I am crop uniform")


@attack_challenge_group.menu(title="Crop (nonuniform)")
def attack_crop_nonuniform():
    print("I am crop nonuniform")


@attack_challenge_group.menu(title="Overlay")
def attack_overlay():
    print("I am overlay")


@attack_challenge_group.menu(title="JPEG Quality")
def attack_jpeg_quality():
    print("I am JPEG quality")


@attack_challenge_group.menu(title="Speckle Noise")
def attack_speckle_noise():
    print("I am speckle_noise")


@attack_challenge_group.menu(title="Salt and Pepper Noise")
def attack_salt_and_pepper_noise():
    print("I am salt_and_pepper_noise")


@attack_challenge_group.menu(title="Gauss Noise")
def attack_gauss_noise():
    print("I am gauss_noise")


@attack_challenge_group.menu(title="Scale")
def attack_scale():
    print("I am scale")


@attack_challenge_group.menu(title="Contrast")
def attack_contrast():
    print("I am contrast")


if __name__ == '__main__':
    pm = Pmatch()
    climenu.run()

# TODO: add shuffle challenge (from set of images x match and 1-x do not
# match; random generated)
