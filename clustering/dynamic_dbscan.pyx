cimport cython

import numpy as np
cimport numpy as cnp

from libc.math cimport sqrt, floor
from libc.stdlib cimport malloc
from libc.stdio cimport printf

cdef int MAXSIZE_CLUSTERS = 100

cdef struct Point:
    double x
    double y


cdef struct ClusterPoint:
    int id
    Point coordinates
    int cluster_id
    bint visited


cdef struct Cluster:
    int end
    int size
    int *ids


cdef struct FrameClusters:
    int end
    int size
    Cluster *clusters


cdef FrameClusters* allocate_clusters(int max_clusters):
    cdef FrameClusters *frame_clusters = <FrameClusters *> malloc(sizeof(FrameClusters))
    frame_clusters.end = -1
    frame_clusters.size = max_clusters
    frame_clusters.clusters = <Cluster *> malloc(sizeof(Cluster) * max_clusters)

    return frame_clusters


cdef append_cluster(FrameClusters *frame_clusters, int cluster_id, int point_id):

    frame_clusters.clusters[cluster_id].end += 1

    if frame_clusters.clusters[cluster_id].end > frame_clusters.clusters[cluster_id].size:
        var = []
        for i in range(frame_clusters.clusters[cluster_id].end):
            var.append(frame_clusters.clusters[cluster_id].ids[i])
        print(f"ids:\n{sorted(var)}")
        print(f"len ids: {len(var)}")
        print(f'point id: {point_id}')
        print(f'ERROR: cluster_size larger than allocated memory! (entry {frame_clusters.clusters[cluster_id].end} size {frame_clusters.clusters[cluster_id].size})')
        quit()

    frame_clusters.clusters[cluster_id].ids[frame_clusters.clusters[cluster_id].end] = point_id


cdef int create_cluster(FrameClusters *frame_cluster, int max_points, int point_id):

    frame_cluster.end = frame_cluster.end + 1

    frame_cluster.clusters[frame_cluster.end].end = -1
    frame_cluster.clusters[frame_cluster.end].size = max_points
    frame_cluster.clusters[frame_cluster.end].ids = <int *> malloc(sizeof(int) * max_points)

    append_cluster(frame_cluster, frame_cluster.end, point_id)

    return frame_cluster.end


cdef reset_cluster(FrameClusters *frame_clusters, int cluster_id):

    if frame_clusters.end != cluster_id:
        print('ERROR: last cluster in frame_clusters is not cluster_id')
        return

    if frame_clusters.end > -1:
        frame_clusters.end -= 1

    frame_clusters.clusters[cluster_id].end = -1


cdef double euclidean_distance_2d(Point p1, Point p2):
    return sqrt((p1.x-p2.x)**2 + (p1.y-p2.y)**2)


cdef int min_point_func(double dist, int OS):
    if dist == 0:
        return 0

    cdef int mp = -1
    if OS == 16:
        mp = int(500/(1.3*dist)-12)
    elif OS == 32:
        mp = int(500/(1.3*dist)-5)
    
    return mp


cdef (double, double, int) dbscan_parameters(Point p, int OS, bint r_min_samp=True):
    cdef int i, rnge, index, min_samples, count
    cdef double eps, dist
    dist = sqrt(p.x ** 2 + p.y ** 2)

    # return dist, eps, min_points
    return dist, .03 * dist, min_point_func(dist, OS)


cpdef dict dynamic_dbscan(cnp.ndarray dynamic_points, int vres):

    cdef int point_index, pid, index, i1, i2, min_samples, d_points_len, cluster_id, core_points, pid_range
    cdef double eps
    cdef bint present
    cdef FrameClusters *frame_clusters

    d_points_len = dynamic_points.shape[0]
    core_points = 4

    cdef double[:, :] dynamic_points_c = dynamic_points
    cdef dict clusters = {}
    cdef ClusterPoint *all_points = <ClusterPoint *> malloc(d_points_len * sizeof(ClusterPoint))
    cdef ClusterPoint d_point

    for index in range(d_points_len):
        d_point.id = index
        d_point.coordinates.x = dynamic_points_c[index, 0]
        d_point.coordinates.y = dynamic_points_c[index, 1]
        d_point.cluster_id = -99
        d_point.visited = 0
        all_points[index] = d_point

    frame_clusters = allocate_clusters(MAXSIZE_CLUSTERS)

    for point_index in range(d_points_len):

        if all_points[point_index].visited:
            continue

        all_points[point_index].visited = True

        _, eps, min_samples = dbscan_parameters(all_points[point_index].coordinates, vres)

        cluster_id = create_cluster(frame_clusters, d_points_len, all_points[point_index].id)

        for index in range(d_points_len):
            if not all_points[index].visited and euclidean_distance_2d(all_points[index].coordinates, all_points[point_index].coordinates) <= eps:
                append_cluster(frame_clusters, cluster_id, all_points[index].id)

        if frame_clusters.clusters[cluster_id].end+1 < core_points:
            reset_cluster(frame_clusters, cluster_id)

        else:
            for pid_range in range(frame_clusters.clusters[cluster_id].size):

                if pid_range > frame_clusters.clusters[cluster_id].end:
                    break

                pid = frame_clusters.clusters[cluster_id].ids[pid_range]

                if all_points[pid].visited:
                    continue
                all_points[pid].visited = True

                for i1 in range(d_points_len):
                    if not all_points[i1].visited:

                        present = False
                        for i2 in range(frame_clusters.clusters[cluster_id].end+1):
                            if i2 > frame_clusters.clusters[cluster_id].end:
                                break

                            if all_points[i1].id == frame_clusters.clusters[cluster_id].ids[i2]:
                                present = True
                                break

                        if not present and euclidean_distance_2d(all_points[pid].coordinates, 
                                                                all_points[i1].coordinates) <= dbscan_parameters(all_points[pid].coordinates,
                                                                                                                vres ,r_min_samp=False)[1]:

                            append_cluster(frame_clusters, cluster_id, all_points[i1].id)

            if frame_clusters.clusters[cluster_id].end+1 >= min_samples:
                for index in range(frame_clusters.clusters[cluster_id].end+1):
                    all_points[frame_clusters.clusters[cluster_id].ids[index]].cluster_id = cluster_id
                    all_points[frame_clusters.clusters[cluster_id].ids[index]].visited = True

            else:
                reset_cluster(frame_clusters, cluster_id)

    for cid in range(frame_clusters.end+1):
        clusters[cid] = np.array([dynamic_points[frame_clusters.clusters[cid].ids[pid]] for pid in range(frame_clusters.clusters[cid].end+1)])

    return clusters
