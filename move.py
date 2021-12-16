move_forward_mode = True
car_avoid_mode = False
pickup_mode = False
turn_mode = False


def turn_left():
    global move_forward_mode, turn_mode
    move_forward_mode = False
    turn_mode = True
    chassis_ctrl.set_rotate_speed(600)  # to tune
    chassis_ctrl.rotate_with_degree(rm_define.anticlockwise, 90)
    turn_mode = False
    move_forward_mode = True


def turn_right():
    global move_forward_mode, turn_mode
    move_forward_mode = False
    turn_mode = True
    chassis_ctrl.set_rotate_speed(600)  # to tune
    chassis_ctrl.rotate_with_degree(rm_define.clockwise, 90)
    turn_mode = False
    move_forward_mode = True


def init():
    vision_ctrl.enable_detection(rm_define.vision_detection_marker)
    vision_ctrl.enable_detection(rm_define.vision_detection_car)
    ir_distance_sensor_ctrl.enable_measure(1)
    media_ctrl.exposure_value_update(rm_define.exposure_value_large)


def move_forward():
    global move_forward_mode
    chassis_ctrl.set_trans_speed(2)  # to tune
    vision_ctrl.set_marker_detection_distance(1)  # to tune with brake distance and turning distance, not setting in init to prevent conflict with other modules

    while move_forward_mode:  # will only exit loop here after move_forward_mode flag is set to False in other functions
        if ir_distance_sensor_ctrl.check_condition("ir_distance_1_ge_20"):  # ir_distance_1_ge_DISTANCE in CM e.g. ir_distance_1_ge_10 -> 10cm
            chassis_ctrl.stop()  # stop moving when detected stuff in 20cm and resume moving when there is none
            tools.timer_ctrl(rm_define.timer_start)
            while tools.timer_current() < 5.0 and ir_distance_sensor_ctrl.check_condition("ir_distance_1_ge_20"):
                pass
            if ir_distance_sensor_ctrl.check_condition("ir_distance_1_ge_20"):  # if after waiting for 5s, still have stuff blocking, move back 20cm and exit move forward mode
                chassis_ctrl.move_with_distance(180, 0.2)
                # add check if robot is here, maybe move below to robot detect callback
                chassis_ctrl.move_with_distance(270, 0.26)  # robot width 24cm, move to left side 26cm to switch lane
                chassis_ctrl.move_with_distance(180, 0.2)
                move_forward_mode = False
                break
        else:
            chassis_ctrl.move(0)  # move infinitely forward


def start():
    global move_forward_mode
    init()
    while True:  # to merge with other modules
        if move_forward_mode:
            move_forward()
        elif pickup_mode:
            pass
        else:
            pass


def chassis_impact_detection(msg):
    global move_forward_mode
    move_forward_mode = False
    chassis_ctrl.move_with_distance(180, 0.2)


def vision_recognized_marker_number_seven(msg):
    turn_right()


def vision_recognized_marker_number_six(msg):
    turn_left()


def vision_recognized_car(msg):
    global move_forward_mode, car_avoid_mode

    car_avoid_mode = True
    while True:  # car might be moving so need constantly check, loop until no more car is detected then can hand control back
        car_info = vision_ctrl.get_car_detection_info()
        if car_info:
            car_w, car_h = car_info[3], car_info[4]
            if car_w > 0.12 or car_h > 0.22:  # to tune see how big the robot is when its close enough
                chassis_ctrl.stop()
        else:
            break
    car_avoid_mode = False


def vision_recognized_marker_number_five(msg):  # terminate
    led_ctrl.set_top_led(rm_define.armor_top_all, 255, 0, 0, rm_define.effect_always_on)
    led_ctrl.set_bottom_led(rm_define.armor_bottom_all, 255, 0, 0, rm_define.effect_always_on)
    rmexit()