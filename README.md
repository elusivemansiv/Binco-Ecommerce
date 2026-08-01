# Binco Ecommerce

Binco Ecommerce is a comprehensive full-stack e-commerce platform. It features a robust backend built with Django and a modern cross-platform mobile application built with Flutter.

## Project Structure

The repository is divided into two main components:

- **Backend** (`/backend`): A RESTful API built with Django and Django REST Framework.
- **Mobile** (`/mobile`): A mobile application built with Flutter.

## Technologies Used

### Backend
- **Framework**: Django (>=4.2) & Django REST Framework
- **Database**: PostgreSQL (psycopg2)
- **Asynchronous Tasks**: Celery & Redis
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Deployment**: Gunicorn & Whitenoise

### Mobile
- **Framework**: Flutter (SDK ^3.11.5)
- **State Management**: Provider
- **Networking**: HTTP
- **Local Storage**: Shared Preferences

## Developer

Developed by **Mansib ahsan**

## Getting Started

### Backend Setup
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment.
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run database migrations:
   ```bash
   python manage.py migrate
   ```
5. Start the development server:
   ```bash
   python manage.py runserver
   ```

### Mobile Setup
1. Navigate to the `mobile` directory:
   ```bash
   cd mobile
   ```
2. Get the Flutter dependencies:
   ```bash
   flutter pub get
   ```
3. Run the application:
   ```bash
   flutter run
   ```
