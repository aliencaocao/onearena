def chassis_impact_detection(msg):  # todo, rotate in a circle and store IR info to decide where to move, check which side is collide
    chassis_ctrl.stop()
    chassis_ctrl.move_with_distance(180, 0.2)


def vision_recognized_marker_number_seven(msg):
    chassis_ctrl.stop()
    print('Distance to marker:', ir_distance_sensor_ctrl.get_distance_info(1))
    chassis_ctrl.move_with_distance(0, ir_distance_sensor_ctrl.get_distance_info(1) / 100)  # move forward until 10cm to obstetrical,
    turn_right()


def vision_recognized_marker_number_six(msg):
    chassis_ctrl.stop()
    print('Distance to marker:', ir_distance_sensor_ctrl.get_distance_info(1))
    chassis_ctrl.move_with_distance(0, ir_distance_sensor_ctrl.get_distance_info(1) / 100)  # move forward until 10cm to obstetrical,
    turn_left()


def vision_recognized_car(msg):
    print('Another robot detected, stopping')
    while vision_ctrl.get_car_detection_info()[0]:  # while there is still car in sight
        chassis_ctrl.set_trans_speed(move_forward_spd * 0.7)  # slow down for safety
        if ir_distance_sensor_ctrl.get_distance_info(1) <= ir_detection_distance:  # if its close enough, stop
            chassis_ctrl.stop()
            chassis_ctrl.set_trans_speed(2)  # overtake at higher speed
            chassis_ctrl.move_with_distance(270, 0.26)  # robot width 24cm, move to left side 26cm to switch lane
            chassis_ctrl.move_with_distance(0, 0.66)  # robot length 41cm + 20cm moved back + 5cm buffer
            chassis_ctrl.move_with_distance(90, 0.26)  # robot width 24cm, move to right side 26cm to switch back lane
            chassis_ctrl.set_trans_speed(move_forward_spd)
        else:
            chassis_ctrl.move(0)
            car_info = vision_ctrl.get_car_detection_info()
            if car_info[0]:  # if there is car detected (just check again in case)
                car_w, car_h = car_info[3], car_info[4]
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
    chassis_ctrl.set_trans_speed(move_forward_spd)


def vision_recognized_marker_number_three(msg):  # pick up
    pickup()


def vision_recognized_letter_A(msg):  # drop off
    dropoff()


def vision_recognized_marker_number_five(msg):  # terminate
    print('terminating')
    led_ctrl.set_top_led(rm_define.armor_top_all, 255, 0, 0, rm_define.effect_always_on)
    led_ctrl.set_bottom_led(rm_define.armor_bottom_all, 255, 0, 0, rm_define.effect_always_on)
    rmexit()
