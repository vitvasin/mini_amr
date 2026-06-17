import numpy as np
import transforms3d as t3d

import rclpy
from rclpy.node import Node
import tf2_ros

from geometry_msgs.msg import Pose, PoseStamped, Point, Quaternion


class SensorOffsetCompensator:
    '''
    Get the pose of a sensor relative to vehicle base (or other frame)
    and use the information to compensate the sensor offset 
    in map coordinate frame. Basically, the conversion sensor pose -> vehicle base pose.
    '''

    def __init__(self, base_frame_name, sensor_frame_name, align_camera_frame=False):

        '''
        frame_id (str): name of the transform source frame
        child_frame_id (str): name of the transform target frame
        align_camera_frame (bool):  The camera coordinate frame convention sometimes differs from
                                    the convention for the robot base and map. This parameter 
                                    defines if a correction is used.
        '''

        tf_subscription_freq = 10
        tf_wait_timeout = 300 # Set to high value to avoid hard-t-find bugs when running with carla
        self.camera_frame_alignment_qvec = np.array([ 0.5, 0.5, -0.5, 0.5])
        self.tvec, self.qvec = self._get_transform(base_frame_name, sensor_frame_name, tf_subscription_freq, tf_wait_timeout, align_camera_frame)

    def _get_transform(self, frame_id, child_frame_id, tf_subscription_freq, tf_wait_timeout, align_camera_frame):

        try:
            # If called independently
            rclpy.init()
            owns_rclpy = True
        except RuntimeError:
            # If called from inside an already initiated rclpy context
            owns_rclpy = False
            pass

        rate_node = Node('sensor_offset_remover_utility_markers')

        tfBuffer = tf2_ros.Buffer()
        tf_listener = tf2_ros.TransformListener(tfBuffer, rate_node, spin_thread=True)
        rate = rate_node.create_rate(tf_subscription_freq)

        transform = None
        wait=0
        print('Waiting to acquire transform {} -> {} from tf2...'.format(frame_id, child_frame_id))
        while rclpy.ok() & (transform is None):
            if wait > tf_wait_timeout:
                print(f'Transform {frame_id} -> {child_frame_id} not received!')
                return None, None
            else:
                try:
                    transform = tfBuffer.lookup_transform( target_frame=frame_id,
                                                    source_frame=child_frame_id,
                                                    time=rclpy.duration.Duration(seconds=0))
                except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
                    pass
                import time
                time.sleep(1.0 / tf_subscription_freq)
                wait += 1.0 / tf_subscription_freq


        rate_node.destroy_node()
        tf_listener.unregister()
        tf_listener.__del__()
        if owns_rclpy:
            rclpy.shutdown()

        tvec = transform.transform.translation
        tvec = np.array([tvec.x, tvec.y, tvec.z])

        qvec = transform.transform.rotation
        qvec = np.array([qvec.w, qvec.x, qvec.y, qvec.z])

        if align_camera_frame:
            qvec = t3d.quaternions.qmult(qvec, self.camera_frame_alignment_qvec)

        print('Initialized sensor offset compensator {} -> {} with parameters'.format(frame_id, child_frame_id))
        print('T: {}'.format(tvec))
        print('Q: {}'.format(qvec.round(3)))
        return tvec, qvec

    def remove_offset_from_array(self, sensor_tvec, sensor_qvec):
        '''
        Prams:
            sensor_tvec: Position of the sensor
            type: np.array

            sensor_qvec: Orientation of the sensor
            type: np.array

        Return:
            base_world_pos: Position of the vehicle the sensor is attached to
            base_world_rot: Orientation of the vehicle the sensor is attached to
            type: np.array
        '''
        base_world_rot = t3d.quaternions.qmult(sensor_qvec, t3d.quaternions.qinverse( self.qvec))
        base_world_rot = base_world_rot/t3d.quaternions.qnorm(base_world_rot)
        base_world_pos = sensor_tvec - t3d.quaternions.rotate_vector(self.tvec, base_world_rot)

        return base_world_pos, base_world_rot
