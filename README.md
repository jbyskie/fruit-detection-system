# Fruit Detection Web Application

A modern web application for detecting and analyzing fruits using YOLOv8 machine learning model.

## Features

### Core Functionality
- **Fruit Detection**: Upload images and detect fruits using YOLOv8 model
- **Ripeness Analysis**: Determine if fruits are ripe or unripe
- **User Authentication**: Secure login and registration system
- **Detection History**: Track all your previous detections

### Dashboard Overview
- **Total Detections Card**: View detection counts with time filters (Today, Week, Month)
- **Most Common Objects Card**: See frequently detected fruits with icons and statistics
- **Ripeness Distribution**: Visual breakdown of ripe vs unripe detections
- **Recent Activity Feed**: Latest detection activities with timestamps and confidence scores
- **Interactive UI**: Modern design with animations, hover effects, and responsive layout

### Modern UI Features
- **Glassmorphism Design**: Beautiful glass-like cards with backdrop blur effects
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile devices
- **Interactive Elements**: Hover animations, ripple effects, and smooth transitions
- **Real-time Updates**: Dynamic statistics with animated counters and progress bars
- **Color-coded Indicators**: Visual feedback for different fruit types and ripeness levels

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```

## Usage

1. **Register/Login**: Create an account or login to access the dashboard
2. **Dashboard**: View your detection statistics and recent activity
3. **Upload Images**: Use the upload feature to detect fruits in your images
4. **View History**: Check your detection history and results
5. **Settings**: Customize your preferences and detection parameters

## Dashboard Features

### Statistics Cards
- **Total Detections**: Toggle between Today, This Week, and This Month views
- **Most Common Objects**: See your most frequently detected fruits with count badges
- **Progress Tracking**: Visual progress bars showing goal achievement

### Interactive Elements
- **Time Filters**: Click to switch between different time periods
- **Animated Counters**: Numbers animate when switching between time periods
- **Hover Effects**: Cards lift and scale on hover with smooth transitions
- **Ripple Buttons**: Material design-inspired button click effects

### Responsive Design
- **Mobile Optimized**: Touch-friendly interface on mobile devices
- **Tablet Ready**: Optimized layout for tablet screens
- **Desktop Enhanced**: Full feature set with enhanced animations on desktop

## Technology Stack

- **Backend**: Flask, SQLAlchemy, SQLite
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Machine Learning**: YOLOv8, OpenCV, PIL
- **Styling**: Custom CSS with glassmorphism effects
- **Icons**: Font Awesome 6

## File Structure

```
Web app/
├── app.py                 # Main Flask application
├── templates/
│   ├── dashboard.html     # Dashboard overview page
│   ├── base.html          # Base template with navigation
│   └── ...                # Other templates
├── static/
│   ├── style.css          # Custom styles with dashboard CSS
│   └── uploads/           # Uploaded and processed images
├── model/
│   └── best.pt           # YOLOv8 trained model
└── instance/
    └── users.db          # SQLite database
```

## Contributing

Feel free to submit issues and enhancement requests! 