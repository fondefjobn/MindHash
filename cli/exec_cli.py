import argparse
from typing import Dict, Any

from tools.pipes import build_pipeline, execute_pipeline, State
from tools.pipes.bundle_list import __generate_list__

"""Project CLI
We will use for debugging and initial usage a simple argparser,
after MVP completion:
*interactive 
"""



def parse_config():
    parser = argparse.ArgumentParser(description='StreetAnalytics Project CLI')
    parser.add_argument('--sensor', default=None,
                        help='Sensor defining input type', choices=['ouster'], type=str.lower, required=True)
    parser.add_argument('--N', type=int, default=None, help='Limit number N of processed frames')
    parser.add_argument('--live',
                        help='Live-stream processing mode', action="store_true")
    parser.add_argument('--post',
                        help='post-process mode', action="store_true")
    parser.add_argument('--eval',
                        help='Evaluate input with a ML Model', action="store_true")
    parser.add_argument('--host', type=str, default=None, help='Sensor hostname')
    parser.add_argument('--port', type=int, default=None, help='Sensor port')
    parser.add_argument('--ml', type=str.upper, default='PVRCNN', choices=['PVRCNN'],
                        help='Model name')
    parser.add_argument('--mlpath', type=str, default=None, help='Model path from content root')
    parser.add_argument('--input', type=str, default=None, help='PCAP/other file for post-processing')
    parser.add_argument('--ext', type=str, default=None, help='File input extension')
    parser.add_argument('--meta', type=str, default=None, help='JSON metadata file for input file')
    parser.add_argument('-v', "--verbose", help='Verbose output', action="store_true")
    parser.add_argument('--visual', help='Visualize results with Open3D', action="store_true")
    parser.add_argument('--export', help='Save results locally', action="store_true")
    parser.add_argument('--stats', help='Generate statistic', action="store_true")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_config()
    pipeline = build_pipeline(state=State(args), bundles=__generate_list__(args))
    execute_pipeline(pipeline)
