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
    GetMovePositionsSquat,
    GetMovePositionsShoulderPress,
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

        # Dynamic Rep tracking
        self.reps = {}
        self.prePntsPosition = {}
        self.lastRepTime = {}
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
            elif self.exercise == "Squats":
                PntsPosition = GetMovePositionsSquat(keypoints, self.conf_threshold)
            elif self.exercise == "Shoulder Press":
                PntsPosition = GetMovePositionsShoulderPress(keypoints, self.conf_threshold)

            self._count_reps(PntsPosition)

        feedback_msg = self._update_text(CmdName)
        return image, self.reps, feedback_msg

    def _count_reps(self, PntsPosition):
        now = time.time()
        
        # Initialize rep stages dictionary if it doesn't exist
        if not hasattr(self, 'rep_stage'):
            self.rep_stage = {}
            
        for key, state in PntsPosition.items():
            # Initialize states for any newly detected keys
            if key not in self.prePntsPosition:
                self.prePntsPosition[key] = MovePosition.Down
                self.rep_stage[key] = MovePosition.Down
                self.reps[key] = 0
                self.lastRepTime[key] = now
            
            # Update the stage tracker
            if state == MovePosition.Down:
                self.rep_stage[key] = MovePosition.Down
            elif state == MovePosition.Up and self.rep_stage[key] == MovePosition.Down:
                # Only count the rep if we are transitioning from a successfully reached Down state
                if now - self.lastRepTime[key] < self.minIncrementTime:
                    self.slowDownMsgUntil = now + self.slowDownMsgDuration
                else:
                    self.reps[key] += 1
                self.lastRepTime[key] = now
                self.rep_stage[key] = MovePosition.Up
                
            self.prePntsPosition[key] = state
            
            
    def _update_text(self, CmdName):
        if time.time() < self.slowDownMsgUntil:
            return GetRecommendationTex(MoveName.SlowDown)
        elif CmdName != MoveName.Nothing:
            return GetRecommendationTex(CmdName)
        return ""