"""
@Module: Stream Processor
@Description: Provides functionalities for data filtering and augmentation tasks
@Author: Radu Rebeja
"""
from argparse import Namespace

from ouster import client, pcap

from sensor.sensor_controller import Convertor
from tools.structs import PopList


class IO:
    """
    IO class contains composite methods for reading input data
    from specific sensor brands using proprietary tools and utilities
    """

    @staticmethod
    def ouster(args: Namespace, file, out_ls: PopList):
        metadata = client.SensorInfo(file.read())
        source = pcap.Pcap(args.input, metadata)
        Convertor.ouster_pcap_to_mxc(source, metadata, frame_ls=out_ls, N=args.N)