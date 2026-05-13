from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import base64
import cv2
import numpy as np
from Camera.CameraProcessor import PoseProcessor

router = APIRouter()

@router.websocket("/ws/{exercise_name}")
async def camera_websocket(websocket: WebSocket, exercise_name: str):
    await websocket.accept()
        
    processor = PoseProcessor(exercise=exercise_name)
    
    try:
        while True:
            # Receive the base64 string from React
            data = await websocket.receive_text()
            
            # Extract the raw base64 data 
            if ',' in data:
                encoded_data = data.split(',')[1]
            else:
                encoded_data = data
                
            # Decode base64 to an OpenCV image (numpy array)
            nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Pass the frame to the existing MoveNet logic
            if frame is not None:
                processed_frame = processor.process(frame)
                
                _, buffer = cv2.imencode('.jpg', processed_frame)
                base64_str = base64.b64encode(buffer).decode('utf-8')
                
                await websocket.send_text(f"data:image/jpeg;base64,{base64_str}")
                
    except WebSocketDisconnect:
        print("Client disconnected from AI Camera")
    except Exception as e:
        print(f"Error in WebSocket: {e}")
