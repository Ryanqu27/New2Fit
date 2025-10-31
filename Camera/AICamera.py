import tensorflow as tf
import numpy as np
import cv2
import tkinter as tk
from PIL import Image, ImageTk
import time
#import funtions from Utilities.py
from Camera.Utilities import movenet, draw_prediction_on_image, GetMoveRecommendation, GetElbow2WristLen, GetMovePositions, StandbackCheck,KEYPOINT_DICT
#import function in PoseAnalysis
from Camera.PoseAnalysis import MoveName, MovePosition, GetRecommendationTex, DrawText, play_video
# CreateAudioFiles()

stopFlag = False

def run_camera():
  global stopFlag
  stopFlag = False
  InRecordMode = False
  TriggerRecordOff = False
  TriggerRecordOn = False

  outVideoAndKeyPnts = None
  outKeyPntsOnly = None
  
  ImageShowWidth = 1000
  IconFileName = 'Camera/New2Fit-Logo.ico'
  window = tk.Tk()
  window.title("New2Fit")
  #window.geometry("250x500")
  window.iconbitmap(IconFileName)
  window.config(background="#FFFFFF")
  app = tk.Frame(window)
  app.grid()

  #Graphics window
  imageFrame = tk.Frame(window, width=1800, height=1000)
  imageFrame.grid(row=0, column=0, padx=10, pady=2)

  # Creating a photoimage object for start and stop button
  renderStart = ImageTk.PhotoImage(file="Camera/StartRecordingButton.png")
  renderStop = ImageTk.PhotoImage(file="Camera/StopRecordingButton.png")

  #Capture video frames
  lmain = tk.Label(imageFrame)
  lmain.grid(row=0, column=0)
  cap = cv2.VideoCapture(0)
  capWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
  capHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # Define the codec and create VideoWriter object
  fourcc = cv2.VideoWriter_fourcc(*'mp4v')
  #fourcc = cv2.VideoWriter_fourcc(*'H264') 
  videoAndKeyntsFile = 'Camera/VideoAndKeyPnts.mp4'
  KeypntsFile = 'Camera/KeyPntsOnly.mp4'
  # outVideoAndKeyPnts = cv2.VideoWriter(videoAndKeyntsFile, fourcc, 20.0, (capWidth,capHeight))
  # outKeyPntsOnly = cv2.VideoWriter(KeypntsFile, fourcc, 20.0, (capWidth,capHeight))  

  KeyPntCheckList = [KEYPOINT_DICT['left_shoulder'],
                    KEYPOINT_DICT['right_shoulder'],
                    KEYPOINT_DICT['left_elbow'],
                    KEYPOINT_DICT['right_elbow'],
                    KEYPOINT_DICT['left_wrist'],
                    KEYPOINT_DICT['right_wrist'] ] 
  prePntsPosition = { 'left_wrist': MovePosition.Down, 'right_wrist': MovePosition.Down}
  preCmdName = MoveName.Nothing
  curUsedCmdName = MoveName.Nothing
  FrameCount = 0
  textPrint=''
  leftArmLift = 0
  rightArmLift = 0
  distElbow2Wrist_l = 0
  distElbow2Wrist_r = 0
  distShoulders = 10
  lastRepTimeRightArm = time.time()
  lastRepTimeLeftArm = time.time()
  slowDownMsgUntil = 0

  # Main function, 
  #   1. capture image, 
  #   2. preprocess the image to make it ready for Tensorflow MoveNet model
  #   3. Add Key points and connection lines to result images
  #   4. Run the move recognition algorithm and add results to image and video
  #   5. Show the image in Main UI and to the record files if needed
  def show_frame():
    nonlocal FrameCount, preCmdName, curUsedCmdName, textPrint
    nonlocal InRecordMode, TriggerRecordOff, TriggerRecordOn
    nonlocal leftArmLift, rightArmLift
    nonlocal distElbow2Wrist_l, distElbow2Wrist_r, distShoulders
    nonlocal lastRepTimeLeftArm, lastRepTimeRightArm, slowDownMsgUntil
    nonlocal outVideoAndKeyPnts, outKeyPntsOnly
    inputsize = 192
    cofident_threshold = 0.35
    FrameTextRefreshThreshold = 6
    minIncrementTime = 1.5
    
    ret, frame = cap.read()
    if ret :
      FrameCount = FrameCount + 1
      image = frame.copy()
      image = cv2.flip(image,1)
      # capHeight, capWidth = image.shape[:2] 
      # prepare the image for Tensorflow    
      imageKeyPnt = np.zeros((capHeight,capWidth,3), np.uint8)
      input_image = tf.image.resize_with_pad(np.expand_dims(image,axis=0),inputsize,inputsize)

      # Run model inference.
      keypoints_with_scores = movenet(input_image)
      # Visualize the predictions with image.  
      draw_prediction_on_image(image,imageKeyPnt, keypoints_with_scores,cofident_threshold) 
      lValid,distLTmp, rValid, distRTmp, distShouldersTmp = GetElbow2WristLen(keypoints_with_scores,cofident_threshold)
      if lValid & rValid:
          if (abs(distShouldersTmp - distShoulders) / distShoulders > 0.1): # location changes
            distShoulders = distShouldersTmp
            distElbow2Wrist_l = distLTmp
            distElbow2Wrist_r = distRTmp
          else:
            if (distLTmp > distElbow2Wrist_l) :
              distElbow2Wrist_l = distLTmp
              distShoulders = distShouldersTmp
            if (distRTmp > distElbow2Wrist_r) :
              distElbow2Wrist_r = distRTmp     
              distShoulders = distShouldersTmp  

      CmdName = GetMoveRecommendation(keypoints_with_scores,cofident_threshold,4)
      # CmdName = StandbackCheck(KeyPntCheckList,keypoints_with_scores,cofident_threshold,1)
      if MoveName.Nothing == CmdName:
        PntsPosition = GetMovePositions(keypoints_with_scores,distElbow2Wrist_l, distElbow2Wrist_r, cofident_threshold) 
        if PntsPosition['left_wrist'] != prePntsPosition['left_wrist']  :
          if (PntsPosition['left_wrist'] == MovePosition.Up) & (prePntsPosition['left_wrist'] == MovePosition.Down):
              if time.time() - lastRepTimeLeftArm < minIncrementTime:
                lastRepTimeLeftArm = time.time()
                CmdName = MoveName.SlowDown
                slowDownMsgUntil = time.time() + 2.0
                textPrint = GetRecommendationTex(CmdName)
              else:
                leftArmLift = leftArmLift + 1
                lastRepTimeLeftArm = time.time()
              prePntsPosition['left_wrist'] = MovePosition.Up
          elif PntsPosition['left_wrist'] == MovePosition.Down:
              prePntsPosition['left_wrist'] = MovePosition.Down
        if PntsPosition['right_wrist'] != prePntsPosition['right_wrist']  :
          if (PntsPosition['right_wrist'] == MovePosition.Up) & (prePntsPosition['right_wrist'] == MovePosition.Down):
              if time.time() - lastRepTimeRightArm < minIncrementTime:
                lastRepTimeRightArm = time.time()
                CmdName = MoveName.SlowDown
                slowDownMsgUntil = time.time() + 2.0
                textPrint = GetRecommendationTex(CmdName)
              else:
                rightArmLift = rightArmLift + 1
                lastRepTimeRightArm = time.time()
              prePntsPosition['right_wrist'] = MovePosition.Up
          elif PntsPosition['right_wrist'] == MovePosition.Down:
              prePntsPosition['right_wrist'] = MovePosition.Down

      if time.time() < slowDownMsgUntil:
        # keep showing slowdown message
        textPrint = GetRecommendationTex(MoveName.SlowDown)
      elif(CmdName != MoveName.Nothing):
        if(FrameCount > FrameTextRefreshThreshold) :
          if (CmdName == preCmdName):
            if curUsedCmdName != CmdName:
                curUsedCmdName = CmdName
                textPrint = GetRecommendationTex(CmdName)
          preCmdName = CmdName
          FrameCount = 0
      else:
        curUsedCmdName = MoveName.Nothing
        textPrint = 'LH Reps:' + str(rightArmLift) + '\nRH Reps:' + str(leftArmLift)
        preCmdName = CmdName
        FrameCount = 0



      DrawText(image,textPrint)
      DrawText(imageKeyPnt,textPrint)

      #Handle the button click 
      if TriggerRecordOn:
        TriggerRecordOn = False
        outVideoAndKeyPnts = cv2.VideoWriter(videoAndKeyntsFile, fourcc, 10.0, (capWidth,capHeight))
        outKeyPntsOnly = cv2.VideoWriter(KeypntsFile, fourcc, 10.0, (capWidth,capHeight))  
        # Logoimage = cv2.imread("Logo.png")
        # Logoimage = cv2.resize (Logoimage,(capWidth, capHeight))
        # for counter in range (0,20):
        #   outVideoAndKeyPnts.write(Logoimage)
        leftArmLift = 0
        rightArmLift = 0 
        InRecordMode = True   
      if TriggerRecordOff:
        TriggerRecordOff = False
        outVideoAndKeyPnts.release()
        outKeyPntsOnly.release()
        InRecordMode = False     

      #Write current frame to video
      if InRecordMode:
        # write the flipped frame
        outVideoAndKeyPnts.write(image)
        outKeyPntsOnly.write(imageKeyPnt)      

      #Resize the image and show on the main window  
      ImageShowHeight= int(ImageShowWidth * capHeight / capWidth)
      dim = (ImageShowWidth, ImageShowHeight)
      imageResized = cv2.resize(image,dim)
      cv2image = cv2.cvtColor(imageResized, cv2.COLOR_BGR2RGBA)
      img = Image.fromarray(cv2image)
      imgtk = ImageTk.PhotoImage(image=img)
      lmain.imgtk = imgtk
      lmain.configure(image=imgtk)
    lmain.after(10, show_frame) 
    #full_key_code = cv2.waitKeyEx(10)

  # Record and stop button handling
  def RecordCmd():  
    nonlocal btn
    nonlocal InRecordMode
    nonlocal TriggerRecordOff
    nonlocal TriggerRecordOn  
    if InRecordMode:
      TriggerRecordOff = True
      btn.configure(image=renderStart)
    else:
      TriggerRecordOn = True
      btn.configure(image=renderStop) 
        
    
  #Slider window (slider controls stage position)
  sliderFrame = tk.Frame(window, width=600, height=100)
  sliderFrame.grid(row = 600, column=0, padx=10, pady=2)       
  btn = tk.Button(sliderFrame,image=renderStart, command=RecordCmd)
  btn.grid(row=0,column=1)

  # Play Recording button
  def PlayRecordingCmd():
    play_video(videoAndKeyntsFile)

  playBtn = tk.Button(sliderFrame, text="Play Recording", command=PlayRecordingCmd)
  playBtn.grid(row=0, column=2)


  # t = Thread (target = VideoCapture(lmain))
  # t.start()
  if stopFlag:
    return
  
  show_frame()
  window.mainloop()
  Exit = True
  cap.release()

def stop_camera():
  global stopFlag
  stopFlag = True
  
