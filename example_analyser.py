#!/usr/bin/env python3

import pandas as pd
from twizzle import AnalysisDataGenerator


if __name__ == "__main__":
    # load data in a pandas dataframe
    sDBPath = "test.db"
    dfTests = AnalysisDataGenerator(sDBPath).get_pandas_dataframe()

    # do something with the dataframe
    print(dfTests)
