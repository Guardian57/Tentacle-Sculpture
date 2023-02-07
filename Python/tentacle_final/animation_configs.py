from configparser import ConfigParser

config = ConfigParser()


config["DEFAULT"] = {
    "animation": "0_100_2 1_100_1 2_100_1 3_100_7",
    "animation2": "0_15_2 1_23_1 2_10_0 3_45_7",
    "animation3": "0_60_2 0_0_3 0_60_0"
}
    
with open("animation_configs.ini", "w") as f:
    config.write(f)

