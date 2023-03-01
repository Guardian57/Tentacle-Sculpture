from configparser import ConfigParser

config = ConfigParser()
'''
    CONFIG FORMATTING GUIDE
    
    "animation_name": 'motorNumber_targetAngle_delayAfterCommand | delay'
    
    "example": '1_180 0_90 | 3',
    motor 1 moves to 180 degrees. Then moves motor 0 to 90 degrees. Then delays by 3 seconds.
    
    IMPORTANT:
    
    Max Angle : 180
    Moves to an angle, not by an angle
    0_90 moves motor 0 to 90 degrees. If the next command is 0_95, it moves to 95 degrees, not to 185
    
    If last animation in list, do not put a comma after the closing quotation mark
    
    Use three apostrophes in actual file
    
    Once finished editing, run the Config_Writer to save to the config file
'''

config["DEFAULT"] = {
    
    "test_animation": '''
        0_100 1_100 
        0_220 1_30 3_150 
        0_10 1_10 2_180 3_30 
        0_0 1_0 2_0 3_0 
        ''',
    
    "motor_test": '''
        0_180
        0_0
        1_180
        1_0
        2_180
        2_0
        3_180
        3_0
        ''',
    
    "idle_twitch": '''
        0_100 1_100 | 1
        0_0 1_0
        '''

}
    
with open("animation_configs.ini", "w") as f:
    config.write(f)

exit()