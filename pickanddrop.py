def predict_dist():
    s1 = vision_ctrl.get_marker_detection_info()  # ir info in list s1
    w1, h1 = s1[3], s1[4]  # y coords, width
    m = 10  # cm TODO
    chassis_ctrl.move_with_distance(0, m / 100)  # moves 10cm
    s2 = vision_ctrl.get_marker_detection_info()
    w2, h2 = s2[3], s2[4]  # y coords2, width2
    new_dist_from_obj = (((w2 / (w2 - w1)) - m) + ((h2 / (h2 - h1)) - m)) / 2  # avg of height and width changes
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
    print("approaching humanoid")
    # dist below are in cm
    minDist = 12  # TODO
    ir_dist = ir_distance_sensor_ctrl.get_distance_info(1)
    if ir_dist > 12:  # this is diff from minDist, this is 10cm + 2cm buffer for measure distance. If there are sth in front within 10cm, we cant crash onto it.
        calcDist = predict_dist()
    else:
        calcDist = ir_dist
    using_ir = True
    if abs(ir_dist - calcDist) >= 10:  # TODO
        dist = calcDist
        using_ir = False
    else:
        dist = ir_dist
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
    print("leaving dropoff point")
    turn_left()  # face marker
    chassis_ctrl.rotate_with_time(rm_define.anticlockwise, 0.3)  # away from marker
    robotic_arm_ctrl.moveto(200, -50, wait_for_complete=True)
    print("dropoff completed")

