move_forward_mode = True
car_avoid_mode = False
turn_mode = False
ir_detection_distance = 'ir_distance_1_ge_20'  # ir_distance_1_ge_DISTANCE in CM e.g. ir_distance_1_ge_10 -> 10cm


def init():
    vision_ctrl.enable_detection(rm_define.vision_detection_marker)
    vision_ctrl.enable_detection(rm_define.vision_detection_car)
    ir_distance_sensor_ctrl.enable_measure(1)
    media_ctrl.exposure_value_update(rm_define.exposure_value_large)


def turn_left():
    global move_forward_mode, turn_mode
    turn_mode = True
    chassis_ctrl.set_rotate_speed(600)  # to tune
    chassis_ctrl.rotate_with_degree(rm_define.anticlockwise, 90)
    turn_mode = False


def turn_right():
    global move_forward_mode, turn_mode
    turn_mode = True
    chassis_ctrl.set_rotate_speed(600)  # to tune
    chassis_ctrl.rotate_with_degree(rm_define.clockwise, 90)
    turn_mode = False


def move_forward():
    global move_forward_mode
    move_forward_spd = 2  # to tune
    chassis_ctrl.set_trans_speed(move_forward_spd)
    vision_ctrl.set_marker_detection_distance(1)  # to tune with brake distance and turning distance, not setting in init to prevent conflict with other modules

    while move_forward_mode:  # will only exit loop here after move_forward_mode flag is set to False in other functions
        if ir_distance_sensor_ctrl.check_condition(ir_detection_distance):
            chassis_ctrl.stop()  # stop moving when detected stuff in 20cm and resume moving when there is none
            tools.timer_ctrl(rm_define.timer_start)
            while tools.timer_current() < 5.0 and ir_distance_sensor_ctrl.check_condition(ir_detection_distance):
                pass  # wait for 5 sec to see if there is no more stuff in 20cm
            if ir_distance_sensor_ctrl.check_condition(ir_detection_distance):  # if after waiting for 5s, still have stuff blocking and its a robot, move back 20cm and then switch to side lane and overtake
                chassis_ctrl.move_with_distance(180, 0.2)  # move back 20cm to easier see if its a robot
                if vision_ctrl.check_condition(rm_define.cond_recognized_car):
                    chassis_ctrl.move_with_distance(270, 0.26)  # robot width 24cm, move to left side 26cm to switch lane
                    chassis_ctrl.set_trans_speed(3.5)  # overtake at max speed
                    chassis_ctrl.move_with_distance(0, 0.6)  # robot length 34cm + 20cm moved back + 6cm buffer
                    chassis_ctrl.set_trans_speed(move_forward_spd)  # to tune
                    chassis_ctrl.move_with_distance(90, 0.26)  # robot width 24cm, move to right side 26cm to switch back lane
        else:
            chassis_ctrl.move(0)  # move infinitely forward

def pickupindex():
    if 13 in vision_ctrl.get_marker_detection_info():
        id_index = vision_ctrl.get_marker_detection_info().index(13)
    else:
        id_index = 1
    human_info = vision_ctrl.get_marker_detection_info()[id_index+1:id_index+5]
    human_x, human_w = human_info[0], human_info[2]

def pickup():
    pickupindex()
    # face marker
    while abs(human_x - 0.5) > 0.05:
        if human_x > 0.5:
            chassis_ctrl.rotate(rm_define.clockwise)
        else if human_x < 0.5:
            chassis_ctrl.rotate(rm_define.anticlockwise)
        pickupindex()

    # init claw above humanoid
    init_y = 0.2 # todo - just above humanoid
    robotic_arm_ctrl.moveto(0.5, init_y, wait_for_complete = False)
    while not(gripper_ctrl.is_open()):
        gripper_ctrl.open() # open claw fully

    # move closer to marker
    minWidth = 30  # todo
    while human_w < minWidth:
        chassis_ctrl.move_degree_with_speed(0,30)
        pickupindex()

    # move arm to humanoid
    grabX, grabY = 0   # todo: in case grip not very secure - extra
    robotic_arm_ctrl.moveto(human_x + grabX, human_y + grabY, wait_for_complete = True) # shift claw to target coordinates

    # grab and lift
    lift = 8 # todo - just enough to not drag on floor
    gripper_ctrl.update_power_level(4)
    while not(gripper_ctrl.is_closed()):
        gripper_ctrl.close() # close fully to grab
    robotic_arm_ctrl.move(0, lift, wait_for_complete = True) # lift off ground
    pickup_mode = False

    
    # reverse and face elsewhere
    chassis_ctrl.move_with_distance(180,0.05)
    rotationTime = 2 # todo - such that vision markers are out of view
    chassis_ctrl.rotate_with_time(rm_define.anticlockwise, 2)


