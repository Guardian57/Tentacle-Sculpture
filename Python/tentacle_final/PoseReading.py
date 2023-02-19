from smbus import SMBus
import time
import numpy as np
import cv2
import mediapipe as mp



#cap = cv2.VideoCapture(0)

class PoseReading:
    
    
    
    def __init__(self):
        self.uptime = time.perf_counter()
        self.stage = ""        
        self.right_wave = [-1, 0, 0]
        self.left_wave = [-1, 0, 0]
        self.is_waving = False
        self.wave_time = 0
        
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        
        print("Pose Reader initialized")
    
    def read_pose(self, cap):
        with self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            
            return cap
        
    def check_pose(self, cap):
        
        
        #Initiate holistic mdel
        with self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            if cap.isOpened():
                ret, frame = cap.read()
                #cv2.imshow('Mediapipe Feed', frame)
                

                #recolor feed
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                
                #make Detections
                results = pose.process(image)
                
                #Recolor image back to BGR for rendering
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
                #extract landmarks ("try/except" because if the landmark cannot be seen, it needs to be able to continue)
                try:
                    landmarks = results.pose_landmarks.landmark
                    
                    #get landmark coordinates of body parts
                    '''
                        Options for Body Parts: 
                        
                        0: NOSE
                        1: LEFT_EYE_INNER | 2: LEFT_EYE | 3: LEFT_EYE_OUTER
                        4: RIGHT_EYE_INNER | 5: RIGHT_EYE | 6: RIGHT_EYE_OUTER
                        7: LEFT_EAR | 8: RIGHT_EAR
                        9: MOUTH_LEFT | 10: MOUTH_RIGHT
                        11: LEFT_SHOULDER | 13: LEFT_ELBOW | 15: LEFT_WRIST
                        12: RIGHT_SHOULDER | 14: RIGHT_ELBOW | 16: RIGHT_WRIST
                        17: LEFT_PINKY | 19: LEFT_INDEX | 21: LEFT_THUMB
                        18: RIGHT_PINKY | 20: RIGHT_INDEX | 22: RIGHT_THUMB
                        23: LEFT_HIP | 24: RIGHT_HIP | 25: LEFT_KNEE | 26: RIGHT_KNEE
                        27: LEFT_ANKLE | 29: LEFT_HEEL | 31: LEFT_FOOT_INDEX
                        28: RIGHT_ANKLE | 30: RIGHT_HEEL | 32: RIGHT_FOOT_INDEX
                        
                    '''
                    
                    # saves each body part used in calculating poses
                    
                    left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y ]
                    left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y ]
                    left_elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y ]
                    left_wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y ]
                    left_pinky = [landmarks[self.mp_pose.PoseLandmark.LEFT_PINKY.value].x,landmarks[self.mp_pose.PoseLandmark.LEFT_PINKY.value].y ]
                    
                    left_arm_angle = calculate_angle(left_hip, left_shoulder, left_elbow)
                    left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
                    left_wrist_angle = calculate_angle_small(left_elbow, left_wrist, left_pinky)
                    
                    left_angles = [left_arm_angle, left_elbow_angle, left_wrist_angle]
                    
                    right_hip = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y ]
                    right_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y ]
                    right_elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y ]
                    right_wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y ]
                    right_pinky = [landmarks[self.mp_pose.PoseLandmark.RIGHT_PINKY.value].x,landmarks[self.mp_pose.PoseLandmark.RIGHT_PINKY.value].y ]
                    
                    right_arm_angle = calculate_angle(right_hip, right_shoulder, right_elbow)
                    right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
                    right_wrist_angle = calculate_angle_small(right_elbow, right_wrist, right_pinky)
                    
                    right_angles = [right_arm_angle, right_elbow_angle, right_wrist_angle]
                    
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

            
        

    def visualize(self, draw_angles):
        for i in range(len(draw_angles)):
            print(tuple(np.multiply(draw_angles[i][1], [1280, 720]).astype(int)))
            cv2.putText(image, str(draw_angles[i][0]),
                        tuple(np.multiply(draw_angles[i][1], [1280, 720]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2, cv2.LINE_AA
                        )



