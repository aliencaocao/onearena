move_forward_mode = True
car_avoid_mode = False
turn_mode = False
ir_detection_distance = 15


def init():
    vision_ctrl.enable_detection(rm_define.vision_detection_marker)
    vision_ctrl.enable_detection(rm_define.vision_detection_car)
    ir_distance_sensor_ctrl.enable_measure(1)
    media_ctrl.exposure_value_update(rm_define.exposure_value_large)
    robotic_arm_ctrl.moveto(0.5, 1, wait_for_complete=True)
    vision_ctrl.set_marker_detection_distance(0.5)  # TODO: to tune with brake distance


def turn_left():
    chassis_ctrl.set_rotate_speed(60)
    chassis_ctrl.rotate_with_degree(rm_define.anticlockwise, 90)


def turn_right():
    chassis_ctrl.set_rotate_speed(60)
    chassis_ctrl.rotate_with_degree(rm_define.clockwise, 90)


def move_forward():
    global move_forward_mode
    move_forward_spd = 0.7  # TODO: to tune
    chassis_ctrl.set_trans_speed(move_forward_spd)
    while move_forward_mode:  # will only exit loop here after move_forward_mode flag is set to False in other functions
        if ir_distance_sensor_ctrl.get_distance_info(1) <= ir_detection_distance:  # stop moving when detected stuff and resume moving when there is none
            print('detected obj at distance:', ir_distance_sensor_ctrl.get_distance_info(1))
            # robot detected callback should be triggered here if it is a robot
            chassis_ctrl.stop()
        else:
            chassis_ctrl.move(0)  # move infinitely forward


def pickupindex():
    global human_x, human_w
    if 13 in vision_ctrl.get_marker_detection_info():
        id_index = vision_ctrl.get_marker_detection_info().index(13)
    else:
        id_index = 1
    human_info = vision_ctrl.get_marker_detection_info()[id_index + 1:id_index + 5]
    human_x, human_y, human_w = human_info[0], human_info[1], human_info[2],


def pickup():
    global pickup_mode, rotationTime, move_forward_mode
    pickupindex()
    print('picking up')
    chassis_ctrl.move(0)
    while ir_distance_sensor_ctrl.get_distance_info(1) > 10:
        pass
    chassis_ctrl.stop()
    # init claw above humanoid
    init_y = 0.2  # todo - just above humanoid
    robotic_arm_ctrl.moveto(0.5, init_y, wait_for_complete=True)
    while not (gripper_ctrl.is_open()):
        gripper_ctrl.open()  # open claw fully

    # move arm to humanoid
    grabX, grabY = 0, 0  # todo: in case grip not very secure - extra
    robotic_arm_ctrl.moveto(human_x + grabX, human_y + grabY, wait_for_complete=True)  # shift claw to target coordinates

    # grab and lift
    gripper_ctrl.update_power_level(4)
    while not (gripper_ctrl.is_closed()):
        gripper_ctrl.close()  # close fully to grab
    robotic_arm_ctrl.move(0.5, 0, wait_for_complete=True)  # lift off ground
    pickup_mode = False
    move_forward_mode = True


def dropoff():
    gripper_ctrl.update_power_level(1)  # humanoid slides down within claw onto floor
    robotic_arm_ctrl.moveto(0.5, 1, wait_for_complete=False)  # move to base of humanoid
    turn_right()
    while not (gripper_ctrl.is_open()()):
        gripper_ctrl.open()  # releases humanoid
    # reverse and face elsewhere
    chassis_ctrl.move_with_distance(180, 0.1)
    turn_left()
    chassis_ctrl.move_with_distance(90, 0.09)  # compensate the 10cm moved above but leave a bit of room


def start():
    global move_forward_mode
    init()
    while True:  # to merge with other modules
        if move_forward_mode:
            move_forward()
        else:
            pass


# def chassis_impact_detection(msg):  # todo, rotate in a circle and store IR info to decide where to move, check which side is collide
#     chassis_ctrl.stop()
#     # chassis_ctrl.move_with_distance(180, 0.2)


def vision_recognized_marker_number_seven(msg):
    print(ir_distance_sensor_ctrl.get_distance_info(1))
    if ir_distance_sensor_ctrl.get_distance_info(1) < 50:  # cases where there is U turn and may not be 1 meter till end of road (check for less than 115cm)
        chassis_ctrl.move_with_distance(0, ir_distance_sensor_ctrl.get_distance_info(1)/100)  # move forward until 10cm to obstetrical, TODO: to tune
        turn_right()
    else:
        chassis_ctrl.move_with_distance(0, 0.5)  # detected at 50cm
        turn_right()


def vision_recognized_marker_number_six(msg):
    print(ir_distance_sensor_ctrl.get_distance_info(1))
    if ir_distance_sensor_ctrl.get_distance_info(1) < 50:  # cases where there is U turn and may not be 1 meter till end of road (check for less than 115cm)
        chassis_ctrl.move_with_distance(0, ir_distance_sensor_ctrl.get_distance_info(1)/100)  # move forward until 10cm to obstetrical, TODO: to tune
        turn_left()
    else:
        chassis_ctrl.move_with_distance(0, 0.5)  # detected at 50cm
        turn_left()


def vision_recognized_car(msg):
    if ir_distance_sensor_ctrl.get_distance_info(1) <= 10:  # its very close to the robot, switch to side lane and overtake (if its face to face, it should not be very close)
        chassis_ctrl.move_with_distance(270, 0.26)  # robot width 24cm, move to left side 26cm to switch lane
        chassis_ctrl.set_trans_speed(3.5)  # overtake at max speed
        chassis_ctrl.move_with_distance(0, 0.6)  # robot length 34cm + 20cm moved back + 6cm buffer
        chassis_ctrl.set_trans_speed(3.5)  # TODO: to tune
        chassis_ctrl.move_with_distance(90, 0.26)  # robot width 24cm, move to right side 26cm to switch back lane
    else:
        car_info = vision_ctrl.get_car_detection_info()
        if car_info[0]:
            car_w, car_h = car_info[3], car_info[4]
            chassis_ctrl.stop()
            wait = 0  # seconds
            while wait <= 5:
                time.sleep(1)  # stops moving for a second to detect
                new_info = vision_ctrl.get_car_detection_info()
                if new_info[0]:  # there is still car detected
                    if (new_info[3], new_info[4]) == (car_w, car_h):
                        car_w, car_h = new_info[3], new_info[4]
                        wait += 1
                    else:
                        wait = 0  # reset back to 5 seconds timeout
                else:  # if car gone then break out this loop
                    break


def vision_recognized_marker_number_three(msg):  # pick up
    pickup()


def vision_recognized_letter_A(msg):  # drop off
    dropoff()


def vision_recognized_marker_number_five(msg):  # terminate
    led_ctrl.set_top_led(rm_define.armor_top_all, 255, 0, 0, rm_define.effect_always_on)
    led_ctrl.set_bottom_led(rm_define.armor_bottom_all, 255, 0, 0, rm_define.effect_always_on)
    rmexit()