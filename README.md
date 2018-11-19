# PIHMATCH

**Perceptual Image Hashing Matching Challenge** is a benchmarking framework to test Perceptual Image Hashing Algorithms that should be used for content identification. It allows researchers to create standardized challenges against which they can run their perceptual image hashing algorithms in different configurations.

## Basic Idea

The underlying idea of PIHMATCH is this: You as a scientist create a standardized set of challenges. These consist of a series of images and comparison images, whereby for each image-comparison image pair it is defined whether the perceptual image hashing algorithm must recognize these images as identical or different. Challenges can be created, for example, by subjecting images to various manipulations (scaling, adding noise, etc.) or by randomly combining images from a larger pool of images. For a more detailed explanation, please refer to the Create challenges section.

| Original Image                       | Comparative Image                      | Equal? |
| ------------------------------------ | -------------------------------------- | ------ |
| <img src="_img/p1.png" height="100"> | <img src="_img/p1_S.png" height="100"> | True   |
| <img src="_img/p2.png" height="100"> | <img src="_img/p2_D.png" height="100"> | False  |
| <img src="_img/p3.png" height="100"> | <img src="_img/p3_S.png" height="100"> | True   |

Having a set of challenges you can run different test on them. A test if defined by a wrapper function around a perceptional image hashing algorithm performing the following steps:

1. load original and comparative images from path
2. for every original and comparative image pair calculate the hash of both images
3. decide if the algorithm considers the images to be equal for example based on a hamming distance and a threshold

Based on the correct decisions defined in the challenge an error-rate will be calculated for the test. Based on the error rates, the suitability of different configurations of the same perceptual image hashing algorithm or different perceptual image hashing algorithms can now be evaluated. Researchers can export the data as pandas dataframe, which provides maximum flexibility for further analysis.

## Requirements

Currently the framework was tested on `Linux` only.

In order to work with `sqlite3` please make sure your environments supports the python wrapper with all libraries needed.

## Installation

Clone the repository, change directory to the repository, create a new virtual environment (optional), run the installer script.

```bash
python3 setup.py
```

## Create challenges

-   challenge creator script
-   types of challenges
-

## Run tests

## Analyze data

```python
s = "Python syntax highlighting"
print s
```
