def 90DegRight():


# when bus stop marker is detected, turn to face humanoid

'''to change'''
turnDeg = 90  # how many degree rotation of wheel to make robot face right
'''during testing'''

chassis_ctrl.rotate_with_degree(rm_define.clockwise, turnDeg)


def pickUp(x, y, w, h):
    # section b: to pick up humanoids
    # if humanoid vision marker detected 0.5m away
    # assumes only 1 humanoid in view

    global centreX  # to centre on horizontal

    '''to change'''
    minimumWidth = 20  # milimetres away before engaging with humanoid
    initialHeight = 0  # so long above 4.5cm humanoid, can lower to save time

    # in case
    grabX = 0
    grabY = 0

    lift = 10  # enough to not drag on the ground, try not to tilt so less likely to topple when putting down
    '''during testing'''

    # lift higher than humanoid to avoid toppling it
    robotic_arm_ctrl.moveto(centreX, initialHeight, wait_for_complete=False)
    while not (gripper_ctrl.is_open()):
        gripper_ctrl.open()  # open claw fully

    while w < minimumWidth:
        # move closer to marker
        chassis_ctrl.move_with_speed(0, 1)
        info = vision_ctrl.get_marker_detection_info()
        w = info[4]

    robotic_arm_ctrl.moveto(x, y, wait_for_complete=True)  # shift claw to target coordinates

    # in case grip not very secure - extra
    robotic_arm_ctrl.move(grabX, grabY, wait_for_complete=True)  # shift claw closer to target to secure pick up

    while not (gripper_ctrl.is_closed()):
        gripper_ctrl.close()  # close fully to grab
    robotic_arm_ctrl.move(0, lift, wait_for_complete=True)  # lift off ground


def dropOff():  # todo

    # section C: put down humanoid without toppling
    '''to change'''
    lift = -10
    '''during testing'''

    robotic_arm_ctrl.move(0, lift, wait_for_complete=True)  # place on ground
    while not (gripper_ctrl.is_open()):
        gripper_ctrl.open()  # open claw fully
    chassis_ctrl.move_with_distance(180, 0.03)  # reverse away from humanoid to avoid collision


def initialise():
    led_ctrl.set_bottom_led(rm_define.armor_bottom_all, 0, 0, 255, rm_define.effect_always_on)
    info = []
    robotic_arm_ctrl.recenter()
    centreX = robotic_arm_ctrl.get_position()[0]
    gripper_ctrl.update_power_level(4)
    chassis_ctrl.set_trans_speed(2)  # arbitrary speed values
    chassis_ctrl.set_rotate_speed(1.5)
    vision_ctrl.enable_detection(rm_define.vision_detection_marker)
    vision_ctrl.set_marker_detection_distance(1)


def driverlessBus():  # todo
    initialise()
    while True: '''change to while endpoint vision marker not detected'''
    info = vision_ctrl.get_marker_detection_info()


# section A: detecting vision markers, conditionals
'''
        if the id of vision marker no 1 corresponds to pick up point:
            pickUp(info[2],info[3],info[4],info[5])
'''
info = vision_ctrl.get_marker_detection_info()

led_ctrl.set_bottom_led(rm_define.armor_bottom_all, 255, 0, 0, rm_define.effect_always_on)  # terminate program


def start():
    # testing bed
    driverlessBus()
#    90DegRight()