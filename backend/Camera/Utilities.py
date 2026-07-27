import tensorflow as tf
import tensorflow_hub as hub
import math

import numpy as np
import cv2
from Camera.pose_analysis import MoveName, MovePosition

import os

useTsLite = True
if useTsLite:
# Initialize the TFLite interpreter
  current_dir = os.path.dirname(os.path.abspath(__file__))
  model_path = os.path.join(current_dir, '3.tflite')
  interpreter = tf.lite.Interpreter(model_path=model_path)
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
    Positions['left_side'] = MovePosition.Middle
  else:
    yDir = y_leftWrist / leftLen
    if yDir > angleTreshold:
      Positions['left_side'] = MovePosition.Down
    elif yDir < (-angleTreshold):
      Positions['left_side'] = MovePosition.Up
    else:
      Positions['left_side'] = MovePosition.Middle
  
  if rightLen <= dTol:
    Positions['right_side'] = MovePosition.Middle
  else:
    yDir = y_rightWrist / rightLen
    if yDir > angleTreshold:
      Positions['right_side'] = MovePosition.Down
    elif yDir < (-angleTreshold):
      Positions['right_side'] = MovePosition.Up
    else:
      Positions['right_side'] = MovePosition.Middle      
  return Positions

def GetMovePositionsBicep(pnts, distElbow2Wrist_l, distElbow2Wrist_r, cofident_threshold):
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
    Positions['left_side'] = MovePosition.Middle
  else:
    yDir = y_leftWrist / leftLen
    if yDir > angleDownTreshold:
      Positions['left_side'] = MovePosition.Down
    elif yDir < (-angleUpTreshold):
      Positions['left_side'] = MovePosition.Up
    else:
      Positions['left_side'] = MovePosition.Middle
  
  if rightLen <= dTol:
    Positions['right_side'] = MovePosition.Middle
  else:
    yDir = y_rightWrist / rightLen
    if yDir > angleDownTreshold:
      Positions['right_side'] = MovePosition.Down
    elif yDir < (-angleUpTreshold):
      Positions['right_side'] = MovePosition.Up
    else:
      Positions['right_side'] = MovePosition.Middle      
  return Positions

def GetMovePositionsLateral(pnts, conf_threshold=0.35):
    lw = KEYPOINT_DICT["left_wrist"]
    ls = KEYPOINT_DICT["left_shoulder"]
    rw = KEYPOINT_DICT["right_wrist"]
    rs = KEYPOINT_DICT["right_shoulder"]

    positions = {}

    # Check confidence first
    if (
        pnts[0][0][lw][2] < conf_threshold or
        pnts[0][0][ls][2] < conf_threshold
    ):
        positions["left_side"] = MovePosition.Middle
    else:
        positions["left_side"] = (
            MovePosition.Up
            if pnts[0][0][lw][0] < pnts[0][0][ls][0]
            else MovePosition.Down
        )

    if (
        pnts[0][0][rw][2] < conf_threshold or
        pnts[0][0][rs][2] < conf_threshold
    ):
        positions["right_side"] = MovePosition.Middle
    else:
        positions["right_side"] = (
            MovePosition.Up
            if pnts[0][0][rw][0] < pnts[0][0][rs][0]
            else MovePosition.Down
        )

    return positions

