"""
Auto-setup script for zero-configuration deployment
This module handles automatic initialization of the application
"""

import os
import json
import logging
from models import User, Agency, Translation, Plan
from app import db
from utils import create_directories

def initialize_application():
    """Initialize application with default data"""
    logger = logging.getLogger(__name__)
    logger.info("Starting application auto-setup...")
    
    try:
        # Create required directories
        create_directories()
        
        # Create database tables
        db.create_all()
        logger.info("Database tables created")
        
        # Create default admin user if none exists
        create_default_admin()
        
        # Create default plans if none exist
        create_default_plans()
        
        # Create sample agencies if none exist
        create_sample_agencies()
        
        # Initialize translations if none exist
        initialize_translations()
        
        logger.info("Application auto-setup completed successfully")
        
    except Exception as e:
        logger.error(f"Error during auto-setup: {e}")
        raise

def create_default_admin():
    """Create default admin user"""
    logger = logging.getLogger(__name__)
    
    # Check if admin user already exists
    admin_user = User.query.filter_by(username='admin').first()
    
    if not admin_user:
        admin_user = User()
        admin_user.username = 'admin'
        admin_user.email = 'admin@marseilleimmobilier.com'
        admin_user.set_password('ChangeMe123!')
        
        db.session.add(admin_user)
        db.session.commit()
        
        logger.info("Default admin user created (admin/ChangeMe123!)")
    else:
        logger.info("Admin user already exists")

def create_default_plans():
    """Create default subscription plans if none exist"""
    logger = logging.getLogger(__name__)
    
    # Check if plans already exist
    plan_count = Plan.query.count()
    
    if plan_count == 0:
        default_plans = [
            {
                'name': 'Basic',
                'price': 9.0,
                'billing_period': 'monthly',
                'description': 'Fiche agence standard\nLien vers votre site\nSupport email'
            },
            {
                'name': 'Premium',
                'price': 19.0,
                'billing_period': 'monthly',
                'description': 'Fiche agence mise en avant\nLogo et images personnalisés\nSupport prioritaire\nStatistiques de visite'
            }
        ]
        
        for plan_data in default_plans:
            plan = Plan()
            plan.name = plan_data['name']
            plan.price = plan_data['price']
            plan.billing_period = plan_data['billing_period']
            plan.description = plan_data['description']
            db.session.add(plan)
        
        db.session.commit()
        logger.info(f"Created {len(default_plans)} default plans")
    else:
        logger.info(f"Plans already exist ({plan_count} found)")

def create_sample_agencies():
    """Create sample agencies if none exist"""
    logger = logging.getLogger(__name__)
    
    # Check if agencies already exist
    agency_count = Agency.query.count()
    
    if agency_count == 0:
        # Get plans for assignment
        basic_plan = Plan.query.filter_by(name='Basic').first()
        premium_plan = Plan.query.filter_by(name='Premium').first()
        
        sample_agencies = [
            {
                'name': 'Immobilier Marseille Centre',
                'city': 'Marseille',
                'website': 'https://example-agency1.com',
                'description': 'Spécialiste de l\'immobilier dans le centre de Marseille',
                'plan_id': premium_plan.id if premium_plan else None,
                'sort_order': 1
            },
            {
                'name': 'Agence du Vieux Port',
                'city': 'Marseille',
                'website': 'https://example-agency2.com',
                'description': 'Votre partenaire immobilier près du Vieux Port',
                'plan_id': basic_plan.id if basic_plan else None,
                'sort_order': 2
            },
            {
                'name': 'Provence Immobilier',
                'city': 'Aix-en-Provence',
                'website': 'https://example-agency3.com',
                'description': 'Immobilier de prestige en Provence',
                'plan_id': premium_plan.id if premium_plan else None,
                'sort_order': 3
            },
            {
                'name': 'Côte Bleue Immobilier',
                'city': 'Martigues',
                'website': 'https://example-agency4.com',
                'description': 'Spécialiste de la Côte Bleue',
                'plan_id': basic_plan.id if basic_plan else None,
                'sort_order': 4
            }
        ]
        
        for agency_data in sample_agencies:
            agency = Agency()
            agency.name = agency_data['name']
            agency.city = agency_data['city']
            agency.website = agency_data['website']
            agency.description = agency_data['description']
            agency.plan_id = agency_data['plan_id']
            agency.sort_order = agency_data['sort_order']
            db.session.add(agency)
        
        db.session.commit()
        logger.info(f"Created {len(sample_agencies)} sample agencies")
    else:
        logger.info(f"Agencies already exist ({agency_count} found)")

