#!/usr/bin/env python3
import time
import math
from enum import Enum, IntEnum
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from std_msgs.msg import Int16, Bool

CMD_START_CHG = 20
CMD_FULL      = 21
CMD_STOP_CHG  = 22

class ManagerState(Enum):
    IDLE_ON_DOCK = 'IDLE_ON_DOCK'
    CHARGING = 'CHARGING'
    COOLDOWN = 'COOLDOWN'
    UNKNOWN = 'UNKNOWN'


class ChargerState(IntEnum):
    IDLE = 0
    READY = 10
    CHARGING = 11
    BATT_FULL = 12
    IR_ERROR = 99


class BatteryManager(Node):
    def __init__(self):
        super().__init__('battery_manager')

        # ---- Parameters ----
        self.soc_target = self.declare_parameter('soc_target', 0.92).value
        self.soc_resume = self.declare_parameter('soc_resume', 0.84).value
        self.capacity_ah = self.declare_parameter('capacity_ah', 20.0).value
        self.full_current_ratio = self.declare_parameter('full_current_ratio', 0.05).value
        self.full_current_hold_sec = self.declare_parameter('full_current_hold_sec', 90).value
        self.cooldown_sec = self.declare_parameter('cooldown_sec', 600).value
        self.temp_ok_c = self.declare_parameter('temp_ok_c', 40.0).value
        self.temp_high_c = self.declare_parameter('temp_high_c', 45.0).value
        self.set_charge_retries = self.declare_parameter('set_charge_retries', 5).value
        self.ready_wait_timeout_sec = self.declare_parameter('ready_wait_timeout_sec', 5.0).value
        self.debug_interval_sec = self.declare_parameter('debug_interval_sec', 2.0).value

        # ---- State ----
        self.state = ManagerState.IDLE_ON_DOCK
        self.last_stop_time = 0.0
        self.full_current_a = self.capacity_ah * self.full_current_ratio
        self.low_current_since = None
        self.last_batt = None
        self.ir_state = ChargerState.IDLE  # 0=Idle,10=Ready,11=Charging,99=Error,12=BATT_FULL
        self.current_known = False
        self.request_stop_charge = False

        # ---- IO ----
        self.sub_batt = self.create_subscription(BatteryState, 'battery', self.on_batt, 10)
        self.sub_ir   = self.create_subscription(Int16, 'ir_charge_state', self.on_ir_state, 10)
        self.pub_set_charge = self.create_publisher(Int16, 'set_charge_state', 10)
        self.sub_request_stop_charge   = self.create_subscription(Bool, 'request_stop_charge', self.on_request_stop_charge, 10)

        self.timer = self.create_timer(0.5, self.loop)
        self.last_debug_time = 0.0

    def set_state(self, new_state: ManagerState):
        if self.state != new_state:
            self.get_logger().info(f'State change: {self.state.name} -> {new_state.name}')
            self.state = new_state

    def code_name(self, code: int) -> str:
        if code == CMD_START_CHG:
            return 'CMD_START_CHG'
        if code == CMD_FULL:
            return 'CMD_FULL'
        if code == CMD_STOP_CHG:
            return 'CMD_STOP_CHG'
        return f'CMD_{code}'

    def on_batt(self, msg: BatteryState):
        self.last_batt = msg
        # Current: treat negative as discharge; 0 or NaN as unknown
        try:
            curr = float(msg.current)
        except Exception:
            curr = float('nan')

        if curr != curr or curr == 0.0:  # NaN or 0.0 => unknown
            self.current_known = False
            self.low_current_since = None
            self.get_logger().debug('Battery current unknown (NaN/0). Will rely on SOC only.')
            return

        self.current_known = True
        chg_current = max(0.0, curr)
        if chg_current <= self.full_current_a:
            if self.low_current_since is None:
                self.low_current_since = time.time()
        else:
            self.low_current_since = None

    def on_ir_state(self, msg: Int16):
        try:
            new_state = ChargerState(int(msg.data))
            if new_state != self.ir_state:
                self.get_logger().info(f'IR state: {self.ir_state.name if isinstance(self.ir_state, IntEnum) else self.ir_state} -> {new_state.name} ({msg.data})')
            self.ir_state = new_state
        except ValueError:
            self.get_logger().warn(f'Unknown IR charge state received: {msg.data}')
    
    def on_request_stop_charge(self, msg: Bool):
        new_state = bool(msg.data)
        if new_state != self.request_stop_charge:
            self.get_logger().info(f'request_stop_charge received: {self.request_stop_charge} -> {new_state}')
        self.request_stop_charge = new_state


    def send_cmd(self, code: int):
        for _ in range(int(self.set_charge_retries)):
            self.get_logger().debug(f'Send command {self.code_name(code)} ({code})')
            self.pub_set_charge.publish(Int16(data=code))
            time.sleep(0.02)

    def wait_for_ir_state(self, desired: IntEnum, timeout: float) -> bool:
        start = time.time()
        while time.time() - start < timeout:
            if self.ir_state == desired:
                return True
            time.sleep(0.05)
        return self.ir_state == desired

    # Note: Dock/undock control removed. This node only
    # starts/stops charging based on battery and dock state.

    def loop(self):
        
        if self.last_batt is None:
            return
        now = time.time()
        # SOC: supports 0..1 or 0..100. 0 or NaN => unknown
        raw_soc = float(self.last_batt.percentage)
        if raw_soc != raw_soc or raw_soc == 0.0:
            soc = None
        else:
            soc = raw_soc / 100.0 if raw_soc > 1.0 else raw_soc
            soc = max(0.0, min(1.0, soc))

        #self.get_logger().info(
        #        f'state={self.state.name} ir={self.ir_state.name} soc={soc} raw_soc={raw_soc}'
        #    )
        
        # Temperature: 0 or NaN => default 25C
        raw_temp = float(self.last_batt.temperature)
        temp = 25.0 if (raw_temp != raw_temp or raw_temp == 0.0) else raw_temp

        # Derive manager state from IR charger when not cooling down
        if self.state != ManagerState.COOLDOWN:
            if self.ir_state == ChargerState.CHARGING:
                self.set_state(ManagerState.CHARGING)
            elif self.ir_state in (ChargerState.READY, ChargerState.BATT_FULL):
                self.set_state(ManagerState.IDLE_ON_DOCK)
            else:
                self.set_state(ManagerState.UNKNOWN)

        # Periodic debug snapshot
        if now - self.last_debug_time >= float(self.debug_interval_sec):
            try:
                raw_soc = float(self.last_batt.percentage)
            except Exception:
                raw_soc = float('nan')
            soc_pct = '?' if (raw_soc != raw_soc or raw_soc == 0.0) else f'{(raw_soc if raw_soc <= 1.0 else raw_soc/100.0)*100.0:.1f}%'
            temp_c = float(self.last_batt.temperature)
            if temp_c != temp_c or temp_c == 0.0:
                temp_str = '25.0*'
            else:
                temp_str = f'{temp_c:.1f}'
            low_curr_age = (time.time() - self.low_current_since) if self.low_current_since is not None else None
            low_curr_str = 'n/a' if low_curr_age is None else f'{low_curr_age:.0f}s'
            self.get_logger().debug(
                f'state={self.state.name} ir={self.ir_state.name} soc={soc_pct} tempC={temp_str} current_known={self.current_known} low_current_for={low_curr_str}'
            )
            self.last_debug_time = now

        if (self.state == ManagerState.UNKNOWN):
            return
        
        if (self.request_stop_charge):
            if (self.state == ManagerState.CHARGING):
                self.get_logger().warn('Request stop charge for undock')
                self.send_cmd(CMD_STOP_CHG)
                self.set_state(ManagerState.COOLDOWN)
                self.last_stop_time = now
            return

        # Safety stop
        if temp > self.temp_high_c and self.state == ManagerState.CHARGING:
            self.get_logger().warn('High temp, stop charging')
            self.send_cmd(CMD_STOP_CHG)
            self.set_state(ManagerState.COOLDOWN)
            self.last_stop_time = now
            return

        if self.state == ManagerState.IDLE_ON_DOCK:
            soc_ok_to_start = (soc is None) or (soc <= self.soc_resume)
            if soc_ok_to_start and temp < self.temp_ok_c and (now - self.last_stop_time) >= self.cooldown_sec:
                # Use IR charger state enum
                if self.ir_state == ChargerState.CHARGING:
                    # already charging (started by another node)
                    self.set_state(ManagerState.CHARGING)
                elif self.ir_state == ChargerState.READY:
                    # ready to charge -> command start
                    self.send_cmd(CMD_STOP_CHG)
                    if self.wait_for_ir_state(ChargerState.READY, self.ready_wait_timeout_sec):
                        self.get_logger().info('Charger READY; starting charge')
                        self.send_cmd(CMD_START_CHG)
                        self.set_state(ManagerState.CHARGING)
                elif self.ir_state == ChargerState.BATT_FULL:
                    # Charger latched full; must STOP before it becomes READY, then START
                    self.get_logger().info('Charger in BATT_FULL; sending STOP to reset to READY')
                    self.send_cmd(CMD_STOP_CHG)
                    if self.wait_for_ir_state(ChargerState.READY, self.ready_wait_timeout_sec):
                        self.get_logger().info('Charger READY; starting charge')
                        self.send_cmd(CMD_START_CHG)
                        self.set_state(ManagerState.CHARGING)
                    else:
                        self.get_logger().warn('Timeout waiting READY after STOP_CHG; will retry next cycle')
            #elif not soc_ok_to_start:
            #    if self.ir_state == ChargerState.READY:
            #        self.get_logger().info('Battery full → stop charging')
            #        self.send_cmd(CMD_FULL)
            #        self.set_state(ManagerState.COOLDOWN)
            #        self.last_stop_time = now

        elif self.state == ManagerState.CHARGING:
            # If no longer charging per IR status, return to idle
            if self.ir_state != ChargerState.CHARGING:
                self.set_state(ManagerState.IDLE_ON_DOCK)
                return
            cond_soc = (soc is not None) and (soc >= self.soc_target)
            cond_curr = self.low_current_since is not None and (now - self.low_current_since) >= self.full_current_hold_sec
            # If current is unknown, allow SOC alone to decide full
            cond_curr_ok = cond_curr if self.current_known else True
            if cond_soc:#and cond_curr_ok:
                self.get_logger().info('Battery full → stop charging')
                #self.send_cmd(CMD_FULL)  # หรือ CMD_STOP_CHG
                self.send_cmd(CMD_STOP_CHG)
                self.set_state(ManagerState.COOLDOWN)
                self.last_stop_time = now

        elif self.state == ManagerState.COOLDOWN:
            if (now - self.last_stop_time) >= self.cooldown_sec:
                # After cooldown, derive state again from IR
                if self.ir_state == ChargerState.CHARGING:
                    self.set_state(ManagerState.CHARGING)
                elif self.ir_state in (ChargerState.READY, ChargerState.BATT_FULL):
                    self.set_state(ManagerState.IDLE_ON_DOCK)
                else:
                    self.set_state(ManagerState.UNKNOWN)

def main():
    rclpy.init()
    node = BatteryManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
