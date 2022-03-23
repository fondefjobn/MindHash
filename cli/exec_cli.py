import argparse
from sensor.sensor_controller import SensorController as SControl
from tools.pipes.pipelines import build_pipeline, execute_pipeline

"""Project CLI
We will use for debugging and initial usage a simple argparser,
after MVP completion:
*interactive 
"""


def parse_config():
    parser = argparse.ArgumentParser(description='StreetAnalytics Project CLI')
    parser.add_argument('--live', default=None,
                        help='Live-stream processing mode', action="store_true")
    parser.add_argument('--post', default=None,
                        help='post-process mode', action="store_true")
    parser.add_argument('--eval', default=None,
                        help='Evaluate input with a ML Model', action="store_true")
    parser.add_argument('--host', type=str, default=None, help='Sensor hostname')
    parser.add_argument('--port', type=str, default=None, help='Sensor port')
    parser.add_argument('--ml', type=str, default='PVRCNN', choices=['PVRCNN'],
                        help='Model name')
    parser.add_argument('--mlpath', type=str, default=None, help='Model path from content root')
    parser.add_argument('--pcap', type=str, default=None, help='PCAP file for post-processing')
    parser.add_argument('--meta', type=str, default=None, help='JSON metadata file for post-processing')
    parser.add_argument('-v', "--verbose", help='Verbose output', action="store_true")
    parser.add_argument('--visual', help='Visualize results with Open3D', action="store_true")
    parser.add_argument('--export', help='Save results locally', action="store_true")
    parser.add_argument('--stats', help='Generate statistics', action="store_true")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    cfg = parse_config()
    pipeline = build_pipeline(cfg)
    execute_pipeline(pipeline)