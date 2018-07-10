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
import attacks as atk
import pandas as pd
import numpy as np
import climenu
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

    rangeMetadata = {"min": minFloat, "max": maxFloat, "step": stepFloat}

    return np.arange(minFloat, maxFloat, stepFloat), rangeMetadata


def save_attacked_image(image, attackedImagesTargetPath, imageName, imageExtension):
    savePath = "%s/%s.%s" % (attackedImagesTargetPath,
                             imageName, imageExtension)
    util.save_image(image, savePath)
    return savePath


########## attack hooks ##############################

def rotation_cropped_hook(originalImagesPathes, attackedImagesTargetPath):

    attackName = "rotation_cropped"
    rotationAngles, rangeMetadata = get_range_parameter(
        "angle in degree", 0, 360)

    originalImagesPathesResult = []
    attackedImagesPathesResult = []
    for originalImagePath in originalImagesPathes:
        originalImage = util.load_image(originalImagePath)
        originalImageName = util.get_filename_without_extension(
            originalImagePath)
        for rotationAngle in rotationAngles:
            # apply attack
            attackedImage = atk.rotation_cropped(
                originalImage, dRotationAngle=rotationAngle)
            imageName = "%s_%s_%s" % (
                originalImageName, attackName, str(rotationAngle))
            # save image
            attackedImagePath = save_attacked_image(
                attackedImage, attackedImagesTargetPath, imageName, "png")
            originalImagesPathesResult.append(originalImagePath)
            attackedImagesPathesResult.append(attackedImagePath)

    targetDecisions = np.full(
        len(originalImagesPathesResult), True, dtype=bool)

    return originalImagesPathesResult, attackedImagesPathesResult, targetDecisions, {"attack": attackName, "parameterRangeMetadata": rangeMetadata}


def rotation_fitted_hook(originalImagesPathes, attackedImagesTargetPath):

    attackName = "rotation_fitted"
    rotationAngles, rangeMetadata = get_range_parameter(
        "angle in degree", 0, 360)

    originalImagesPathesResult = []
    attackedImagesPathesResult = []
    for originalImagePath in originalImagesPathes:
        originalImage = util.load_image(originalImagePath)
        originalImageName = util.get_filename_without_extension(
            originalImagePath)
        for rotationAngle in rotationAngles:
            # apply attack
            attackedImage = atk.rotation(
                originalImage,  dRotationAngle=rotationAngle, bFit=True, tpBorderValue=(0, 0, 0))
            imageName = "%s_%s_%s" % (
                originalImageName, attackName, str(rotationAngle))
            # save image
            attackedImagePath = save_attacked_image(
                attackedImage, attackedImagesTargetPath, imageName, "png")
            originalImagesPathesResult.append(originalImagePath)
            attackedImagesPathesResult.append(attackedImagePath)

    targetDecisions = np.full(
        len(originalImagesPathesResult), True, dtype=bool)

    return originalImagesPathesResult, attackedImagesPathesResult, targetDecisions, {"attack": attackName, "parameterRangeMetadata": rangeMetadata}


def crop_uniform_hook(originalImagesPathes, attackedImagesTargetPath):

    attackName = "crop_uniform"
    cropSteps, rangeMetadata = get_range_parameter(
        "crop percent of the image from top, left, bottom, right", 0, 0.5)

    originalImagesPathesResult = []
    attackedImagesPathesResult = []
    for originalImagePath in originalImagesPathes:
        originalImage = util.load_image(originalImagePath)
        originalImageName = util.get_filename_without_extension(
            originalImagePath)
        for cropStep in cropSteps:
            # apply attack
            attackedImage = atk.crop_percentage(
                originalImage,  tpSlice=(cropStep, cropStep, cropStep, cropStep))
            imageName = "%s_%s_%s" % (
                originalImageName, attackName, str(cropStep))
            # save image
            attackedImagePath = save_attacked_image(
                attackedImage, attackedImagesTargetPath, imageName, "png")
            originalImagesPathesResult.append(originalImagePath)
            attackedImagesPathesResult.append(attackedImagePath)

    targetDecisions = np.full(
        len(originalImagesPathesResult), True, dtype=bool)

    return originalImagesPathesResult, attackedImagesPathesResult, targetDecisions, {"attack": attackName, "parameterRangeMetadata": rangeMetadata}


