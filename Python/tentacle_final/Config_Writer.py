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

    
    "test_animation": "0_250_* 1_250_0 0_500_0 1_500_0 0_0_0 1_0_0"
    
}
    
with open("animation_configs.ini", "w") as f:
    config.write(f)

exit()