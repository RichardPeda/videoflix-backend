# 🎬 Movie API – Django Backend

A RESTful API backend for a video streaming platform with features like user registration, email verification, video conversion, and playback tracking.

---

## ⚙️ Technologies Used

- **Python**, **Django**, **Django REST Framework**
- **drf-spectacular** for OpenAPI (Swagger) documentation
- **FFmpeg** for video processing
- **Celery + Redis** for asynchronous email tasks and video convert
- **TokenAuthentication** for secured endpoints

---

### Requirements
You have to install the latest Python version on your computer.
[Download Python](https://www.python.org/downloads/)

## 🔧 Installation

 1. Clone this repository
 2. Create a virtual environment `python -m venv env`
 3. Activate the virtual environment `"env/Scripts/activate"`
 4. then you can run
    
 ```
 pip install -r requirements.txt
```
 3. Go to the folder "Videoflix_backend"
 4. Generate the database with command `python manage.py migrate`
 5. Run the command `python manage.py createsuperuser` to have access to the admin page
 6. Run the command `python manage.py runserver` to start the app on your machine

## Documentation
The documentation of the endpoints was made with SwaggerUi.
With your local server running, you can find it at the endpoint: [/api/docs/](http://127.0.0.1:8000/api/docs/)

## 🚀 API Endpoints Overview

### 🔐 Authentication & User Management

| Method | Endpoint                       | Description                                                  |
|--------|--------------------------------|--------------------------------------------------------------|
| POST   | `/login_or_signup/`            | Checks if a user exists by email (login/signup flow)         |
| POST   | `/register/`                   | Registers a new user and sends a verification email          |
| POST   | `/verify/`                     | Verifies a user's email using a code                         |
| POST   | `/password_reset/inquiry/`     | Sends a password reset email (if account exists)             |
| POST   | `/password_reset/`             | Resets the password using a reset code                       |

---

### 🎞️ Movies & Convertables

| Method | Endpoint                        | Description                                                       |
|--------|----------------------------------|-------------------------------------------------------------------|
| GET    | `/movies/`                       | Returns a list of all movies (ordered by creation date)           |
| GET    | `/convertables/`                 | Returns all uploaded videos converted via FFmpeg                  |
| GET    | `/convertables/<id>/`            | Returns a specific converted video's details                      |
| GET    | `/connection_test/`              | Returns a test file to verify media/connection functionality      |

> ⚙️ Each "convertable" video is processed into 120p, 360p, 720p, and 1080p versions via FFmpeg.

---

### ▶️ Movie Watch Progress

| Method | Endpoint                                | Description                                                     |
|--------|------------------------------------------|-----------------------------------------------------------------|
| GET    | `/progress/`                             | Returns all progress entries for the authenticated user         |
| GET    | `/progress/<movie_id>/`                  | Returns progress for a specific movie                           |
| POST   | `/progress/<movie_id>/`                  | Creates or updates the user's progress for the specified movie  |

---

## 📚 API Documentation (Swagger UI)

Interactive API documentation is available at:

- **Swagger UI**: [`/api/docs/`](http://localhost:8000/api/docs/)
- **OpenAPI schema (JSON)**: [`/api/schema/`](http://localhost:8000/api/schema/)

---

# Videoflix API
 This is the API of Videoflix App written with Django 5.1.
 
 You can download the corresponding frontend app of Videoflix
 [Videoflix-Frontend-App](https://github.com/RichardPeda/videoflix-frontend)