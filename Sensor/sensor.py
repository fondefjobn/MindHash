import _io
import io
import threading
from contextlib import closing
from queue import Queue, Full
from typing import List, Any
import utils.utils as u
import _thread as th
import time
from ouster import client, sdk, pcap
import numpy as np
from ouster.client import _client as cl, core, LidarPacket

default_pcap: str = '/pcap'
default_metadata: str = '/metadata'

all_channels: list[cl.ChanField] = [cl.ChanField.RANGE, cl.ChanField.NEAR_IR, cl.ChanField.REFLECTIVITY]  # immutable


class SensorCommand:
    pass


class StreamConfig:
    sample_rate: int
    queue_size: int
    timer: bool
    time_end: int
    azimuth: float
    range: float
    elevation: float
    save_local: bool
    local_path: bool
    cache_size: int


class SensorParams:
    def __init__(self, config: dict):  # change to YML parser
        self.host = config['hostname']
        self.lidar_port = config['lidar_port']
        self.imu_port = config['imu_port']
        self.op_mode = config['operating_mode']
        self.lidar_mode = config['lidar_mode']
        self.pcap_path = default_pcap
        self.metadat_path = default_metadata


class MatrixCloud:
    def __init__(self):
        self.clouds = {}


class _IO:
    config: cl.SensorConfig = cl.SensorConfig()
    source: client.PacketSource = None

    def __init__(self, params: SensorParams):
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

    def stream_scans(self, queue: Queue[MatrixCloud], config: dict,
                     channels: list[cl.ChanField] = all_channels):
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
                    time.sleep(1)
                    continue
                time.sleep(config['sample_rate'])

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


default_sens_config = 'Sensor/sensor_config.yaml'
default_stream_config = 'Sensor/stream_config.yaml'


class StreamThread(threading.Thread):
    q: Queue[MatrixCloud]
    io: _IO

    def __init__(self, _io: _IO, conf: dict):
        threading.Thread.__init__(self)
        self.q = Queue(maxsize=conf['queue_size'])
        self.config = conf
        self.io = _io

    def run(self) -> None:
        self.io.stream_scans(self.q, self.config)


class Sensor:
    _io: _IO
    stream_config: StreamConfig = StreamConfig
    stream: StreamThread

    def __init__(self, path=default_sens_config):
        c_dict = u.FileUtils.load_file(path, ext='yaml')
        self._io = _IO(c_dict)

    def start_sensor(self):  # requires netcat
        pass

    def stop_sensor(self):  # requires netcat
        pass

    def read_stream(self) -> StreamThread:
        c_dict = u.FileUtils.load_file(default_stream_config, ext='yaml')
        stream = StreamThread(self._io, c_dict)
        self.stream = stream
        stream.run()
        return stream

    def stop_stream(self):
        if self.stream is not None:
            self.stream.join()

    def get_oper_mode(self) -> str:  # requires netcat
        pass
