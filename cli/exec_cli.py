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
    # argprs.add_argument('-v', "--verbose", help='Verbose output', action="store_true") unsafe
    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='StreetAnalytics Project CLI')
    pd = Pipeline()
    pd.build_pipeline(state=State(parser=parser), rs=StreetAnalytics())
    pd.execute_pipeline()
