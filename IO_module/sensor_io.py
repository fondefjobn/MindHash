from contextlib import closing
from queue import Queue, Full
from typing import List, Any

from ouster import client, sdk, pcap
import numpy as np
from ouster.client import _client as cl, core, LidarPacket

default_pcap: str = '/pcap'
default_metadata: str = '/metadata'

all_channels: list[cl.ChanField] = [cl.ChanField.RANGE, cl.ChanField.NEAR_IR, cl.ChanField.REFLECTIVITY]  # immutable


class ConfigParams:
    def __init__(self, hostname: str):  # change to YML parser
        self.host = hostname
        self.lidar_port = 7502
        self.imu_port = 7503
        self.op_mode = cl.OperatingMode.OPERATING_NORMAL
        self.lidar_mode = cl.LidarMode.MODE_1024x10
        self.pcap_path = default_pcap
        self.metadat_path = default_metadata


class MatrixCloud:
    def __init__(self):
        self.clouds = {}


class IO:
    config: cl.SensorConfig = cl.SensorConfig()
    source: client.PacketSource = None

    def __init__(self, params: ConfigParams):
        self.host = params.host
        self.config = cl.SensorConfig()
        self.config.udp_port_lidar = params.lidar_port
        self.config.udp_port_imu = params.imu_port
        self.config.operating_mode = params.op_mode
        self.config.lidar_mode = params.lidar_mode
        self.pcap_path = params.pcap_path
        self.meta_path = params.metadat_path
        cl.set_config(self.host, self.config,
                      persist=True, udp_dest_auto=True)
        self.__set_paths()
        self.__get_source()

    def __set_paths(self, sep='/'):
        pcap_p = self.pcap_path
        meta_p = self.meta_path
        pcap_file = {f"{self.host}.pcap"}
        meta_file = {f"{self.host}.json"}
        self.pcap_path = sep.join([pcap_p, pcap_file])
        self.meta_path = sep.join([meta_p, meta_file])

    def __init_dirs(self):
        pass

    def __fetch_meta(self):
        with closing(client.Sensor(self.host)) as source:
            source.write_metadata(self.meta_path)

    def __get_source(self):
        self.__fetch_meta()
        with open(self.pcap_path, 'r') as f:
            self.metadata = cl.SensorInfo(f.read())
        return pcap.Pcap(self.pcap_path, self.metadata)

    def stream_packets(self, queue: Queue[LidarPacket]):
        """Only LiDAR data! Read stream from pcap file. Less latency. More packet access.
         Packet does not represent full frame"""
        for packet in self.source:
            if isinstance(packet, LidarPacket):
                try:
                    queue.put_nowait(packet)
                except Full:
                    continue

    def stream_scans(self, queue: Queue[MatrixCloud], channels: list[cl.ChanField] = all_channels):
        """
        Read SDK-controlled stream of lidar data. More latency.
         Incomplete & late frames are dropped from stream internally.
         """
        with closing(client.Scans.stream(self.host, self.config.udp_port_lidar,
                                         complete=False)) as stream:
            xyzlut = cl.XYZLut(self.metadata)
            for scan in stream:
                try:
                    queue.put_nowait(self.__get_matrix_cloud(xyzlut, scan, channels))
                except Full:
                    continue

    @staticmethod
    def __get_matrix_cloud(xyzlut: cl.XYZLut, scan,
                           channels: list[cl.ChanField]) -> MatrixCloud:
        """"Create separate XYZ point-clouds for separate channels.
            Reading from cloud is done through dict destructuring.
            For keys use the client.ChanFields RANGE | SIGNAL | NEAR_IR | REFLECTIVITY"""
        matrix_cloud = MatrixCloud()
        for channel in channels:
            xyz = xyzlut(scan.field(channel))
            x, y, z = [c.flatten() for c in np.dsplit(xyz, 3)]
            matrix_cloud.clouds[channel] = [x, y, z]
        return matrix_cloud
