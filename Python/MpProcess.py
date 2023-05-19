from threading import Thread
import cv2
import mediapipe as mp
from smbus import SMBus
import time
from AnimationMethods import AnimationMethods
from timer import Timer

addr = 0x8 # bus address
bus = SMBus(7) # indicates /dev/ic2-1




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


      
    def __init__(self, curPos, frame=None):
        
        self.currentPos = curPos
         
        

        
        
        
        self.frame = frame
        self.image = frame
        self.hand_state = 0
        self.stopped = False
        
        #animation Merge variables 
        self.motionAnimToggle = 0 # toggle for switching in between animation and motion tracking mode for each run
        self.animation = AnimationMethods(addr, bus)
        
        '''
        self.animation.run_animation("nine-d")
        while(True):
            pass
        '''
        time.sleep(1)
        bus.write_i2c_block_data(addr,0x09,[1])
        
        while(bus.read_byte(addr) == 0):
            pass
        
        time.sleep(1)

        # while(bus.read_byte(addr)):
        #     pass

        #plays animation on startup before doing anything else. "wake up" animation
        self.animation.run_animation("left")
        print("yo")
        #timer for playing animation
        self.anim_timer = Timer(30)
#         self.anim_timer_time = time.perf_counter()
#         self.anim_timer_duration = 20
        self.anim_name_string = "jake_test"
        self.tracking_start = True #tells if its the first time through tracking loop
        self.idle_start = True #tells if its the first time through idle loop
        
        #timer for tracking
        self.track_timer_time = time.perf_counter()
        self.track_timer_duration = 2
        
        #timer so one person doesn't hog it
        self.turn_timer = Timer(65)
#         self.turn_timer_time = time.perf_counter()
#         self.turn_timer_duration = 65
        self.turn_start = True
        self.endOfSession = False
        
        #timer to prevent glitches while in idle mode
        self.glitch_timer = Timer(5)
#         self.glitch_timer_time = time.perf_counter()
#         self.glitch_timer_duration = 5
        
        
    
    def start (self):
        Thread(target=self.process,args = ()).start()
        return self
    
    def process (self):
        
        motor_top_one = 180 #motors labeled one are on the same side. top and bottom controls. operators right viewers left
        motor_top_two = 180
        
        maxlim = 640 - 20
        minlim = 0 + 20
        
        maxlimY = 480 - 20
        minlimY = 0 + 20
        
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
                cv2.line(image, (15, minlimY), (15, maxlimY), (0,255,0), 5) #draws verticle line
                
                self.image = image
                
                
                try:
                    
                    landmarks = results.pose_landmarks.landmark
                        
                    soulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    hand = [landmarks[mp_pose.PoseLandmark.LEFT_INDEX.value].x, landmarks[mp_pose.PoseLandmark.LEFT_INDEX.value].y]
                    
                    if self.glitch_timer.is_done():
                        
                        if self.tracking_start: #if it is the first time through the loop, reset timer, set animation interval and animation
                            
                            self.anim_timer.start()
                            print('tracking reset')
                            
                            
                            
                            self.tracking_start = False
                            self.idle_start = True
                            
                        if self.turn_start:
                            print('reset turn time')
                            
                            self.turn_timer.start()
                            self.turn_start = False
                        
                        
                        
                            
                        
                    
                    if self.turn_timer.is_done():
                        self.endOfSession = True
                    
                    if cmd_out == False:
                        
                        #position of the hand
                        self.handPos = hand[0] * 640 #multiplied by screen dimentions
                        self.handPosY = hand[1] * 640
                        
                        
                        
                        if time.perf_counter() >= self.track_timer_time:
                            
                            self.delayedPos = self.handPos
                            
                            self.track_timer_time = time.perf_counter() + self.track_timer_duration
                            
                        #influence over the range of the horizontal influence.
                        #adjusting the influence range with the Y axis moves the motor positions to the respective position within the new range resulting in verticle movement. 
                        #simple way of adding verticle movement
                        verticle_influence = map_range(self.handPosY, minlimY, maxlimY, 0.9, 0.3)    
                        
                        #motor position of top section from a delayed handPos
                        motor_top_one_map = map_range(self.delayedPos, minlim, maxlim, 0, 180)
                        motor_top_two_map = map_range(self.delayedPos, minlim, maxlim, 180, 0) #flipped so motors rotate in twards the center
                        
                        #clamps the top section motors so they don't over rotate past 180
                        motor_top_one_clamped = clamp_number(motor_top_one_map, 0, 180)
                        motor_top_two_clamped = clamp_number(motor_top_two_map, 180, 0)
                        
