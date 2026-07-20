# New2Fit
New2Fit is a personalized AI fitness application for beginners featuring an AI camera with real-time pose analysis and feedback.

## Overview
New2Fit uses a TensorFlow pose model (MoveNet) to analyze exercise form in real time and provides per-rep feedback on range of motion, speed, and joint angles. The application features a modern full-stack architecture with a **React** (Vite) frontend and a **FastAPI** backend. Real-time video processing is handled via WebSockets, and user data is managed securely using **SQLAlchemy**.

## Features
- **Real-time AI Camera Body Tracking**: Analyzes video frames using MoveNet via WebSockets.
- **Form Analysis & Feedback**: Provides per-rep feedback, angle measurement, and speed monitoring.
- **Modern Web Interface**: Built with React and TypeScript for a highly responsive user experience.
- **Workout Logging**: Track your exercises, sets, reps, and weights over time.
- **Personalized Dashboard & Questionnaire**: Customize your fitness journey based on your personal preferences and goals.
- **Real-time Chat & User Communication**: Instant user-to-user messaging powered by WebSockets, complete with live unread message badges and active conversation state syncing.
- **Gym Locator**: Gym locations and websites retrieved from a web scraping algorithm. 
- **Google OAuth**: Secure user authentication.

## Tech Stack
- **Frontend**: React, TypeScript, Vite, React Router
- **Backend**: FastAPI, Python, WebSockets, SQLAlchemy, Pydantic
- **AI/ML**: TensorFlow (MoveNet)

