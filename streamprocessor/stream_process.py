from queue import Queue
from typing import List, Tuple

import numpy as np
from easydict import EasyDict
from numba import jit

from tools.pipeline.structures import RNode
from tools.pipeline.structures import RModule
from tools.structs.custom_structs import PopList, MatrixCloud
from utilities.utils import FileUtils as Fs, \
    Cloud3dUtils, FileUtils
import open3d as o3d

"""
@Module: Stream Processor
@Description: Provides functionalities for data filtering and augmentation tasks
@Author: Radu Rebeja
"""


class ConfigMap:
    """"""
    rate = 'sample_rate'
    q_size = 'queue_size'
    timer = 'timer'
    t_end = 'timer_stop'
    sl = 'local_saves'
    lp = 'local_path'
    live = 'livestream'


"""Aliases & Global values"""
################
Cm = ConfigMap
Q = Queue


################

class StreamProcessor(RModule):
    """
    StreamProcessor
    Executes data filtering and augmentation tasks
    Configuration file establishes the behavior of this class
    See Also config.yaml within package
    """

    c: dict = None

    idle: bool = False

    def __init__(self, cfg_path=None):  # def __init__(self, cfg_path=None): #
        super().__init__()
        self.load_config(__file__)
        print(self.config)
        config = self.config
        param = config.STEPS.LIST[0].CONFIG
        bounds = np.transpose(np.array([param.X, param.Y, param.Z], dtype=float))
        self.lower = bounds[0]
        self.upper = bounds[1]

    def read_stream(self, mx: MatrixCloud, filter = None):
        """
        Converts PCD to required format and applies scene
        editing techniques
        Parameters
        ----------
        mx :

        Returns
        -------

        """
        pcd: np.ndarray = Cloud3dUtils.to_pcdet(mx)
        comp_pcd = pcd[:, [0, 1, 2]]
        pcd = pcd[np.all((self.lower < comp_pcd) & (comp_pcd < self.upper), axis=1)]
        if filter == "statistical":
            pcd = self.statistical_filter(pcd)
        elif filter == "radius":
            pcd = self.radius_filter(pcd)
        return pcd

    def fconfig(self):
        return "config.yaml"

    def filter_inlier(self, cloud, ind):
        in_list = cloud.select_by_index(ind)
        pcd: np.ndarray = Cloud3dUtils.to_pcdet(in_list.points)
        return pcd

    def statistical_filter(self, pcd_init):
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(pcd_init)

        voxel_down_pcd = pcd.voxel_down_sample(voxel_size=0.02)
        cl, ind = voxel_down_pcd.remove_statistical_outlier(nb_neighbors=20,
                                                            std_ratio=2.0)
        return self.display_inlier_outlier(voxel_down_pcd, ind)

    def radius_filter(self, pcd_init):
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(pcd_init)

        voxel_down_pcd = pcd.voxel_down_sample(voxel_size=0.02)
        cl, ind = voxel_down_pcd.remove_radius_outlier(nb_points=16, radius=0.05)
        return self.display_inlier_outlier(voxel_down_pcd, ind)


class Routines(RNode):
    """
    StreamProcessor routine
    """
    ix: int = 0

    def get_index(self) -> int:
        return self.ix

    @classmethod
    def script(cls, parser) -> bool:
        return True

    def __init__(self, state):
        super().__init__(state)

    sp: StreamProcessor = StreamProcessor()

    @RNode.assist
    def run(self, _input: List[PopList], output: PopList, **kwargs):
        """
        Routine to read from a parsed list of PopList elements
        and output to an allocated PopList
        Parameters
        ----------
        output
        _input
        kwargs

        Returns
        -------

        """
        self.state.logger.info(msg="Stream Processor started...")
        while not _input[0].full(self.ix):
            out = _input[0].qy(self.ix, self.event)
            output.append(self.sp.read_stream(out))
            self.ix += 1
        self.state.logger.info(msg="Stream Processor : DONE")

    def dependencies(self):
        from sensor.sensor_controller import Routines as Input
        return [Input]
