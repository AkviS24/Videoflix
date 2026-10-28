
# Videoflix Backend

Videoflix is the backend for a video streaming application. It provides a Django REST API for user authentication, account management, video metadata, and authenticated HLS video delivery.

The backend uses PostgreSQL for persistent data storage, Redis for caching and background task processing, and Docker Compose to run the application and its supporting services.

The frontend is maintained separately. This repository contains the backend only.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation and Setup](#installation-and-setup)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Authentication](#authentication)
- [Video Streaming](#video-streaming)
- [Background Tasks](#background-tasks)
- [Testing](#testing)
- [Security](#security)
- [Frontend](#frontend)

## Features

- User registration with email activation
- Login and logout using JWTs stored in HttpOnly cookies
- Access-token refresh using a refresh-token cookie
- Refresh-token blacklisting on logout
- Password-reset workflow via email
- Authenticated video metadata API
- Video metadata including title, description, thumbnail URL, category, and creation date
- Authenticated HLS playlist and video segment delivery
- PostgreSQL database integration
- Redis caching and Django RQ background worker
- Docker-based development environment
- FFmpeg available in the backend container for video-processing tasks

The API endpoints for HLS delivery are implemented. Generating HLS playlists, video segments, and thumbnails is a separate processing step and must be implemented and verified as part of the complete video-processing workflow.

## Technology Stack

- **Python 3.12** — backend runtime in the Docker image
- **Django** — web framework
- **Django REST Framework** — REST API
- **Django REST Framework Simple JWT** — JWT authentication
- **PostgreSQL** — relational database
- **Redis** — caching and background task infrastructure
- **Django RQ** — background job processing
- **FFmpeg** — video processing tool installed in the Docker image
- **Gunicorn** — WSGI application server
- **WhiteNoise** — static file handling
- **Docker Compose** — local development environment

Python dependencies and their pinned versions are listed in `requirements.txt`. FFmpeg is installed as a system package in the Docker image and is therefore not a Python package listed in `requirements.txt`.

## Prerequisites

Install the following tools before setting up the project:

- [Git](https://git-scm.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with Docker Compose
- [Visual Studio Code](https://code.visualstudio.com/) or another code editor
- An SMTP account and credentials if you want to test email delivery

The documented development workflow runs Python, Django, PostgreSQL, Redis, and FFmpeg through Docker. A separate local Python installation is not required for this workflow.

## Installation and Setup

### 1. Clone the backend repository

```bash
git clone https://github.com/AkviS24/Videoflix.git
cd Videoflix
```

Run the following commands from the directory containing `docker-compose.yml`.

### 2. Create the environment file

The repository provides `.env.template` as a configuration template. Create a local `.env` file from it.

**Windows (CMD):**

```cmd
copy .env.template .env
```

**Linux / macOS:**

```bash
cp .env.template .env
```

Open `.env` and replace the example values with the appropriate values for your environment.

Do not commit `.env` to Git.

### 3. Configure the environment

At a minimum, configure:

- A private Django `SECRET_KEY`
- PostgreSQL database credentials
- Initial Django superuser credentials
- SMTP credentials if email delivery is required

See [Environment Variables](#environment-variables) for the full list.

The values in `.env.template` are examples for local development. In particular, change the example superuser password and replace the placeholder secret key before starting the application.

### 4. Build and start the containers

Make sure Docker is running, then execute:

```bash
docker compose up --build -d
```

The Docker Compose configuration starts three services:

| Service | Purpose |
|---|---|
| `web` | Django backend served by Gunicorn |
| `db` | PostgreSQL database |
| `redis` | Redis for caching and background tasks |

The backend entrypoint waits for PostgreSQL, collects static files, applies database migrations, creates the configured superuser if it does not already exist, starts the Django RQ worker, and launches Gunicorn.

Check the service status:

```bash
docker compose ps
```

View backend logs:

```bash
docker compose logs -f web
```

### 5. Access the backend

The backend is available locally at:

`http://127.0.0.1:8000/`

The root URL does not provide a separate API landing page.

- API base path: `http://127.0.0.1:8000/api/`
- Django administration: `http://127.0.0.1:8000/admin/`

Use the superuser credentials configured in `.env` to sign in to Django administration.

The video list and HLS endpoints require authentication. A `401 Unauthorized` response from these endpoints without a valid access-token cookie is expected.

### 6. Stop the containers

To stop the services without deleting their persistent volumes:

```bash
docker compose down
```

**Warning:** The following command also removes Compose-managed volumes, including persistent database data:

```bash
docker compose down -v
```

Use it only when you intentionally want to remove that data.

## Environment Variables

The following variables are provided in `.env.template`.

| Variable | Description |
|---|---|
| `DJANGO_SUPERUSER_USERNAME` | Username for the initial Django superuser |
| `DJANGO_SUPERUSER_PASSWORD` | Password for the initial Django superuser |
| `DJANGO_SUPERUSER_EMAIL` | Email address for the initial Django superuser |
| `SECRET_KEY` | Private Django secret key |
| `DEBUG` | Enables or disables Django debug mode |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hostnames |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated list of trusted origins for CSRF protection |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL database username |
| `DB_PASSWORD` | PostgreSQL database password |
| `DB_HOST` | PostgreSQL hostname; normally `db` in Docker Compose |
| `DB_PORT` | PostgreSQL port; normally `5432` |
| `REDIS_HOST` | Redis hostname; normally `redis` in Docker Compose |
| `REDIS_LOCATION` | Redis connection URL used by the cache |
| `REDIS_PORT` | Redis port; normally `6379` |
| `REDIS_DB` | Redis database index used by the RQ queue configuration |
| `EMAIL_HOST` | SMTP server hostname |
| `EMAIL_PORT` | SMTP server port |
| `EMAIL_HOST_USER` | SMTP username |
| `EMAIL_HOST_PASSWORD` | SMTP password or app-specific password |
| `EMAIL_USE_TLS` | Enables SMTP TLS |
| `EMAIL_USE_SSL` | Enables SMTP SSL |
| `DEFAULT_FROM_EMAIL` | Default sender address for outgoing email |

### Configuration notes

- Replace the placeholder values with the credentials for your environment.
- Generate a secure Django secret key and keep it private.
- Do not use the example superuser password beyond local development.
- Keep `DB_HOST=db` and `REDIS_HOST=redis` when using the provided Docker Compose service names, unless you deliberately change the service configuration.
- `REDIS_LOCATION` and `REDIS_DB` serve different purposes in the current settings. The cache URL defaults to `redis://redis:6379/1`, while the RQ queue configuration uses `REDIS_DB`, whose template value is `0`.
- `CORS_ALLOWED_ORIGINS` is not listed in `.env.template`, but the Django settings provide a default for the local frontend origins `http://localhost:5500` and `http://127.0.0.1:5500`. You can add `CORS_ALLOWED_ORIGINS` to `.env` if you need to override that default.
- The template's `CSRF_TRUSTED_ORIGINS` uses port `5500`. Ensure that the trusted origins and CORS origins match the actual frontend setup.
- The activation and password-reset email links currently point to frontend pages served at `http://127.0.0.1:5500`. If the frontend uses a different address or port, update the corresponding backend configuration or implementation.
- Email delivery requires valid SMTP settings. The example SMTP hostname and credentials will not work as supplied.
- For production, use `DEBUG=False` and configure secure deployment settings, trusted origins, allowed hosts, HTTPS, and secure cookie behavior.

## Project Structure

The backend repository is organized as follows:

```text
Videoflix/
├── auth_app/
│   ├── api/
│   │   ├── functions.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   └── authentication.py
├── core/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   └── middleware.py
├── video_app/
│   ├── api/
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── functions.py
│   ├── models.py
│   └── tests/
├── backend.Dockerfile
├── backend.entrypoint.sh
├── docker-compose.yml
├── .env.template
├── .gitignore
├── manage.py
└── requirements.txt
```

## API Reference

All endpoints are exposed under the `/api/` prefix.

### Authentication and account management

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/register/` | Register a user and initiate account activation |
| `GET` | `/api/activate/<uidb64>/<token>/` | Activate a user account |
| `POST` | `/api/login/` | Authenticate a user and set JWT cookies |
| `POST` | `/api/logout/` | Blacklist the refresh token and clear authentication cookies |
| `POST` | `/api/token/refresh/` | Issue a new access token using the refresh-token cookie |
| `POST` | `/api/password_reset/` | Request a password-reset email |
| `POST` | `/api/password_confirm/<uidb64>/<token>/` | Confirm a password reset |

### Video endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/video/` | Retrieve the authenticated video list |
| `GET` | `/api/video/<movie_id>/<resolution>/index.m3u8` | Retrieve an HLS playlist |
| `GET` | `/api/video/<movie_id>/<resolution>/<segment>/` | Retrieve an HLS video segment |

Replace URL placeholders with the relevant values.

### Registration

**Endpoint:** `POST /api/register/`

Request body:

```json
{
  "email": "user@example.com",
  "password": "your-password",
  "confirmed_password": "your-password"
}
```

The registration endpoint creates an inactive account and initiates the activation email flow. Successful delivery depends on valid email configuration.

### Login

**Endpoint:** `POST /api/login/`

Request body:

```json
{
  "email": "user@example.com",
  "password": "your-password"
}
```

A successful login sets the `access_token` and `refresh_token` cookies.

### Logout

**Endpoint:** `POST /api/logout/`

The endpoint expects a valid `refresh_token` cookie. It blacklists the refresh token and deletes the authentication cookies.

### Refresh access token

**Endpoint:** `POST /api/token/refresh/`

The endpoint reads the `refresh_token` cookie and sets a new `access_token` cookie when the refresh token is valid.

### Request a password reset

**Endpoint:** `POST /api/password_reset/`

Request body:

```json
{
  "email": "user@example.com"
}
```

For an eligible active account, the backend sends a password-reset email. The response does not disclose whether the email address belongs to an account.

### Confirm a password reset

**Endpoint:** `POST /api/password_confirm/<uidb64>/<token>/`

Request body:

```json
{
  "new_password": "your-new-password",
  "confirm_password": "your-new-password"
}
```

The UID and token must come from the password-reset flow.

### Retrieve the video list

**Endpoint:** `GET /api/video/`

This endpoint requires a valid access-token cookie.

Example response:

```json
[
  {
    "id": 1,
    "created_at": "2026-01-01T12:00:00Z",
    "title": "Example Video",
    "description": "An example video description.",
    "thumbnail_url": "http://127.0.0.1:8000/media/thumbnails/example.jpg",
    "category": "Drama"
  }
]
```

This is an illustrative response, not actual database data. The returned values depend on the stored video records. `thumbnail_url` may be `null` when a video has no thumbnail.

## Authentication

The backend uses JSON Web Tokens (JWT) stored in cookies.

- **Login:** Sets `access_token` and `refresh_token` cookies.
- **Protected endpoints:** Use `CookieJWTAuthentication` to read and validate the `access_token` cookie.
- **Token refresh:** Reads the `refresh_token` cookie and issues a new access token.
- **Logout:** Requires a refresh token, blacklists it, and clears both authentication cookies.

The video list, HLS playlist, and HLS segment endpoints require an authenticated user.

The login and refresh responses configure the access-token cookie as `HttpOnly`, with `Secure` enabled when `DEBUG` is false and `SameSite=Lax`. The login response applies the same cookie attributes to the refresh token.

Cookie-based authentication must be configured carefully for the intended frontend origin. For production, use HTTPS, secure cookie settings, appropriate CSRF protection, and matching CORS and trusted-origin settings.

## Video Streaming

The backend provides endpoints for serving HLS playlists and video segments.

The supported resolution identifiers are:

- `480p`
- `720p`
- `1080p`

The HLS file lookup expects generated files in the following directory structure:

```text
media/
└── hls/
    └── <video_id>/
        └── <resolution>/
            ├── index.m3u8
            ├── segment_000.ts
            ├── segment_001.ts
            └── ...
```

The playlist endpoint serves `index.m3u8`. The segment endpoint accepts filenames in the `segment_###.ts` format, where `###` represents exactly three digits, for example `segment_000.ts`.

The requested resolution and file name must be valid, and the requested file must exist. Otherwise, the file lookup returns a 404 response.

### FFmpeg and video processing

FFmpeg is installed in the backend Docker image through the system package manager. It is available for video-processing tasks without needing to be added to `requirements.txt`.

The complete workflow for converting uploaded source videos into HLS playlists and segments, generating thumbnails, and storing the generated files must be implemented and verified separately. The existence of the HLS delivery endpoints alone does not mean that video conversion is automatically performed.

## Background Tasks

The project includes Redis and Django RQ for background task processing.

The Docker entrypoint starts an RQ worker for the `default` queue. This infrastructure can be used for long-running work such as video conversion and thumbnail generation.

The actual tasks performed depend on the jobs implemented and enqueued by the application.

## Testing

Run the full Django test suite inside the running backend container:

```bash
docker compose exec web python manage.py test
```

Run the token refresh tests:

```bash
docker compose exec web python manage.py test auth_app.tests.test_token_refresh
```

Run the video list tests:

```bash
docker compose exec web python manage.py test video_app.tests.test_video_list
```

If the test database already exists and you intentionally want to reuse it, add `--keepdb`:

```bash
docker compose exec web python manage.py test --keepdb
```

Use the test results to verify the behavior of the current implementation before considering a feature complete.

## Security

- Keep `.env` private and never commit it.
- Use a unique, securely generated Django `SECRET_KEY`.
- Change the example superuser credentials before using the application beyond local development.
- Set `DEBUG=False` in production.
- Configure `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and CORS origins for the actual deployment.
- Use HTTPS and secure authentication cookies in production.
- Protect SMTP credentials and other secrets.
- Do not expose PostgreSQL or Redis publicly without an intentional and secured configuration.
- Ensure protected API endpoints enforce authentication and authorization as required.

## Frontend

The original frontend repository provided by the Developer Akademie is available here:

[Developer Akademie — Videoflix Frontend](https://github.com/Developer-Akademie-Backendkurs/project.Videoflix)

The frontend is maintained separately from this backend repository and communicates with it through the REST API.

For local development, make sure the frontend's API URL, development port, cookie behavior, CORS origins, and CSRF configuration match the backend settings.
