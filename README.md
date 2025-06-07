# 🎬 Movie API – Django Backend

A RESTful API backend for a video streaming platform with features like user registration, email verification, video conversion, and playback tracking.

---

## ⚙️ Technologies Used

- **Python**, **Django**, **Django REST Framework**
- **drf-spectacular** for OpenAPI (Swagger) documentation
- **ffmpeg** for video processing
- **Celery + Redis** for asynchronous email tasks and video conversion
- **TokenAuthentication** for secured endpoints

---

## Deployment with Docker
If you prefer to run the project using Docker instead of a local virtual environment, follow the steps below:

### Prerequisites
 - Install [Git](https://git-scm.com/)
 - Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
 - Install [Redis](https://redis.io/)

### 🔧 Setup Instructions
1. Clone this repository
2. Use the `template.env` file in the root of the project and change it´s name to `.env`.
   Or use following command to create the `.env` file.

```bash
cp .env.template .env
```

#### `.env`

This are default values used in settings.py. For your application, the values should be changed to your needs.

- The database creates automatically a superuser with default name and password
- Check the url of your allowed hosts
- Change the database name and password for your needs
- **Please check your login data of your email provider and whether tls and ssl are used** 


```bash
# Superuser settings:
DJANGO_SUPERUSER_USERNAME=admin           # default superuser name
DJANGO_SUPERUSER_PASSWORD=adminpassword   # default superuser password
DJANGO_SUPERUSER_EMAIL=admin@example.com  # default superuser email

# host settings:
ALLOWED_HOSTS=localhost,127.0.0.1         # customize for your frontend application
CSRF_TRUSTED_ORIGINS=http://localhost:4200,http://127.0.0.1:4200 # customize for your frontend application

# database settings:
DB_NAME=your_database_name,               # default database name
DB_USER=your_database_user,               # default database user
DB_PASSWORD=your_database_password,       # default database password
DB_HOST=db,          
DB_PORT=5432
FRONTEND_BASEURL="http://localhost:4200/" # customize this url. If an registration email
                                          # has been sent, this url will be referenced

# redis settings:
REDIS_HOST=redis
REDIS_LOCATION=redis://redis:6379/1
REDIS_PORT=6379                           # customize when you use different port
REDIS_DB=0

# email settings:
EMAIL_HOST=smtp.example.com                  # customize to your host url
EMAIL_PORT=587                               # customize to your email port
EMAIL_HOST_USER=your_email_user              # customize to your email user
EMAIL_HOST_PASSWORD=your_email_user_password # customize to your email password
EMAIL_USE_TLS=True                           # check, if TLS is used
EMAIL_USE_SSL=False                          # check, if SSL is used
DEFAULT_FROM_EMAIL=default_from_email        # customize to your email

# celery settings:
CELERY_BROKER_URL='redis://redis:6379/0'
CELERY_RESULT_BACKEND= 'django-db'
```



3. Build and start the project using `docker-compose`.

```bash
docker-compose up --build
```

This will automatically launch the following services from the Dockerfile:

- Installs the PostgreSQL client tool (psql) to establish database connections
- Installs temporary build dependencies to compile Python bindings and packages
- Installs ffmpeg, which is required for video processing
- Installs all dependencies for the django project from the requirements.txt
- Defines the entrypoint for the container

### Entrypoint.sh
The script checks in a loop whether PostgreSQL is accessible.
After that it runs important django commands:

- collectstatic: Copies additional files in the project folder
- makemigrations: Migrates the database
- migrate: Applies all migrations (sets the DB to the current status)

- Reads environment variables (such as DJANGO_SUPERUSER_USERNAME) and automatically creates an admin user if it does not already exist.
- Starts the Celery Worker, which processes background jobs (e-mails, video conversion).
- Starts the Django app with Gunicorn, a production-grade Python web server, accessible at port 8000.

When the docker container is ready, the django app should be accessible under the following url: http://localhost:8000

Admin Panel: http://localhost:8000/admin/

Swagger API Docs: http://localhost:8000/api/docs/

#### 🧹 Stop Containers
To stop all running containers:

```bash
docker-compose down
```

To stop and remove all volumes:  
❗**Warning: This command also removes the PostgreSQL database** ❗

```bash
docker-compose down -v
```
---

## Documentation
The documentation of the endpoints was made with SwaggerUi.
Once your local server is running, you can find it at the endpoint: [/api/docs/](http://127.0.0.1:8000/api/docs/)

---

## 👩‍💻 Admin Functionality

Once logged into the [Django admin panel](http://localhost:8000/admin/), administrators can:

- Manage users and verification codes
- Upload original video files
> Trigger automated video conversion (120p, 360p, 720p, 1080p)  
> Videos are processed via ffmpeg after upload and made available in multiple resolutions.  
> Thumbnail image is processed via ffmpeg after upload.  
> Determines the duration of an uploaded video.

---

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
| GET    | `/convertables/`                 | Returns all uploaded videos converted via ffmpeg                  |
| GET    | `/convertables/<id>/`            | Returns a specific converted video's details                      |
| GET    | `/connection_test/`              | Returns a test file to verify media/connection functionality      |

> ⚙️ Each "convertable" video is processed into 120p, 360p, 720p, and 1080p versions via ffmpeg.

---

### ▶️ Movie Watch Progress

| Method | Endpoint                                | Description                                                     |
|--------|------------------------------------------|-----------------------------------------------------------------|
| GET    | `/progress/`                             | Returns all progress entries for the authenticated user         |
| GET    | `/progress/<movie_id>/`                  | Returns progress for a specific movie                           |
| POST   | `/progress/<movie_id>/`                  | Creates or updates the user's progress for the specified movie  |


---

## Videoflix Frontend
  
 You can find the corresponding frontend application here:
 [Videoflix-Frontend-App](https://github.com/RichardPeda/videoflix-frontend)

---

## 📚 API Documentation (Swagger UI)

Interactive API documentation is available at:

- **Swagger UI**: [`/api/docs/`](http://localhost:8000/api/docs/)
- **OpenAPI schema (JSON)**: [`/api/schema/`](http://localhost:8000/api/schema/)

---

