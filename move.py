led_ctrl.set_bottom_led(rm_define.armor_bottom_all, 255, 0, 0, rm_define.effect_always_on)
ir_detection_distance = 50
move_forward_spd = 0.7

def init():
    print('Initializing...')
    media_ctrl.exposure_value_update(rm_define.exposure_value_large)
    robotic_arm_ctrl.moveto(200, -50, wait_for_complete=True)
    vision_ctrl.set_marker_detection_distance(3)  # set to furthest distance to detect humanoid better
    ir_distance_sensor_ctrl.enable_measure(1)
    vision_ctrl.enable_detection(rm_define.vision_detection_car)
    vision_ctrl.enable_detection(rm_define.vision_detection_marker)


def turn_left():
    print('Turning Left')
    chassis_ctrl.set_rotate_speed(60)
    chassis_ctrl.rotate_with_degree(rm_define.anticlockwise, 90)


def turn_right():
    print('Turning Right')
    chassis_ctrl.set_rotate_speed(60)
    chassis_ctrl.rotate_with_degree(rm_define.clockwise, 90)


def move_forward(distance=''):  # distance in m
    chassis_ctrl.set_trans_speed(move_forward_spd)
    if ir_distance_sensor_ctrl.get_distance_info(1) <= ir_detection_distance:  # stop moving when detected stuff and resume moving when there is none
        if distance and not vision_ctrl.check_condition(rm_define.cond_recognized_car):  # if distance param is passed and not car blocking, means it is the marker block, then can continue
            print('Detected object but is not a car and current travelling to a marker. Continue moving forward by distance (m):', ir_distance_sensor_ctrl.get_distance_info(1) / 100)
            chassis_ctrl.move_with_distance(0, ir_distance_sensor_ctrl.get_distance_info(1) / 100)
        else:
            print('Stopping as detected obj at distance:', ir_distance_sensor_ctrl.get_distance_info(1))
            # robot detected callback should be triggered here if it is a robot
            chassis_ctrl.stop()
    else:
        if distance:
            print('Moving forward by distance (m):', distance)
            chassis_ctrl.move_with_distance(0, distance)
        else:
            print('Moving forward')
            chassis_ctrl.move(0)  # move infinitely forward


def predict_dist():
    print('predicting distance')
    s1 = vision_ctrl.get_marker_detection_info()  # ir info in list s1
    w1, h1 = s1[3], s1[4]  # y coords, width
    m = 10  # cm TODO
    chassis_ctrl.move_with_distance(0, m / 100)  # moves 10cm
    s2 = vision_ctrl.get_marker_detection_info()
    w2, h2 = s2[3], s2[4]  # y coords2, width2
    new_dist_from_obj = (((m * w2 / (w2 - w1)) - m) + ((m * h2 / (h2 - h1)) - m)) / 2  # avg of height and width changes
    print('predicted distance (cm):', new_dist_from_obj)
    return new_dist_from_obj  # cm


def pickup():
    # begin
    print('pickup started')
    chassis_ctrl.stop()  # stop movement for measurement
    print('claw opening')
    # open claw fully
    while not gripper_ctrl.is_open():
        gripper_ctrl.open()
    # position claw at upper body of humanoid (8.97cm from ground)
    print("readying claw for pickup")
    robotic_arm_ctrl.moveto(200, -15, wait_for_complete=True) # TODO

    # approach humanoid until it is minimum distance away
    # dist below are in cm
    minDist = 12  # TODO
    ir_dist = ir_distance_sensor_ctrl.get_distance_info(1)
    if ir_dist > 12:  # this is diff from minDist, this is 10cm + 2cm buffer for measure distance. If there are sth in front within 10cm, we cant crash onto it.
        calcDist = predict_dist()
    else:
        calcDist = ir_dist
    using_ir = True
    if abs(ir_dist - calcDist) >= 10:  # TODO
        print('Using calculated distance')
        dist = calcDist
        using_ir = False
    else:
        print('Trusting IR sensor')
        dist = ir_dist
    print("Approaching humanoid")
    if using_ir:
        chassis_ctrl.set_trans_speed(0.25)  # need go super slow TODO
        while dist > minDist:
            chassis_ctrl.move(0)
            dist = ir_distance_sensor_ctrl.get_distance_info(1)
    else:
        chassis_ctrl.set_trans_speed(move_forward_spd*0.7)  # no need go super slow TODO
        chassis_ctrl.move_with_distance(0, dist / 10)

    # grab
    print('securing humanoid')
    gripper_ctrl.update_power_level(4)
    while not gripper_ctrl.is_closed():
        gripper_ctrl.close()  # close fully to grab

    # lift
    print("lifting off ground")
    robotic_arm_ctrl.move(0, 10, wait_for_complete=True)  # lift 1cm off ground

    # end
    print('pickup completed')


def dropoff():
    # begin
    print("dropoff started")

    # turning to face drop off
    print("turning to dropoff point")
    turn_right()

    # humanoid slides down within claw onto floor
    print("reducing grip strength")
    gripper_ctrl.update_power_level(1)

    # open claw
    print("dropping off humanoid")
    while not (gripper_ctrl.is_open()):
        gripper_ctrl.open()

    # reverse and face away from dropoff vision marker
    print("reversing")  # to prevent topple
    chassis_ctrl.set_trans_speed(0.05)
    chassis_ctrl.move_with_distance(180, 0.15)
    print("leaving dropoff point")
    turn_left()  # face back the road
    chassis_ctrl.move_with_distance(90, 0.14)
    robotic_arm_ctrl.moveto(200, -50, wait_for_complete=True)
    chassis_ctrl.set_trans_speed(move_forward_spd)
    print("dropoff completed")


def start():
    init()
    while True:
        print(vision_ctrl.get_marker_detection_info())
        if vision_ctrl.check_condition(rm_define.cond_recognized_marker_number_two):
            chassis_ctrl.stop()
            print('Distance to marker:', ir_distance_sensor_ctrl.get_distance_info(1))
            chassis_ctrl.move_with_distance(0, (ir_distance_sensor_ctrl.get_distance_info(1) - 2) / 100)
            turn_right()
        elif vision_ctrl.check_condition(rm_define.cond_recognized_marker_trans_red_heart):
            chassis_ctrl.stop()
            print('Distance to marker:', ir_distance_sensor_ctrl.get_distance_info(1))
            chassis_ctrl.move_with_distance(0, (ir_distance_sensor_ctrl.get_distance_info(1) - 2) / 100)
            turn_left()
        elif vision_ctrl.check_condition(rm_define.cond_recognized_marker_number_three):
            pickup()
        elif vision_ctrl.check_condition(rm_define.cond_recognized_marker_number_four):
            dropoff()
        else:
            move_forward()


# def vision_recognized_marker_number_five(msg):  # terminate
#     print('terminating')
#     led_ctrl.set_top_led(rm_define.armor_top_all, 255, 0, 0, rm_define.effect_always_on)
#     led_ctrl.set_bottom_led(rm_define.armor_bottom_all, 255, 0, 0, rm_define.effect_always_on)
#     rmexit()