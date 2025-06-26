from flask import Flask, render_template, request, redirect, url_for, flash, current_app, send_from_directory, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from PIL import Image, ImageDraw
import numpy as np
from sklearn.cluster import KMeans
import cv2
from werkzeug.utils import secure_filename
import logging
from dotenv import load_dotenv
from ultralytics import YOLO
from collections import Counter
from sqlalchemy import func
import pandas as pd
import tempfile
from io import BytesIO
import json
from excel_template import create_detection_export, create_summary_export

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mangosteen.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    settings = db.Column(db.JSON, default=lambda: {
        'dark_mode': False,
        'show_notifications': True,
        'confidence_threshold': 50,
        'save_history': True,
        'email_results': False,
        'email_updates': False
    })
    detections = db.relationship('Detection', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_settings(self, settings_dict):
        current_settings = self.settings or {}
        current_settings.update(settings_dict)
        self.settings = current_settings

# Detection History Model
class Detection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    fruit_type = db.Column(db.String(50), nullable=False)
    ripeness = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Fruit Model
class Fruit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    image_path = db.Column(db.String(255), nullable=True)

def get_dominant_colors(image_path, num_colors=3):
    # Load image and convert to RGB
    img = Image.open(image_path)
    img = img.convert('RGB')
    
    # Resize image for faster processing
    img = img.resize((150, 150))
    
    # Convert image to numpy array
    img_array = np.array(img)
    
    # Reshape array to 2D
    pixels = img_array.reshape(-1, 3)
    
    # Use KMeans to find dominant colors
    kmeans = KMeans(n_clusters=num_colors, random_state=42)
    kmeans.fit(pixels)
    
    # Get the dominant colors
    colors = kmeans.cluster_centers_
    
    return colors

def allowed_file(filename):
    """Check if the file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def draw_bounding_box(image, contour):
    """Draw a bounding box around the detected fruit."""
    try:
        # Get the bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)
        
        # Calculate adaptive padding based on fruit size
        size = min(w, h)
        max_size = max(image.shape[0], image.shape[1])
        padding = 0.05 + (0.15 * (1 - size/max_size))  # 5-20% padding
        
        # Add padding
        x = int(x - w * padding)
        y = int(y - h * padding)
        w = int(w * (1 + 2 * padding))
        h = int(h * (1 + 2 * padding))
        
        # Ensure coordinates are within image bounds
        x = max(0, x)
        y = max(0, y)
        w = min(w, image.shape[1] - x)
        h = min(h, image.shape[0] - y)
        
        # Draw the bounding box
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Add label
        label = "Mangosteen"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        
        # Calculate label size and position
        (label_width, label_height), _ = cv2.getTextSize(label, font, font_scale, thickness)
        label_x = x + (w - label_width) // 2
        label_y = y - 10
        
        # Draw label background
        cv2.rectangle(image, 
                     (label_x - 5, label_y - label_height - 5),
                     (label_x + label_width + 5, label_y + 5),
                     (0, 255, 0), -1)
        
        # Draw label text
        cv2.putText(image, label, (label_x, label_y), font, font_scale, (0, 0, 0), thickness)
        
        return image
    except Exception as e:
        print(f"Error drawing bounding box: {str(e)}")
        return image

def draw_adaptive_box(image, contour):
    """Draw an adaptive bounding box around the detected fruit."""
    try:
        # Get the bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)
        
        # Calculate adaptive padding based on fruit size
        size = min(w, h)
        max_size = max(image.shape[0], image.shape[1])
        padding = 0.05 + (0.15 * (1 - size/max_size))  # 5-20% padding
        
        # Add padding
        x = int(x - w * padding)
        y = int(y - h * padding)
        w = int(w * (1 + 2 * padding))
        h = int(h * (1 + 2 * padding))
        
        # Ensure coordinates are within image bounds
        x = max(0, x)
        y = max(0, y)
        w = min(w, image.shape[1] - x)
        h = min(h, image.shape[0] - y)
        
        # Draw the bounding box
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Add label
        label = "Mangosteen"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        
        # Calculate label size and position
        (label_width, label_height), _ = cv2.getTextSize(label, font, font_scale, thickness)
        label_x = x + (w - label_width) // 2
        label_y = y - 10
        
        # Draw label background
        cv2.rectangle(image, 
                     (label_x - 5, label_y - label_height - 5),
                     (label_x + label_width + 5, label_y + 5),
                     (0, 255, 0), -1)
        
        # Draw label text
        cv2.putText(image, label, (label_x, label_y), font, font_scale, (0, 0, 0), thickness)
        
        return image
    except Exception as e:
        print(f"Error drawing adaptive box: {str(e)}")
        return image

# Load YOLO model at startup
try:
    yolo_model = YOLO('model/best.pt')
    logging.info("YOLO model loaded successfully")
    logging.debug(f"Model classes: {yolo_model.names}")
    print("YOLO model class names:", yolo_model.names)
except Exception as e:
    logging.error(f"Error loading YOLO model: {str(e)}")
    yolo_model = None

def detect_fruit(image_path):
    """Detect fruit and ripeness using YOLOv8 model. Returns a summary of all detections."""
    if yolo_model is None:
        raise ValueError("YOLO model not loaded properly")
    try:
        results = yolo_model(image_path)
        detections_summary = []
        seen_boxes = set()
        image = Image.open(image_path).convert('RGB')
        draw = ImageDraw.Draw(image)
        confidence_threshold = 0.5  # Set your desired threshold
        for r in results:
            boxes = r.boxes
            if len(boxes) == 0:
                logging.warning("No detections found in image")
                continue
            for i, box in enumerate(boxes):
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                if conf < confidence_threshold:
                    continue
                if not hasattr(yolo_model, 'names'):
                    raise ValueError("Model classes not found")
                fruit_type = yolo_model.names[cls]
                # Extract fruit type and ripeness
                if '_' in fruit_type:
                    fruit_name, ripeness = fruit_type.split('_', 1)
                    fruit_name = fruit_name.strip().title()
                    ripeness = ripeness.lower().strip()
                else:
                    fruit_name = fruit_type.strip().title()
                    ripeness = 'unknown'
                    if 'unripe' in fruit_type.lower():
                        ripeness = 'unripe'
                    elif 'ripe' in fruit_type.lower():
                        ripeness = 'ripe'
                # Get box coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                box_tuple = (x1, y1, x2, y2)
                if box_tuple in seen_boxes:
                    continue
                seen_boxes.add(box_tuple)
                # Set color: green for unripe, red for others
                if ripeness == 'unripe':
                    box_color = (0, 200, 0)
                else:
                    box_color = (255, 0, 0)
                # Draw bounding box
                draw.rectangle([x1, y1, x2, y2], outline=box_color, width=3)
                # Draw label background
                label_text = f"{ripeness} {conf:.2f}"
                text_width = draw.textlength(label_text)
                label_height = 18
                draw.rectangle([x1, y1 - label_height, x1 + text_width + 8, y1], fill=box_color)
                draw.text((x1 + 4, y1 - label_height + 2), label_text, fill=(255, 255, 255))
                detections_summary.append({
                    'fruit_type': fruit_name,
                    'ripeness': ripeness,
                    'confidence': conf,
                    'is_mangosteen': fruit_name.lower() == 'mangosteen'
                })
        processed_filename = f"processed_{os.path.basename(image_path)}"
        processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
        image.save(processed_path)
        logging.debug(f"Processed image saved to: {processed_path}")
        if not detections_summary:
            raise ValueError("No valid detections found in the image")
        return detections_summary
    except Exception as e:
        logging.error(f"Error in detect_fruit: {str(e)}")
        raise ValueError(f"Error during detection: {str(e)}")

@app.route('/')
def index():
    """Home page route"""
    try:
        return render_template('index.html')
    except Exception as e:
        logging.error(f"Error in index route: {str(e)}")
        flash('Error loading home page')
        return redirect(url_for('login'))

@app.route('/debug/users')
def debug_users():
    """Debug route to check users in the database"""
    try:
        users = User.query.all()
        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'username': user.username
            })
        return {'users': user_list}
    except Exception as e:
        return {'error': str(e)}

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            logging.debug(f"Login attempt for username: {username}")
            
            if not username or not password:
                flash('Please enter both username and password')
                return render_template('login.html')
            
            user = User.query.filter_by(username=username).first()
            if user:
                logging.debug("User found in database")
                if user.check_password(password):
                    logging.debug("Password check passed")
                    login_user(user)
                    logging.debug("User logged in successfully")
                    return redirect(url_for('detect'))
                else:
                    logging.debug("Password check failed")
                    flash('Invalid username or password')
            else:
                logging.debug("User not found in database")
                flash('Invalid username or password')
        
        return render_template('login.html')
    except Exception as e:
        logging.error(f"Error in login route: {str(e)}")
        flash('An error occurred during login. Please try again.')
        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            logging.debug(f"Registration attempt for username: {username}")
            
            if not username or not password:
                flash('Please enter both username and password')
                return render_template('register.html')
            
            # Check if username already exists
            if User.query.filter_by(username=username).first():
                logging.debug("Username already exists")
                flash('Username already exists')
                return render_template('register.html')
            
            try:
                # Create new user
                user = User(username=username)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                logging.debug("New user created successfully")
                
                flash('Registration successful! Please login.')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                logging.error(f"Database error during registration: {str(e)}")
                flash('An error occurred during registration. Please try again.')
                return render_template('register.html')
        
        return render_template('register.html')
    except Exception as e:
        logging.error(f"Error in register route: {str(e)}")
        flash('An error occurred. Please try again.')
        return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard overview with statistics"""
    try:
        # Get current date and calculate time ranges
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)
        
        # Get detections for different time periods
        today_detections = Detection.query.filter(
            Detection.user_id == current_user.id,
            Detection.timestamp >= today_start
        ).count()
        
        week_detections = Detection.query.filter(
            Detection.user_id == current_user.id,
            Detection.timestamp >= week_start
        ).count()
        
        month_detections = Detection.query.filter(
            Detection.user_id == current_user.id,
            Detection.timestamp >= month_start
        ).count()
        
        # Get most common objects (fruit types)
        common_objects = db.session.query(
            Detection.fruit_type,
            func.count(Detection.id).label('count')
        ).filter(
            Detection.user_id == current_user.id
        ).group_by(
            Detection.fruit_type
        ).order_by(
            func.count(Detection.id).desc()
        ).limit(5).all()
        
        # Get ripeness distribution
        ripeness_stats = db.session.query(
            Detection.ripeness,
            func.count(Detection.id).label('count')
        ).filter(
            Detection.user_id == current_user.id,
            Detection.ripeness != 'unknown'
        ).group_by(
            Detection.ripeness
        ).order_by(
            func.count(Detection.id).desc()
        ).all()
        
        # Get recent detections for the activity feed
        recent_detections = Detection.query.filter_by(
            user_id=current_user.id
        ).order_by(
            Detection.timestamp.desc()
        ).limit(5).all()
        
        return render_template('dashboard.html',
                             today_detections=today_detections,
                             week_detections=week_detections,
                             month_detections=month_detections,
                             common_objects=common_objects,
                             ripeness_stats=ripeness_stats,
                             recent_detections=recent_detections)
    except Exception as e:
        logging.error(f"Error in dashboard route: {str(e)}")
        flash('Error loading dashboard')
        return redirect(url_for('detect'))

