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


def get_challenge_name():
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
    return challengeName


def get_source_image_path(target="original"):
    if target == "original":
        instruction = '\nSpecify a path to the original images.'
        inputLabel = "Original Images: "
    elif target == "comparative":
        instruction = '\nSpecify a path to the comparative images.'
        inputLabel = "Comparative Images: "
    else:
        raise Exception('invalid value for target: %s' % target)

    print(instruction)
    while True:
        imagesPath = util.escape_home_in_path(
            input(inputLabel))
        if util.check_if_path_exists(imagesPath):
            # return all images in path as sorted list
            return sorted(util.list_all_images_in_directory(imagesPath))
        else:
            print("path %s is not existend" % imagesPath)
            correctionDecision = input(
                "would you like to correct it or quit [c/Q]: ")
            print(correctionDecision)
            if not correctionDecision.lower() == "c":
                sys.exit(1)


def get_target_image_path():
    print("Specify a target path for the attacked images.")
    while True:
        targetPath = util.escape_home_in_path(
            input("Target path: "))
        if util.check_if_path_exists(targetPath):
            # return all images in path as sorted list
            return targetPath
        else:
            print("path %s is not existend" % targetPath)
            correctionDecision = input(
                "would you like to correct it or quit [c/Q]: ")
            print(correctionDecision)
            if not correctionDecision.lower() == "c":
                sys.exit(1)


def get_range_parameter(parameterName, paramMinLimit, paramMaxLimit):
    # ask for min
    # ask for max // will not reach max
    # ask for step
    minFloat = 0.0
    maxFloat = 0.0
    stepFloat = 0.0
    print("Specify the range for %s [%s, %s]:" % (
        parameterName, str(paramMinLimit), str(paramMaxLimit)))
    while True:
        minString = input("min (<=): ")
        try:
            minFloat = float(minString)
        except:
            print("input is no number")
            continue
        if (paramMinLimit <= minFloat <= paramMaxLimit):
            break
        else:
            print("input %f is bigger or smaller as domain of attack[%s, %s]" % (
                minFloat, str(paramMinLimit), str(paramMaxLimit)))
            continue

    while True:
        maxString = input("max (<): ")
        try:
            maxFloat = float(maxString)
        except:
            print("input is no number")
            continue
        if (paramMinLimit <= maxFloat <= paramMaxLimit):
            break
        else:
            print("input %f is bigger or smaller as domain of attack [%s, %s]" % (
                maxFloat, str(paramMinLimit), str(paramMaxLimit)))
            continue

    while True:
        stepString = input("step : ")
        try:
            stepFloat = float(stepString)
        except:
            print("input is no number")
            continue
        if (paramMinLimit <= stepFloat <= paramMaxLimit):
            break
        else:
            print("input %f is bigger or smaller as domain of attack [%s, %s]" % (
                stepFloat, str(paramMinLimit), str(paramMaxLimit)))
            continue

    return np.arange(minFloat, maxFloat, stepFloat)


def save_attacked_image(image, attackedImagesTargetPath, imageName, imageExtension):
    util.save_image(image, "%s/%s.%s" %
                    (attackedImagesTargetPath, imageName, imageExtension))


def rotation_hook(originalImagesPathes, attackedImagesTargetPath):
    print("I am rotation hook")
    # TODO: add attack name and range/set of parameters when saving attacked
    # images

    parameterRange = get_range_parameter("angle in degree", 0, 360)

    # TODO continue here
    print(parameterRange)

    # apply attack
    # save image

    return ["orig/i1.png", "orig/i1.png", "orig/i1.png", "orig/i2.png", "orig/i2.png", "orig/i2.png", "orig/i3.png", "orig/i3.png", "orig/i3.png"], ["attacked/rot_scaled_0-2/i1_0.png", "attacked/rot_scaled_0-20/i1_1.png", "attacked/rot_scaled_0-2/i1_2.png", "attacked/rot_scaled_0-2/i2_0.png", "attacked/rot_scaled_0-20/i2_1.png", "attacked/rot_scaled_0-2/i2_2.png", "attacked/rot_scaled_0-2/i3_0.png", "attacked/rot_scaled_0-20/i3_1.png", "attacked/rot_scaled_0-2/i3_2.png"], [True, True, True, True, True, True, True, True, True], {}


def attack_challenge_creator(attackHook):
    # get challenge name
    # select basic images
    # select save path for attacked images
    # attack hook hook(originalImagesList, attackedImagesTargetPath) => originals, comparatives, decisions, otherStuff (object..decompose to challenge object)
    #    define range/ set of parameters
    #    for originalImage:
    #       for rangeItem/setItem:
    #           attack
    #           save => pathToImage (relative)
    # save challenge in db

    challengeName = get_challenge_name()

    originalImagesPathes = get_source_image_path(target="original")

    attackedImagesTargetPath = get_target_image_path()

    originalImages, comparativeImages, targetDecisions, metaData = attackHook(
        originalImagesPathes, attackedImagesTargetPath)

    pm.add_challenge(challengeName, originalImages,
                     comparativeImages, targetDecisions, metaData)

    print("Added attack challenge")


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

    challengeName = get_challenge_name()

    # get path to original images
    originalImages = get_source_image_path(target="original")

    # get path to comparative images
    comparativeImages = get_source_image_path(target="comparative")

    # filter originals ans comparatives if they are in the same folder
    regMatcher = r"_[SD]\."
    originalImages = [
        imgPath for imgPath in originalImages if not re.search(regMatcher, imgPath)]
    comparativeImages = [
        imgPath for imgPath in comparativeImages if re.search(regMatcher, imgPath)]

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
    attack_challenge_creator(rotation_hook)


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
