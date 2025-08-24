"""
Public routes for the Marseille Immobilier application
"""

import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, make_response, send_from_directory
from flask_mail import Message
from models import Agency, ContactMessage, Translation, CarouselSettings, CarouselItem
from app import db
from utils import get_translation, get_available_languages, send_contact_email

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage with agency listings"""
    language = session.get('language', 'fr')
    
    # Get active agencies ordered by plan (Premium first) then by sort_order
    from models import Plan
    agencies = Agency.query.join(Plan).filter(Agency.is_active == True).order_by(
        Plan.name.desc(),  # Premium before Basic (alphabetically desc)
        Agency.sort_order.asc()
    ).all()
    
    # Get all active plans for the pricing section  
    plans = Plan.query.filter_by(is_active=True).order_by(Plan.price.asc()).all()
    
    # Get carousel settings and items
    carousel_settings = CarouselSettings.query.first()
    carousel_items = []
    
    if carousel_settings and carousel_settings.is_active:
        carousel_items = CarouselItem.query.filter_by(is_active=True).order_by(
            CarouselItem.sort_order.asc()
        ).all()
    
    return render_template('index.html', 
                         agencies=agencies, 
                         plans=plans, 
                         language=language,
                         carousel_settings=carousel_settings,
                         carousel_items=carousel_items)

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact form page"""
    language = session.get('language', 'fr')
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        subject = request.form.get('subject', '').strip()
        message_text = request.form.get('message', '').strip()
        
        # Validate required fields
        if not all([name, email, subject, message_text]):
            flash(get_translation('contact_error_required', language), 'error')
            return render_template('contact.html', language=language)
        
        # Save message to database
        contact_message = ContactMessage()
        contact_message.name = name
        contact_message.email = email
        contact_message.phone = phone
        contact_message.subject = subject
        contact_message.message = message_text
        
        try:
            db.session.add(contact_message)
            db.session.commit()
            
            # Send email notification
            if send_contact_email(name, email, phone, subject, message_text):
                flash(get_translation('contact_success', language), 'success')
            else:
                flash(get_translation('contact_email_error', language), 'warning')
            
            return redirect(url_for('main.contact'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error saving contact message: {e}")
            flash(get_translation('contact_error_save', language), 'error')
    
    return render_template('contact.html', language=language)

@main_bp.route('/privacy')
def privacy():
    """Privacy policy page"""
    language = session.get('language', 'fr')
    return render_template('privacy.html', language=language)

@main_bp.route('/set-language/<language>')
def set_language(language):
    """Set user language preference"""
    available_languages = get_available_languages()
    if language in available_languages:
        session['language'] = language
    
    # Redirect back to referring page or home
    return redirect(request.referrer or url_for('main.index'))

@main_bp.route('/robots.txt')
def robots_txt():
    """Serve robots.txt for SEO"""
    content = """User-agent: *
Allow: /
Disallow: /admin/
Disallow: /uploads/

Sitemap: {}/sitemap.xml""".format(request.url_root.rstrip('/'))
    
    response = make_response(content)
    response.headers['Content-Type'] = 'text/plain'
    return response

@main_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@main_bp.route('/sitemap.xml')
def sitemap_xml():
    """Serve sitemap.xml for SEO"""
    base_url = request.url_root.rstrip('/')
    
    urls = [
        {'loc': base_url + '/', 'changefreq': 'daily', 'priority': '1.0'},
        {'loc': base_url + '/contact', 'changefreq': 'monthly', 'priority': '0.8'},
        {'loc': base_url + '/privacy', 'changefreq': 'yearly', 'priority': '0.3'},
    ]
    
    # Add agency pages if needed
    agencies = Agency.query.filter_by(is_active=True).all()
    for agency in agencies:
        if agency.website:
            urls.append({
                'loc': agency.website,
                'changefreq': 'monthly',
                'priority': '0.6'
            })
    
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url in urls:
        xml_content += '  <url>\n'
        xml_content += f'    <loc>{url["loc"]}</loc>\n'
        xml_content += f'    <changefreq>{url["changefreq"]}</changefreq>\n'
        xml_content += f'    <priority>{url["priority"]}</priority>\n'
        xml_content += '  </url>\n'
    
    xml_content += '</urlset>'
    
    response = make_response(xml_content)
    response.headers['Content-Type'] = 'application/xml'
    return response

# Template context processors
@main_bp.app_context_processor
def inject_globals():
    """Inject global variables into templates"""
    language = session.get('language', 'fr')
    return {
        'get_translation': get_translation,
        'current_language': language,
        'available_languages': get_available_languages()
    }