@app.route('/detect', methods=['GET', 'POST'])
@login_required
def detect():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return render_template('detect.html')
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return render_template('detect.html')
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload an image (PNG, JPG, JPEG, or GIF)')
            return render_template('detect.html')
        
        try:
            # Create a unique filename
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save the file
            file.save(file_path)
            logging.debug(f"File saved to: {file_path}")
            
            # Verify file was saved
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Failed to save file: {file_path}")
            
            # Process the image
            logging.debug("Starting fruit detection...")
            detections = detect_fruit(file_path)
            logging.debug(f"Detection results: {detections}")
            
            if not detections:
                raise ValueError("No detections found in the image")
            
            # Save every detection (bounding box/object) as a separate Detection row
            for det in detections:
                detection = Detection(
                    user_id=current_user.id,
                    image_path=f"processed_{unique_filename}",
                    fruit_type=det['fruit_type'],
                    ripeness=det['ripeness'],
                    confidence=det['confidence'],
                    timestamp=datetime.utcnow()
                )
                db.session.add(detection)
            db.session.commit()
            
            # Count breakdown of detected classes
            class_counts = Counter([det['fruit_type'] for det in detections])
            # Count ripe and unripe objects in the current detection
            total_ripe = sum(1 for det in detections if det['ripeness'] == 'ripe')
            total_unripe = sum(1 for det in detections if det['ripeness'] == 'unripe')
            ripeness_counts = Counter([det['ripeness'] for det in detections if det['ripeness'] != 'unknown'])
            for key in ['ripe', 'unripe']:
                if key not in ripeness_counts:
                    ripeness_counts[key] = 0
            
            logging.debug(f"Class counts: {class_counts}")
            logging.debug(f"Ripeness counts: {ripeness_counts}")
            
            logging.info(f"Number of ripe: {ripeness_counts.get('ripe', 0)}")
            logging.info(f"Number of unripe: {ripeness_counts.get('unripe', 0)}")
            
            # Query the total sum of ripe and unripe detections for the current user
            total_ripe_sum = Detection.query.filter_by(user_id=current_user.id, ripeness='ripe').count()
            total_unripe_sum = Detection.query.filter_by(user_id=current_user.id, ripeness='unripe').count()
            
            return render_template('result.html',
                                image_path=f"processed_{unique_filename}",
                                fruit_type=detections[0]['fruit_type'],
                                ripeness=detections[0]['ripeness'],
                                confidence=detections[0]['confidence'],
                                detections_summary=detections,
                                class_counts=class_counts,
                                ripeness_counts=ripeness_counts,
                                total_ripe=total_ripe,
                                total_unripe=total_unripe,
                                total_ripe_sum=total_ripe_sum,
                                total_unripe_sum=total_unripe_sum,
                                is_mangosteen=detections[0]['is_mangosteen'])
            
        except FileNotFoundError as e:
            logging.error(f"File error: {str(e)}")
            flash('Error saving the uploaded file')
            return render_template('detect.html')
        except ValueError as e:
            logging.error(f"Detection error: {str(e)}")
            flash(str(e))
            return render_template('detect.html')
        except Exception as e:
            logging.error(f"Unexpected error in detect route: {str(e)}")
            flash('An unexpected error occurred while processing the image')
            return render_template('detect.html')
    
    return render_template('detect.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Add a route to serve images directly
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Test route to verify image serving
@app.route('/test_image/<filename>')
def test_image(filename):
    """Test route to serve images"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        logging.error(f"Error serving image {filename}: {str(e)}")
        return str(e), 404

@app.route('/list_images')
def list_images():
    """List all images in the upload folder"""
    try:
        images = os.listdir(app.config['UPLOAD_FOLDER'])
        return jsonify(images)
    except Exception as e:
        logging.error(f"Error listing images: {str(e)}")
        return str(e), 500

@app.route('/test')
def test():
    """Test route to verify image display"""
    try:
        return render_template('test_image.html')
    except Exception as e:
        logging.error(f"Error in test route: {str(e)}")
        return str(e), 500

@app.route('/history', methods=['GET'])
@login_required
def history():
    """Display user's detection history with filtering and search, and remove duplicate results per image. Also provide ripe/unripe counts for each detection."""
    try:
        query = Detection.query.filter_by(user_id=current_user.id)
        ripeness = request.args.get('ripeness')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        if ripeness and ripeness != 'all':
            query = query.filter(Detection.ripeness == ripeness)
        if date_from:
            query = query.filter(Detection.timestamp >= date_from)
        if date_to:
            query = query.filter(Detection.timestamp <= date_to)
        # Remove duplicates: get only the most recent detection per image_path
        subquery = query.with_entities(
            Detection.image_path,
            db.func.max(Detection.timestamp).label('max_timestamp')
        ).group_by(Detection.image_path).subquery()
        detections = db.session.query(Detection).join(
            subquery,
            (Detection.image_path == subquery.c.image_path) & (Detection.timestamp == subquery.c.max_timestamp)
        ).order_by(Detection.timestamp.desc()).all()
        # For each detection, count ripe and unripe for that image
        ripe_unripe_counts = {}
        for det in detections:
            all_for_image = Detection.query.filter_by(user_id=current_user.id, image_path=det.image_path).all()
            ripe_count = sum(1 for d in all_for_image if d.ripeness == 'ripe')
            unripe_count = sum(1 for d in all_for_image if d.ripeness == 'unripe')
            ripe_unripe_counts[det.id] = {'ripe': ripe_count, 'unripe': unripe_count}
        return render_template('history.html', detections=detections, ripe_unripe_counts=ripe_unripe_counts)
    except Exception as e:
        logging.error(f"Error in history route: {str(e)}")
        flash('Error loading history')
        return redirect(url_for('detect'))

@app.route('/export_history')
@login_required
def export_history():
    """Export filtered detection history as Excel file with professional formatting and title."""
    try:
        query = Detection.query.filter_by(user_id=current_user.id)
        ripeness = request.args.get('ripeness')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        if ripeness and ripeness != 'all':
            query = query.filter(Detection.ripeness == ripeness)
        if date_from:
            query = query.filter(Detection.timestamp >= date_from)
        if date_to:
            query = query.filter(Detection.timestamp <= date_to)
        # Remove duplicates: get only the most recent detection per image_path
        subquery = query.with_entities(
            Detection.image_path,
            db.func.max(Detection.timestamp).label('max_timestamp')
        ).group_by(Detection.image_path).subquery()
        detections = db.session.query(Detection).join(
            subquery,
            (Detection.image_path == subquery.c.image_path) & (Detection.timestamp == subquery.c.max_timestamp)
        ).order_by(Detection.timestamp.desc()).all()
        
        if not detections:
            flash('No data to export.')
            return redirect(url_for('history'))
        
        # Prepare filters dictionary
        filters = {}
        if ripeness and ripeness != 'all':
            filters['ripeness'] = ripeness
        if date_from:
            filters['date_from'] = date_from
        if date_to:
            filters['date_to'] = date_to
        
        # Use the Excel template to create the export
        output, filename = create_detection_export(detections, current_user, filters)
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        logging.error(f"Error exporting history: {str(e)}")
        flash('Error exporting history: ' + str(e))
        return redirect(url_for('history'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Display and edit user profile"""
    try:
        if request.method == 'POST':
            email = request.form.get('email')
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            # Update email if provided
            if email and email != current_user.email:
                if User.query.filter_by(email=email).first():
                    flash('Email already in use')
                else:
                    current_user.email = email
                    flash('Email updated successfully')

            # Update password if provided
            if current_password and new_password and confirm_password:
                if not current_user.check_password(current_password):
                    flash('Current password is incorrect')
                elif new_password != confirm_password:
                    flash('New passwords do not match')
                else:
                    current_user.set_password(new_password)
                    flash('Password updated successfully')

            db.session.commit()
            return redirect(url_for('profile'))

        # Calculate statistics
        total_detections = Detection.query.filter_by(user_id=current_user.id).count()
        successful_detections = Detection.query.filter(
            Detection.user_id == current_user.id,
            Detection.confidence >= 0.8
        ).count()
        accuracy_rate = (successful_detections / total_detections * 100) if total_detections > 0 else 0

        return render_template(
            'profile.html',
            total_detections=total_detections,
            successful_detections=successful_detections,
            accuracy_rate=accuracy_rate
        )
    except Exception as e:
        logging.error(f"Error in profile route: {str(e)}")
        flash('Error updating profile')
        return redirect(url_for('profile'))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Display and edit user settings"""
    try:
        if request.method == 'POST':
            settings_dict = {
                'dark_mode': bool(request.form.get('dark_mode')),
                'show_notifications': bool(request.form.get('show_notifications')),
                'confidence_threshold': int(request.form.get('confidence_threshold', 50)),
                'save_history': bool(request.form.get('save_history')),
                'email_results': bool(request.form.get('email_results')),
                'email_updates': bool(request.form.get('email_updates'))
            }
            
            current_user.update_settings(settings_dict)
            db.session.commit()
            flash('Settings updated successfully')
            return redirect(url_for('settings'))

        return render_template('settings.html')
    except Exception as e:
        logging.error(f"Error in settings route: {str(e)}")
        flash('Error updating settings')
        return redirect(url_for('settings'))

@app.route('/export_dashboard_summary')
@login_required
def export_dashboard_summary():
    """Export dashboard summary statistics as Excel file."""
    try:
        # Get summary statistics
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Get detection counts
        today_detections = Detection.query.filter(
            Detection.user_id == current_user.id,
            db.func.date(Detection.timestamp) == today
        ).count()
        
        week_detections = Detection.query.filter(
            Detection.user_id == current_user.id,
            Detection.timestamp >= week_ago
        ).count()
        
        month_detections = Detection.query.filter(
            Detection.user_id == current_user.id,
            Detection.timestamp >= month_ago
        ).count()
        
        total_detections = Detection.query.filter_by(user_id=current_user.id).count()
        
        # Get ripeness statistics
        ripe_count = Detection.query.filter(
            Detection.user_id == current_user.id,
            Detection.ripeness == 'ripe'
        ).count()
        
        unripe_count = Detection.query.filter(
            Detection.user_id == current_user.id,
            Detection.ripeness == 'unripe'
        ).count()
        
        # Get average confidence
        avg_confidence = db.session.query(db.func.avg(Detection.confidence)).filter(
            Detection.user_id == current_user.id
        ).scalar() or 0
        
        # Prepare summary data
        summary_data = {
            'Total Detections': total_detections,
            'Today Detections': today_detections,
            'This Week Detections': week_detections,
            'This Month Detections': month_detections,
            'Ripe Mangosteen': ripe_count,
            'Unripe Mangosteen': unripe_count,
            'Average Confidence (%)': f'{avg_confidence * 100:.2f}%',
            'Account Created': current_user.created_at.strftime('%Y-%m-%d'),
            'Report Generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Use the Excel template to create the export
        output, filename = create_summary_export(summary_data, current_user)
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        logging.error(f"Error exporting dashboard summary: {str(e)}")
        flash('Error exporting dashboard summary: ' + str(e))
        return redirect(url_for('dashboard'))

# Add error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Create database tables
with app.app_context():
    db.create_all()
    # Create test user if it doesn't exist
    if not User.query.filter_by(username='test').first():
        test_user = User(username='test')
        test_user.set_password('test')
        db.session.add(test_user)
        db.session.commit()
        print("Test user created successfully")

if __name__ == '__main__':
    app.run(debug=True) 