def crop_nonuniform_hook(originalImagesPathes, attackedImagesTargetPath):

    attackName = "crop_nonuniform"

    cropSets = []
    paramMinLimit = 0
    paramMaxLimit = 1
    print("Specify crop percentage (top, left, bottom, right)")
    while True:
        edgesDic = {"top": None, "left": None, "bottom": None, "right": None}
        for edgeKey in edgesDic:
            while True:
                valueString = input(edgeKey + ": ")
                try:
                    edgesDic[edgeKey] = float(valueString)
                except:
                    print("input is no number")
                    continue
                if (paramMinLimit <= edgesDic[edgeKey] <= paramMaxLimit):
                    break
                else:
                    print("input %f is bigger or smaller as domain of attack[%s, %s]" % (
                        edgesDic[edgeKey], str(paramMinLimit), str(paramMaxLimit)))
                    continue
        if (edgesDic["top"] + edgesDic["bottom"]) <= 1.0 and (edgesDic["left"] + edgesDic["right"] <= 1.0):
            cropSets.append(
                (edgesDic["top"], edgesDic["left"], edgesDic["bottom"], edgesDic["right"]))
        else:
            print("left + right and top + bottom have to be <= 1.0 ... once again")
            continue
        print("Would you like to add (a) another set of parameters or continue (c)?")
        addAdditionalParameters = input("[a/C]: ")
        if(addAdditionalParameters.lower() != "a"):
            break

    parameterSetMetadata = {"cropSets": cropSets}

    originalImagesPathesResult = []
    attackedImagesPathesResult = []
    for originalImagePath in originalImagesPathes:
        originalImage = util.load_image(originalImagePath)
        originalImageName = util.get_filename_without_extension(
            originalImagePath)
        for cropSet in cropSets:
            # apply attack
            attackedImage = atk.crop_percentage(
                originalImage,  tpSlice=cropSet)
            imageName = "%s_%s_%s" % (
                originalImageName, attackName, util.format_filename(str(cropSet)))
            # save image
            attackedImagePath = save_attacked_image(
                attackedImage, attackedImagesTargetPath, imageName, "png")
            originalImagesPathesResult.append(originalImagePath)
            attackedImagesPathesResult.append(attackedImagePath)

    targetDecisions = np.full(
        len(originalImagesPathesResult), True, dtype=bool)

    return originalImagesPathesResult, attackedImagesPathesResult, targetDecisions, {"attack": attackName, "parameterSetMetadata": parameterSetMetadata}


def jpeg_quality_hook(originalImagesPathes, attackedImagesTargetPath):

    attackName = "JPEG_quality"
    qualitySteps, rangeMetadata = get_range_parameter(
        "JPEG quality in percent", 0, 100)

    originalImagesPathesResult = []
    attackedImagesPathesResult = []
    for originalImagePath in originalImagesPathes:
        originalImage = util.load_image(originalImagePath)
        originalImageName = util.get_filename_without_extension(
            originalImagePath)
        for qualityStep in qualitySteps:
            # apply attack
            attackedImage = atk.jpeg_compression(
                originalImage,  lJPEGQuality=qualityStep)
            imageName = "%s_%s_%s" % (
                originalImageName, attackName, str(qualityStep))
            # save image
            attackedImagePath = save_attacked_image(
                attackedImage, attackedImagesTargetPath, imageName, "png")
            originalImagesPathesResult.append(originalImagePath)
            attackedImagesPathesResult.append(attackedImagePath)

    targetDecisions = np.full(
        len(originalImagesPathesResult), True, dtype=bool)

    return originalImagesPathesResult, attackedImagesPathesResult, targetDecisions, {"attack": attackName, "parameterRangeMetadata": rangeMetadata}


def speckle_noise_hook(originalImagesPathes, attackedImagesTargetPath):

    attackName = "speckle_noise"
    sigmaSteps, rangeMetadata = get_range_parameter(
        "sigma", 0, 1)

    originalImagesPathesResult = []
    attackedImagesPathesResult = []
    for originalImagePath in originalImagesPathes:
        originalImage = util.load_image(originalImagePath)
        originalImageName = util.get_filename_without_extension(
            originalImagePath)
        for sigmaStep in sigmaSteps:
            # apply attack
            attackedImage = atk.speckle_noise(originalImage,  dSigma=sigmaStep)
            imageName = "%s_%s_%s" % (
                originalImageName, attackName, str(sigmaStep))
            # save image
            attackedImagePath = save_attacked_image(
                attackedImage, attackedImagesTargetPath, imageName, "png")
            originalImagesPathesResult.append(originalImagePath)
            attackedImagesPathesResult.append(attackedImagePath)

    targetDecisions = np.full(
        len(originalImagesPathesResult), True, dtype=bool)

    return originalImagesPathesResult, attackedImagesPathesResult, targetDecisions, {"attack": attackName, "parameterRangeMetadata": rangeMetadata}


