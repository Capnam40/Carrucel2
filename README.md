# Marseille Immobilier - Annuaire Immobilier

Une application web complète pour un annuaire d'agences immobilières avec interface multi-langues et panneau d'administration.

## ✨ Fonctionnalités

### Site Public
- 🏠 **Page d'accueil** avec liste des agences immobilières
- 🌍 **Interface multi-langues** (Français, Anglais, Italien, Espagnol, Portugais)
- 💰 **Section tarifs** avec plans Basic et Premium
- 📧 **Formulaire de contact** avec envoi par Gmail SMTP
- 📱 **Design responsive** avec TailwindCSS
- 🔍 **SEO optimisé** (robots.txt, sitemap.xml)

### Panneau d'Administration
- 🔐 **Connexion sécurisée** (admin/ChangeMe123!)
- ✏️ **CRUD complet** pour les agences (Créer, Lire, Modifier, Supprimer)
- 🖼️ **Upload d'images** (logo et image de couverture)
- 🔄 **Réorganisation** par glisser-déposer
- 📨 **Gestion des messages** de contact
- 📊 **Tableau de bord** avec statistiques

### Configuration Zéro
- 🚀 **Auto-initialisation** complète au premier démarrage
- 📦 **Base de données SQLite** créée automatiquement
- 👤 **Utilisateur admin** créé par défaut
- 🏢 **Données d'exemple** pré-chargées
- 📁 **Dossiers requis** créés automatiquement
- 🌐 **Traductions** générées automatiquement

## 🛠️ Technologies Utilisées

- **Backend:** Flask (Python)
- **Base de données:** SQLite3
- **Frontend:** HTML5, Jinja2, TailwindCSS
- **Authentification:** Flask-Login
- **Email:** Flask-Mail (Gmail SMTP)
- **Upload:** Werkzeug
- **Icons:** Font Awesome

## 🚀 Démarrage Rapide

### Installation Locale

1. **Cloner le projet**
   ```bash
   git clone <repository-url>
   cd marseille-immobilier
   ```

2. **Installer les dépendances**
   ```bash
   pip install flask flask-sqlalchemy flask-login flask-mail werkzeug
   