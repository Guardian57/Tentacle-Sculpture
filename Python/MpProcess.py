from threading import Thread
import cv2
import mediapipe as mp
from smbus import SMBus
import time
from AnimationMethods import AnimationMethods

addr = 0x8 # bus address
bus = SMBus(1) # indicates /dev/ic2-1




mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def map_range(val, inMin, inMax, outMin, outMax):
    #find the 'width' of each range
    inSpan = inMax - inMin
    outSpan = outMax - outMin

    #normalize the val in the input range between 0-1
    normalizedVal = float(val - inMin) / float(inSpan)
    #scale the normalized val to the output range
    return outMin + (normalizedVal * outSpan)

def clamp_number(num, a, b):
  return max(min(num, max(a, b)), min(a, b))

class MpProcess:
    """
    Class that process the frame from video capture through Mediapipe

    """  


      
    def __init__(self, reset, curPos, frame=None):
        
        self.currentPos = curPos
        
        if reset:
            bus.write_i2c_block_data(addr,0x00,[curPos])
        
        self.frame = frame
        self.image = frame
        self.hand_state = 0
        self.stopped = False
        
        #animation Merge variables 
        self.motionAnimToggle = 0 # toggle for switching in between animation and motion tracking mode for each run
        self.animation = AnimationMethods(addr, bus)
        
        
        #plays animation on startup before doing anything else. "wake up" animation
        self.animation.run_animation("left")
        
        #timers for playing animation
        self.anim_timer_time = time.perf_counter()
        self.anim_timer_duration = 20
        self.anim_name_string = "jake_test"
        self.tracking_start = True #tells if its the first time through tracking loop
        self.idle_start = True #tells if its the first time through idle loop
        
        #timers for tracking
        self.track_timer_time = time.perf_counter()
        self.track_timer_duration = time.perf_counter()
        
    
    def start (self):
        Thread(target=self.process,args = ()).start()
        return self
    
    def process (self):
        
        motor_top_one = 180; #motors labeled one are on the same side. top and bottom controls. operators right viewers left
        motor_top_two = 180;
        
        maxlim = 540
        minlim = 100
        cmd_out = False
        val_when_enter = None
        
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            
            while not self.stopped:
                
                image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                
                #make Detections
                results = holistic.process(image)
                
                #Recolor image back to BGR for rendering
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
                #draw face landmarks
            #mp_drawing.draw_landmarks(image,results.face_landmarks, mp_holistic.FACEMESH_CONTOURS,
                                    #mp_drawing.DrawingSpec(color=(255,0,0),thickness=2, circle_radius=0),
                                    #mp_drawing.DrawingSpec(color=(255,0,0),thickness=2, circle_radius=2))

            #right hand
            #mp_drawing.draw_landmarks(self.frame, self.results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

            #left hand
            #mp_drawing.draw_landmarks(self.frame, self.results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

            #pose 
                mp_drawing.draw_landmarks(image,results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                
                cv2.line(image, (minlim, 15), (maxlim, 15), (255,0,0), 5) #draws horizontal line
                
                self.image = image
                
                
                try:
                    
                    if self.tracking_start: #if it is the first time through the loop, reset timer, set animation interval and animation
                        self.anim_timer_duration = 30
                        
                        self.anim_timer_time = time.perf_counter() + self.anim_timer_duration
                        
                        self.tracking_start = False
                        self.idle_start = True
                        
                    
                    
                    
                    
                        
                    landmarks = results.pose_landmarks.landmark
                    
                    soulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    hand = [landmarks[mp_pose.PoseLandmark.LEFT_INDEX.value].x, landmarks[mp_pose.PoseLandmark.LEFT_INDEX.value].y]
                    
                    if cmd_out == False:
                        
                        #position of the hand
                        self.handPos = hand[0] * 640 #multiplied by screen dimentions
                        
                        motor_top_one_map = map_range(self.handPos, minlim, maxlim, 180, 0)
                        motor_top_two_map = map_range(self.handPos, minlim, maxlim, 0, 180)
                        
                        motor_top_one_clamped = clamp_number(motor_top_one_map, 180, 0)
                        motor_top_two_clamped = clamp_number(motor_top_two_map, 0, 180)
                        
                        motor_top_one = int(motor_top_one_clamped)
                        motor_top_two = int(motor_top_two_clamped)
                        
                        print("Top Motor 01 pos: ",motor_top_one)
                        print("Top Motor 02 pos: ",motor_top_two)
                        
                        #determins the influence the top motors have over the bottom motors position based on top motors position. 180 Deg = range of motion, 0 Deg = full range of motion
                        motor_influence_one = map_range(motor_top_one, 0 , 180, 0.5, 1)
                        motor_influence_two = map_range(motor_top_two, 0 , 180, 0.5, 1)
                        
                        print('influence 1: ',motor_influence_one)
                        print('influence 2: ',motor_influence_two)
                        
                        # the limits for the mapping function aftected by an influence value that is tied to the top motors positioning 
                        motor_bot_one_limit = 180 * motor_influence_one
                        motor_bot_two_limit = 180 * motor_influence_two
                            
                        #mapping the hand position to the motor range with limits applied
                        motor_bot_one_map = map_range(self.handPos, minlim, maxlim, 180, 180 - motor_bot_one_limit) #mapping hand screen pos to 180 deg rotation. 
                        motor_bot_two_map = map_range(self.handPos, minlim, maxlim, 180 - motor_bot_two_limit, 180) #reverses the direction of the motor by changing the upper limit to a lower limit (subtracting 180) and mapping it backwards
                        
                        #making sure motor position does not go past limits
                        motor_bot_one_clamped = clamp_number(motor_bot_one_map, 180, 180 - motor_bot_one_limit)
                        motor_bot_two_clamped = clamp_number(motor_bot_two_map, 180 - motor_bot_two_limit, 180)
                        
                        motor_bot_one = int(motor_bot_one_clamped)
                        motor_bot_two = int(motor_bot_two_clamped)
                        
 
                        
 
 
 
 
                        if cmd_out == False:
                            cmd_out = True
                            print("cmd started ", format(cmd_out))
                            val_when_enter = motor_bot_one
                            print('Motor_bottom_one: ', motor_bot_one)
                            print('Motor_bottom_two: ', motor_bot_two)
                            bus.write_i2c_block_data(addr,0x07,[motor_top_one, motor_top_two, motor_bot_one, motor_bot_two])
                            
                    elif cmd_out == True:
                        status = bus.read_byte(addr)
                        print(status)
                
                        if status == 1:
                            cmd_out = False
                            #print(self.currentPos)
                        self.currentPos = val_when_enter
                    
                    
                        
                            
                            
                    
                                       
                    #print("try finished")
                  
                except:
                    
                    if self.idle_start: #if it is the first time through the loop, reset timer, set animation interval and animation
                        
                        self.anim_timer_duration = 50
                        
                        self.anim_timer_time = time.perf_counter() + self.anim_timer_duration
                        
                        #makes sure this code only runs once and resets tracking loops code to run once on start 
                        self.idle_start = False
                        self.tracking_start = True
                    
                    #resets the position to resting position 0
                    bus.write_i2c_block_data(addr,0x07,[180,180,180,180])
                    
                    pass
                
                
                if time.perf_counter() >= self.anim_timer_time:
                    print('playing animation')
                    
                    if self.handPos >= 320:
                        self.animation.run_animation("left")
                    else:
                        #play animation
                        self.animation.run_animation("right")
                    
                    #reset timer
                    self.anim_timer_time = time.perf_counter() + self.anim_timer_duration
                    
                    #resets both starting loops to play first iteration 
                    self.idle_start = True
                    self.tracking_start = True
                
    
    def stop(self):
        self.stopped = True 
