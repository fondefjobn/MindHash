import collections
import gc
import logging
import time
from argparse import Namespace
from contextlib import closing
from dataclasses import dataclass
from queue import Queue, Full
from typing import List

import numpy as np
from easydict import EasyDict
from ouster import client, pcap
from ouster.client import LidarPacket
from requests import get

from sensor.sensor_template import Sensor, SensorData
from tools.structs.custom_structs import Ch, MatrixCloud, PopList
from utilities.utils import FileUtils

"""
@Module: Ouster Sensor 
@Description: Tools for livestreaming from an Ouster Sensor
This module uses functionalities from Ouster-SDK python library to 
operate with an Ouster Sensor
Tasks:
-Reading sensor output files in post-processing (tested)
-Reading live from a sensor (not tested)
@Author: Radu Rebeja
"""

default_pcap: str = '/pcap'
default_metadata: str = '/metadata'
CONFIG: str = 'config.yaml'

@dataclass
class IO_CONFIG:
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

    def __init__(self, args: Namespace, output: PopList, logger: logging.Logger = None):
        super().__init__(sd=SensorData(output, CONFIG, args=args, logger=logger, __file__=__file__))
        config = self.config
        print(config)
        self.host = config.HOST if args.host is None else args.host
        self.udp_port = config.LIDAR_PORT if args.port is None else args.port
        self.PCAP = config.PCAP if args.input is None else args.input
        self.META = config.META if args.meta is None else args.meta
        self.s_cfg = client.SensorConfig()
        self.s_cfg.udp_port_lidar = config.LIDAR_PORT
        self.s_cfg.udp_port_imu = config.IMU_PORT
        self.meta_path = config.META_PATH
        self.pcap_path = config.PCAP_PATH
        self.METADATA = None
        udp_dest = str(get('https://api.ipify.org').content.decode('utf8'))
        print('API read IPv4: ', udp_dest)
        if not (self.PCAP or self.META):
            raise IOError("Missing input for post-processing")
        self.s_cfg.udp_dest = udp_dest
        self.s_cfg.operating_mode = client.OperatingMode.OPERATING_NORMAL
        self.s_cfg.lidar_mode = client.LidarMode.MODE_2048x10
        self.__set_paths__()
        #  client.set_config(self.host, self.config) Requires testing with live sensor
        #  self.__fetch_meta__()

    def __set_paths__(self, sep='/'):
        pcap_p = self.PCAP
        meta_p = self.meta_path
        self.pcap_file = f"{self.host}.pcap"
        self.meta_file = f"{self.host}.json"
        self.pcap_path = sep.join([pcap_p, self.pcap_file])
        self.meta_path = sep.join([meta_p, self.meta_file])

    def fconfig(self):
        return CONFIG

    def __fetch_meta__(self):
        print(self.host, self.s_cfg.udp_port_lidar)
        with closing(client.Sensor(hostname=self.host,
                                   lidar_port=self.s_cfg.udp_port_lidar)) as source:
            source.write_metadata(self.meta_file)

    def __get_source__(self):
        with open(self.meta_file, 'r') as f:
            self.SENSOR_INFO = client.SensorInfo(f.read())

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
        with closing(client.Scans.stream(self.host, self.s_cfg.udp_port_lidar,
                                         complete=False)) as stream:
            xyzlut = client.XYZLut(self.SENSOR_INFO)
            pls: PopList = self.output
            for scan in stream:
                m = self.get_matrix_cloud(xyzlut, scan, Ch.channel_arr)  # TODO add batching
                self.logger.info(msg='Received frame')
                pls.append(m)
                time.sleep(self.config.SAMPLE_RATE)

    def convert(self):
        """
        Convert sensor output files from sensor native format to MatrixCloud
        for post-processing
        Returns
        -------

        """
        with open(self.META) as f:
            metadata = client.SensorInfo(f.read())
            self.METADATA = metadata
        source = pcap.Pcap(self.PCAP, metadata)
        self.ouster_pcap_to_mxc(source, metadata, frame_ls=self.output, frames_n=self.N)

    def ouster_pcap_to_mxc(self, source: client.PacketSource, metadata: client.SensorInfo, frame_ls: PopList,
                           frames_n: int = None):
        """

        Parameters
        ----------
        source : ouster-SDK source class for PCD packets
        metadata : ouster-SDK sensor calibration & metadata class created from provided JSON
        frame_ls : output PopList
        frames_n : number of frames to read

        Returns
        -------

        """
        from itertools import islice
        # precompute xyzlut to save computation in a loop
        xyzlut = client.XYZLut(metadata)
        # create an iterator of LidarScans from pcap and bound it if num is specified
        scans = iter(client.Scans(source))
        batch_sz = self.BATCH_SIZE
        if frames_n < batch_sz:
            batch_sz = frames_n

        DELAY = self.config.DELAY

        try:
            for interval in range(0, frames_n, batch_sz):
                batch = islice(scans, 0, batch_sz - 1, self.sample_rate)
                frame_ls.append(self.get_matrix_cloud(xyzlut, next(batch), Ch.channel_arr))  # sampling batch
                for scan in batch:
                    frame_ls.append(self.get_matrix_cloud(xyzlut, scan, Ch.channel_arr))
                while (frame_ls.first < interval - DELAY) \
                        and len(frame_ls) != frame_ls.first:
                    time.sleep(2)
        except StopIteration:
            self.logger.info("Sensor input completed, but stepped out of bounds for N.")

    def get_matrix_cloud(self, xyzlut: client.XYZLut, scan, channel_arr: List[str]) -> MatrixCloud:
        """"Create separate XYZ point-clouds for separate channels.
            Reading from cloud is done through dict destructuring.
            For keys use the client.ChanFields RANGE | SIGNAL | NEAR_IR | REFLECTIVITY"""
        matrix_cloud = MatrixCloud()
        field_names = channel_arr

        #   use integer mm to avoid loss of precision casting timestamps
        xyz = (xyzlut(scan.field(client.ChanField.RANGE))).astype(float)
        #   destagger mode
        xyz = client.destagger(self.METADATA, xyz)
        for ix, ch in enumerate(scan.fields):
            matrix_cloud.channels[field_names[ix]] = client.destagger(self.METADATA, scan.field(ch))
        matrix_cloud.xyz = np.array([c.flatten() for c in np.dsplit(xyz, 3)], dtype=float)
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

    io = _IO_(q, )
    io.read()


if __name__ == "__main__":
    main()
