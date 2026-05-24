from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
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
                processed_frame = processor.process(frame)
                
                # Encode the processed frame back to a JPEG buffer
                _, buffer = cv2.imencode('.jpg', processed_frame)
                
                # Send the raw bytes back to React
                await websocket.send_bytes(buffer.tobytes())
                
    except WebSocketDisconnect:
        print("Client disconnected from AI Camera")
    except Exception as e:
        print(f"Error in WebSocket: {e}")
