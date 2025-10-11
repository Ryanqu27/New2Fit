import tensorflow as tf
import tensorflow_hub as hub
import math

import numpy as np
import cv2
from PoseAnalysis import MoveName, MovePosition
useTsLite = True
if useTsLite:
# Initialize the TFLite interpreter
  interpreter = tf.lite.Interpreter(model_path='3.tflite')
  interpreter.allocate_tensors()
else:
# Download the model from TF Hub.
  module = hub.load("https://www.kaggle.com/models/google/movenet/frameworks/TensorFlow2/variations/singlepose-lightning/versions/4")

# Dictionary that maps from joint names to keypoint indices.
KEYPOINT_DICT = {
    'nose': 0,
    'left_eye': 1,
    'right_eye': 2,
    'left_ear': 3,
    'right_ear': 4,
    'left_shoulder': 5,
    'right_shoulder': 6,
    'left_elbow': 7,
    'right_elbow': 8,
    'left_wrist': 9,
    'right_wrist': 10,
    'left_hip': 11,
    'right_hip': 12,
    'left_knee': 13,
    'right_knee': 14,
    'left_ankle': 15,
    'right_ankle': 16
}

# Maps bones to a matplotlib color name.
KEYPOINT_EDGE_INDS_TO_COLOR = {
    (0, 1): 'm',
    (0, 2): 'c',
    (1, 3): 'm',
    (2, 4): 'c',
    (0, 5): 'm',
    (0, 6): 'c',
    (5, 7): 'm',
    (7, 9): 'm',
    (6, 8): 'c',
    (8, 10): 'c',
    (5, 6): 'y',
    (5, 11): 'm',
    (6, 12): 'c',
    (11, 12): 'y',
    (11, 13): 'm',
    (13, 15): 'm',
    (12, 14): 'c',
    (14, 16): 'c'
}

def movenet(input_image):
  """Runs detection on an input image.

  Args:
    input_image: A [1, height, width, 3] tensor represents the input image
      pixels. Note that the height/width should already be resized and match the
      expected input resolution of the model before passing into this function.

  Returns:
    A [1, 1, 17, 3] float numpy array representing the predicted keypoint
    coordinates and scores.
  """
  if useTsLite:
    # TF Lite format expects tensor type of uint8.
    input_image = tf.cast(input_image, dtype=tf.float32)
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    interpreter.set_tensor(input_details[0]['index'], input_image.numpy())
    # Invoke inference.
    interpreter.invoke()
    # Get the model prediction.
    keypoints_with_scores = interpreter.get_tensor(output_details[0]['index'])
    return keypoints_with_scores
  else:      
    model = module.signatures['serving_default']
    # SavedModel format expects tensor type of int32.
    input_image = tf.cast(input_image, dtype=tf.int32)
    # Run model inference.
    outputs = model(input_image)
    # Output is a [1, 1, 17, 3] tensor.
    keypoints_with_scores = outputs['output_0'].numpy()
    return keypoints_with_scores  

def draw_prediction_on_image(image, imageKeyPnt, keypoints_with_scores, cofident_threshold):
  """Draws the keypoint predictions on image.

  Args:
    image: A numpy array with shape [height, width, channel] representing the
      pixel values of the input image.
    keypoints_with_scores: A numpy array with shape [1, 1, 17, 3] representing
      the keypoint coordinates and scores returned from the MoveNet model.
 

  Returns:
   
  """
  height, width, channel = image.shape
  widthadd = 0
  heightadd = 0
  scalesize = height
  if width > height:
    scalesize = width
    heightadd = 0.5*(height - width)
  else:
    widthadd = 0.5*(width - height) 
  shaped = np.squeeze(np.multiply(keypoints_with_scores,[scalesize,scalesize,1]))

  for kp in shaped:
    ky,kx,kp_conf = kp
    if kp_conf > cofident_threshold:
      cv2.circle(image, (int(kx + widthadd), int(ky + heightadd)),6,(0,255,0),-1)
      cv2.circle(imageKeyPnt, (int(kx + widthadd), int(ky + heightadd)),8,(0,255,0),-1)
  for edge_pair, color in KEYPOINT_EDGE_INDS_TO_COLOR.items():
    p1,p2 = edge_pair
    y1,x1,c1 = shaped[p1]
    y2,x2,c2 = shaped[p2]
    linecolor = (255,255,0) 
    if color == 'c':
      linecolor = (255, 0, 255)
    elif color == 'y':
      linecolor = (0, 255, 255) 
    if (c1 > cofident_threshold) & (c2 > cofident_threshold):
      cv2.line(image, (int(x1 + widthadd),int(y1 + heightadd)),(int(x2 + widthadd),int(y2 + heightadd)), linecolor, 2)
      cv2.line(imageKeyPnt, (int(x1 + widthadd),int(y1 + heightadd)),(int(x2 + widthadd),int(y2 + heightadd)), linecolor, 4)
  return 1 

