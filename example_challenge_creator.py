from twizzle import Twizzle


if __name__ == "__main__":
    sDBPath = "test.db"
    tw = Twizzle(sDBPath)

    sChallengeName = "image_hashing_challenge_print_scan_1"

    aOriginals = ["c1.png", "c2.png", "c3.png"]
    aComparatives = ["c1.png", "c5.png", "c6.png"]
    aTargetDecisions = [True, False, False]

    dicMetadata = {
        "printer": "DC783",
        "paper": "recycled paper",
        "print_dpi": 300
    }

    tw.add_challenge(sChallengeName, aOriginals,
                     aComparatives, aTargetDecisions, dicMetadata)
