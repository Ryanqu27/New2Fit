import time
import numpy as np
import tensorflow as tf
import cv2

from Camera.utilities import (
    movenet,
    draw_prediction_on_image,
    GetMoveRecommendation,
    GetElbow2WristLen,
    GetMovePositionsBicep,
    GetMovePositionsLateral,
)

from Camera.pose_analysis import (
    MoveName,
    MovePosition,
    GetRecommendationTex,
    DrawText
)


class PoseProcessor:
    def __init__(self, exercise):
        self.exercise = exercise
        self.input_size = 192
        self.conf_threshold = 0.35
        self.minIncrementTime = 1.5

        # Rep tracking
        self.leftArmLift = 0
        self.rightArmLift = 0

        self.prePntsPosition = {
            'left_side': MovePosition.Down,
            'right_side': MovePosition.Down
        }

        self.lastRepTimeLeftArm = time.time()
        self.lastRepTimeRightArm = time.time()
        self.slowDownMsgUntil = 0
        self.slowDownMsgDuration = 2
        
        self.distElbow2Wrist_l = 0
        self.distElbow2Wrist_r = 0
        self.distShoulders = 10

        self.textPrint = ""

    def process(self, frame):
        image = cv2.flip(frame, 1)

        input_image = tf.image.resize_with_pad(
            np.expand_dims(image, axis=0),
            self.input_size,
            self.input_size
        )

        keypoints = movenet(input_image)

        draw_prediction_on_image(
            image, image, keypoints, self.conf_threshold
        )

        # Distance normalization
        lValid, distLTmp, rValid, distRTmp, distShouldersTmp = \
            GetElbow2WristLen(keypoints, self.conf_threshold)

        if lValid and rValid:
            self.distElbow2Wrist_l = max(self.distElbow2Wrist_l, distLTmp)
            self.distElbow2Wrist_r = max(self.distElbow2Wrist_r, distRTmp)
            self.distShoulders = distShouldersTmp

        CmdName = GetMoveRecommendation(
            keypoints, self.conf_threshold, 4
        )

        if CmdName == MoveName.Nothing:
            if self.exercise == "Bicep Curls":
                PntsPosition = GetMovePositionsBicep(
                    keypoints,
                    self.distElbow2Wrist_l,
                    self.distElbow2Wrist_r,
                    self.conf_threshold
                )
            elif self.exercise == "Lateral Raises":
                PntsPosition = GetMovePositionsLateral(keypoints)

            self._count_reps(PntsPosition)

        self._update_text(CmdName)

        DrawText(image, self.textPrint)
        return image

    def _count_reps(self, PntsPosition):
        now = time.time()
        
        # Right side Since Camera is Flipped
        if PntsPosition.get('left_side') != self.prePntsPosition['left_side']:
            if PntsPosition.get('left_side') == MovePosition.Up:
                if now - self.lastRepTimeLeftArm < self.minIncrementTime:
                    self.slowDownMsgUntil = now + self.slowDownMsgDuration
                else:
                    self.rightArmLift += 1
                self.lastRepTimeLeftArm = now
            self.prePntsPosition['left_side'] = PntsPosition.get('left_side', MovePosition.Down)

        # Left side Since Camera is Flipped
        if PntsPosition.get('right_side') != self.prePntsPosition['right_side']:
            if PntsPosition.get('right_side') == MovePosition.Up:
                if now - self.lastRepTimeRightArm < self.minIncrementTime:
                    self.slowDownMsgUntil = now + self.slowDownMsgDuration
                else:
                    self.leftArmLift += 1
                self.lastRepTimeRightArm = now
            self.prePntsPosition['right_side'] = PntsPosition.get('right_side', MovePosition.Down)
            
            
    def _update_text(self, CmdName):
        if time.time() < self.slowDownMsgUntil:
            self.textPrint = GetRecommendationTex(MoveName.SlowDown)
        elif CmdName != MoveName.Nothing:
            self.textPrint = GetRecommendationTex(CmdName)
        else:
            self.textPrint = (
                f"LH Reps: {self.leftArmLift}\n"
                f"RH Reps: {self.rightArmLift}"
            )