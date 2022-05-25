import argparse

from tools.pipes import PipelineDaemon, State

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
    pd = PipelineDaemon()
    pd.build_pipeline(state=State(parser=parser))
    pd.execute_pipeline()