def GetMovePositionsSquat(pnts, conf_threshold=0.35):
    """Detects squat position using the knee angle (hip → knee → ankle).
    
    Returns a single {'squat': MovePosition} key:
      - MovePosition.Up   = standing (legs nearly straight, ≥160°) → triggers rep count
      - MovePosition.Down = deep squat (knee angle ≤90°, past parallel)
      - MovePosition.Middle = transitioning between the two
    """
    lh = KEYPOINT_DICT['left_hip']
    lk = KEYPOINT_DICT['left_knee']
    la = KEYPOINT_DICT['left_ankle']
    rh = KEYPOINT_DICT['right_hip']
    rk = KEYPOINT_DICT['right_knee']
    ra = KEYPOINT_DICT['right_ankle']

    def calc_knee_angle(hip, knee, ankle):
        v_hip   = (hip[0] - knee[0],   hip[1] - knee[1])
        v_ankle = (ankle[0] - knee[0], ankle[1] - knee[1])
        dot = v_hip[0] * v_ankle[0] + v_hip[1] * v_ankle[1]
        len_hip   = math.sqrt(v_hip[0]**2   + v_hip[1]**2)
        len_ankle = math.sqrt(v_ankle[0]**2 + v_ankle[1]**2)
        if len_hip < 0.0001 or len_ankle < 0.0001:
            return 180.0
        cos_a = max(-1.0, min(1.0, dot / (len_hip * len_ankle)))
        return math.degrees(math.acos(cos_a))

    l_visible = (pnts[0][0][lh][2] > conf_threshold and
                 pnts[0][0][lk][2] > conf_threshold and
                 pnts[0][0][la][2] > conf_threshold)
    r_visible = (pnts[0][0][rh][2] > conf_threshold and
                 pnts[0][0][rk][2] > conf_threshold and
                 pnts[0][0][ra][2] > conf_threshold)

    if not l_visible and not r_visible:
        return {'squat': MovePosition.Middle}

    angles = []
    if l_visible:
        angles.append(calc_knee_angle(
            pnts[0][0][lh][:2], pnts[0][0][lk][:2], pnts[0][0][la][:2]
        ))
    if r_visible:
        angles.append(calc_knee_angle(
            pnts[0][0][rh][:2], pnts[0][0][rk][:2], pnts[0][0][ra][:2]
        ))

    avg_angle = sum(angles) / len(angles)

    STANDING_THRESHOLD = 160  
    SQUAT_THRESHOLD = 90 

    if avg_angle >= STANDING_THRESHOLD:
        return {'squat': MovePosition.Up}
    elif avg_angle <= SQUAT_THRESHOLD:
        return {'squat': MovePosition.Down}
    else:
        return {'squat': MovePosition.Middle}

def GetMovePositionsShoulderPress(pnts, conf_threshold=0.35):
    """Detects shoulder press using elbow angle and wrist position.
    
    Returns {'left_side': MovePosition, 'right_side': MovePosition}:
      - MovePosition.Up   = arms straight up (angle >= 150° and wrist above shoulder)
      - MovePosition.Down = arms down at shoulders (angle <= 80°)
      - MovePosition.Middle = transitioning
    """
    ls = KEYPOINT_DICT['left_shoulder']
    le = KEYPOINT_DICT['left_elbow']
    lw = KEYPOINT_DICT['left_wrist']
    rs = KEYPOINT_DICT['right_shoulder']
    re = KEYPOINT_DICT['right_elbow']
    rw = KEYPOINT_DICT['right_wrist']

    positions = {}

    def calc_joint_angle(p1, p2, p3):
        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        dot = v1[0] * v2[0] + v1[1] * v2[1]
        len1 = math.sqrt(v1[0]**2 + v1[1]**2)
        len2 = math.sqrt(v2[0]**2 + v2[1]**2)
        if len1 < 0.0001 or len2 < 0.0001:
            return 180.0
        cos_a = max(-1.0, min(1.0, dot / (len1 * len2)))
        return math.degrees(math.acos(cos_a))

    STRAIGHT_ARM_THRESHOLD = 150
    BENT_ARM_THRESHOLD = 80

    if (pnts[0][0][ls][2] > conf_threshold and
        pnts[0][0][le][2] > conf_threshold and
        pnts[0][0][lw][2] > conf_threshold):
        
        angle = calc_joint_angle(pnts[0][0][ls][:2], pnts[0][0][le][:2], pnts[0][0][lw][:2])
        is_above_shoulder = pnts[0][0][lw][0] < pnts[0][0][ls][0]

        if angle >= STRAIGHT_ARM_THRESHOLD and is_above_shoulder:
            positions['left_side'] = MovePosition.Up
        elif angle <= BENT_ARM_THRESHOLD:
            positions['left_side'] = MovePosition.Down
        else:
            positions['left_side'] = MovePosition.Middle
    else:
        positions['left_side'] = MovePosition.Middle

    if (pnts[0][0][rs][2] > conf_threshold and
        pnts[0][0][re][2] > conf_threshold and
        pnts[0][0][rw][2] > conf_threshold):
        
        angle = calc_joint_angle(pnts[0][0][rs][:2], pnts[0][0][re][:2], pnts[0][0][rw][:2])
        is_above_shoulder = pnts[0][0][rw][0] < pnts[0][0][rs][0]

        if angle >= STRAIGHT_ARM_THRESHOLD and is_above_shoulder:
            positions['right_side'] = MovePosition.Up
        elif angle <= BENT_ARM_THRESHOLD:
            positions['right_side'] = MovePosition.Down
        else:
            positions['right_side'] = MovePosition.Middle
    else:
        positions['right_side'] = MovePosition.Middle

    return positions

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
                    
                              