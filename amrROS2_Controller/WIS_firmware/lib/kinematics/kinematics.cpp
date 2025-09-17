// Copyright (c) 2021 Juan Miguel Jimeno
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "Arduino.h"
#include "kinematics.h"

Kinematics::Kinematics(base robot_base, int motor_max_rpm, float max_rpm_ratio,
                       float motor_operating_voltage, float motor_power_max_voltage,
                       float wheel_diameter, float wheels_y_distance):
    base_platform_(robot_base),
    wheels_y_distance_(wheels_y_distance),
    wheel_circumference_(PI * wheel_diameter),
    total_wheels_(getTotalWheels(robot_base))
{    
    motor_power_max_voltage = constrain(motor_power_max_voltage, 0, motor_operating_voltage);
    max_rpm_ =  ((motor_power_max_voltage / motor_operating_voltage) * motor_max_rpm) * max_rpm_ratio;
}

Kinematics::rpm Kinematics::calculateRPM(float linear_x, float linear_y, float angular_z)
{

    float tangential_vel = angular_z * (wheels_y_distance_ / 2.0);

    //convert m/s to m/min
    float linear_vel_x_mins = linear_x * 60.0;
    float linear_vel_y_mins = linear_y * 60.0;
    //convert rad/s to rad/min
    float tangential_vel_mins = tangential_vel * 60.0;

    float x_rpm = linear_vel_x_mins / wheel_circumference_;
    float y_rpm = linear_vel_y_mins / wheel_circumference_;
    float tan_rpm = tangential_vel_mins / wheel_circumference_;

    float a_x_rpm = fabs(x_rpm);
    float a_y_rpm = fabs(y_rpm);
    float a_tan_rpm = fabs(tan_rpm);

    float xy_sum = a_x_rpm + a_y_rpm;
    float xtan_sum = a_x_rpm + a_tan_rpm;

    //calculate the scale value how much each target velocity
    //must be scaled down in such cases where the total required RPM
    //is more than the motor's max RPM
    //this is to ensure that the required motion is achieved just with slower speed
    if(xy_sum >= max_rpm_ && angular_z == 0)
    {
        float vel_scaler = max_rpm_ / xy_sum;

        x_rpm *= vel_scaler;
        y_rpm *= vel_scaler;
    }
    
    else if(xtan_sum >= max_rpm_ && linear_y == 0)
    {
        float vel_scaler = max_rpm_ / xtan_sum;

        x_rpm *= vel_scaler;
        tan_rpm *= vel_scaler;
    }

    Kinematics::rpm rpm;

    //calculate for the target motor RPM and direction
    //front-left motor
    rpm.motor1 = x_rpm - y_rpm - tan_rpm;
    rpm.motor1 = constrain(rpm.motor1, -max_rpm_, max_rpm_);

    //front-right motor
    rpm.motor2 = x_rpm + y_rpm + tan_rpm;
    rpm.motor2 = constrain(rpm.motor2, -max_rpm_, max_rpm_);

    //rear-left motor
    rpm.motor3 = x_rpm + y_rpm - tan_rpm;
    rpm.motor3 = constrain(rpm.motor3, -max_rpm_, max_rpm_);

    //rear-right motor
    rpm.motor4 = x_rpm - y_rpm + tan_rpm;
    rpm.motor4 = constrain(rpm.motor4, -max_rpm_, max_rpm_);

    return rpm;
}

Kinematics::rpm Kinematics::getRPM(float linear_x, float linear_y, float angular_z)
{
    if(base_platform_ == DIFFERENTIAL_DRIVE || base_platform_ == SKID_STEER)
    {
        linear_y = 0;
    }

    return calculateRPM(linear_x, linear_y, angular_z);;
}

// Kinematics::velocities Kinematics::getVelocities(float rpm1, float rpm2, float rpm3, float rpm4)
// {
//     Kinematics::velocities vel;
//     float average_rps_x;
//     float average_rps_y;
//     float average_rps_a;