#                       #final top section motor positons with clamp
                        motor_top_one = int(motor_top_one_clamped)
                        motor_top_two = int(motor_top_two_clamped)
                        
                        
                        #adjusts the ratio between the top sections motor positions and the bottom sections motor range. 
                        #180 Deg top section motor = half range of motion for bottom section motor. 0 Deg top = full range bottom
                        motor_influence_one = map_range(motor_top_one, 180 , 0, 0.5, 1)
                        motor_influence_two = map_range(motor_top_two, 180 , 0, 0.5, 1)
                                            
                        #the upper limits of the bottom sections motor range adjusted by the motor influence. this is serving as direct motor position of now
                        motor_bot_one_limit = (180 * motor_influence_one)  
                        motor_bot_two_limit = (180 * motor_influence_two)
                        
                        divid_one_low = map_range(motor_top_one, 180, 0, 2, 1.5)
                        divid_one_high = map_range(motor_top_one, 180, 0, 4, 10)
                        
                        clamped_v1 = clamp_number(divid_one_low, 2, 1)
                        clamped_v2 = clamp_number(divid_one_high, 4, 1)
                        
                        divid_two_low = map_range(motor_top_two, 180, 0, 2, 1.5)
                        divid_two_high = map_range(motor_top_two, 180, 0, 4, 10)
                        
                        clamped_v1_1 = clamp_number(divid_two_low, 2, 1)
                        clamped_v2_1 = clamp_number(divid_two_high, 4, 1)
                        
#                       #secondary limit which expands the range of bottom section motors based on the positon of the hand on the Y axis. limit is determined by adding a persentage of the range to the current motor postion
                        m_b_1_l2 = motor_bot_one_limit + map_range(self.handPosY, minlimY, maxlimY, motor_bot_one_limit/divid_one_low , -motor_bot_one_limit/divid_one_high)                                                             
                        m_b_2_l2 = motor_bot_two_limit + map_range(self.handPosY, minlimY, maxlimY, motor_bot_two_limit/divid_two_low, -motor_bot_two_limit/divid_two_high)    
                        
                        #mapping the hand position to the motor range with secondary limits applied 
                        motor_bot_one_map = map_range(self.handPos, minlim, maxlim, 0, m_b_1_l2) 
                        motor_bot_two_map = map_range(self.handPos, minlim, maxlim, m_b_2_l2, 0) 
                        
                        #making sure motor position does not go past limits
                        motor_bot_one_clamped = clamp_number(motor_bot_one_map, 0, m_b_1_l2)
                        motor_bot_two_clamped = clamp_number(motor_bot_two_map, m_b_2_l2, 0)
                        
                        #final bottom section motor positions with clamp
                        motor_bot_one = int(motor_bot_one_clamped)
                        motor_bot_two = int(motor_bot_two_clamped)
                        
 
                        
 
 
 
 
                        if cmd_out == False:
#                             cmd_out = True
#                             print("cmd started ", format(cmd_out))
                            val_when_enter = motor_bot_one
#                             print('Motor_bottom_one: ', motor_bot_one)
#                             print('Motor_bottom_two: ', motor_bot_two)
                            bus.write_i2c_block_data(addr,0x07,[motor_top_one, motor_top_two, motor_bot_one, motor_bot_two])
                            
                    elif cmd_out == True:
                        status = bus.read_byte(addr)
#                         print(status)
                
                        if status == 1:
                            cmd_out = False
                            #print(self.currentPos)
                        self.currentPos = val_when_enter
                    
                    
                        
                            
                            
                    
                                       
                    #print("try finished")
                  
                except:
                    
                    if self.idle_start: #if it is the first time through the loop, reset timer, set animation interval and animation
                        print('idle reset')
                        self.anim_timer.start()
                        self.glitch_timer.start()
                        #makes sure this code only runs once and resets tracking loops code to run once on start 
                        self.idle_start = False
                        self.tracking_start = True
                        self.turn_start = True
                    
                    
                        #resets the position to resting position 0 
                        bus.write_i2c_block_data(addr,0x07,[0,0,0,0])
                        
                        print('reset position check')
                        
                    
                    
                
                
                
                if self.anim_timer.is_done():
                    print('playing animation')
                    if self.tracking_start == False:
                        if self.handPos >= 320:
                            self.animation.run_animation("left")
                        else:
                            #play animation
                            self.animation.run_animation("right")
                    else:
                        self.animation.run_animation(self.anim_name_string)
                    
                    #reset timer
                    self.anim_timer.start()
                    
                    #resets both starting loops to play first iteration 
                    self.idle_start = True
                    self.tracking_start = True
                    
                if self.endOfSession:
                    print("Session Ended")
                    #resets the position to resting position 0
                    
                    bus.write_i2c_block_data(addr,0x07,[0,0,0,0])
                    
                    time.sleep(15)
                    self.turn_start = True
                    self.endOfSession = False
                    
                    #reset timers on start of new session 
                    self.idle_start = True
                    self.tracking_start = True
                
    
    def stop(self):
        self.stopped = True 
