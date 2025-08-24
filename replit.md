# Overview

Marseille Immobilier is a comprehensive multilingual real estate directory web application that serves as a centralized platform for real estate agencies in the Marseille region. The application provides a public-facing website showcasing real estate agencies alongside a complete admin panel for content management. It features zero-configuration deployment with automatic database initialization, sample data creation, and multi-language support across French, English, Italian, Spanish, and Portuguese.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 with Flask for server-side rendering
- **CSS Framework**: TailwindCSS for responsive design and utility-first styling
- **JavaScript**: Vanilla JavaScript for client-side interactions and admin panel functionality
- **Multi-language Support**: JSON-based translation system with dynamic language switching
- **Responsive Design**: Mobile-first approach with responsive grid layouts

## Backend Architecture
- **Web Framework**: Flask (Python) with Blueprint-based route organization
- **Application Structure**: Modular design separating public routes, admin routes, and utility functions
- **Authentication**: Flask-Login for session management with secure password hashing
- **Auto-initialization**: Zero-config deployment with automatic setup of database, admin user, and sample data
- **File Upload Handling**: Werkzeug for secure file uploads with image processing

## Data Storage
- **Database**: SQLite for simplicity and portability
- **ORM**: SQLAlchemy with declarative models
- **File Storage**: Local filesystem for uploaded images (logos and cover photos)
- **Database Models**: User (admin authentication), Agency (real estate listings), ContactMessage (form submissions), Translation (multilingual content)

## Authentication & Authorization
- **Admin Authentication**: Flask-Login with username/password authentication
- **Session Management**: Secure session handling with configurable secret keys
- **Default Credentials**: Auto-created admin user (admin/ChangeMe123!) for immediate access
- **Route Protection**: Login-required decorators for admin-only functionality

## Content Management
- **CRUD Operations**: Complete create, read, update, delete functionality for agencies
- **Image Management**: Logo and cover photo upload with file validation
- **Drag-and-Drop Ordering**: Sortable agency listings with custom ordering
- **Plan Management**: Basic and Premium agency tiers with visual differentiation

# External Dependencies

## Email Service Integration
- **SMTP Provider**: Gmail SMTP with TLS encryption for contact form submissions
- **Configuration**: Environment-based email credentials with fallback defaults
- **Email Templates**: HTML email formatting for contact form notifications

## CDN Dependencies
- **TailwindCSS**: CDN-delivered CSS framework for styling
- **Font Awesome**: Icon library for UI elements and navigation
- **External Assets**: SVG icons and placeholder images served from static directory

## Python Package Dependencies
- **Flask**: Core web framework
- **Flask-SQLAlchemy**: Database ORM integration
- **Flask-Login**: User session management
- **Flask-Mail**: Email functionality
- **Werkzeug**: HTTP utilities and file upload handling

## Deployment Considerations
- **Zero Configuration**: Automatic setup eliminates manual database configuration
- **Environment Variables**: Support for production environment overrides
- **Static File Serving**: Local file serving for development with production-ready structure
- **Database Portability**: SQLite database file for easy migration and backup