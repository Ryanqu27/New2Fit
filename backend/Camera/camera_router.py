from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import base64
from Camera.camera_processor import PoseProcessor

router = APIRouter(prefix="/api/camera", tags=["Camera"])

@router.websocket("/ws/{exercise_name}")
async def camera_websocket(websocket: WebSocket, exercise_name: str):
    await websocket.accept()
        
    processor = PoseProcessor(exercise=exercise_name)
    
    try:
        while True:
            # Receive the binary bytes from React
            data = await websocket.receive_bytes()
                
            # Decode bytes directly to an OpenCV image (numpy array)
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Pass the frame to the existing MoveNet logic
            if frame is not None:
                processed_frame, reps_data, feedback_message = processor.process(frame)
                
                # Encode the processed frame back to a JPEG buffer
                _, buffer = cv2.imencode('.jpg', processed_frame)
                base64_image = base64.b64encode(buffer).decode('utf-8')
                
                # Send the clean JSON payload back to React
                await websocket.send_json({
                    "image": base64_image,
                    "reps": reps_data,
                    "message": feedback_message
                })
                
    except WebSocketDisconnect:
        print("Client disconnected from AI Camera")
    except Exception as e:
        print(f"Error in WebSocket: {e}")
