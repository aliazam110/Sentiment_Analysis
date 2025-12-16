

# PayFast Sentiment Analysis System

A comprehensive sentiment analysis platform designed for PayFast Pakistan that enables users to submit reviews and receive sentiment analysis feedback. The system includes role-based access control for regular users and administrators.

## Project Overview

This system provides a seamless interface for customers to submit their reviews about PayFast services, which are then analyzed using advanced sentiment analysis techniques. Administrators can monitor all submitted reviews and user activities through a dedicated dashboard.

## Key Features

### User Features
- **User Authentication**: Secure login system with session management
- **Review Submission**: Simple interface for submitting customer reviews
- **Sentiment Analysis**: Real-time analysis of submitted reviews
- **Review History**: View and track previously submitted reviews
- **Responsive Design**: Works seamlessly across all device types

### Administrator Features
- **Admin Dashboard**: Comprehensive overview of system activities
- **User Management**: Monitor and manage registered users
- **Review Monitoring**: Access all submitted reviews with user information
- **Sentiment Analytics**: View sentiment analysis results across all reviews
- **Role-Based Access**: Secure access control for administrative functions

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **MySQL**: Relational database for data persistence
- **Python**: Core programming language
- **JWT**: Secure token-based authentication
- **Session Management**: Server-side session handling

### Frontend
- **HTML5/CSS3**: Structure and styling
- **Bootstrap 5**: Responsive UI framework
- **JavaScript**: Client-side interactivity
- **Font Awesome**: Icon library

### Machine Learning
- **BERT**: Transformer-based model for sentiment analysis
- **PyTorch**: Deep learning framework
- **Transformers Library**: Pre-trained models and tokenization

## System Architecture

### Authentication Flow
1. **Unified Login**: Single login endpoint for both users and administrators
2. **Role Verification**: System checks user role during authentication
3. **Dynamic Redirection**: Users are redirected based on their role (user to review page, admin to dashboard)
4. **Session Management**: Secure session handling with automatic invalidation on navigation away

### Sentiment Analysis Pipeline
1. **Text Preprocessing**: Cleaning and preparing review text
2. **Tokenization**: Converting text to model-compatible format
3. **Model Inference**: BERT model predicts sentiment categories
4. **Result Storage**: Analysis results stored with original review
5. **Visualization**: Results presented in user-friendly format

## Security Features

### Authentication Security
- **Password Hashing**: Secure storage of user credentials
- **Session Tokens**: Encrypted session management
- **Automatic Logout**: Sessions invalidated when navigating away
- **Cache Control**: Prevents sensitive data caching in browsers

### Access Control
- **Role-Based Authorization**: Strict separation of user and admin privileges
- **Protected Routes**: All sensitive endpoints require authentication
- **Session Validation**: Continuous verification of user sessions
- **Secure Headers**: Implementation of security best practices

## Database Schema

### Users Table
- `id`: Unique user identifier
- `name`: User's full name
- `email`: User's email address (unique)
- `cnic`: User's CNIC (unique)
- `password`: Hashed password
- `role`: User role (USER or ADMIN)
- `created_at`: Account creation timestamp

### Reviews Table
- `id`: Unique review identifier
- `user_id`: Reference to user who submitted review
- `review_text`: Content of the review
- `sentiment_results`: JSON object containing analysis results
- `created_at`: Review submission timestamp

## Project Structure

```
project/
├── main.py                 # Application entry point
├── routes.py              # User authentication and review routes
├── admin_routes.py        # Administrative routes
├── models.py              # Pydantic models and schemas
├── auth.py                # Authentication utilities
├── database.py            # Database connection and setup
├── crud.py                # Database operations
├── model_loader.py        # Machine learning model loading
├── predict.py             # Sentiment prediction logic
├── templates/             # HTML templates
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── review.html
│   └── admin_dashboard.html
└── static/                # Static assets
    ├── css/
    ├── js/
    └── images/
```

## Key Components

### Authentication System
- **Unified Login**: Single endpoint handles both user and admin authentication
- **Role Detection**: Automatic role detection during login process
- **Session Invalidation**: Automatic session clearing when navigating away from protected pages
- **Secure Redirection**: Users redirected based on their assigned role

### Sentiment Analysis Engine
- **BERT Model**: State-of-the-art transformer model for accurate sentiment analysis
- **Multi-label Classification**: Detects multiple sentiment categories in each review
- **Real-time Processing**: Instant analysis results upon review submission
- **Result Persistence**: Analysis results stored for future reference

### User Interface
- **Responsive Design**: Optimized for all device sizes
- **Intuitive Navigation**: Clear user flow and information architecture
- **Visual Feedback**: Immediate feedback for user actions
- **Accessibility**: Designed with accessibility best practices

## Future Enhancements

1. **Advanced Analytics**: Enhanced dashboard with detailed sentiment trends
2. **Notification System**: Email notifications for new reviews and admin actions
3. **Review Moderation**: Workflow for managing inappropriate content
4. **Multi-language Support**: Expansion to support multiple languages
5. **Mobile Application**: Native mobile apps for improved accessibility
6. **Integration APIs**: Third-party system integration capabilities

## Development Team

Developed by Syed Ali Azam for PayFast Pakistan.

This system represents a comprehensive solution for gathering and analyzing customer sentiment, providing valuable insights for improving service quality and customer satisfaction.
