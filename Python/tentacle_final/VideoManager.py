from threading import Thread
import cv2
import mediapipe as mp
import time

class VideoManager:
    def __init__(self, show):
        
        # whether certain features are running
        self.stopped = False
        self.show = show
        
        # pose reading and display information
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        
        
        # idle animation timers and triggers
        self.idle_timer = 0 # amount of time program has been checking for idle animations
        self.idle_trigger = 5 # amount of time in seconds of no people detected for the code to enable idle mode
        self.model_present = False # whether or not a model is in the viewing window
        
        self.idle = False # whether the program is idling
        self.model_timer = 0 # amount of time a person has been visible on screen
        self.model_trigger = 3 # timer to make sure model detection isn't a fluke. model must be present for several seconds
        
        
        pass

    def start(self):
        self.cap = cv2.VideoCapture(0) # starts video capture
        Thread(target=self.main, args=()).start() # starts threading to reduce load on main program
        
        return self

    def main(self):
        
        with self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose: # allows for easier calling of pose

            while self.cap.isOpened(): # whether or not the capture is open
                ret, frame = self.cap.read() # reading the capture
                
                #recolor feed
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                
                #make Detections
                results = pose.process(image)
                
                #Recolor image back to BGR for rendering
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
                # in a try because no detectable model will throw an error. this is used to detect whether to idle the tentacle
                try: 
                    landmarks = results.pose_landmarks.landmark # reading the landmarks of the figure
                    self.track_landmarks(landmarks) # finds the x and y of important landmarks for processing
                    
                    # detecting whether to switch off idle mode when a model is present
                    # code will except before reaching this point if no model is available
                    # this is to prevent a single, brief glitch from interrupting idle mode
                    if self.idle == True and self.model_present == False:
                        print("Model Present, waiting for confirmation to cancel idle")
                        self.model_timer = time.perf_counter()+self.model_trigger
                        self.model_present = True
                    
                    elif time.perf_counter()>=self.model_timer and self.idle == True:
                        self.idle = False
                        print("Model Present, tracking data ready")
                    
                except:
                    
                    # setting timers to detect whether to switch to idle mode
                    # code wants to go a certain gap of time without a model present before idling
                    if self.model_present and self.idle == False:
                        print("Start Idle Timer")
                        self.model_present = False
                        self.idle_timer = time.perf_counter() + self.idle_trigger
                    
                    elif time.perf_counter() >= self.idle_timer and self.idle == False:
                        self.idle = True
                        print("Idling")
                    
                    pass
                
                if self.show:
                    self.visualize(image, results) # code for visualizing everything
                

                if cv2.waitKey(10) & 0xFF == ord('q'): # breaks out of loop if q is pressed
                    break
            
        self.stopped = True
        #self.video_getter.stop()
        print("Stopping Program")
        
    
    def track_landmarks(self, landmarks):
        
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
        try:
            
            self.head_landmark = [landmarks[self.mp_pose.PoseLandmark.NOSE.value].x,landmarks[self.mp_pose.PoseLandmark.NOSE.value].y ]
            
            left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y ]
            left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y ]
            left_elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y ]
            left_wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y ]
            left_pinky = [landmarks[self.mp_pose.PoseLandmark.LEFT_PINKY.value].x,landmarks[self.mp_pose.PoseLandmark.LEFT_PINKY.value].y ]
                
            self.left_landmarks = [left_hip, left_shoulder, left_elbow, left_wrist, left_pinky]
            
            right_hip = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y ]
            right_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y ]
            right_elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y ]
            right_wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y ]
            right_pinky = [landmarks[self.mp_pose.PoseLandmark.RIGHT_PINKY.value].x,landmarks[self.mp_pose.PoseLandmark.RIGHT_PINKY.value].y ]
                        
            self.right_landmarks = [right_hip, right_shoulder, right_elbow, right_wrist, right_pinky]
            
            
            
        except:
            print("Angle Calculation Error")
            

    def get_landmarks(self):
        landmarks = [self.head_landmark, self.left_landmarks, self.right_landmarks]
        return landmarks

    def visualize(self, image, results):
        self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                                    self.mp_drawing.DrawingSpec(color=(255,0,0),thickness=2, circle_radius=0),
                                    self.mp_drawing.DrawingSpec(color=(255,0,0),thickness=2, circle_radius=2))

        cv2.imshow('Holistic Model Detections', image)

    def get_stopped(self):
        return self.stopped
        
