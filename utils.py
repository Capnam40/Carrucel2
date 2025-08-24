"""
Utility functions for the Marseille Immobilier application
"""

import os
import json
import uuid
from flask import current_app
from flask_mail import Message
from werkzeug.utils import secure_filename
# mail is imported at function level to avoid circular imports

def get_translation(key, language='fr'):
    """Get translation for a given key and language"""
    try:
        translations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'translations')
        translation_file = os.path.join(translations_dir, f'{language}.json')
        
        if os.path.exists(translation_file):
            with open(translation_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
                return translations.get(key, key)
        
        # Fallback to French if language file doesn't exist
        if language != 'fr':
            return get_translation(key, 'fr')
        
        return key
    except Exception as e:
        current_app.logger.error(f"Error loading translation {key} for {language}: {e}")
        return key

def get_available_languages():
    """Get list of available languages"""
    try:
        translations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'translations')
        languages = []
        
        for filename in os.listdir(translations_dir):
            if filename.endswith('.json'):
                lang_code = filename[:-5]  # Remove .json extension
                languages.append(lang_code)
        
        return sorted(languages)
    except Exception:
        return ['fr']  # Fallback to French only

def allowed_file(filename):
    """Check if uploaded file is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_video_file(filename):
    """Check if uploaded video file is allowed"""
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'ogg'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

def save_uploaded_file(file, subfolder):
    """Save uploaded file and return filename"""
    try:
        # Create upload directories if they don't exist
        upload_dir = current_app.config['UPLOAD_FOLDER']
        subfolder_path = os.path.join(upload_dir, subfolder)
        
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(subfolder_path, exist_ok=True)
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        
        # Save file
        file_path = os.path.join(subfolder_path, unique_filename)
        file.save(file_path)
        
        return unique_filename
    except Exception as e:
        current_app.logger.error(f"Error saving uploaded file: {e}")
        return None

def send_contact_email(name, email, phone, subject, message):
    """Send contact form email notification"""
    try:
        # Import mail here to avoid circular imports
        from app import mail
        
        # Skip email sending if not properly configured
        if (current_app.config['MAIL_USERNAME'] == 'your-email@gmail.com' or 
            current_app.config['MAIL_PASSWORD'] == 'your-app-password'):
            current_app.logger.info("Email not configured, skipping email send")
            return True
        
        msg = Message(
            subject=f"[Marseille Immobilier] {subject}",
            recipients=[current_app.config['MAIL_DEFAULT_SENDER']],
            reply_to=email
        )
        
        msg.body = f"""
Nouveau message de contact depuis Marseille Immobilier

Nom: {name}
Email: {email}
Téléphone: {phone or 'Non fourni'}
Sujet: {subject}

Message:
{message}

---
Ce message a été envoyé depuis le formulaire de contact de Marseille Immobilier.
        """
        
        mail.send(msg)
        current_app.logger.info(f"Contact email sent for {email}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Error sending contact email: {e}")
        return False

def get_file_url(filename, subfolder):
    """Get URL for uploaded file"""
    if not filename:
        return None
    return f"/uploads/{subfolder}/{filename}"

def create_directories():
    """Create required directories if they don't exist"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    directories = [
        os.path.join(base_dir, 'uploads'),
        os.path.join(base_dir, 'uploads', 'logos'),
        os.path.join(base_dir, 'uploads', 'covers'),
        os.path.join(base_dir, 'uploads', 'carousel'),
        os.path.join(base_dir, 'uploads', 'agencies'),
        os.path.join(base_dir, 'static', 'images'),
        os.path.join(base_dir, 'translations')
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        current_app.logger.debug(f"Created directory: {directory}")
