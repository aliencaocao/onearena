pickup_mode = False

def vision_recognized_marker_number_three(msg):
    global pickup_mode
    pickup_mode = True
    while True:
        id_index = vision_ctrl.get_marker_detection_info().index(13)
        if id_index:
            human_info = vision_ctrl.get_marker_detection_info()[id_index+1:id_index+5]
            human_x, human_y = human_info[0], human_info[1]
            human_w, human_h = human_info[2], human_info[3]
        else:
            break
    pickup_mode = False

def pickup():
    global human_x, human_y, human_w, human_h

    # face marker
    while abs(human_x - 0.5) > 0.05: 
        if human_x > 0.5:
            chassis_ctrl.rotate(rm_define.clockwise)
        else if human_x < 0.5:
            chassis_ctrl.rotate(rm_define.anticlockwise)

    # init claw above humanoid
    init_y = 0.2 # todo - just above humanoid
    robotic_arm_ctrl.moveto(0.5, init_y, wait_for_complete = False) 
    while not(gripper_ctrl.is_open()):
        gripper_ctrl.open() # open claw fully

    # move closer to marker
    minWidth = 30  # todo 
    while human_w < minWidth:
        chassis_ctrl.move_degree_with_speed(0,30)

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


def vision recognized_letter_A(msg):
    dropoff()

def dropoff():
    gripper_ctrl.update_power_level(1) # humanoid slides down within claw onto floor
#    robotic_arm_ctrl.moveto(0.5, 1, wait_for_complete = False) # move to base of humanoid
    while not(gripper_ctrl.is_closed()):
        gripper_ctrl.close() # releases humanoid

    # reverse and face elsewhere
    chassis_ctrl.move_with_distance(180,0.05) 
    rotationTime = 2 # todo - such that vision marker is out of view
    chassis_ctrl.rotate_with_time(rm_define.clockwise,2)


def start():
    global move_forward_mode
    init()
    while True:  # to merge with other modules
        if move_forward_mode:
            move_forward()
        elif pickup_mode:
            pickup()
        else:
            pass

