from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node

def generate_launch_description():

    # เรียก ROS2 Modbus Server Node ปกติ
    modbus_server = Node(
        package='modbus_server',
        executable='modbus_server',
        name='modbus_server',
        output='screen'
    )

    # รอให้ Modbus Node start 3 วินาที แล้วค่อย start UI script
    # ui_process = TimerAction(
    #     period=3.0,
    #     actions=[
    #         ExecuteProcess(
    #             cmd=['python3', '/home/smr/workspaces/mini_amr/amrROS2_UI/ICEAMR/main.py'],  # <- ใส่ path ของ UI คุณ
    #             output='screen'
    #         )
    #     ]
    # )

    return LaunchDescription([
        modbus_server,
        # ui_process
    ])