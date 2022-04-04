import json
from argparse import Namespace
from threading import Thread, Event
import time
from contextlib import closing
from queue import Queue, Full
from typing import List

import numpy as np
from easydict import EasyDict
from ouster import client, pcap
from ouster.client import LidarPacket
from requests import get

from sensor.sensor_template import Sensor
from utilities.utils import FileUtils, Cloud3dUtils
from tools.structs.custom_structs import Ch, MatrixCloud, PopList

default_pcap: str = '/pcap'
default_metadata: str = '/metadata'
CONFIG: str = '../sensor/set/ouster/config.yaml'
"""
@Module: Ouster Sensor 
@Description: Tools for livestreaming from an Ouster Sensor
@Author: Radu Rebeja
"""


class _IO_CONFIG_:
    """
    dictionary
    """
    SAMPLE_RATE: str
    LIST_SIZE: str
    timer: bool  #
    time_end: int  #
    azimuth: float  #
    range: float  #
    elevation: float  #
    save_local: bool  #
    local_path: bool  #


class _IO_(Sensor):
    source: client.PacketSource = None

    def __init__(self, args: Namespace, output: PopList):
        params = EasyDict(FileUtils.parse_yaml(CONFIG))
        print(params)
        self.output = output
        self.host = params.HOST if args.host is None else args.host
        self.udp_port = params.LIDAR_PORT if args.port is None else args.port
        self.PCAP = params.PCAP if args.input is None else args.input
        self.META = params.META if args.meta is None else args.meta
        self.config = client.SensorConfig()
        self.config.udp_port_lidar = params.LIDAR_PORT
        self.config.udp_port_imu = params.IMU_PORT
        self.meta_path = params.META_PATH
        self.pcap_path = params.PCAP_PATH
        udp_dest = str(get('https://api.ipify.org').content.decode('utf8'))
        print('API read IPv4: ', udp_dest)
        self.config.udp_dest = udp_dest
        self.config.operating_mode = client.OperatingMode.OPERATING_NORMAL
        self.config.lidar_mode = client.LidarMode.MODE_2048x10
        self.__set_paths__()
        #  client.set_config(self.host, self.config) Requires testing with live sensor
        #   self.__fetch_meta__()

    def __set_paths__(self, sep='/'):
        pcap_p = self.PCAP
        meta_p = self.meta_path
        self.pcap_file = f"{self.host}.pcap"
        self.meta_file = f"{self.host}.json"
        self.pcap_path = sep.join([pcap_p, self.pcap_file])
        self.meta_path = sep.join([meta_p, self.meta_file])

    def __init_dirs__(self):
        pass

    def __fetch_meta__(self):
        print(self.host, self.config.udp_port_lidar)
        with closing(client.Sensor(hostname=self.host,
                                   lidar_port=self.config.udp_port_lidar)) as source:
            source.write_metadata(self.meta_file)

    def __get_source__(self):
        with open(self.meta_file, 'r') as f:
            self.metadata = client.SensorInfo(f.read())

    def stream_packets(self, q: Queue):
        """Only LiDAR data! Read stream from pcap file. Less latency. More packet access.
         Packet does not represent full frame"""
        for packet in self.source:
            if isinstance(packet, LidarPacket):
                try:
                    q.put_nowait(packet)
                except Full:
                    continue

    def read(self):
        """
        Read SDK-controlled stream of lidar data. More latency.
         Incomplete & late frames are dropped from stream internally.
         """
        with closing(client.Scans.stream(self.host, self.config.udp_port_lidar,
                                         complete=False)) as stream:
            xyzlut = client.XYZLut(self.metadata)
            pls: PopList = self.output
            for scan in stream:
                m = self.get_matrix_cloud(xyzlut, scan, Ch.channel_arr)
                print('Sampled frame')
                pls.add(m)
                time.sleep(self.config['sample_rate'])

    def convert(self):
        with open(self.META) as f:
            metadata = client.SensorInfo(f.read())
            self.METADATA = metadata
            source = pcap.Pcap(self.PCAP, metadata)
            self.ouster_pcap_to_mxc(source, metadata, frame_ls=self.output, N=100)

    def ouster_pcap_to_mxc(self, source: client.PacketSource, metadata: client.SensorInfo, frame_ls: PopList,
                           N: int = 1,
                           ) -> List[MatrixCloud]:
        # [doc-stag-pcap-to-csv]

        from itertools import islice
        # precompute xyzlut to save computation in a loop
        xyzlut = client.XYZLut(metadata)
        # create an iterator of LidarScans from pcap and bound it if num is specified
        scans = iter(client.Scans(source))
        if N:
            scans = islice(scans, N)
        for idx, scan in enumerate(scans):
            frame_ls.add(self.get_matrix_cloud(xyzlut, scan, Ch.channel_arr))
        return frame_ls

    def get_matrix_cloud(self, xyzlut: client.XYZLut, scan, channel_arr: List[str]) -> MatrixCloud:
        """"Create separate XYZ point-clouds for separate channels.
            Reading from cloud is done through dict destructuring.
            For keys use the client.ChanFields RANGE | SIGNAL | NEAR_IR | REFLECTIVITY"""
        matrix_cloud = MatrixCloud()
        field_names = channel_arr

        # use integer mm to avoid loss of precision casting timestamps
        xyz = (xyzlut(scan.field(client.ChanField.RANGE))).astype(float)
        xyz = client.destagger(self.METADATA, xyz)

        for ix, ch in enumerate(scan.fields):
            f = scan.field(ch)
            matrix_cloud.channels[field_names[ix]] = f
        x, y, z = [c.flatten() for c in np.dsplit(xyz, 3)]
        matrix_cloud.clouds[Ch.XYZ] = [x, y, z]
        return matrix_cloud


default_sens_config = 'sensor/config.yaml'
default_stream_config = 'sensor/config.yaml'


def main():
    """
    Script testing function
    Returns void
    -------

    """
    sensor_ip = '192.168.178.11'
    sensor_port = 7502

    q: PopList[MatrixCloud] = PopList()

    io = _IO_(q)
    io.read()


if __name__ == "__main__":
    main()
