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
    parser = argparse.ArgumentParser(description='StreetAnalytics Project CLI')
    parser.add_argument('--sensor', default=None,
                        help='Sensor defining input type', choices=['ouster'], type=str.lower, required=True)
    parser.add_argument('--n', type=int, default=None, help='Limit number N of processed frames')
    parser.add_argument('--live',
                        help='Live-stream processing mode', action="store_true")
    parser.add_argument('--eval',
                        help='Evaluate input with a ML Model', action="store_true")
    parser.add_argument('--host', type=str, default=None, help='Sensor hostname')
    parser.add_argument('--port', type=int, default=None, help='Sensor port')
    parser.add_argument('--ml', type=str.upper, default='PVRCNN', choices=['PVRCNN', 'POINTRCNN', 'POINTPILLAR',
                                                                           'PARTA2', 'PP_NU'],
                        help='Model name')
    parser.add_argument('--mlpath', type=str, default=None, help='Model path from content root')
    parser.add_argument('--input', type=str, default=None, help='PCAP/other file for post-processing')
    parser.add_argument('--ext', type=str, default=None, help='File input extension')
    parser.add_argument('--meta', type=str, default=None, help='JSON metadata file for input file')
    parser.add_argument('-v', "--verbose", help='Verbose output', action="store_true")
    parser.add_argument('--visual', help='Visualize results with Open3D', action="store_true")
    parser.add_argument('--export', nargs='+', choices=['predictions', 'points'], help='Save results locally')
    parser.add_argument('--stats', help='Generate statistic', action="store_true")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_config()
    pd = PipelineDaemon()
    pd.build_pipeline(state=State(args))
    pd.execute_pipeline()