def GetEar2ShouderDist(pnts, cofident_threshold):  
  dTol = 0.0001
  dist = 0
  lEar = KEYPOINT_DICT['left_ear']
  lShoulder = KEYPOINT_DICT['left_shoulder']
  rEar= KEYPOINT_DICT['right_ear']
  rShoulder = KEYPOINT_DICT['right_shoulder']
  if (pnts[0][0][lEar][2] > cofident_threshold):
     if (pnts[0][0][lShoulder][2] > cofident_threshold) :
       if(pnts[0][0][rEar][2] > cofident_threshold) :
         if (pnts[0][0][rShoulder][2] > cofident_threshold) :
           yEar = 0.5*(pnts[0][0][lEar][0] + pnts[0][0][rEar][0])
           yShouder = 0.5*(pnts[0][0][lShoulder][0] + pnts[0][0][rShoulder][0])
           dist = abs(yShouder - yEar)
  if(dist > dTol):
    return True, dist
  else:
    return False, 0

def GetShouldersDist(pnts, cofident_threshold):
  dist = 0
  lShoulder = KEYPOINT_DICT['left_shoulder'] 
  rShoulder = KEYPOINT_DICT['right_shoulder']
 
  if (pnts[0][0][lShoulder][2] > cofident_threshold) :
    if (pnts[0][0][rShoulder][2] > cofident_threshold) :
      xDist = pnts[0][0][lShoulder][1] - pnts[0][0][rShoulder][1]
      yDist = pnts[0][0][lShoulder][0] - pnts[0][0][rShoulder][0]
      dist = math.sqrt(xDist * xDist + yDist * yDist)
  if(dist > 0.00001):
    return True, dist
  else:
    return False, 0  
           

def GetElbow2WristLen(keypoints_with_scores, cofident_threshold):

  bSuccess, dShouldDist = GetShouldersDist(keypoints_with_scores,cofident_threshold)
  if bSuccess == False:
    return False,0,False,0,dShouldDist
  lElbow = KEYPOINT_DICT['left_elbow']
  lWrist = KEYPOINT_DICT['left_wrist']
  rElbow = KEYPOINT_DICT['right_elbow']
  rWrist = KEYPOINT_DICT['right_wrist']
  lLen = 0
  rLen = 0
  lValid = False
  rValid = False
  if (keypoints_with_scores[0][0][lElbow][2] > cofident_threshold) & (keypoints_with_scores[0][0][lWrist][2] > cofident_threshold) :
    # x_lElbow = keypoints_with_scores[0][0][lElbow][1]
    y_lElbow = keypoints_with_scores[0][0][lElbow][0]
    # x_lWrist = keypoints_with_scores[0][0][lWrist][1]
    y_lWrist = keypoints_with_scores[0][0][lWrist][0]  
    # x_lLen = x_lWrist  - x_lElbow
    y_lLen = y_lWrist  - y_lElbow
    # lLen = x_lLen * x_lLen + y_lLen * y_lLen
    # lLen = y_lLen * y_lLen
    lLen = abs(y_lLen)
    lValid = True

  if (keypoints_with_scores[0][0][rElbow][2] > cofident_threshold) & (keypoints_with_scores[0][0][rWrist][2] > cofident_threshold) :
    # x_rElbow = keypoints_with_scores[0][0][rElbow][1]
    y_rElbow = keypoints_with_scores[0][0][rElbow][0]
    # x_rWrist = keypoints_with_scores[0][0][rWrist][1]
    y_rWrist = keypoints_with_scores[0][0][rWrist][0]    
    # x_rLen = x_rWrist  - x_rElbow
    y_rLen = y_rWrist  - y_rElbow
    # rLen = x_rLen * x_rLen + y_rLen * y_rLen
    # rLen = y_rLen * y_rLen
    rLen = abs(y_rLen)
    rValid = True
  return lValid, lLen, rValid, rLen, dShouldDist
  # if lValid & rValid:
  #   return 0, False
  # elif lLen > rLen:
  #   return math.sqrt(lLen) , True
  # else:
  #   return math.sqrt(rLen), True


