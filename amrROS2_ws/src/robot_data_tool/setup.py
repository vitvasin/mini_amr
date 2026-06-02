from setuptools import setup

package_name = 'robot_data_tool'
import os
from glob import glob
setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sunday',
    maintainer_email='sunday@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "map_pose_provider = robot_data_tool.map_pose_provider:main",
            "robot_detail = robot_data_tool.robot_detail:main",
            "absolute_origin_laser = robot_data_tool.absolute_origin_laser:main",

        ],
    },
)
