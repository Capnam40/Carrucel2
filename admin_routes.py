"""
Admin routes for the Marseille Immobilier application
"""

import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from models import User, Agency, ContactMessage, Plan, CarouselSettings, CarouselItem, AgencyImage
from app import db
from utils import get_translation, allowed_file, save_uploaded_file

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    language = session.get('language', 'fr')
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash(get_translation('login_error_required', language), 'error')
            return render_template('admin/login.html', language=language)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin.dashboard'))
        else:
            flash(get_translation('login_error_invalid', language), 'error')
    
    return render_template('admin/login.html', language=language)

@admin_bp.route('/logout')
@login_required
def logout():
    """Admin logout"""
    logout_user()
    language = session.get('language', 'fr')
    flash(get_translation('logout_success', language), 'success')
    return redirect(url_for('main.index'))

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard"""
    language = session.get('language', 'fr')
    
    # Get statistics
    total_agencies = Agency.query.count()
    active_agencies = Agency.query.filter_by(is_active=True).count()
    total_messages = ContactMessage.query.count()
    unread_messages = ContactMessage.query.filter_by(is_read=False).count()
    
    # Get recent messages
    recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    
    stats = {
        'total_agencies': total_agencies,
        'active_agencies': active_agencies,
        'total_messages': total_messages,
        'unread_messages': unread_messages
    }
    
    return render_template('admin/dashboard.html', 
                         language=language, 
                         stats=stats, 
                         recent_messages=recent_messages)

@admin_bp.route('/agencies')
@login_required
def agencies():
    """List all agencies"""
    language = session.get('language', 'fr')
    agencies = Agency.query.order_by(Agency.sort_order.asc()).all()
    return render_template('admin/agencies.html', language=language, agencies=agencies)

@admin_bp.route('/agencies/add', methods=['GET', 'POST'])
@login_required
def add_agency():
    """Add new agency"""
    language = session.get('language', 'fr')
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        city = request.form.get('city', '').strip()
        website = request.form.get('website', '').strip()
        description = request.form.get('description', '').strip()
        plan_id = request.form.get('plan_id', type=int)
        
        if not all([name, city, website]):
            flash(get_translation('agency_error_required', language), 'error')
            return render_template('admin/agency_form.html', language=language)
        
        # Ensure website has protocol
        if not website.startswith(('http://', 'https://')):
            website = 'https://' + website
        
        # Handle file uploads
        logo_filename = None
        cover_filename = None
        
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file and logo_file.filename and allowed_file(logo_file.filename):
                logo_filename = save_uploaded_file(logo_file, 'logos')
        
        if 'cover' in request.files:
            cover_file = request.files['cover']
            if cover_file and cover_file.filename and allowed_file(cover_file.filename):
                cover_filename = save_uploaded_file(cover_file, 'covers')
        
        # Get next sort order
        max_order = db.session.query(db.func.max(Agency.sort_order)).scalar() or 0
        
        agency = Agency()
        agency.name = name
        agency.city = city
        agency.website = website
        agency.description = description
        agency.plan_id = plan_id
        agency.logo_filename = logo_filename
        agency.cover_filename = cover_filename
        agency.sort_order = max_order + 1
        
        try:
            db.session.add(agency)
            db.session.commit()
            flash(get_translation('agency_add_success', language), 'success')
            return redirect(url_for('admin.agencies'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding agency: {e}")
            flash(get_translation('agency_error_save', language), 'error')
    
    plans = Plan.query.filter_by(is_active=True).order_by(Plan.name).all()
    return render_template('admin/agency_form.html', language=language, agency=None, plans=plans)

@admin_bp.route('/agencies/edit/<int:agency_id>', methods=['GET', 'POST'])
@login_required
def edit_agency(agency_id):
    """Edit existing agency"""
    language = session.get('language', 'fr')
    agency = Agency.query.get_or_404(agency_id)
    
    if request.method == 'POST':
        agency.name = request.form.get('name', '').strip()
        agency.city = request.form.get('city', '').strip()
        agency.website = request.form.get('website', '').strip()
        agency.description = request.form.get('description', '').strip()
        agency.plan_id = request.form.get('plan_id', type=int)
        agency.is_active = 'is_active' in request.form
        
        if not all([agency.name, agency.city, agency.website]):
            flash(get_translation('agency_error_required', language), 'error')
            plans = Plan.query.filter_by(is_active=True).order_by(Plan.name).all()
            return render_template('admin/agency_form.html', language=language, agency=agency, plans=plans)
        
        # Ensure website has protocol
        if not agency.website.startswith(('http://', 'https://')):
            agency.website = 'https://' + agency.website
        
        # Handle file uploads
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file and logo_file.filename and allowed_file(logo_file.filename):
                # Delete old logo if exists
                if agency.logo_filename:
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'logos', agency.logo_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                agency.logo_filename = save_uploaded_file(logo_file, 'logos')
        
        if 'cover' in request.files:
            cover_file = request.files['cover']
            if cover_file and cover_file.filename and allowed_file(cover_file.filename):
                # Delete old cover if exists
                if agency.cover_filename:
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'covers', agency.cover_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                agency.cover_filename = save_uploaded_file(cover_file, 'covers')
        
        # Handle multiple gallery images
        if 'gallery_images' in request.files:
            gallery_files = request.files.getlist('gallery_images')
            for gallery_file in gallery_files:
                if gallery_file and gallery_file.filename and allowed_file(gallery_file.filename):
                    image_filename = save_uploaded_file(gallery_file, 'agencies')
                    if image_filename:
                        # Create AgencyImage record
                        agency_image = AgencyImage()
                        agency_image.agency_id = agency.id
                        agency_image.image_filename = image_filename
                        agency_image.alt_text = f"Imagen de {agency.name}"
                        agency_image.sort_order = len(agency.images)
                        db.session.add(agency_image)
        
        try:
            db.session.commit()
            flash(get_translation('agency_edit_success', language), 'success')
            return redirect(url_for('admin.agencies'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating agency: {e}")
            flash(get_translation('agency_error_save', language), 'error')
    
    plans = Plan.query.filter_by(is_active=True).order_by(Plan.name).all()
    return render_template('admin/agency_form.html', language=language, agency=agency, plans=plans)

@admin_bp.route('/agencies/delete/<int:agency_id>', methods=['POST'])
@login_required
def delete_agency(agency_id):
    """Delete agency"""
    language = session.get('language', 'fr')
    agency = Agency.query.get_or_404(agency_id)
    
    try:
        # Delete associated files
        if agency.logo_filename:
            logo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'logos', agency.logo_filename)
            if os.path.exists(logo_path):
                os.remove(logo_path)
        
        if agency.cover_filename:
            cover_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'covers', agency.cover_filename)
            if os.path.exists(cover_path):
                os.remove(cover_path)
        
        db.session.delete(agency)
        db.session.commit()
        flash(get_translation('agency_delete_success', language), 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting agency: {e}")
        flash(get_translation('agency_error_delete', language), 'error')
    
    return redirect(url_for('admin.agencies'))

@admin_bp.route('/agencies/reorder', methods=['POST'])
@login_required
def reorder_agencies():
    """Reorder agencies via AJAX"""
    try:
        agency_ids = request.get_json().get('agency_ids', [])
        
        for index, agency_id in enumerate(agency_ids):
            agency = Agency.query.get(agency_id)
            if agency:
                agency.sort_order = index
        
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error reordering agencies: {e}")
        return jsonify({'status': 'error'}), 500

@admin_bp.route('/messages')
@login_required
def messages():
    """View contact messages"""
    language = session.get('language', 'fr')
    page = request.args.get('page', 1, type=int)
    
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/messages.html', language=language, messages=messages)

@admin_bp.route('/messages/mark-read/<int:message_id>', methods=['POST'])
@login_required
def mark_message_read(message_id):
    """Mark message as read"""
    message = ContactMessage.query.get_or_404(message_id)
    message.is_read = True
    
    try:
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error marking message as read: {e}")
        return jsonify({'status': 'error'}), 500

# Carousel Management Routes
@admin_bp.route('/carousel')
@login_required
def carousel():
    """Manage carousel settings and items"""
    language = session.get('language', 'fr')
    
    # Get or create carousel settings
    settings = CarouselSettings.query.first()
    if not settings:
        settings = CarouselSettings()
        db.session.add(settings)
        db.session.commit()
    
    # Get carousel items ordered by sort_order
    items = CarouselItem.query.order_by(CarouselItem.sort_order.asc()).all()
    
    return render_template('admin/carousel.html', 
                         language=language, 
                         settings=settings, 
                         items=items)

@admin_bp.route('/carousel/settings', methods=['POST'])
@login_required
def update_carousel_settings():
    """Update carousel settings"""
    language = session.get('language', 'fr')
    
    # Get or create settings
    settings = CarouselSettings.query.first()
    if not settings:
        settings = CarouselSettings()
        db.session.add(settings)
    
    # Update settings
    settings.is_active = request.form.get('is_active') == 'on'
    settings.interval_seconds = int(request.form.get('interval_seconds', 5))
    settings.show_video = request.form.get('show_video') == 'on'
    
    # Handle video upload
    if 'video' in request.files:
        video_file = request.files['video']
        if video_file and video_file.filename:
            allowed_video_extensions = {'mp4', 'webm', 'ogg'}
            if '.' in video_file.filename and \
               video_file.filename.rsplit('.', 1)[1].lower() in allowed_video_extensions:
                # Delete old video if exists
                if settings.video_filename:
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'carousel', settings.video_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                settings.video_filename = save_uploaded_file(video_file, 'carousel')
    
    try:
        db.session.commit()
        flash('Configuración del carrusel actualizada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating carousel settings: {e}")
        flash('Error al actualizar la configuración', 'error')
    
    return redirect(url_for('admin.carousel'))

@admin_bp.route('/carousel/item/add', methods=['POST'])
@login_required
def add_carousel_item():
    """Add new carousel item"""
    language = session.get('language', 'fr')
    
    if 'image' not in request.files:
        flash('No se seleccionó ninguna imagen', 'error')
        return redirect(url_for('admin.carousel'))
    
    image_file = request.files['image']
    if not image_file or not image_file.filename:
        flash('No se seleccionó ninguna imagen', 'error')
        return redirect(url_for('admin.carousel'))
    
    if not allowed_file(image_file.filename):
        flash('Formato de imagen no permitido', 'error')
        return redirect(url_for('admin.carousel'))
    
    # Save image
    image_filename = save_uploaded_file(image_file, 'carousel')
    if not image_filename:
        flash('Error al guardar la imagen', 'error')
        return redirect(url_for('admin.carousel'))
    
    # Create carousel item
    item = CarouselItem()
    item.image_filename = image_filename
    item.link_url = request.form.get('link_url', '').strip()
    item.alt_text = request.form.get('alt_text', '').strip()
    item.sort_order = CarouselItem.query.count()
    
    try:
        db.session.add(item)
        db.session.commit()
        flash('Imagen agregada al carrusel exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding carousel item: {e}")
        flash('Error al agregar la imagen', 'error')
    
    return redirect(url_for('admin.carousel'))

@admin_bp.route('/carousel/item/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_carousel_item(item_id):
    """Delete carousel item"""
    item = CarouselItem.query.get_or_404(item_id)
    
    try:
        # Delete image file
        if item.image_filename:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'carousel', item.image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(item)
        db.session.commit()
        flash('Imagen eliminada del carrusel exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting carousel item: {e}")
        flash('Error al eliminar la imagen', 'error')
    
    return redirect(url_for('admin.carousel'))

@admin_bp.route('/carousel/item/toggle/<int:item_id>', methods=['POST'])
@login_required
def toggle_carousel_item(item_id):
    """Toggle carousel item active status"""
    item = CarouselItem.query.get_or_404(item_id)
    item.is_active = not item.is_active
    
    try:
        db.session.commit()
        status = 'activada' if item.is_active else 'desactivada'
        flash(f'Imagen {status} exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error toggling carousel item: {e}")
        flash('Error al cambiar el estado de la imagen', 'error')
    
    return redirect(url_for('admin.carousel'))

@admin_bp.route('/carousel/reorder', methods=['POST'])
@login_required
def reorder_carousel():
    """Reorder carousel items via AJAX"""
    try:
        item_ids = request.get_json().get('item_ids', [])
        
        for index, item_id in enumerate(item_ids):
            item = CarouselItem.query.get(item_id)
            if item:
                item.sort_order = index
        
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error reordering carousel items: {e}")
        return jsonify({'status': 'error'}), 500

# Agency Images Management Routes
@admin_bp.route('/agency/<int:agency_id>/images')
@login_required
def agency_images(agency_id):
    """Manage images for a specific agency"""
    language = session.get('language', 'fr')
    agency = Agency.query.get_or_404(agency_id)
    images = AgencyImage.query.filter_by(agency_id=agency_id).order_by(AgencyImage.sort_order.asc()).all()
    
    return render_template('admin/agency_images.html', 
                         language=language, 
                         agency=agency, 
                         images=images)

@admin_bp.route('/agency/<int:agency_id>/images/add', methods=['POST'])
@login_required
def add_agency_images(agency_id):
    """Add images to agency"""
    language = session.get('language', 'fr')
    agency = Agency.query.get_or_404(agency_id)
    
    if 'images' not in request.files:
        flash('No se seleccionaron imágenes', 'error')
        return redirect(url_for('admin.agency_images', agency_id=agency_id))
    
    images = request.files.getlist('images')
    added_count = 0
    
    for image_file in images:
        if image_file and image_file.filename and allowed_file(image_file.filename):
            image_filename = save_uploaded_file(image_file, 'agencies')
            if image_filename:
                agency_image = AgencyImage()
                agency_image.agency_id = agency_id
                agency_image.image_filename = image_filename
                agency_image.alt_text = request.form.get('alt_text', f'Imagen de {agency.name}')
                agency_image.sort_order = AgencyImage.query.filter_by(agency_id=agency_id).count()
                
                # Set as primary if it's the first image
                if not agency.images:
                    agency_image.is_primary = True
                
                db.session.add(agency_image)
                added_count += 1
    
    if added_count > 0:
        try:
            db.session.commit()
            flash(f'{added_count} imagen(es) agregada(s) exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding agency images: {e}")
            flash('Error al agregar las imágenes', 'error')
    else:
        flash('No se agregaron imágenes válidas', 'warning')
    
    return redirect(url_for('admin.agency_images', agency_id=agency_id))

@admin_bp.route('/agency/image/<int:image_id>/delete', methods=['POST'])
@login_required
def delete_agency_image(image_id):
    """Delete agency image"""
    image = AgencyImage.query.get_or_404(image_id)
    agency_id = image.agency_id
    
    try:
        # Delete image file
        if image.image_filename:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'agencies', image.image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(image)
        db.session.commit()
        flash('Imagen eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting agency image: {e}")
        flash('Error al eliminar la imagen', 'error')
    
    return redirect(url_for('admin.agency_images', agency_id=agency_id))

@admin_bp.route('/agency/image/<int:image_id>/set-primary', methods=['POST'])
@login_required
def set_primary_agency_image(image_id):
    """Set image as primary for agency"""
    image = AgencyImage.query.get_or_404(image_id)
    agency_id = image.agency_id
    
    try:
        # Remove primary status from all images of this agency
        AgencyImage.query.filter_by(agency_id=agency_id).update({'is_primary': False})
        
        # Set this image as primary
        image.is_primary = True
        db.session.commit()
        flash('Imagen principal actualizada', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error setting primary image: {e}")
        flash('Error al establecer imagen principal', 'error')
    
    return redirect(url_for('admin.agency_images', agency_id=agency_id))

@admin_bp.route('/agency/<int:agency_id>/images/reorder', methods=['POST'])
@login_required
def reorder_agency_images(agency_id):
    """Reorder agency images via AJAX"""
    try:
        image_ids = request.get_json().get('image_ids', [])
        
        for index, image_id in enumerate(image_ids):
            image = AgencyImage.query.get(image_id)
            if image and image.agency_id == agency_id:
                image.sort_order = index
        
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error reordering agency images: {e}")
        return jsonify({'status': 'error'}), 500

# Plans management routes
@admin_bp.route('/plans')
@login_required
def plans():
    """List all plans"""
    language = session.get('language', 'fr')
    plans = Plan.query.order_by(Plan.name.asc()).all()
    return render_template('admin/plans.html', language=language, plans=plans)

@admin_bp.route('/plans/add', methods=['GET', 'POST'])
@login_required
def add_plan():
    """Add new plan"""
    language = session.get('language', 'fr')
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price = request.form.get('price', type=float)
        billing_period = request.form.get('billing_period', 'monthly')
        description = request.form.get('description', '').strip()
        
        if not name or price is None:
            flash(get_translation('plan_error_required', language), 'error')
            return render_template('admin/plan_form.html', language=language)
        
        # Check if plan name already exists
        existing_plan = Plan.query.filter_by(name=name).first()
        if existing_plan:
            flash(get_translation('plan_error_exists', language), 'error')
            return render_template('admin/plan_form.html', language=language)
        
        plan = Plan()
        plan.name = name
        plan.price = price
        plan.billing_period = billing_period
        plan.description = description
        
        try:
            db.session.add(plan)
            db.session.commit()
            flash(get_translation('plan_add_success', language), 'success')
            return redirect(url_for('admin.plans'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding plan: {e}")
            flash(get_translation('plan_error_save', language), 'error')
    
    return render_template('admin/plan_form.html', language=language, plan=None)

@admin_bp.route('/plans/edit/<int:plan_id>', methods=['GET', 'POST'])
@login_required
def edit_plan(plan_id):
    """Edit existing plan"""
    language = session.get('language', 'fr')
    plan = Plan.query.get_or_404(plan_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price = request.form.get('price', type=float)
        billing_period = request.form.get('billing_period', 'monthly')
        description = request.form.get('description', '').strip()
        is_active = 'is_active' in request.form
        
        if not name or price is None:
            flash(get_translation('plan_error_required', language), 'error')
            return render_template('admin/plan_form.html', language=language, plan=plan)
        
        # Check if plan name already exists (excluding current plan)
        existing_plan = Plan.query.filter(Plan.name == name, Plan.id != plan_id).first()
        if existing_plan:
            flash(get_translation('plan_error_exists', language), 'error')
            return render_template('admin/plan_form.html', language=language, plan=plan)
        
        plan.name = name
        plan.price = price
        plan.billing_period = billing_period
        plan.description = description
        plan.is_active = is_active
        
        try:
            db.session.commit()
            flash(get_translation('plan_edit_success', language), 'success')
            return redirect(url_for('admin.plans'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating plan: {e}")
            flash(get_translation('plan_error_save', language), 'error')
    
    return render_template('admin/plan_form.html', language=language, plan=plan)

@admin_bp.route('/plans/delete/<int:plan_id>', methods=['POST'])
@login_required
def delete_plan(plan_id):
    """Delete plan"""
    language = session.get('language', 'fr')
    plan = Plan.query.get_or_404(plan_id)
    
    # Check if plan is used by any agencies
    agencies_count = Agency.query.filter_by(plan_id=plan_id).count()
    if agencies_count > 0:
        flash(get_translation('plan_error_in_use', language), 'error')
        return redirect(url_for('admin.plans'))
    
    try:
        db.session.delete(plan)
        db.session.commit()
        flash(get_translation('plan_delete_success', language), 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting plan: {e}")
        flash(get_translation('plan_error_delete', language), 'error')
    
    return redirect(url_for('admin.plans'))

# Template context processors for admin
@admin_bp.route('/password-change', methods=['GET', 'POST'])
@login_required
def password_change():
    """Change admin password."""
    from models import User
    from app import db
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not current_password or not new_password or not confirm_password:
            flash('Todos los campos son obligatorios', 'error')
            return render_template('admin/password_change.html')
        
        if len(new_password) < 6:
            flash('La nueva contraseña debe tener al menos 6 caracteres', 'error')
            return render_template('admin/password_change.html')
        
        if new_password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('admin/password_change.html')
        
        # Check current password
        if not check_password_hash(current_user.password_hash, current_password):
            flash('La contraseña actual es incorrecta', 'error')
            return render_template('admin/password_change.html')
        
        # Update password
        try:
            current_user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash('Contraseña actualizada exitosamente', 'success')
            return render_template('admin/password_change.html')
        except Exception as e:
            flash('Error al actualizar la contraseña', 'error')
            return render_template('admin/password_change.html')
    
    return render_template('admin/password_change.html')


@admin_bp.app_context_processor
def inject_admin_globals():
    """Inject admin-specific global variables into templates"""
    from utils import get_translation, get_available_languages
    language = session.get('language', 'fr')
    return {
        'get_translation': get_translation,
        'current_language': language,
        'available_languages': get_available_languages()
    }
