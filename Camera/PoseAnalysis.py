import cv2
from enum import Enum

# font 
font = cv2.FONT_ITALIC 
  
# org 
org = (00, 50) 
  
# fontScale 
fontScale = 1
   
# Red color in BGR 
color = (255, 255, 255) 
bkColor = (0,0,0)
  
# Line thickness of 2 px 
thickness = 2

class MovePosition(Enum):
    Down = 1
    Up = 2
    Middle = 3


class MoveName(Enum):
    Nothing = 1
    StandBack = 2
    MoveToLeft = 3
    MoveToRight = 4
    SlowDown = 5
CommandString = {
    MoveName.Nothing: ' ',
    MoveName.StandBack: 'Please Stand Back',
    MoveName.MoveToLeft: 'Please shift to the left',
    MoveName.MoveToRight: 'Please shift to the right',        
    MoveName.SlowDown: 'Please slow your reps down',
}

def GetRecommendationTex(CmdName):
    if type(CmdName) is MoveName:
        return CommandString[CmdName]
    else:
        return ""

def play_video(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video file {video_path}")
        return
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('Playback', frame)
        # Press 'q' to exit playback
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def DrawText(image, text):
    xSize = 0
    ySize = 0
    margin = 5
    line_heights = list()
    for i, line in enumerate(text.split("\n")):
        text_size, _ = cv2.getTextSize(line,font,fontScale,thickness)
        if text_size[0] > xSize:
            xSize = text_size[0]
        curLineHeight = text_size[1] + margin
        ySize = ySize + curLineHeight
        line_heights.append(curLineHeight)
    if len(line_heights) <= 0:
        return

    x0, y0 = org
    cv2.rectangle(image,(x0-margin, y0-line_heights[0]), 
                  (x0+xSize+margin, y0-line_heights[0] + ySize + margin), bkColor, -1 )
    # image = cv2.putText(image, text, org, font, fontScale,  
    #              color, thickness, cv2.LINE_AA, False) 
    for i, line in enumerate(text.split("\n")):
        if i <= 0:
            y = y0
        else:
            y = y0 + line_heights[i - 1]
        cv2.putText(image,
                    line,
                    (x0, y),
                    font,
                    fontScale,
                    color,
                    thickness,
                    cv2.LINE_AA, False)
