from smbus import SMBus
import time
import numpy as np

#cap = cv2.VideoCapture(0)

class PoseReader:
    
    
    
    def __init__(self):
        #self.stage = ""
        self.tracking = False
        
        # sets up variables necessary for individual pose checks. split into functions for organization
        self.set_target()
        self.set_wave()
        
        
        print("Pose Reader initialized")
    
    
    def set_target(self):
        self.priority_limb = "head"
        
    
    def set_wave(self):
        self.right_wave = [-1, 0, 0]
        self.left_wave = [-1, 0, 0]
        self.is_waving = False
        self.wave_time = 0
        
    
    def read_pose(self, landmarks):
        '''
            LANDMARK INFO:
                landmarks[0] : head x and y
                landmarks[1] : left landmarks
                landmarks[2] : right landmarks
                
                arm landmark order:
                0: hip
                1: shoulder
                2: elbow
                3: wrist
                4: pinky
                
                angle order:
                0: arm
                1: elbow
                2: wrist
        '''
        
        left_angles = self.create_joint_angles(landmarks[1])
        right_angles = self.create_joint_angles(landmarks[2])
        
        
        
        if self.tracking == False:
            self.uptime = time.perf_counter()
            self.tracking = True
            print("Reading Pose!")
        
        
        #self.is_waving = (waving(self.right_wave, right_angles) or waving(self.left_wave, left_angles) or self.wave_time!=0)
        #print("waving: " + str(self.is_waving))
    
    
    
    def create_joint_angles(self, landmarks):
        '''
            arm landmark order:
                0: hip
                1: shoulder
                2: elbow
                3: wrist
                4: pinky
                
            angle order:
                0: arm
                1: elbow
                2: wrist
                
                left_arm_angle = calculate_angle(left_hip, left_shoulder, left_elbow)
                left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
                left_wrist_angle = calculate_angle_small(left_elbow, left_wrist, left_pinky)
                
                left_angles = [left_arm_angle, left_elbow_angle, left_wrist_angle]
        '''
        
        arm_angle = self.calculate_angle(landmarks[0], landmarks[1], landmarks[2])
        elbow_angle = self.calculate_angle(landmarks[1], landmarks[2], landmarks[3])
        wrist_angle = self.calculate_angle_small(landmarks[2], landmarks[3], landmarks[4])
        
        angles = [arm_angle, elbow_angle, wrist_angle]
        return angles
        
    
    def calculate_angle(self, a, b, c): # calculates angle between three given points
        a = np.array(a) #first
        b = np.array(b) #mid
        c = np.array(c) #end
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])  # radian calculation of angle 
        angle = np.abs(radians*180.0/np.pi) # converts angle to degrees for ease of use

        if angle > 180.0: # keeps angles under 180 degrees instead of using unit circle angles. 
            angle = 360-angle # remove if statement and this line if unit circle angles are desired

        return angle

    def calculate_angle_small(self, a, b, c): # calculates angle between three given points
        a = np.array(a) #first
        b = np.array(b) #mid
        c = np.array(c) #end
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])  # radian calculation of angle 
        angle = np.abs(radians*180.0/np.pi) # converts angle to degrees for ease of use


        return angle

    '''
    def waving(self, wave_list, angles):
        #wave_list order: wave step, wave time, current state
        #angles order: arm elbow wrist
        timer_wait = 1.5
        wave_max = 5
        try:
            elapsed_time = time.perf_counter() - self.uptime
            wrist_angle = angles[2] - 180
            #print("Arm: " + str(angles[0]))
            #print("Elbow: " + str(angles[1]))
            if wave_list[0] == -1:
                if elapsed_time > 3:
                    wave_list[0] = 0
                    print("ready for wave")
            
            if (angles[0] > 50) or (angles[1] < 90):
                
                if wave_list[0] == 0:
                    wave_list[0] = 1
                    wave_list[1] = time.perf_counter()+timer_wait
                    
                    if wrist_angle > 0:
                        wave_list[2] = 1
                    else:
                        wave_list[2] = -1
                        
                    print("first wave. angle: " + str(wrist_angle))
                    
                    
                
            
                elif wave_list[0] > 0 and wave_list[1] - time.perf_counter() > 0:
                    #print(str(waveList[2]) + " " + str(wristAngle))
                    
                    if (wave_list[2] > 0 and wrist_angle < 0) or (wave_list[2] < 0 and wrist_angle > 0):
                        print("wave " + str(wave_list[0]))
                        wave_list[0] +=1
                        wave_list[1] = time.perf_counter()+timer_wait
                        wave_list[2] *= -1
                        
                        if wave_list[0] == wave_max:
                            wave_list[0] = wave_list[0]+1
                            wave_list[1] = 0
                            wave_list[2] = 0
                            print("final wave")
                            return True
                    
                        
                elif wave_list[1] - time.perf_counter() < 0 and wave_list[0] < wave_max:
                    print("wave timeout")
                    print()
                    wave_list[0] = 0
                    wave_list[1] = 0
                    
            else:
                if wave_list[0] > wave_max:
                    print("Reset Waiting")
                    wave_list[0] = 0
                    wave_list[1] = 0
                    
            #print()
            return False
            
            
        except:
            print("wave error")
        return False

            '''
    
    
    '''
    def read_pose(self, cap):
        pass
                     
                    # 50 is about arm up
                    # 90 is about elbow up
                    
                    
                    new_stage = ""
                    
                    if left_arm_angle > 50:
                        new_stage += "_lArUp" # left arm up
                    if right_arm_angle > 50:
                        new_stage += "_rArUp" # right arm up
                    if left_elbow_angle < 90:
                        new_stage += "_lElUp" # left elbow up
                    if right_elbow_angle < 90:
                        new_stage += "_rElUp" # right elbow up
                    
                    
                    self.is_waving = (waving(self.right_wave, right_angles) or waving(self.left_wave, left_angles) or self.wave_time!=0)
                    
                    
                    if self.is_waving == True and self.wave_time == 0:
                        
                        self.wave_time = time.perf_counter()
                        new_stage+= "_wave"
                    
                    
                    
                    if time.perf_counter() - self.wave_time > 3 and self.is_waving == True:
                        try:
                            print("stop wave")
                            self.is_waving = False
                            self.wave_time = 0
                            new_stage+= "_!waving"
                        except:
                            print("pose search error")
                    
                    
                    if self.stage != new_stage: # checks if the current poses differ from the previously recorded ones
                        if len(self.stage) > 1:
                            #print(new_stage)
                            pass
                        #write_data(new_stage)
                        self.stage = new_stage
                    
                    #drawAngles = [[leftArmAngle, leftShoulder]]
                    #visualize(drawAngles)
                    
                    
                except:
                    print("check_pose error")
                    # runs if a person or pose cannot be calculated
                    pass
        
    '''