//     if(base_platform_ == DIFFERENTIAL_DRIVE)
//     {
//         rpm3 = 0.0;
//         rpm4 = 0.0;
//     }
 
//     //convert average revolutions per minute to revolutions per second
//     average_rps_x = ((float)(rpm1 + rpm2 + rpm3 + rpm4) / total_wheels_) / 60.0; // RPM
//     vel.linear_x = average_rps_x * wheel_circumference_; // m/s

//     //convert average revolutions per minute in y axis to revolutions per second
//     average_rps_y = ((float)(-rpm1 + rpm2 + rpm3 - rpm4) / total_wheels_) / 60.0; // RPM
//     if(base_platform_ == MECANUM)
//         vel.linear_y = average_rps_y * wheel_circumference_; // m/s
//     else
//         vel.linear_y = 0;

//     //convert average revolutions per minute to revolutions per second
//     average_rps_a = ((float)(-rpm1 + rpm2 - rpm3 + rpm4) / total_wheels_) / 60.0;
//     vel.angular_z =  (average_rps_a * wheel_circumference_) / (wheels_y_distance_ / 2.0); //  rad/s

//     return vel;
// }
Kinematics::velocities Kinematics::getVelocities_filtered(float rpm1, float rpm2, float rpm3, float rpm4)
{
    Kinematics::velocities vel{0.0f, 0.0f, 0.0f};

    // --- Validation (same as before, with Serial5.println) ---
    if (total_wheels_ <= 0) {
        Serial5.println("Error: total_wheels_ must be > 0");
        return vel;
    }
    if (wheels_y_distance_ <= 0.0f) {
        Serial5.println("Error: wheels_y_distance_ must be > 0");
        return vel;
    }

    // Clamp inputs
    auto clampRpm = [](float rpm) {
        constexpr float MAX_RPM = 300.0f;
        if (rpm > MAX_RPM)  return MAX_RPM;
        if (rpm < -MAX_RPM) return -MAX_RPM;
        return rpm;
    };

    rpm1 = clampRpm(rpm1);
    rpm2 = clampRpm(rpm2);
    rpm3 = clampRpm(rpm3);
    rpm4 = clampRpm(rpm4);

    // Adjust for drive type
    int active_wheels = total_wheels_;
    if (base_platform_ == DIFFERENTIAL_DRIVE) {
        rpm3 = 0.0f;
        rpm4 = 0.0f;
        active_wheels = 2;
    }

    // --- Raw velocity computation (unfiltered) ---
    float average_rps_x = ((rpm1 + rpm2 + rpm3 + rpm4) / static_cast<float>(active_wheels)) / 60.0f;
    float raw_linear_x = average_rps_x * wheel_circumference_;
    

    float average_rps_y = ((-rpm1 + rpm2 + rpm3 - rpm4) / static_cast<float>(active_wheels)) / 60.0f;
    float raw_linear_y = (base_platform_ == MECANUM) ? 
                          average_rps_y * wheel_circumference_ : 0.0f;

    float average_rps_a = ((-rpm1 + rpm2 - rpm3 + rpm4) / static_cast<float>(active_wheels)) / 60.0f;
    float raw_angular_z = (average_rps_a * wheel_circumference_) / (wheels_y_distance_ / 2.0f);

    // --- Apply low-pass filter ---
    float k =0.5f;
    filtered_linear_x_ = k * raw_linear_x + (1.0f - k) * filtered_linear_x_;
    filtered_linear_y_ = k * raw_linear_y + (1.0f - k) * filtered_linear_y_;
    filtered_angular_z_ = k * raw_angular_z + (1.0f - k) * filtered_angular_z_;

    // Assign filtered outputs
    vel.linear_x = filtered_linear_x_;
    vel.linear_y = filtered_linear_y_;
    vel.angular_z = filtered_angular_z_;

    return vel;
}