def StandbackCheck (KeypntCheckList,keypoints_with_scores, cofident_threshold, NumOfFailedAllowed) :
  NumofFailed = 0
  for pntIndex in KeypntCheckList:
      kp_conf = keypoints_with_scores[0][0][pntIndex][2]
      if kp_conf < cofident_threshold:  
        NumofFailed = NumofFailed + 1
  if NumofFailed >= NumOfFailedAllowed:
    return MoveName.StandBack
  else:
    return MoveName.Nothing  
  
  

def GetMovePositions_1(keypoints_with_scores, distElbow2Wrist, cofident_threshold):
  dTol = 0.00001
  angleTreshold = 0.7 # 0.7 # about 45 degree
  Positions = dict()
  y_leftWrist = keypoints_with_scores[0][0][KEYPOINT_DICT['left_wrist']][0] - keypoints_with_scores[0][0][KEYPOINT_DICT['left_elbow']][0] 
  x_leftWrist = keypoints_with_scores[0][0][KEYPOINT_DICT['left_wrist']][1] - keypoints_with_scores[0][0][KEYPOINT_DICT['left_elbow']][1] 
  y_rightWrist = keypoints_with_scores[0][0][KEYPOINT_DICT['right_wrist']][0] - keypoints_with_scores[0][0][KEYPOINT_DICT['right_elbow']][0] 
  x_rightWrist = keypoints_with_scores[0][0][KEYPOINT_DICT['right_wrist']][1] - keypoints_with_scores[0][0][KEYPOINT_DICT['right_elbow']][1] 
  leftLen = math.sqrt(x_leftWrist * x_leftWrist + y_leftWrist * y_leftWrist)
  rightLen = math.sqrt(x_rightWrist * x_rightWrist + y_rightWrist * y_rightWrist)
  if leftLen <= dTol:
    Positions['left_wrist'] = MovePosition.Middle
  else:
    yDir = y_leftWrist / leftLen
    if yDir > angleTreshold:
      Positions['left_wrist'] = MovePosition.Down
    elif yDir < (-angleTreshold):
      Positions['left_wrist'] = MovePosition.Up
    else:
      Positions['left_wrist'] = MovePosition.Middle
  
  if rightLen <= dTol:
    Positions['right_wrist'] = MovePosition.Middle
  else:
    yDir = y_rightWrist / rightLen
    if yDir > angleTreshold:
      Positions['right_wrist'] = MovePosition.Down
    elif yDir < (-angleTreshold):
      Positions['right_wrist'] = MovePosition.Up
    else:
      Positions['right_wrist'] = MovePosition.Middle      
  return Positions

