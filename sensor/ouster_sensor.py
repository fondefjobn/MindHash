import json
from threading import Thread
import time
from contextlib import closing
from queue import Queue, Full
from typing import List

from ouster import client as cl, pcap
from ouster.client import LidarPacket
from utilities.utils import FileUtils, Cloud3dUtils, Ch, MatrixCloud

default_pcap: str = '/pcap'
default_metadata: str = '/metadata'

# all_channels: list[cl.ChanField] = [cl.ChanField.RANGE, cl.ChanField.NEAR_IR, cl.ChanField.REFLECTIVITY]  # immutable

meta = {"prod_line": "OS-1-16-A2", "prod_pn": "840-101855-02", "prod_sn": "991937000749",
        "image_rev": "ousteros-image-prod-aries-v2.2.1+20220215193703.patch-v2.2.1", "build_rev": "v2.2.1",
        "build_date": "2022-02-15T19:39:39Z", "status": "RUNNING", "initialization_id": 2573178, "base_pn": "",
        "base_sn": "", "proto_rev": "", "udp_ip": "192.168.178.255", "udp_dest": "192.168.178.25",
        "udp_port_lidar": 7502,
        "udp_port_imu": 7503, "udp_profile_lidar": "LEGACY", "udp_profile_imu": "LEGACY",
        "columns_per_packet": 16, "timestamp_mode": "TIME_FROM_PTP_1588", "sync_pulse_in_polarity": "ACTIVE_LOW",
        "nmea_in_polarity": "ACTIVE_HIGH", "nmea_ignore_valid_char": 0, "nmea_baud_rate": "BAUD_9600",
        "nmea_leap_seconds": 0, "multipurpose_io_mode": "OFF", "sync_pulse_out_polarity": "ACTIVE_HIGH",
        "sync_pulse_out_frequency": 1, "sync_pulse_out_angle": 360, "sync_pulse_out_pulse_width": 0,
        "auto_start_flag": 1, "operating_mode": "NORMAL", "lidar_mode": "2048x10", "azimuth_window": [0, 360000],
        "signal_multiplier": 1, "phase_lock_enable": False, "phase_lock_offset": 0,
        "beam_altitude_angles": [15.893000000000001, 13.715999999999999, 11.585000000000001, 9.4779999999999998,
                                 7.3789999999999996, 5.2919999999999998, 3.2029999999999998, 1.1279999999999999,
                                 -0.95799999999999996, -3.0470000000000002, -5.1269999999999998, -7.218,
                                 -9.3179999999999996, -11.42, -13.548999999999999, -15.718999999999999],
        "beam_azimuth_angles": [0.91600000000000004, 0.93000000000000005, 0.92100000000000004, 0.93600000000000005,
                                0.93300000000000005, 0.95699999999999996, 0.98199999999999998, 0.99099999999999999,
                                1.0249999999999999, 1.0329999999999999, 1.0780000000000001, 1.1040000000000001,
                                1.1439999999999999, 1.1779999999999999, 1.222, 1.2849999999999999]}


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
    def __init__(self, config: dict):  # change to YML parser
        self.host = config['hostname']
        self.lidar_port = config['lidar_port']
        #        self.imu_port = config['imu_port']
        #        self.op_mode = config['operating_mode']
        #       self.lidar_mode = config['lidar_mode']
        self.pcap_path = default_pcap
        self.metadat_path = default_metadata


class _IO:
    source: cl.PacketSource = None

    def __init__(self, params: SensorParams):
        self.host = params.host
        self.config = cl.SensorConfig()
        self.config.udp_port_lidar = 7502
        self.config.udp_port_imu = 7503
        self.config.operating_mode = cl.OperatingMode.OPERATING_NORMAL
        self.config.lidar_mode = cl.LidarMode.MODE_1024x10
        self.config.udp_dest = ''
        self.pcap_path = params.pcap_path
        self.meta_path = params.metadat_path
        self.config.udp_dest = '255.255.255.255'
        # cl.set_config(self.host, self.config)
        self.__set_paths()
        # self.__get_source()

    def __set_paths(self, sep='/'):
        pcap_p = self.pcap_path
        meta_p = self.meta_path
        pcap_file = f"{self.host}.pcap"
        meta_file = f"{self.host}.json"
        self.pcap_path = sep.join([pcap_p, pcap_file])
        self.meta_path = sep.join([meta_p, meta_file])

    def __init_dirs(self):
        pass

    def __fetch_meta(self):
        with closing(cl.Sensor(hostname=self.host, lidar_port=7502)) as source:
            source.write_metadata(self.meta_path)

    def __get_source(self):
        self.__fetch_meta()
        with open(self.pcap_path, 'r') as f:
            self.metadata = cl.SensorInfo(f.read())
        # return pcap.Pcap(self.pcap_path, self.metadata)

    def stream_packets(self, q: Queue):
        """Only LiDAR data! Read stream from pcap file. Less latency. More packet access.
         Packet does not represent full frame"""
        for packet in self.source:
            if isinstance(packet, LidarPacket):
                try:
                    q.put_nowait(packet)
                except Full:
                    continue

    def stream_scans(self, q: Queue, config: dict):
        """
        Read SDK-controlled stream of lidar data. More latency.
         Incomplete & late frames are dropped from stream internally.
         """
        sensor_info = cl.SensorInfo(json.dumps(meta))
        with closing(cl.Scans.stream(self.host, self.config.udp_port_lidar,
                                     metadata=sensor_info,
                                     complete=False)) as stream:
            xyzlut = cl.XYZLut(self.metadata)
            for scan in stream:
                m = Cloud3dUtils.get_matrix_cloud(xyzlut, scan, Ch.channel_arr)
                print(m)
                q.put(m, block=True)
                time.sleep(config['sample_rate'])


default_sens_config = 'sensor/sensor_config.yaml'
default_stream_config = 'sensor/stream_config.yaml'


class StreamThread(Thread):
    q: Queue
    io: _IO

    def __init__(self, _io: _IO, conf: dict, channels: List[int]):
        super().__init__()
        self.q = Queue(maxsize=conf['queue_size'])
        self.config = conf
        self.io = _io
        self.channels = channels

    def run(self) -> None:
        self.io.stream_scans(self.q, self.config)


class Sensor:
    _io: _IO
    stream: StreamThread
    channels: List[int] = [1, 2, 3, 4]

    def __init__(self, path=default_sens_config):
        c_dict = FileUtils.load_file(path, ext='yaml')
        self._io = _IO(c_dict)

    def start_stream(self) -> StreamThread:
        c_dict = FileUtils.load_file(default_stream_config, ext='yaml')
        stream = StreamThread(self._io, c_dict, self.channels)
        self.stream = stream
        stream.run()
        return stream

    def stop_stream(self):
        if self.stream is not None:
            self.stream.join()


sensor_ip = '169.254.132.100'
sensor_port = 7502


def main():
    q: Queue[MatrixCloud] = Queue(maxsize=200)
    params = {
        'hostname': sensor_ip,
        'lidar_port': sensor_port,
        'sample_rate': 1
    }

    io = _IO(SensorParams(params))
    io.stream_scans(q, params)


if __name__ == "__main__":
    main()
