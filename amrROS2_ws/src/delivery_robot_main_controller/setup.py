from setuptools import find_packages, setup

package_name = 'delivery_robot_main_controller'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/delivery.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Kittipong',
    maintainer_email='your@email.com',
    description='Main controller for delivery robot with multi-compartment',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'delivery_robot_main_controller = delivery_robot_main_controller.main_controller_node:main',
            'robot_sound = delivery_robot_main_controller.robot_sound:main',
            'call_robot_button = delivery_robot_main_controller.call_button:main',
            'rpc_run_node = delivery_robot_main_controller.rpc_run_node:main',
        ],
    },
)
