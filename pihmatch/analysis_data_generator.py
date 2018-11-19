
import pandas as pd
from pihmatch import Pihmatch


class AnalysisDataGenerator(object):
    def __init__(self, sDBPath=None):
        pm = Pihmatch(sDBPath)
        dfChallenges = pd.DataFrame(pm.get_challenges())
        if dfChallenges.empty:
            raise Exception("currently there are no challenges defined yet")
        dfTests = pd.DataFrame(pm.get_tests())
        if dfTests.empty:
            raise Exception("currently no test have been run yet")

        dfChallenges = dfChallenges.drop(
            labels=["originalImages", "comparativeImages", "targetDecisions"], axis=1)
        dfTests = pd.merge(dfTests, dfChallenges, how="inner",
                           left_on="challenge", right_on="challenge")
        self.dataframe = dfTests

    def get_pandas_dataframe(self):
        return self.dataframe

    def save_pandas_dataframe_to_file(self, sPathToFile):
        if no sPathToFile:
            raise Exception("path to file not specified")
        self.dataframe.to_csv(sPathToFile)
