import json
from threading import Thread, Event
import time
from contextlib import closing
from queue import Queue, Full
from typing import List
from ouster import client as cl, pcap
from ouster.client import LidarPacket
from requests import get

from utilities.utils import FileUtils, Cloud3dUtils
from tools.structs.custom_structs import Ch, MatrixCloud, PopList

default_pcap: str = '/pcap'
default_metadata: str = '/metadata'


# all_channels: list[cl.ChanField] = [cl.ChanField.RANGE, cl.ChanField.NEAR_IR, cl.ChanField.REFLECTIVITY]  # immutable

class SensorCommand:
    pass


class StreamConfig:
    s_rate = 'sample_rate'  # pause between scan sampling in seconds
    queue_size = 'queue_size'
    timer: bool
    time_end: int
    azimuth: float
    range: float
    elevation: float
    save_local: bool
    local_path: bool
    cache_size: int


class SensorParams:
    def __init__(self, config: dict):
        self.host = config['hostname']
        self.lidar_port = config['lidar_port']
        self.imu_port = config['imu_port']
        self.pcap_path = default_pcap
        self.metadat_path = default_metadata

        # these 2 to stream config
        self.output: PopList = config['output']
        self.sample_rate = config['sample_rate']


class _IO:
    source: cl.PacketSource = None

    def __init__(self, params: SensorParams):
        self.host = params.host
        self.output = params.output
        self.config = cl.SensorConfig()
        self.config.udp_port_lidar = params.lidar_port
        self.config.udp_port_imu = 7503
        udp_dest = str(get('https://api.ipify.org').content.decode('utf8'))
        print(udp_dest)
        self.config.udp_dest = udp_dest
        self.config.operating_mode = cl.OperatingMode.OPERATING_NORMAL
        self.config.lidar_mode = cl.LidarMode.MODE_2048x10
        self.pcap_path = params.pcap_path
        self.meta_path = params.metadat_path
        cl.set_config(self.host, self.config)
        self.__set_paths()
        self.__fetch_meta()

    def __set_paths(self, sep='/'):
        pcap_p = self.pcap_path
        meta_p = self.meta_path
        self.pcap_file = f"{self.host}.pcap"
        self.meta_file = f"{self.host}.json"
        self.pcap_path = sep.join([pcap_p, self.pcap_file])
        self.meta_path = sep.join([meta_p, self.meta_file])

    def __init_dirs(self):
        pass

    def __fetch_meta(self):
        print(self.host, self.config.udp_port_lidar)
        with closing(cl.Sensor(hostname=self.host,
                               lidar_port=self.config.udp_port_lidar)) as source:
            source.write_metadata(self.meta_file)

    def __get_source(self):
        with open(self.meta_file, 'r') as f:
            self.metadata = cl.SensorInfo(f.read())

    def stream_packets(self, q: Queue):
        """Only LiDAR data! Read stream from pcap file. Less latency. More packet access.
         Packet does not represent full frame"""
        for packet in self.source:
            if isinstance(packet, LidarPacket):
                try:
                    q.put_nowait(packet)
                except Full:
                    continue

    def stream_scans(self):
        """
        Read SDK-controlled stream of lidar data. More latency.
         Incomplete & late frames are dropped from stream internally.
         """
        with closing(cl.Scans.stream(self.host, self.config.udp_port_lidar,
                                     complete=False)) as stream:
            xyzlut = cl.XYZLut(self.metadata)
            pls: PopList = self.output
            for scan in stream:
                m = Cloud3dUtils.get_matrix_cloud(xyzlut, scan, Ch.channel_arr)
                print('Sampled frame')
                pls.add(m)
                time.sleep(self.config['sample_rate'])


default_sens_config = 'sensor/sensor_config.yaml'
default_stream_config = 'sensor/stream_config.yaml'

sensor_ip = '192.168.178.11'
sensor_port = 7502


def main():
    q: PopList[MatrixCloud] = PopList()
    params = {
        'hostname': sensor_ip,
        'port': sensor_port,
        'sample_rate': 1
    }

    io = _IO(SensorParams(params))
    io.stream_scans(q, params)


if __name__ == "__main__":
    main()
