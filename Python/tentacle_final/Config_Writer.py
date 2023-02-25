from configparser import ConfigParser

config = ConfigParser()
'''
    CONFIG FORMATTING GUIDE
    
    "animation_name": "motorNumber_targetAngle_delayAfterCommand",
    
    "example": "1_200_2 0_100_0",
    motor 1 moves to 200 degrees then waits 2 seconds. Then moves motor 0 to 100 degrees and does not delay after
    
    to make two animations trigger simultaneously, replace delayAfterCommand with *
    "example": 2_100_* 1_200_0",
    
    IMPORTANT:
    if last animation in list, do not put a comma after the closing quotation mark
    
    Once finished editing, run the Config_Writer to save to the config file
'''

config["DEFAULT"] = {

    
    "test_animation": "0_150_* 1_50_* 2_25_* 0_0_* 3_150_0 2_0_* 3_0_* 1_0_0",
    "test_animation2": "0_250_* 1_250_0 0_500_0 1_500_0 0_0_0 1_0_0",
    "idle_twitch": "0_100_* 1_100_0 0_200_0 1_200_0 0_0_0 1_0_0",
    "motor_test": "0_200_3 0_0_3 1_200_3 1_0_3 2_200_3 2_0_3 3_200_3 3_0_3"
    
}
    
with open("animation_configs.ini", "w") as f:
    config.write(f)

exit()