def salt_pepper_noise_hook(originalImagesPathes, attackedImagesTargetPath):

    attackName = "salt_pepper_noise"
    sigmaSteps, rangeMetadata = get_range_parameter(
        "sigma", 0, 1)

    originalImagesPathesResult = []
    attackedImagesPathesResult = []
    for originalImagePath in originalImagesPathes:
        originalImage = util.load_image(originalImagePath)
        originalImageName = util.get_filename_without_extension(
            originalImagePath)
        for sigmaStep in sigmaSteps:
            # apply attack
            attackedImage = atk.salt_and_pepper_noise(
                originalImage,  dAmount=sigmaStep)
            imageName = "%s_%s_%s" % (
                originalImageName, attackName, str(sigmaStep))
            # save image
            attackedImagePath = save_attacked_image(
                attackedImage, attackedImagesTargetPath, imageName, "png")
            originalImagesPathesResult.append(originalImagePath)
            attackedImagesPathesResult.append(attackedImagePath)

    targetDecisions = np.full(
        len(originalImagesPathesResult), True, dtype=bool)

    return originalImagesPathesResult, attackedImagesPathesResult, targetDecisions, {"attack": attackName, "parameterRangeMetadata": rangeMetadata}


def gauss_noise_hook(originalImagesPathes, attackedImagesTargetPath):

    attackName = "gauss_noise"
    sigmaSteps, rangeMetadata = get_range_parameter(
        "sigma", 0, 1)

    originalImagesPathesResult = []
    attackedImagesPathesResult = []
    for originalImagePath in originalImagesPathes:
        originalImage = util.load_image(originalImagePath)
        originalImageName = util.get_filename_without_extension(
            originalImagePath)
        for sigmaStep in sigmaSteps:
            # apply attack
            attackedImage = atk.gauss_noise(
                originalImage,  dSigma=sigmaStep)
            imageName = "%s_%s_%s" % (
                originalImageName, attackName, str(sigmaStep))
            # save image
            attackedImagePath = save_attacked_image(
                attackedImage, attackedImagesTargetPath, imageName, "png")
            originalImagesPathesResult.append(originalImagePath)
            attackedImagesPathesResult.append(attackedImagePath)

    targetDecisions = np.full(
        len(originalImagesPathesResult), True, dtype=bool)

    return originalImagesPathesResult, attackedImagesPathesResult, targetDecisions, {"attack": attackName, "parameterRangeMetadata": rangeMetadata}


def scale_uniform_hook(originalImagesPathes, attackedImagesTargetPath):

    attackName = "scale_uniform"
    scaleFactors, rangeMetadata = get_range_parameter(
        "scale factor", 0, 10)

    originalImagesPathesResult = []
    attackedImagesPathesResult = []
    for originalImagePath in originalImagesPathes:
        originalImage = util.load_image(originalImagePath)
        originalImageName = util.get_filename_without_extension(
            originalImagePath)
        for scaleFactor in scaleFactors:
            # apply attack
            attackedImage = atk.scale(
                originalImage,  lScalefactorX=scaleFactor, lScaleFactorY=scaleFactor)
            imageName = "%s_%s_%s" % (
                originalImageName, attackName, str(scaleFactor))
            # save image
            attackedImagePath = save_attacked_image(
                attackedImage, attackedImagesTargetPath, imageName, "png")
            originalImagesPathesResult.append(originalImagePath)
            attackedImagesPathesResult.append(attackedImagePath)

    targetDecisions = np.full(
        len(originalImagesPathesResult), True, dtype=bool)

    return originalImagesPathesResult, attackedImagesPathesResult, targetDecisions, {"attack": attackName, "parameterRangeMetadata": rangeMetadata}


