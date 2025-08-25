from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'wis_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
	(os.path.join('share', package_name), glob("launch/*.launch.py")),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='smr',
    maintainer_email='peerawich.tangsiritham@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
	"map_name = wis_pkg.map_name_publisher_node:main",
	"map_info = wis_pkg.map_info_publisher_node:main",
	"map_load = wis_pkg.map_load_subscriber_node:main",
	"map_save = wis_pkg.map_save_subscriber_node:main",
	"map_scan = wis_pkg.map_scan_subscriber_node:main",
	"map_nav = wis_pkg.map_nav_subscriber_node:main",
	"point_save = wis_pkg.point_save_subscriber_node:main",
	"map_shutdown = wis_pkg.map_shutdown_subscriber_node:main",
        ],
    },
)
