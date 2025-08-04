# AI Bird Detection Project

A comprehensive cloud-based bird detection and media management system built on AWS infrastructure. This project provides intelligent bird species identification from images, videos, and audio files with a modern web interface.

## Project Overview

This application allows users to upload media files (images, videos, audio) and automatically detects and tags bird species using advanced AI models. Users can then search and query their media collection by bird species tags, thumbnails, and other metadata.

## Technologies Used

### Frontend

- **React** - Modern JavaScript framework for building user interfaces
- **React Router DOM** - Client-side routing
- **AWS Amplify** - Authentication and AWS service integration
- **Amazon Cognito** - User authentication and management
- **Axios** - HTTP client for API requests

### Backend & Cloud Services

- **AWS Lambda** - Serverless compute for processing functions
- **Amazon S3** - Object storage for media files and thumbnails
- **Amazon DynamoDB** - NoSQL database for metadata storage
- **Amazon SNS** - Simple Notification Service for messaging
- **Amazon EventBridge** - Event-driven architecture coordination
- **Amazon container Registry** - Containerisation for Lambda functions

### AI/ML Technologies

- **BirdNET Analyzer** - Audio-based bird species identification
- **YOLOv8 (Ultralytics)** - Object detection for image/video analysis
- **OpenCV** - Computer vision processing
- **Supervision** - Computer vision utilities

## Key Features

- Multi-modal bird detection (image, video, audio)
- Automated thumbnail generation
- Real-time species tagging and metadata storage
- Query system for searching by bird species
- User authentication and file management
- Bulk tagging capabilities
- SNS notifications for processing updates
