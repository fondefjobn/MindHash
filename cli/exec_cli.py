import argparse
import pipes
from sensor.sensor_controller import SensorController as SControl

"""Project CLI
We will use for debugging and initial usage a simple argparser,
after MVP completion:
*interactive 
"""


arg_dict:dict = {
    'live': SControl.
}

def build_pipeline(args):
    pass

def parse_config():
    parser = argparse.ArgumentParser(description='StreetAnalytics Project CLI')
    parser.add_argument('--live', type=int, default=0,
                        help='Specify data processing type: 1 = live-stream  , 0 = post-process')
    parser.add_argument('-h', '--host', type=str, default=None, help = 'Sensor hostname')
    parser.add_argument('-p', '--port', type=str, default=None, help='Sensor port')
    parser.add_argument('--ml', type=str, default='demo_data',
                        help='Model name')
    parser.add_argument('--mlpath', type=str, default=None, help='Model path from content root')
    parser.add_argument('--pcap', type=str, default=None, help='PCAP file for post-processing')
    parser.add_argument('--meta', type=str, default=None, help='JSON metadata file for post-processing')
    parser.add_argument('-v', "--verbose", help='Verbose output', action="store_true")
    parser.add_argument('-vi', '--visual', help='Visualize results', action="store_true")
    parser.add_argument('-l', '--local', help='Save results locally', action="store_true")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    exec_pipeline(parse_config())