def scale_nonuniform_hook(originalImagesPathes, attackedImagesTargetPath):

    attackName = "scale_nonuniform"

    scaleSets = []
    paramMinLimit = 0
    paramMaxLimit = 10
    print("Specify scale set (x, y)")
    while True:
        scaleDic = {"x": None, "y": None}
        for scaleKey in scaleDic:
            while True:
                valueString = input(scaleKey + ": ")
                try:
                    scaleDic[scaleKey] = float(valueString)
                except:
                    print("input is no number")
                    continue
                if (paramMinLimit <= scaleDic[scaleKey] <= paramMaxLimit):
                    break
                else:
                    print("input %f is bigger or smaller as domain of attack[%s, %s]" % (
                        scaleDic[scaleKey], str(paramMinLimit), str(paramMaxLimit)))
                    continue

        scaleSets.append(
            {"lScalefactorX": scaleDic["x"], "lScaleFactorY": scaleDic["y"]})

        print("Would you like to add (a) another set of parameters or continue (c)?")
        addAdditionalParameters = input("[a/C]: ")
        if(addAdditionalParameters.lower() != "a"):
            break

    parameterSetMetadata = {"scaleSets": scaleSets}

    originalImagesPathesResult = []
    attackedImagesPathesResult = []
    for originalImagePath in originalImagesPathes:
        originalImage = util.load_image(originalImagePath)
        originalImageName = util.get_filename_without_extension(
            originalImagePath)
        for scaleSet in scaleSets:
            # apply attack
            attackedImage = atk.scale(
                originalImage,  **scaleSet)
            imageName = "%s_%s_%s" % (
                originalImageName, attackName, util.format_filename(str(scaleSet)))
            # save image
            attackedImagePath = save_attacked_image(
                attackedImage, attackedImagesTargetPath, imageName, "png")
            originalImagesPathesResult.append(originalImagePath)
            attackedImagesPathesResult.append(attackedImagePath)

    targetDecisions = np.full(
        len(originalImagesPathesResult), True, dtype=bool)

    return originalImagesPathesResult, attackedImagesPathesResult, targetDecisions, {"attack": attackName, "parameterSetMetadata": parameterSetMetadata}


def contrast_hook(originalImagesPathes, attackedImagesTargetPath):

    attackName = "contrast"
    contrastFactors, rangeMetadata = get_range_parameter(
        "contrast factor", -128, 128)

    originalImagesPathesResult = []
    attackedImagesPathesResult = []
    for originalImagePath in originalImagesPathes:
        originalImage = util.load_image(originalImagePath)
        originalImageName = util.get_filename_without_extension(
            originalImagePath)
        for contrastFactor in contrastFactors:
            # apply attack
            attackedImage = atk.contrast(
                originalImage,  lContrast=contrastFactor)
            imageName = "%s_%s_%s" % (
                originalImageName, attackName, str(contrastFactor))
            # save image
            attackedImagePath = save_attacked_image(
                attackedImage, attackedImagesTargetPath, imageName, "png")
            originalImagesPathesResult.append(originalImagePath)
            attackedImagesPathesResult.append(attackedImagePath)

    targetDecisions = np.full(
        len(originalImagesPathesResult), True, dtype=bool)

    return originalImagesPathesResult, attackedImagesPathesResult, targetDecisions, {"attack": attackName, "parameterRangeMetadata": rangeMetadata}


def gamma_hook(originalImagesPathes, attackedImagesTargetPath):

    attackName = "gamma"
    gammaFactors, rangeMetadata = get_range_parameter(
        "gamma factor", 0, 10)

    originalImagesPathesResult = []
    attackedImagesPathesResult = []
    for originalImagePath in originalImagesPathes:
        originalImage = util.load_image(originalImagePath)
        originalImageName = util.get_filename_without_extension(
            originalImagePath)
        for gammaFactor in gammaFactors:
            # apply attack
            attackedImage = atk.gamma_adjustment(
                originalImage,  dGamma=gammaFactor)
            imageName = "%s_%s_%s" % (
                originalImageName, attackName, str(gammaFactor))
            # save image
            attackedImagePath = save_attacked_image(
                attackedImage, attackedImagesTargetPath, imageName, "png")
            originalImagesPathesResult.append(originalImagePath)
            attackedImagesPathesResult.append(attackedImagePath)

    targetDecisions = np.full(
        len(originalImagesPathesResult), True, dtype=bool)

    return originalImagesPathesResult, attackedImagesPathesResult, targetDecisions, {"attack": attackName, "parameterRangeMetadata": rangeMetadata}