def vision_recognized_letter_A(msg):  # drop off
    dropoff()


def dropoff():
    gripper_ctrl.update_power_level(1) # humanoid slides down within claw onto floor
    # robotic_arm_ctrl.moveto(0.5, 1, wait_for_complete = False) # move to base of humanoid
    while not(gripper_ctrl.is_closed()):
        gripper_ctrl.close() # releases humanoid

    # reverse and face elsewhere
    chassis_ctrl.move_with_distance(180,0.05)
    rotationTime = 2 # todo - such that vision markers are out of view
    chassis_ctrl.rotate_with_time(rm_define.anticlockwise,2)


def start():
    global move_forward_mode
    init()
    while True:  # to merge with other modules
        if move_forward_mode:
            move_forward()
        else:
            pass


def chassis_impact_detection(msg):  # todo, rotate in a circle and store IR info to decide where to move, check which side is collide
    global move_forward_mode
    move_forward_mode = False
    chassis_ctrl.stop()
    # chassis_ctrl.move_with_distance(180, 0.2)


def vision_recognized_marker_number_seven(msg):
    global move_forward_mode
    move_forward_mode = False
    if ir_distance_sensor_ctrl.get_distance_info(1) < 10:  # cases where there is U turn and may not be 1 meter till end of road
        turn_right()
    elif ir_distance_sensor_ctrl.get_distance_info(1) < 115:  # cases where there is U turn and may not be 1 meter till end of road (check for less than 115cm)
        chassis_ctrl.move_with_distance(0, ir_distance_sensor_ctrl.get_distance_info(1)-10)  # move forward until 10cm to obstetrical, TODO: to tune
        turn_right()
    else:
        chassis_ctrl.move_with_distance(0, 1.1)  # detected at 1m + 10cm buffer to go into middle of the road TODO: to tune
        turn_right()
    move_forward_mode = True


def vision_recognized_marker_number_six(msg):
    global move_forward_mode
    move_forward_mode = False
    if ir_distance_sensor_ctrl.get_distance_info(1) < 10:  # cases where there is U turn and may not be 1 meter till end of road
        turn_left()
    elif ir_distance_sensor_ctrl.get_distance_info(1) < 115:  # cases where there is U turn and may not be 1 meter till end of road (check for less than 115cm)
        chassis_ctrl.move_with_distance(0, ir_distance_sensor_ctrl.get_distance_info(1)-12)  # move forward until 12cm to obstetrical (extra 2cm for buffer in sensor processing time), TODO: to tune
        turn_left()
    else:
        chassis_ctrl.move_with_distance(0, 1.1)  # detected at 1m + 10cm buffer to go into middle of the road TODO: to tune
        turn_left()
    move_forward_mode = True


def vision_recognized_car(msg):
    global move_forward_mode, car_avoid_mode
    if ir_distance_sensor_ctrl.check_condition('ir_distance_1_ge_10'):  # its very close to the robot, move back 20cm and then switch to side lane and overtake (if its face to face, it should not be very close)
        chassis_ctrl.move_with_distance(180, 0.2)  # move back 20cm to easier see if its a robot
        if vision_ctrl.check_condition(rm_define.cond_recognized_car):
            chassis_ctrl.move_with_distance(270, 0.26)  # robot width 24cm, move to left side 26cm to switch lane
            chassis_ctrl.set_trans_speed(3.5)  # overtake at max speed
            chassis_ctrl.move_with_distance(0, 0.6)  # robot length 34cm + 20cm moved back + 6cm buffer
            chassis_ctrl.set_trans_speed(move_forward_spd)  # to tune
            chassis_ctrl.move_with_distance(90, 0.26)  # robot width 24cm, move to right side 26cm to switch back lane
    else:
        move_forward_mode = False
        car_avoid_mode = True
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
        car_avoid_mode = False
        move_forward_mode = True


def vision_recognized_marker_number_three(msg):  # pick up
    pickup()




def vision_recognized_marker_number_five(msg):  # terminate
    led_ctrl.set_top_led(rm_define.armor_top_all, 255, 0, 0, rm_define.effect_always_on)
    led_ctrl.set_bottom_led(rm_define.armor_bottom_all, 255, 0, 0, rm_define.effect_always_on)
    rmexit()