def GetMovePositions(pnts, distElbow2Wrist_l, distElbow2Wrist_r, cofident_threshold):
  dTol = 0.0001
  angleUpTreshold = 0.5 # 0.7 # about 45 degree
  angleDownTreshold = 0.5
  lElbow = KEYPOINT_DICT['left_elbow']
  lWrist = KEYPOINT_DICT['left_wrist']
  rElbow = KEYPOINT_DICT['right_elbow']
  rWrist = KEYPOINT_DICT['right_wrist']  
  Positions = dict()
  y_leftWrist = pnts[0][0][lWrist][0] - pnts[0][0][lElbow][0] 
  y_rightWrist = pnts[0][0][rWrist][0] - pnts[0][0][rElbow][0]   
  leftLen = distElbow2Wrist_l 
  rightLen = distElbow2Wrist_r 
  # print(y_leftWrist, y_rightWrist, distElbow2Wrist_l*angleUpTreshold, distElbow2Wrist_r*angleUpTreshold, 
  #       pnts[0][0][lWrist][2],pnts[0][0][lElbow][2], pnts[0][0][rWrist][2],pnts[0][0][rElbow][2] )
  if leftLen <= dTol:
    Positions['left_wrist'] = MovePosition.Middle
  else:
    yDir = y_leftWrist / leftLen
    if yDir > angleDownTreshold:
      Positions['left_wrist'] = MovePosition.Down
    elif yDir < (-angleUpTreshold):
      Positions['left_wrist'] = MovePosition.Up
    else:
      Positions['left_wrist'] = MovePosition.Middle
  
  if rightLen <= dTol:
    Positions['right_wrist'] = MovePosition.Middle
  else:
    yDir = y_rightWrist / rightLen
    if yDir > angleDownTreshold:
      Positions['right_wrist'] = MovePosition.Down
    elif yDir < (-angleUpTreshold):
      Positions['right_wrist'] = MovePosition.Up
    else:
      Positions['right_wrist'] = MovePosition.Middle      
  return Positions

   
def GetMoveRecommendation(keypoints_with_scores, cofident_threshold, NumOfFailedAllowed):
  iIndex = 0
  numOfLeftFailed = 0
  numOfRightFailed = 0
  for iIndex in range(0,17):    
    kp_conf = keypoints_with_scores[0][0][iIndex][2]
    if kp_conf < cofident_threshold:
      if iIndex == KEYPOINT_DICT.get('left_eye'):
        numOfLeftFailed = numOfLeftFailed + 1
      elif iIndex == KEYPOINT_DICT.get('left_ear'):
        numOfLeftFailed = numOfLeftFailed + 1
      elif iIndex == KEYPOINT_DICT.get('left_shoulder'):
        numOfLeftFailed = numOfLeftFailed + 1
      elif iIndex == KEYPOINT_DICT.get('left_elbow'):
        numOfLeftFailed = numOfLeftFailed + 1
      elif iIndex == KEYPOINT_DICT.get('left_wrist'):
        numOfLeftFailed = numOfLeftFailed + 1
      elif iIndex == KEYPOINT_DICT.get('left_hip'):
        numOfLeftFailed = numOfLeftFailed + 1
      elif iIndex == KEYPOINT_DICT.get('left_knee'):
        numOfLeftFailed = numOfLeftFailed + 1
      elif iIndex == KEYPOINT_DICT.get('left_ankle'):
        numOfLeftFailed = numOfLeftFailed + 1
      elif iIndex == KEYPOINT_DICT.get('right_eye'):
        numOfRightFailed = numOfRightFailed + 1
      elif iIndex == KEYPOINT_DICT.get('right_ear'):
        numOfRightFailed = numOfRightFailed + 1
      elif iIndex == KEYPOINT_DICT.get('right_shoulder'):
        numOfRightFailed = numOfRightFailed + 1
      elif iIndex == KEYPOINT_DICT.get('right_elbow'):
        numOfRightFailed = numOfRightFailed + 1
      elif iIndex == KEYPOINT_DICT.get('right_wrist'):
        numOfRightFailed = numOfRightFailed + 1
      elif iIndex == KEYPOINT_DICT.get('right_hip'):
        numOfRightFailed = numOfRightFailed + 1
      elif iIndex == KEYPOINT_DICT.get('right_knee'):
        numOfRightFailed = numOfRightFailed + 1
      elif iIndex == KEYPOINT_DICT.get('right_ankle'):
        numOfRightFailed = numOfRightFailed + 1

  if (numOfLeftFailed >= NumOfFailedAllowed) & (numOfRightFailed >= NumOfFailedAllowed):  
    return MoveName.StandBack 
  elif numOfLeftFailed >= NumOfFailedAllowed:
    return MoveName.MoveToLeft  
  elif numOfRightFailed >= NumOfFailedAllowed:
    return MoveName.MoveToRight
  else:
    return MoveName.Nothing       
                    
                              