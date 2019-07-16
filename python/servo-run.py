# servo-run.py
# Script for using keyboard to control the Junkbot robot

hardware = True   # Is i2c PWM controller board present. It is useful to
                  # be able to turn this off during development.
tuning   = True   # Additionsl options for adjusting tuning parameters.
debug    = False

from pynput.keyboard import Key, Listener

import time

if hardware:
    import board
    import busio
    from adafruit_servokit import ServoKit
    kit = ServoKit(channels=16)

motorLeft  = 0
motorRight = 1

# Motor Labels
Left                  = 0
Right                 = 1
motor                 = [motorLeft,motorRight] # Motor channels
# Drive Tuning
drive_direction       = [1,1]
drive_throttle_step   = 1
drive_steering_step   = 1
drive_bias            = 0 # Left/Right ratio fix for motor variation

# There are a couple of different driving/stearing modes
drive_mode            = 0

microservo0 = 2
microservo1 = 3

# Dynamic variables
throttle = 0  # Use signed integer -100..100 for integer steps
steering = 0  # Used for differential motor driving Range -100..100

# Zero Throttle
if hardware:
    kit.continuous_servo[motorLeft].throttle  = 0.0
    kit.continuous_servo[motorRight].throttle = 0.0

def show_tuning():
    print()
    print('  Throttle:  {0}'.format(throttle))
    print('  Steering:  {0}'.format(steering))
    print('  drive_direction     = [{0},{1}]'.format(drive_direction[Left],
                                                     drive_direction[Right]))
    print('  drive_throttle_step = {0}'.format(drive_throttle_step))
    print('  drive_steering_step = {0}'.format(drive_steering_step))
    print('  drive_bias          = {0}'.format(drive_bias))

def show_keys():    
    print("-------")
    print("Junkbot")
    print("-------")
    print("");
    print("To drive the Junkbot from the keyboard use the following keys.")
    print("Press a key multiple times to increase the movement speed.")
    print("")
    print("  Keys:")
    print("            w     - Forward")
    print("         a  s  d  - Left / Reverse / Right")
    print("")
    print("          space   - Emergency Stop")
    print("")
    print("            q     - Quit program")
    print("")
    if tuning:
        print("  Tuning:")
        print("    t      - Show tuning numbers")
        print("    r f    - Increase/decrease throttle step size")
        print("    z x    - Decrease/increase steering step size")
        print("    [ ]    - Toggle Motor directions")
        print("    , .    - Adjust Left/Right Bias Ratio")
        show_tuning()

def on_press(key):
    global throttle
    global steering
    global drive_direction
    global drive_bias
    global drive_throttle_step
    global drive_steering_step

    do_quit = False
    
    try:
        if debug:
            print('{0} pressed'.format(key.char))

        if key.char == 'w':
            throttle = throttle + drive_throttle_step
        if key.char == 's':
            throttle = throttle - drive_throttle_step
        if key.char == 'a':
            steering = steering - drive_steering_step
        if key.char == 'd':
            steering = steering + drive_steering_step
        if key.char == ' ':
            throttle = 0
            steering = 0
        if key.char == 'q':
            throttle = 0
            steering = 0
            do_quit  = True

        # Tuning
        if key.char == 't':
            show_tuning()

        # Drive throttle step size
        if key.char == 'r':
            drive_throttle_step    = drive_throttle_step + 1
        if key.char == 'f':
            drive_throttle_step    = drive_throttle_step - 1

        # Drive steering  step size
        if key.char == 'x':
            drive_steering_step    = drive_steering_step + 1
        if key.char == 'z':
            drive_steering_step    = drive_steering_step - 1

        # Drive direction
        if key.char == '[':
            drive_direction[Left]  = -1 * drive_direction[Left]
        if key.char == ']':
            drive_direction[Right] = -1 * drive_direction[Right]

        # Bias
        if key.char == ',':
            drive_bias             = drive_bias - 1
        if key.char == '.':
            drive_bias             = drive_bias + 1
            
        # Raw Limits
        if throttle > 100:  throttle = 100
        if throttle < -100: throttle = -100
        if steering > 100:  steering = 100
        if steering < -100: steering = -100

        # Tuning limits
        if drive_throttle_step < 1: drive_throttle_step = 1
        if drive_steering_step < 1: drive_steering_step = 1
        if drive_bias > 100:  drive_bias = 100
        if drive_bias < -100: drive_bias = -100

        # Scale integers to range -1.0 to 1.0
        if drive_mode == 0:
            left_throttle = drive_direction[Left] \
                * (100 - drive_bias) / 100.0 \
                * ((throttle - steering) / 100.0)

            right_throttle = drive_direction[Right] \
                * (100 + drive_bias) / 100.0 \
                * ((throttle + steering) / 100.0)
            # Not true steering as turn rate does not increase with throttle
            # Might need to use ratio's instead
   
        # Scaled limits
        if left_throttle > 1.0:
            left_throttle = 1.0
        if left_throttle < -1.0:
            left_throttle = -1.0

        if right_throttle > 1.0:
            right_throttle = 1.0
        if right_throttle < -1.0:
            right_throttle = -1.0

        if debug:
            print('Throttle {0}'.format(throttle))
            print('Steering {0}'.format(steering))
        if hardware:
            kit.continuous_servo[motorLeft].throttle  = left_throttle
            kit.continuous_servo[motorRight].throttle = right_throttle

        if do_quit:
            return False
        
    except AttributeError:
        if debug:
            print('Key {0} pressed'.format(key))

        if key == Key.space:
            # Emergency Reset
            throttle = 0
            steering = 0
            if debug:
                print('Throttle {0}'.format(throttle))
                print('Steering {0}'.format(steering))
            if hardware:
                kit.continuous_servo[motorLeft].throttle  = 0.0
                kit.continuous_servo[motorRight].throttle = 0.0
            
        #Add Code

def on_release(key):
    if debug:
        print('{0} release'.format(key))

    if key == Key.esc:
        # Shutdown and Stop listener
        if hardware:
            kit.continuous_servo[motorLeft].throttle  = 0.0
            kit.continuous_servo[motorRight].throttle = 0.0
        return False

show_keys()
# Collect events until released
with Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()
