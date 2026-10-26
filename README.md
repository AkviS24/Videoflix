
# Videoflix

## Project Setup

Videoflix is a video streaming application with a Django REST Framework backend and a separate frontend.

### Repository

- **Backend:** [Videoflix Backend](https://github.com/AkviS24/Videoflix)
- **Original Frontend Repository:** [Developer Akademie – Videoflix](https://github.com/Developer-Akademie-Backendkurs/project.Videoflix)

The frontend is maintained separately from the backend repository.

### Prerequisites

Make sure the following tools are installed:

- [Git](https://git-scm.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with Docker Compose
- [Visual Studio Code](https://code.visualstudio.com/) or another editor
- An SMTP account and the corresponding credentials, if you want to use email delivery

### 1. Clone the backend

Clone the repository and open the project directory:

```bash
git clone https://github.com/AkviS24/Videoflix.git
cd Videoflix
```

### 2. Configure environment variables

Create a file named `.env` in the backend root directory, next to `docker-compose.yml`.

Add the following configuration and replace the example values with your own settings:

```dotenv
# Django
SECRET_KEY=replace_with_a_secure_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500

# Initial superuser
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=replace_with_a_secure_password
DJANGO_SUPERUSER_EMAIL=admin@example.com

# PostgreSQL
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_LOCATION=redis://redis:6379/1
REDIS_PORT=6379
REDIS_DB=0

# Email
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email_user
EMAIL_HOST_PASSWORD=your_email_user_password
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=default_from_email
```

**Important:**

- Generate a unique Django `SECRET_KEY`. Never publish the real value.
- Replace all example database credentials with your own values.
- Configure the email settings for your chosen SMTP provider if email delivery is required.
- Keep `.env` private and never commit it to Git.
- The frontend runs on port `5500` in the current local development setup. If you use a different port or origin, adjust the relevant settings accordingly.
- The configuration above is intended for local development, not production.

### 3. Start the backend with Docker

Make sure Docker Desktop is running, then execute:

```bash
docker compose up --build -d
```

The Docker setup starts the following services:

- **web:** Django application served by Gunicorn
- **db:** PostgreSQL database
- **redis:** Redis for caching and background task processing

The backend entry point waits for PostgreSQL, collects static files, applies database migrations, creates the configured superuser if it does not exist, starts the Django RQ worker and launches the application.

Check the running containers:

```bash
docker compose ps
```

View the backend logs if necessary:

```bash
docker compose logs -f web
```

The backend API is available at:

```text
http://127.0.0.1:8000/
```

The Django administration interface is available at:

```text
http://127.0.0.1:8000/admin/
```

Use the superuser credentials configured in `.env` to log in to the administration interface.

### 4. Set up the frontend

The frontend is maintained separately from the backend. Use the original frontend repository linked above as the starting point if you need to set it up locally.

Open the frontend folder in Visual Studio Code and follow the frontend's development instructions. In the current local setup, the frontend is served using Visual Studio Code's Live Server extension on port `5500`.

The activation and password-reset email links are configured for frontend pages served at `127.0.0.1:5500`. Make sure the frontend uses the expected address and port for these flows to work as configured.

### 5. Verify the installation

Check that the backend containers are running:

```bash
docker compose ps
```

Review the latest backend logs:

```bash
docker compose logs --tail=100 web
```

The video list endpoint requires an authenticated user. A `401 Unauthorized` response without an access-token cookie is therefore expected.

To run the automated backend tests, see the Testing section below.

---

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Authentication](#authentication)
- [API Reference](#api-reference)
- [Video Streaming](#video-streaming)
- [Testing](#testing)
- [Security and Configuration](#security-and-configuration)

## Features

- User registration with email activation
- Login and logout using JWTs stored in HttpOnly cookies
- Access-token refresh using the refresh-token cookie
- Password-reset email workflow
- Video metadata API for the dashboard
- Authenticated delivery of HLS playlists and video segments
- PostgreSQL as the relational database
- Redis for caching and background task processing
- Django RQ worker for queued tasks
- Docker-based local development environment
- Configurable SMTP support for outgoing emails

## Technology Stack

| Technology | Purpose |
| --- | --- |
| Python | Backend programming language |
| Django | Web framework |
| Django REST Framework | REST API |
| Simple JWT | JWT authentication and token management |
| PostgreSQL | Relational database |
| Redis | Caching and task queue backend |
| Django RQ | Background task processing |
| FFmpeg | Video and media processing dependency |
| Gunicorn | WSGI application server |
| WhiteNoise | Static file serving |
| Docker Compose | Local multi-container environment |
| SMTP | Email delivery |

## Project Structure

The main backend files and directories are organized as follows:

```text
Videoflix/
├── auth_app/
│   ├── api/
│   │   ├── functions.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── authentication.py
│   ├── tests/
│   └── ...
├── core/
│   ├── middleware.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── video_app/
│   ├── api/
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── ...
│   ├── functions.py
│   ├── models.py
│   ├── admin.py
│   └── tests/
├── backend.Dockerfile
├── backend.entrypoint.sh
├── docker-compose.yml
├── manage.py
├── requirements.txt
└── README.md
```

The frontend is maintained separately and is not part of the backend repository.

## Authentication

Videoflix uses JWT authentication with tokens stored in HttpOnly cookies.

- Registration creates an inactive account and sends an activation email.
- Account activation enables the user to log in.
- Login sets the `access_token` and `refresh_token` cookies.
- The access token authenticates requests to protected endpoints.
- The refresh endpoint issues a new access token using the refresh-token cookie.
- Logout blacklists the refresh token and clears both authentication cookies.
- Password reset uses a time-limited token delivered by email.

The browser handles the authentication cookies. JavaScript should not need to read the token values directly.

The backend also validates request origins for state-changing requests. The frontend origin must match the configured allowed origins.

## API Reference

All endpoints are served by the Django REST Framework backend at `http://127.0.0.1:8000`.

### Authentication endpoints

| Method | Endpoint | Description | Authentication |
| --- | --- | --- | --- |
| `POST` | `/api/register/` | Register a user and send an activation email | Not required |
| `GET` | `/api/activate/<uidb64>/<token>/` | Activate a user account | Not required |
| `POST` | `/api/login/` | Authenticate a user and set JWT cookies | Not required |
| `POST` | `/api/logout/` | Blacklist the refresh token and clear cookies | Refresh-token cookie required |
| `POST` | `/api/token/refresh/` | Issue a new access token | Refresh-token cookie required |
| `POST` | `/api/password_reset/` | Request a password-reset email | Not required |
| `POST` | `/api/password_confirm/<uidb64>/<token>/` | Set a new password using a valid reset token | Not required |

#### Registration request example

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "confirmed_password": "SecurePassword123!"
}
```

#### Login request example

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

#### Password-reset request example

```json
{
  "email": "user@example.com"
}
```

#### Password-confirmation request example

```json
{
  "new_password": "NewSecurePassword123!",
  "confirm_password": "NewSecurePassword123!"
}
```

### Video endpoints

| Method | Endpoint | Description | Authentication |
| --- | --- | --- | --- |
| `GET` | `/api/video/` | Return video metadata for the dashboard | Access-token cookie required |
| `GET` | `/api/video/<movie_id>/<resolution>/index.m3u8` | Return an HLS playlist | Access-token cookie required |
| `GET` | `/api/video/<movie_id>/<resolution>/<segment>/` | Return an HLS video segment | Access-token cookie required |

The video list returns metadata fields including `id`, `created_at`, `title`, `description`, `thumbnail_url` and `category`.

The supported resolutions for HLS delivery are `480p`, `720p` and `1080p`. Playlist and segment requests return `404 Not Found` when the requested file is missing or the path does not match the accepted format.

## Video Streaming

The backend exposes endpoints for delivering HLS playlists and MPEG-TS segments. It expects the relevant HLS files to exist under the configured media directory:

```text
media/
└── hls/
    └── <video_id>/
        ├── 480p/
        │   ├── index.m3u8
        │   └── segment_000.ts
        ├── 720p/
        │   ├── index.m3u8
        │   └── segment_000.ts
        └── 1080p/
            ├── index.m3u8
            └── segment_000.ts
```

The segment names must follow the format `segment_###.ts`, where `###` consists of three digits.

FFmpeg is installed in the backend container as a media-processing dependency. The playlist and segment endpoints serve existing files; the availability of these endpoints alone does not mean that every uploaded video has already been converted into HLS.

## Testing

Run the backend test suite inside the running Docker container:

```bash
docker compose exec web python manage.py test --keepdb
```

The `--keepdb` option reuses an existing test database. If the test database does not exist, Django creates it.

To run a specific test module, for example:

```bash
docker compose exec web python manage.py test auth_app.tests.test_token_refresh --keepdb
```

The tests cover authentication flows, token refresh, logout, password reset and video-list behavior. Test results can change as the project evolves; run the suite locally to verify the current state.

## Security and Configuration

- Never commit `.env` or other files containing credentials.
- Use a unique, securely generated `SECRET_KEY`.
- Do not use `DEBUG=True` in production.
- Configure `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` and `CORS_ALLOWED_ORIGINS` for the actual environment.
- Use HTTPS in production so secure authentication cookies can be transmitted safely.
- Use a dedicated database password and protect access to PostgreSQL and Redis.
- Configure valid SMTP credentials if email delivery is required.
- Do not expose private user data, credentials or activation/reset tokens in logs or public documentation.
- Review the Django deployment checklist before deploying the application publicly.