def overlay_hook(originalImagesPathes, attackedImagesTargetPath):

    attackName = "overlay"

    print("\nSpecify the full path to the overlay image.")
    overlayImage = None
    overlayImageFilePath = None
    while True:
        overlayImageFilePath = util.escape_home_in_path(
            input("Overlay image: "))
        if util.check_if_file_exists(overlayImageFilePath):
            # return all images in path as sorted list
            try:
                overlayImage = util.load_image(overlayImageFilePath)
                break
            except:
                print("%s seems to be no image file." % overlayImageFilePath)
        else:
            print("image %s is not existend" % overlayImageFilePath)
            correctionDecision = input(
                "would you like to correct it or quit [c/Q]: ")
            print(correctionDecision)
            if not correctionDecision.lower() == "c":
                sys.exit(1)

    originalImagesPathesResult = []
    attackedImagesPathesResult = []
    for originalImagePath in originalImagesPathes:
        originalImage = util.load_image(originalImagePath)
        originalImageName = util.get_filename_without_extension(
            originalImagePath)

        # apply attack
        attackedImage = atk.blend_pattern(
            originalImage,  aPatternImage=overlayImage)
        imageName = "%s_%s_%s" % (
            originalImageName, attackName, util.get_filename_without_extension(overlayImageFilePath))
        # save image
        attackedImagePath = save_attacked_image(
            attackedImage, attackedImagesTargetPath, imageName, "png")
        originalImagesPathesResult.append(originalImagePath)
        attackedImagesPathesResult.append(attackedImagePath)

    targetDecisions = np.full(
        len(originalImagesPathesResult), True, dtype=bool)

    return originalImagesPathesResult, attackedImagesPathesResult, targetDecisions, {"attack": attackName, "blend_image": overlayImageFilePath}


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


@attack_challenge_group.menu(title="Rotation (cropped)")
def attack_rotation_cropped():
    print("I am cropped rotation")
    attack_challenge_creator(rotation_cropped_hook)


@attack_challenge_group.menu(title="Rotation (fitted)")
def attack_rotation_fitted():
    print("I am fitted rotation")
    attack_challenge_creator(rotation_fitted_hook)


@attack_challenge_group.menu(title="Crop (uniform)")
def attack_crop_uniform():
    print("I am crop uniform")
    attack_challenge_creator(crop_uniform_hook)


@attack_challenge_group.menu(title="Crop (nonuniform)")
def attack_crop_nonuniform():
    print("I am crop nonuniform")
    attack_challenge_creator(crop_nonuniform_hook)


@attack_challenge_group.menu(title="Overlay")
def attack_overlay():
    print("I am overlay")
    attack_challenge_creator(overlay_hook)


@attack_challenge_group.menu(title="JPEG Quality")
def attack_jpeg_quality():
    print("I am JPEG quality")
    attack_challenge_creator(jpeg_quality_hook)


@attack_challenge_group.menu(title="Speckle Noise")
def attack_speckle_noise():
    print("I am speckle_noise")
    attack_challenge_creator(speckle_noise_hook)


@attack_challenge_group.menu(title="Salt and Pepper Noise")
def attack_salt_and_pepper_noise():
    print("I am salt_and_pepper_noise")
    attack_challenge_creator(salt_pepper_noise_hook)


@attack_challenge_group.menu(title="Gauss Noise")
def attack_gauss_noise():
    print("I am gauss_noise")
    attack_challenge_creator(gauss_noise_hook)


@attack_challenge_group.menu(title="Scale (uniform)")
def attack_scale_uniform():
    print("I am scale (uniform)")
    attack_challenge_creator(scale_uniform_hook)


@attack_challenge_group.menu(title="Scale (nonuniform)")
def attack_scale_nonuniform():
    print("I am scale (nonuniform)")
    attack_challenge_creator(scale_nonuniform_hook)


@attack_challenge_group.menu(title="Contrast")
def attack_contrast():
    print("I am contrast")
    attack_challenge_creator(contrast_hook)


@attack_challenge_group.menu(title="Gamma")
def attack_gamma():
    print("I am gamma")
    attack_challenge_creator(gamma_hook)


if __name__ == '__main__':
    pm = Pmatch()
    climenu.run()

# TODO: add shuffle challenge (from set of images x match and 1-x do not
# match; random generated)