def initialize_translations():
    """Initialize translation files if they don't exist"""
    logger = logging.getLogger(__name__)
    
    translations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'translations')
    os.makedirs(translations_dir, exist_ok=True)
    
    # Define translations for all languages
    translations = {
        'fr': {
            # Navigation
            'nav_home': 'Accueil',
            'nav_contact': 'Contact',
            'nav_admin': 'Administration',
            'nav_language': 'Langue',
            
            # Homepage
            'site_title': 'Marseille Immobilier',
            'site_subtitle': 'Tous les portails en un seul endroit - Annuaire Immobilier',
            'hero_title': 'Trouvez votre agence immobilière à Marseille',
            'hero_subtitle': 'Découvrez les meilleures agences immobilières de la région marseillaise',
            'agencies_title': 'Nos Agences Partenaires',
            'agency_visit': 'Visiter le site',
            'pricing_title': 'Nos Tarifs',
            'pricing_subtitle': 'Choisissez le plan qui vous convient',
            'plan_basic': 'Basic',
            'plan_premium': 'Premium',
            'plan_basic_price': '99€/an',
            'plan_premium_price': '199€/an',
            'plan_basic_features': 'Fiche agence standard\nLien vers votre site\nSupport email',
            'plan_premium_features': 'Fiche agence mise en avant\nLogo et images personnalisés\nSupport prioritaire\nStatistiques de visite',
            'plan_contact': 'Nous contacter',
            
            # Contact
            'contact_title': 'Contactez-nous',
            'contact_subtitle': 'Une question ? Un projet ? N\'hésitez pas à nous écrire',
            'contact_name': 'Nom complet',
            'contact_email': 'Email',
            'contact_phone': 'Téléphone',
            'contact_subject': 'Sujet',
            'contact_message': 'Message',
            'contact_send': 'Envoyer',
            'contact_success': 'Votre message a été envoyé avec succès !',
            'contact_error_required': 'Veuillez remplir tous les champs obligatoires.',
            'contact_error_save': 'Erreur lors de l\'enregistrement du message.',
            'contact_email_error': 'Message enregistré mais erreur lors de l\'envoi de l\'email.',
            
            # Admin
            'admin_login': 'Connexion Admin',
            'admin_username': 'Nom d\'utilisateur',
            'admin_password': 'Mot de passe',
            'admin_login_btn': 'Se connecter',
            'admin_dashboard': 'Tableau de bord',
            'admin_agencies': 'Agences',
            'admin_messages': 'Messages',
            'admin_logout': 'Déconnexion',
            'login_error_required': 'Nom d\'utilisateur et mot de passe requis.',
            'login_error_invalid': 'Identifiants invalides.',
            'logout_success': 'Déconnexion réussie.',
            
            # Agencies management
            'agencies_add': 'Ajouter une agence',
            'agencies_edit': 'Modifier',
            'agencies_delete': 'Supprimer',
            'agency_name': 'Nom de l\'agence',
            'agency_city': 'Ville',
            'agency_website': 'Site web',
            'agency_description': 'Description',
            'agency_logo': 'Logo',
            'agency_cover': 'Image de couverture',
            'agency_plan': 'Plan',
            'agency_active': 'Agence active',
            'agency_save': 'Enregistrer',
            'agency_cancel': 'Annuler',
            'agency_add_success': 'Agence ajoutée avec succès.',
            'agency_edit_success': 'Agence modifiée avec succès.',
            'agency_delete_success': 'Agence supprimée avec succès.',
            'agency_error_required': 'Nom, ville et site web sont obligatoires.',
            'agency_error_save': 'Erreur lors de l\'enregistrement.',
            'agency_error_delete': 'Erreur lors de la suppression.',
            
            # Footer
            'footer_privacy': 'Politique de confidentialité',
            'footer_copyright': '© 2024 Marseille Immobilier. Tous droits réservés.',
            
            # Privacy
            'privacy_title': 'Politique de confidentialité',
            'privacy_content': 'Cette page décrit notre politique de confidentialité...'
        },
        'en': {
            # Navigation
            'nav_home': 'Home',
            'nav_contact': 'Contact',
            'nav_admin': 'Admin',
            'nav_language': 'Language',
            
            # Homepage
            'site_title': 'Marseille Real Estate',
            'site_subtitle': 'All portals in one place - Real Estate Directory',
            'hero_title': 'Find your real estate agency in Marseille',
            'hero_subtitle': 'Discover the best real estate agencies in the Marseille region',
            'agencies_title': 'Our Partner Agencies',
            'agency_visit': 'Visit website',
            'pricing_title': 'Our Pricing',
            'pricing_subtitle': 'Choose the plan that suits you',
            'plan_basic': 'Basic',
            'plan_premium': 'Premium',
            'plan_basic_price': '€99/year',
            'plan_premium_price': '€199/year',
            'plan_basic_features': 'Standard agency listing\nLink to your website\nEmail support',
            'plan_premium_features': 'Featured agency listing\nCustom logo and images\nPriority support\nVisit statistics',
            'plan_contact': 'Contact us',
            
            # Contact
            'contact_title': 'Contact us',
            'contact_subtitle': 'A question? A project? Don\'t hesitate to write to us',
            'contact_name': 'Full name',
            'contact_email': 'Email',
            'contact_phone': 'Phone',
            'contact_subject': 'Subject',
            'contact_message': 'Message',
            'contact_send': 'Send',
            'contact_success': 'Your message has been sent successfully!',
            'contact_error_required': 'Please fill in all required fields.',
            'contact_error_save': 'Error saving the message.',
            'contact_email_error': 'Message saved but error sending email.',
            
            # Admin
            'admin_login': 'Admin Login',
            'admin_username': 'Username',
            'admin_password': 'Password',
            'admin_login_btn': 'Login',
            'admin_dashboard': 'Dashboard',
            'admin_agencies': 'Agencies',
            'admin_messages': 'Messages',
            'admin_logout': 'Logout',
            'login_error_required': 'Username and password required.',
            'login_error_invalid': 'Invalid credentials.',
            'logout_success': 'Successfully logged out.',
            
            # Agencies management
            'agencies_add': 'Add agency',
            'agencies_edit': 'Edit',
            'agencies_delete': 'Delete',
            'agency_name': 'Agency name',
            'agency_city': 'City',
            'agency_website': 'Website',
            'agency_description': 'Description',
            'agency_logo': 'Logo',
            'agency_cover': 'Cover image',
            'agency_plan': 'Plan',
            'agency_active': 'Active agency',
            'agency_save': 'Save',
            'agency_cancel': 'Cancel',
            'agency_add_success': 'Agency added successfully.',
            'agency_edit_success': 'Agency updated successfully.',
            'agency_delete_success': 'Agency deleted successfully.',
            'agency_error_required': 'Name, city and website are required.',
            'agency_error_save': 'Error saving the agency.',
            'agency_error_delete': 'Error deleting the agency.',
            
            # Footer
            'footer_privacy': 'Privacy Policy',
            'footer_copyright': '© 2024 Marseille Real Estate. All rights reserved.',
            
            # Privacy
            'privacy_title': 'Privacy Policy',
            'privacy_content': 'This page describes our privacy policy...'
        },
        'it': {
            # Navigation
            'nav_home': 'Home',
            'nav_contact': 'Contatto',
            'nav_admin': 'Admin',
            'nav_language': 'Lingua',
            
            # Homepage
            'site_title': 'Immobiliare Marsiglia',
            'site_subtitle': 'Tutti i portali in un unico posto - Elenco Immobiliare',
            'hero_title': 'Trova la tua agenzia immobiliare a Marsiglia',
            'hero_subtitle': 'Scopri le migliori agenzie immobiliari della regione di Marsiglia',
            'agencies_title': 'Le Nostre Agenzie Partner',
            'agency_visit': 'Visita il sito',
            'pricing_title': 'I Nostri Prezzi',
            'pricing_subtitle': 'Scegli il piano che fa per te',
            'plan_basic': 'Basic',
            'plan_premium': 'Premium',
            'plan_basic_price': '99€/anno',
            'plan_premium_price': '199€/anno',
            'plan_basic_features': 'Scheda agenzia standard\nLink al tuo sito\nSupporto email',
            'plan_premium_features': 'Scheda agenzia in evidenza\nLogo e immagini personalizzate\nSupporto prioritario\nStatistiche visite',
            'plan_contact': 'Contattaci',
            
            # Contact
            'contact_title': 'Contattaci',
            'contact_subtitle': 'Una domanda? Un progetto? Non esitare a scriverci',
            'contact_name': 'Nome completo',
            'contact_email': 'Email',
            'contact_phone': 'Telefono',
            'contact_subject': 'Oggetto',
            'contact_message': 'Messaggio',
            'contact_send': 'Invia',
            'contact_success': 'Il tuo messaggio è stato inviato con successo!',
            'contact_error_required': 'Compila tutti i campi obbligatori.',
            'contact_error_save': 'Errore nel salvare il messaggio.',
            'contact_email_error': 'Messaggio salvato ma errore nell\'invio email.',
            
            # Footer
            'footer_privacy': 'Politica Privacy',
            'footer_copyright': '© 2024 Immobiliare Marsiglia. Tutti i diritti riservati.',
            
            # Privacy
            'privacy_title': 'Politica sulla Privacy',
            'privacy_content': 'Questa pagina descrive la nostra politica sulla privacy...'
        },
        'es': {
            # Navigation
            'nav_home': 'Inicio',
            'nav_contact': 'Contacto',
            'nav_admin': 'Admin',
            'nav_language': 'Idioma',
            
            # Homepage
            'site_title': 'Inmobiliaria Marsella',
            'site_subtitle': 'Todos los portales en un solo lugar - Directorio Inmobiliario',
            'hero_title': 'Encuentra tu agencia inmobiliaria en Marsella',
            'hero_subtitle': 'Descubre las mejores agencias inmobiliarias de la región de Marsella',
            'agencies_title': 'Nuestras Agencias Asociadas',
            'agency_visit': 'Visitar sitio',
            'pricing_title': 'Nuestros Precios',
            'pricing_subtitle': 'Elige el plan que más te convenga',
            'plan_basic': 'Básico',
            'plan_premium': 'Premium',
            'plan_basic_price': '99€/año',
            'plan_premium_price': '199€/año',
            'plan_basic_features': 'Ficha de agencia estándar\nEnlace a tu sitio web\nSoporte por email',
            'plan_premium_features': 'Ficha de agencia destacada\nLogo e imágenes personalizadas\nSoporte prioritario\nEstadísticas de visitas',
            'plan_contact': 'Contáctanos',
            
            # Contact
            'contact_title': 'Contáctanos',
            'contact_subtitle': '¿Una pregunta? ¿Un proyecto? No dudes en escribirnos',
            'contact_name': 'Nombre completo',
            'contact_email': 'Email',
            'contact_phone': 'Teléfono',
            'contact_subject': 'Asunto',
            'contact_message': 'Mensaje',
            'contact_send': 'Enviar',
            'contact_success': '¡Tu mensaje ha sido enviado con éxito!',
            'contact_error_required': 'Por favor completa todos los campos obligatorios.',
            'contact_error_save': 'Error al guardar el mensaje.',
            'contact_email_error': 'Mensaje guardado pero error al enviar email.',
            
            # Footer
            'footer_privacy': 'Política de Privacidad',
            'footer_copyright': '© 2024 Inmobiliaria Marsella. Todos los derechos reservados.',
            
            # Privacy
            'privacy_title': 'Política de Privacidad',
            'privacy_content': 'Esta página describe nuestra política de privacidad...'
        },
        'pt': {
            # Navigation
            'nav_home': 'Início',
            'nav_contact': 'Contato',
            'nav_admin': 'Admin',
            'nav_language': 'Idioma',
            
            # Homepage
            'site_title': 'Imobiliária Marselha',
            'site_subtitle': 'Todos os portais em um só lugar - Diretório Imobiliário',
            'hero_title': 'Encontre sua agência imobiliária em Marselha',
            'hero_subtitle': 'Descubra as melhores agências imobiliárias da região de Marselha',
            'agencies_title': 'Nossas Agências Parceiras',
            'agency_visit': 'Visitar site',
            'pricing_title': 'Nossos Preços',
            'pricing_subtitle': 'Escolha o plano que mais te convém',
            'plan_basic': 'Básico',
            'plan_premium': 'Premium',
            'plan_basic_price': '99€/ano',
            'plan_premium_price': '199€/ano',
            'plan_basic_features': 'Ficha de agência padrão\nLink para seu site\nSuporte por email',
            'plan_premium_features': 'Ficha de agência destacada\nLogo e imagens personalizadas\nSuporte prioritário\nEstatísticas de visitas',
            'plan_contact': 'Entre em contato',
            
            # Contact
            'contact_title': 'Entre em contato',
            'contact_subtitle': 'Uma pergunta? Um projeto? Não hesite em nos escrever',
            'contact_name': 'Nome completo',
            'contact_email': 'Email',
            'contact_phone': 'Telefone',
            'contact_subject': 'Assunto',
            'contact_message': 'Mensagem',
            'contact_send': 'Enviar',
            'contact_success': 'Sua mensagem foi enviada com sucesso!',
            'contact_error_required': 'Por favor preencha todos os campos obrigatórios.',
            'contact_error_save': 'Erro ao salvar a mensagem.',
            'contact_email_error': 'Mensagem salva mas erro ao enviar email.',
            
            # Footer
            'footer_privacy': 'Política de Privacidade',
            'footer_copyright': '© 2024 Imobiliária Marselha. Todos os direitos reservados.',
            
            # Privacy
            'privacy_title': 'Política de Privacidade',
            'privacy_content': 'Esta página descreve nossa política de privacidade...'
        }
    }
    
    for lang_code, lang_translations in translations.items():
        translation_file = os.path.join(translations_dir, f'{lang_code}.json')
        
        if not os.path.exists(translation_file):
            with open(translation_file, 'w', encoding='utf-8') as f:
                json.dump(lang_translations, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Created translation file: {lang_code}.json")
        else:
            logger.info(f"Translation file already exists: {lang_code}.json")
