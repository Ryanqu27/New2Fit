import { useState, useRef, useEffect } from 'react';
import './AICamera.css';

export default function AICamera() {
  const [exercise, setExercise] = useState('Bicep Curls');
  const [isRecording, setIsRecording] = useState(false);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const lastObjectUrlRef = useRef<string | null>(null);

  const stopRecording = () => {
    setIsRecording(false);

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    
    if (imageRef.current) {
      imageRef.current.src = '';
    }
    
    // Clean up any remaining object URL to prevent memory leaks
    if (lastObjectUrlRef.current) {
      URL.revokeObjectURL(lastObjectUrlRef.current);
      lastObjectUrlRef.current = null;
    }
  };

  const startRecording = async () => {
    try {
      setIsRecording(true);

      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }


      const wsUrl = `ws://localhost:8000/api/camera/ws/${encodeURIComponent(exercise)}`;
      const ws = new WebSocket(wsUrl);
      ws.binaryType = 'blob'; 
      wsRef.current = ws;

      const captureAndSend = () => {
        if (videoRef.current && canvasRef.current && ws.readyState === WebSocket.OPEN) {
          const canvas = canvasRef.current;
          const video = videoRef.current;
          
          const MAX_WIDTH = 640;
          const MAX_HEIGHT = 480;
          let width = video.videoWidth;
          let height = video.videoHeight;

          if (width > MAX_WIDTH) {
            height = Math.round((height * MAX_WIDTH) / width);
            width = MAX_WIDTH;
          }
          if (height > MAX_HEIGHT) {
            width = Math.round((width * MAX_HEIGHT) / height);
            height = MAX_HEIGHT;
          }

          canvas.width = width;
          canvas.height = height;
          
          const context = canvas.getContext('2d');
          if (context) {
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            canvas.toBlob((blob) => {
              if (blob) {
                ws.send(blob);
              }
            }, 'image/jpeg', 0.5);
          }
        }
      };

      ws.onopen = () => {
        captureAndSend();
      };

      ws.onmessage = (event) => {
        if (imageRef.current && event.data instanceof Blob) {
          // Clean up the old image URL from memory before creating a new one
          if (lastObjectUrlRef.current) {
            URL.revokeObjectURL(lastObjectUrlRef.current);
          }
          
          // Create a new image URL from the raw Blob data
          const objectUrl = URL.createObjectURL(event.data);
          lastObjectUrlRef.current = objectUrl;
          imageRef.current.src = objectUrl;

          requestAnimationFrame(() => {
            captureAndSend();
          });
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket Error:', error);
        stopRecording();
      };

      ws.onclose = () => {
        stopRecording();
      };

    } catch (err) {
      console.error("Error accessing webcam: ", err);
      setIsRecording(false);
    }
  };

  useEffect(() => {
    return () => {
      stopRecording();
    };
  }, []);

  return (
    <div className="camera-container">
      <h1 className="camera-title">AI Exercise Form Checker</h1>
      <p className="camera-description">Select an exercise to perform and click start</p>
      <div className="camera-controls">
        <select 
          className="exercise-select"
          value={exercise} 
          onChange={(e) => setExercise(e.target.value)}
          disabled={isRecording}
        >
          <option value="Bicep Curls">Bicep Curls</option>
          <option value="Lateral Raises">Lateral Raises</option>
          <option value="Squats">Squats</option>
          <option value="Shoulder Press">Shoulder Press</option>
        </select>

        {!isRecording ? (
          <button className="record-btn start" onClick={startRecording}>
            Start Camera
          </button>
        ) : (
          <button className="record-btn stop" onClick={stopRecording}>
            Stop Camera
          </button>
        )}
      </div>

      <div className="video-display-area">
        <img 
          ref={imageRef} 
          alt="AI Camera Feed" 
          className="ai-feed"
          style={{ display: isRecording ? 'block' : 'none' }} 
        />
        {!isRecording && (
          <div className="camera-placeholder">
            <p style={{ fontSize: '0.85rem', marginTop: '0.5rem', color: '#4b5563' }}>Camera is currently off</p>
          </div>
        )}
        <video ref={videoRef} style={{ display: 'none' }} playsInline muted />
        <canvas ref={canvasRef} style={{ display: 'none' }} />
      </div>
    </div>
  );
}
