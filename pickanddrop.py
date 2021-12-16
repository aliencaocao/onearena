def pickup():
    # begin
    global move_forward_mode, pickup_mode
    print('pickup started')
    move_forward_mode = False
    pickup_mode = True

    # open claw fully
    while not (gripper_ctrl.is_open()):
        print("claw opening")
        gripper_ctrl.open()  
    
    # position claw at middle of humanoid (5.2cm from ground)
    print("readying claw for pickup")
    robotic_arm_ctrl.moveto(200, -15, wait_for_complete = True) 


    # approach humanoid until it is minimum distance away
    print("approaching humanoid")
    minDist = 12 # todo: replace with math figure later
    dist = ir_distance_sensor_ctrl.get_distance_info(1)
    while dist > minDist:
        chassis_ctrl.move(0)
        dist = ir_distance_sensor_ctrl.get_distance_info(1)


    # grab
    print('securing humanoid')
    gripper_ctrl.update_power_level(4)
    while not (gripper_ctrl.is_closed()):
        gripper_ctrl.close()  # close fully to grab

    #lift
    print("lifting off ground")
    robotic_arm_ctrl.move(0, 5, wait_for_complete=True)  # lift 5mm off ground

    # end
    print('pickup completed')
    pickup_mode = False
    move_forward_mode = True


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
    turn_left() # face marker
    chassis_ctrl.rotate_with_time(rm_define.anticlockwise, 0.3)  # away from marker

    print("dropoff completed")