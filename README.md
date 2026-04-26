# Simplex Manager

> A full-stack business management platform for a real tutoring operation — handling student sessions, invoicing, payments, scheduling, and resource delivery.

**[Live →](https://simplex-manager.vercel.app)**

---

## What it does

- **Session management** — track tutoring sessions per student, attach notes and outcomes
- **Invoicing** — generate and send invoices; Stripe integration for online payment collection
- **Scheduling** — manage tutor availability and book sessions
- **Resource delivery** — upload and distribute learning materials (stored on AWS S3 / Cloudinary)
- **Background jobs** — async task queue (Django-Q2 + Redis) for sending reminders and processing invoices
- **Auth** — JWT-based authentication with role separation (tutor / admin)

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Django 5.2 + Django REST Framework |
| Auth | djangorestframework-simplejwt |
| Payments | Stripe API |
| Task queue | Django-Q2 + Redis |
| File storage | AWS S3 + Cloudinary |
| Database | PostgreSQL (psycopg3) |
| Frontend | React + Vite |
| E2E tests | Cypress |
| Deployment | Heroku (Procfile) + WhiteNoise |

## Local setup

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env   # fill in DB, Stripe, AWS, Redis keys
python manage.py migrate
python manage.py runserver

# Frontend
cd frontend
npm install
npm run dev
```

## Project structure

```
backend/
├── api/            # REST API endpoints
├── tutoring/       # Core domain: students, sessions, scheduling
├── stripeInt/      # Stripe webhook handlers and invoice logic
├── resources/      # File upload and delivery
└── manage.py
frontend/
├── src/            # React components and pages
└── cypress/        # E2E test specs
APIDocs/            # API documentation
```
