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
    argprs.add_argument('--sensor', default=None,
                           help='Sensor defining input type', choices=['ouster'], type=str.lower, required=True)
    argprs.add_argument('--n', type=int, default=None, help='Limit number N of processed frames')
    argprs.add_argument('--live',
                           help='Live-stream processing mode', action="store_true")
    argprs.add_argument('--eval',
                           help='Evaluate input with a ML Model', action="store_true")
    argprs.add_argument('--host', type=str, default=None, help='Sensor hostname')
    argprs.add_argument('--port', type=int, default=None, help='Sensor port')
    argprs.add_argument('--ml', type=str.upper, default='PVRCNN', choices=['PVRCNN','PVRCNN++', 'POINTRCNN', 'POINTPILLAR',
                                                                           'PARTA2', 'PP_NU'],
                           help='Model name')
    argprs.add_argument('--mlpath', type=str, default=None, help='Model path from content root')
    argprs.add_argument('--input', type=str, default=None, help='PCAP/other file for post-processing')
    argprs.add_argument('--ext', type=str, default=None, help='File input extension')
    argprs.add_argument('--meta', type=str, default=None, help='JSON metadata file for input file')
    argprs.add_argument('-v', "--verbose", help='Verbose output', action="store_true")
    argprs.add_argument('--visual', help='Visualize results with Open3D', action="store_true")

    argprs.add_argument('--stats', help='Generate statistic', action="store_true")
    return argprs


if __name__ == '__main__':
    parser = parse_config()
    pd = PipelineDaemon()
    pd.build_pipeline(state=State(parser=parser))
    pd.execute_pipeline()
