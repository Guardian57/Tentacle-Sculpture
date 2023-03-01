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
        
        maxlim = 430
        minlim = 50
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
                    
                        handPosToRot = map_range(hand[0] * 640, minlim, maxlim, 0, 180) #mapping hand screen pos to 180 deg rotation. hand[] is multiplied by screen dimentions
                        
                        clamped = clamp_number(handPosToRot, 0, 180)
                        
                        hexClamp = int(clamped)
                        
                        opp = 180 - hexClamp
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        if cmd_out == False:
                            cmd_out = True
                            print("cmd started ", format(cmd_out))
                            val_when_enter = hexClamp
                            print("runs")
                            bus.write_i2c_block_data(addr,0x07,[hexClamp,hexClamp])
                            
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
