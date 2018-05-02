#!/usr/bin/env python3

import config as conf
import numpy as np
import pandas as pd
from pmatch import Pmatch


if __name__ == "__main__":
    # load data in a pandas dataframe
    pm = Pmatch()
    dfTests = pd.DataFrame(pm.get_tests())

    # do something with the dataframe
    print(dfTests)
