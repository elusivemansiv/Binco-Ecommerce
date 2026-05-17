# Project Documentation: Binco E-commerce Platform

## 1. Project Overview
**Binco E-commerce** is a robust, multi-vendor electronic commerce platform built with Django. It features a complete shopping experience, advanced vendor management, automated notifications, content management (CMS), and a modern, responsive user interface. The platform is designed to handle products with complex variations, detailed administrative reporting, and dynamic global configuration.

---

## 2. Core Features & Apps

### 🛍️ Store (Customer Features)
* **Dynamic Product Catalog:** Browse products by categories, search functionality, and advanced filtering.
* **Product Variations:** Select sizes and colors for products, with individual stock management.
* **Shopping Cart & Checkout:** Support for registered and anonymous users. Includes Coupon application.
* **Order Tracking & Invoices:** PDF Invoice generation and detailed order history.
* **Wishlist & Reviews:** Save favorites and review products.

### 👨‍💼 Accounts (User & Vendor Management)
* **Profiles:** Custom user profiles with distinct roles (Customer, Seller, Admin).
* **Seller Dashboard:** Front-end dashboard for sellers to view active orders and stats.

### ⚙️ Siteconfig (Global Settings)
* **Singleton Configuration:** Manage site identity (logo, name, socials), currency, SEO, and contact info without touching code.
* **Shipping & Payment:** Control delivery charges, thresholds, and gateway toggles.
* **Notification Settings:** Global toggle for Email and SMS providers.

### 🔔 Notifications (Event-Driven Alerts)
* **Multi-channel Delivery:** Framework to send In-App, Email, and SMS notifications.
* **Triggers:** Automated alerts for Order Placement, Order Status Changes, Seller New Order alerts, and Promotions.

### 📊 Reports (Analytics & Dashboard)
* **Advanced Admin Dashboard:** Custom high-fidelity UI replacing the default Django admin home.
* **Metrics:** Lifetime revenue, total orders, daily sales, active products tracing, and trending items.
* **Visualizations:** Chart.js integration for revenue trajectory.

### 📝 CMS (Content Management)
* **Dynamic Pages:** Generate static-style pages (About, Terms, Policy) from the DB.
* **Articles & Blog:** Publish rich-text articles with featured images.

---

## 3. Technical Architecture

### 🏗️ Technology Stack
* **Backend:** Python 3.10+, Django 5.x
* **Database:** PostgreSQL (Production), SQLite (Development)
* **Frontend:** HTML5, CSS3, Vanilla JS, Chart.js (Dashboard), FontAwesome.
* **PDF Engine:** xhtml2pdf for dynamic invoice rendering.

### 🗃️ Data Model Highlights
* **ProductVariation:** Independent stock tracking for Color/Size combos.
* **Order Lifecycle:** Auto-restores stock on cancellations/returns.
* **Singleton Model:** Base abstract model used in `siteconfig` to enforce 1-row DB configurations.

---

## 4. Local Development Setup

1. **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd Binco_Ecommerce/bincoecom
    ```
2. **Virtual Environment:**
    ```bash
    python -m venv .venv
    # Windows: .venv\Scripts\activate
    # Mac/Linux: source .venv/bin/activate
    ```
3. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4. **Database Migration & Superuser:**
    ```bash
    python manage.py migrate
    python manage.py createsuperuser
    ```
5. **Run Server:**
    ```bash
    python manage.py runserver
    ```

---

## 5. cPanel Deployment Guide

Deploying a Django application to cPanel using Phusion Passenger.

### Step 1: Prepare the Project
1. Open `bincoecom/settings.py`.
2. Set `DEBUG = False`.
3. Add your domain to ALLOWED_HOSTS: `ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']`.
4. Define your static and media roots properly for production (bottom of settings.py):
   ```python
   STATIC_URL = '/static/'
   STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
   
   MEDIA_URL = '/media/'
   MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
   ```
5. ZIP your project files **(exclude `.venv`, `__pycache__`, and `db.sqlite3` if moving to MySQL)**.

### Step 2: Database Setup in cPanel
1. Go to **MySQL® Databases** in cPanel.
2. Create a new Database (e.g., `cpuser_bincodb`).
3. Create a new User and generate a strong password.
4. Add the User to the Database with **All Privileges**.
5. Update your `settings.py` `DATABASES` dictionary with these credentials, or use a `.env` file (recommended). Ensure `psycopg2` or `mysqlclient` is in `requirements.txt`.

### Step 3: Upload Files
1. Open **File Manager** in cPanel.
2. Create a folder right in your home directory (not inside `public_html` for security), e.g., `binco_app`.
3. Upload and extract your ZIP file into `binco_app`.

### Step 4: Setup Python App
1. Go to **Setup Python App** (under Software in cPanel).
2. Click **Create Application**.
3. **Python version**: Select 3.10 or higher.
4. **Application root**: Enter the folder name (`binco_app/bincoecom` - matching where `manage.py` is).
5. **Application URL**: Your domain (e.g., `yourdomain.com`).
6. **Application startup file**: `passenger_wsgi.py`.
7. **Application Entry point**: `application`.
8. Click **Create**.

### Step 5: Configure Passenger WSGI
1. In the File Manager, inside your `binco_app/bincoecom` folder, cPanel created a file named `passenger_wsgi.py`. Edit it.
2. Replace all its contents with:
   ```python
   import os
   import sys
   from bincoecom.wsgi import application
   ```

### Step 6: Install Requirements & Migrate
1. Go back to **Setup Python App**.
2. Stop the App.
3. In the "Configuration files" section, enter `requirements.txt` and click **Add**, then click **Run Pip Install**.
4. To run migrations and collect static files, SSH into your server OR use the "Run command" section if cPanel provides it, or a terminal in cPanel:
   * Activate the virtual environment path shown at the top of the Setup Python App page.
   * `cd binco_app/bincoecom`
   * `python manage.py migrate`
   * `python manage.py collectstatic --noinput`
   * `python manage.py createsuperuser`

### Step 7: Final Media & Static Routing
If cPanel's Apache server is overriding Passenger for static/media routing:
1. Go to `public_html`.
2. Delete the automatically created folder if it conflicts, and create a symlink to your staticfiles and media folders.
   * Command via SSH: 
     `ln -s /home/yourcpaneluser/binco_app/bincoecom/staticfiles /home/yourcpaneluser/public_html/static`
     `ln -s /home/yourcpaneluser/binco_app/bincoecom/media /home/yourcpaneluser/public_html/media`

### Step 8: Restart App
Go back to **Setup Python App** and click **Restart**. Your Django site should now be live on your domain.
