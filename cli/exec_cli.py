import argparse

from routine_set.routine_sets import StreetAnalytics
from tools.pipeline import Pipeline, State

"""
@Module: CLI
@Description: Simple CLI with 
@Author: Radu Rebeja
"""
"""Project CLI
First interface a simple ArgumentParser
"""


def parse_config():
    argprs = argparse.ArgumentParser(description='StreetAnalytics Project CLI')
    argprs.add_argument('-v', "--verbose", help='Verbose output', action="store_true")
    return argprs


if __name__ == '__main__':
    parser = parse_config()
    pd = Pipeline()
    pd.build_pipeline(state=State(parser=parser), rs=StreetAnalytics())
    pd.execute_pipeline()
