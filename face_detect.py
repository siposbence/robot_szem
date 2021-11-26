import cv2
import mediapipe as mp
import numpy as np
from scipy.ndimage.filters import gaussian_filter
import paho.mqtt.client as mqtt

client =mqtt.Client("robot_base")
client.connect("localhost")


mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

DIM=(744, 600)
K=np.array([[328.66960044713676, 0.0, 461.9005635813701], [0.0, 329.7390185115684, 296.8864597194912], [0.0, 0.0, 1.0]])
D=np.array([[-0.03254196233072562], [0.058705976062386735], [-0.08592867131653371], [0.04283255216208141]])

temp_x, temp_y, temp_depth = (120, 160, 3)#(480, 640, 3)

temp_matrix = np.zeros((temp_x, temp_y, temp_depth), dtype = np.uint8)

def undistort(img):
    x,y,_ = img.shape
    w, h = [500, 300]
    img = img[int(x/2)-h:int(x/2)+h, int(y/2)-w:int(x/2)+w,:]
    h,w = img.shape[:2]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return undistorted_img


cap = cv2.VideoCapture(-1)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
# width = 2048
# height = 1536
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

with mp_face_detection.FaceDetection(
    model_selection=0, min_detection_confidence=0.7) as face_detection:
  while cap.isOpened():
    success, image = cap.read()
    #x,y,_ = image.shape
    #w, h = [500, 300]
    #image = image[int(x/2)-h:int(x/2)+h, int(y/2)-w:int(x/2)+w,:]
    
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue
    
    #image = undistort(image)

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_detection.process(image)

    # Draw the face detection annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.detections:
      for detection in results.detections:
        #print(detection.location_data.relative_bounding_box.xmin) #["relative_bounding_box"]
        temp_matrix[int(temp_x*detection.location_data.relative_bounding_box.ymin):int(temp_x*detection.location_data.relative_bounding_box.ymin+temp_x*detection.location_data.relative_bounding_box.height), 
                    int(temp_y*detection.location_data.relative_bounding_box.xmin):int(temp_y*detection.location_data.relative_bounding_box.xmin+temp_y*detection.location_data.relative_bounding_box.width),:] += 20
        #print(int(640*detection.location_data.relative_bounding_box.xmin),int(640*detection.location_data.relative_bounding_box.xmin+detection.location_data.relative_bounding_box.width), int(480*detection.location_data.relative_bounding_box.ymin),int(480*detection.location_data.relative_bounding_box.ymin+detection.location_data.relative_bounding_box.height))

        mp_drawing.draw_detection(image, detection)
    temp_matrix = (temp_matrix*.9).astype(np.uint8)
    # Flip the image horizontally for a selfie-view display.
    a = np.array(cv2.flip(cv2.GaussianBlur(temp_matrix, (61, 61), 0), 1))
    x_, y_, _ = np.argwhere(a==a.max())[0] 
    print(x_, y_)
    #temp_x, temp_y 
    if x_ == 0 and y_ == 0:
        client.publish("move","0,0")
    else:
        client.publish("move",str(100*((y_)/temp_y-.5))+","+str(100*((x_)/temp_x-.5)))
    cv2.imshow('mask', a)
    cv2.imshow('MediaPipe Face Detection', cv2.flip(image, 1))
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()