from setuptools import setup
import os
from glob import glob

package_name = 'prost_scratch'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'rviz'),
            glob('rviz/*')),
        (os.path.join('share', package_name, 'model'),
            glob('model/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sobit-x2',
    maintainer_email='sobit-x2@todo.todo',
    description='The prost_scratch package for ROS2 Jazzy - TurtleBot2 control with Scratch integration',
    license='TODO',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'prost_scratch_ros2_connector = prost_scratch.prost_scratch_ros2_connector:main',
            'prost_scratch_ros2_controller = prost_scratch.prost_scratch_ros2_controller:main',
            'test_prost_scratch_ros2 = prost_scratch.test_prost_scratch_ros2:main',
        ],
    },
)