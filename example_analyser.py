#!/usr/bin/env python3

import pandas as pd
from pihmatch import AnalysisDataGenerator


if __name__ == "__main__":
    # load data in a pandas dataframe
    dfTests = AnalysisDataGenerator().get_pandas_dataframe()

    # do something with the dataframe
    print(dfTests)