Kinematics::velocities Kinematics::getVelocities(float rpm1, float rpm2, float rpm3, float rpm4)
{
    // Initialize with safe defaults
    Kinematics::velocities vel{0.0f, 0.0f, 0.0f};

    // --- Input validation with Serial5 logs ---
    if (total_wheels_ <= 0) {
        Serial5.println("Error: total_wheels_ must be > 0");
        return vel; // return safe zero velocities
    }
    if (wheels_y_distance_ <= 0.0f) {
        Serial5.println("Error: wheels_y_distance_ must be > 0");
        return vel;
    }

    // Clamp inputs to reasonable range (adjust MAX_RPM per hardware)
    auto clampRpm = [](float rpm) {
        constexpr float MAX_RPM = 300.0f; // safe bound
        if (rpm > MAX_RPM)  return MAX_RPM;
        if (rpm < -MAX_RPM) return -MAX_RPM;
        return rpm;
    };

    rpm1 = clampRpm(rpm1);
    rpm2 = clampRpm(rpm2);
    rpm3 = clampRpm(rpm3);
    rpm4 = clampRpm(rpm4);

    // --- Adjust logic depending on platform type ---
    int active_wheels = total_wheels_;
    if (base_platform_ == DIFFERENTIAL_DRIVE) {
        rpm3 = 0.0f;
        rpm4 = 0.0f;
        active_wheels = 2; // only two wheels contribute
    }

    Serial5.print("Input RPMs: ");
    Serial5.print(rpm1); Serial5.print(", ");
    Serial5.print(rpm2); Serial5.print(", ");
    Serial5.print(rpm3); Serial5.print(", ");
    Serial5.println(rpm4);

    // --- Compute velocities ---
    // Revolutions per second average (X)
    float rpm_sum = rpm1 + rpm2 + rpm3 + rpm4;
    Serial5.print("rpm_sum: "); Serial5.println(rpm_sum);
    // float rpm_convert = rpm_sum * 0.0167f; // 1/60
    // Serial5.print("rpm_convert: "); Serial5.println(rpm_convert);
    float average_rps_x = rpm_sum * 0.0083f;
    // float average_rps_x = ((rpm1 + rpm2 + rpm3 + rpm4) / static_cast<float>(active_wheels)) / 60.0f;
    
    vel.linear_x = average_rps_x * wheel_circumference_;
    Serial5.print("average_rps_x "); Serial5.print(average_rps_x);
    Serial5.print(", vel.linear_x: "); Serial5.println(vel.linear_x);

    // Revolutions per second average (Y)
    float average_rps_y = 0.0f; // ((-rpm1 + rpm2 + rpm3 - rpm4) / static_cast<float>(active_wheels)) / 60.0f;
    if (base_platform_ == MECANUM) {
        vel.linear_y = average_rps_y * wheel_circumference_;
    } else {
        vel.linear_y = 0.0f;
    }

    // Angular velocity (rotation around Z)
    float average_rps_a = ((-rpm1 + rpm2 - rpm3 + rpm4) / static_cast<float>(active_wheels)) / 60.0f;
    vel.angular_z = (average_rps_a * wheel_circumference_) / (wheels_y_distance_ / 2.0f);
    // Serial5.print("average_rps_a "); Serial5.print(average_rps_a);
    // Serial5.print(", vel.angular_z: "); Serial5.println(vel.angular_z);

    // vel = k*vel_old + (1-k)*cmd_vel;           //  k = 0-1  k=0.5               
    // vel_old = vel;
    

    return vel;
}

int Kinematics::getTotalWheels(base robot_base)
{
    switch(robot_base)
    {
        case DIFFERENTIAL_DRIVE:    return 2;
        case SKID_STEER:            return 4;
        case MECANUM:               return 4;
        default:                    return 2;
    }
}

float Kinematics::getMaxRPM()
{
    return max_rpm_;
}