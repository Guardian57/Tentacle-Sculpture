from threading import Thread
import cv2
import mediapipe as mp
from smbus import SMBus
import time

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


      
    def __init__(self, curPos, frame=None):
        self.currentPos = curPos
        bus.write_i2c_block_data(addr,0x00,[curPos])
        self.frame = frame
        self.image = frame
        self.hand_state = 0
        self.stopped = False
    
    def start (self):
        Thread(target=self.process,args = ()).start()
        return self
    
    
    
    def process (self):
        #Initiate holistic mdel
        motor_top_one = 180; #motors labeled one are on the same side. top and bottom controls. operators right viewers left
        motor_top_two = 0;
        
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
                    landmarks = results.pose_landmarks.landmark
                    
                     
                   
                    soulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    hand = [landmarks[mp_pose.PoseLandmark.LEFT_INDEX.value].x, landmarks[mp_pose.PoseLandmark.LEFT_INDEX.value].y]
                    
                    if cmd_out == False:
                        
                        largest_mpose_top = max(motor_top_one, motor_top_two)
                        
                        handPos = hand[0] * 640
                        
                        motor_influence_one = map_range(motor_top_one, 0 , 180, 1 , 2)
                        motor_influence_two = map_range(motor_top_two, 0 , 180, 1 , 2)
                        
                        # the limits for the mapping function aftected by an influence value that is tied to the top motors positioning 
                        motor_bot_one_limit = motor_top_one/motor_influence_one
                        motor_bot_two_limit = 180 - (motor_top_one/motor_influence_two)
                        
                        print(motor_bot_one_limit)
                        print(motor_bot_two_limit)
                        
                        motor_bot_one_map = map_range(handPos, minlim, maxlim, 0, motor_bot_one_limit) #mapping hand screen pos to 180 deg rotation. hand[] is multiplied by screen dimentions
                        motor_bot_two_map = map_range(handPos, minlim, maxlim, 180, motor_bot_two_limit)
                        
                        motor_bot_one_clamped = clamp_number(motor_bot_one_map, 0, motor_bot_one_limit)
                        motor_bot_two_clamped = clamp_number(motor_bot_two_map, 180, motor_bot_two_limit)
                        
                        motor_bot_one = int(motor_bot_one_clamped)
                        
                        motor_bot_two = int(motor_bot_two_clamped)
                        
 
 
 
 
 
 
                        if cmd_out == False:
                            cmd_out = True
                            print("cmd started ", format(cmd_out))
                            val_when_enter = motor_bot_one
                            print('Motor_bottom_one: ', motor_bot_one)
                            print('Motor_bottom_one: ', motor_bot_two)
                            bus.write_i2c_block_data(addr,0x07,[motor_bot_one, motor_bot_two])
                            
                    elif cmd_out == True:
                        status = bus.read_byte(addr)
                        print(status)
                #bus.write_byte(addr, hexClamp)
                        if status == 1:
                            cmd_out = False
                            #print(self.currentPos)
                        self.currentPos = val_when_enter
                    
                                       
                    #print("try finished")
                  
                except:
                    print('oh no')
                    pass
                  
    
    def stop(self):
        self.stopped = True 
