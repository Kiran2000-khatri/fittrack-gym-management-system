# FitTrack - Gym Management System

A simple, working gym management system built with **Django + SQLite** (no external database needed).

## Features
- Staff login
- Dashboard: total/active members, monthly revenue, today's check-ins, expiring memberships, 6-month revenue chart
- Members: add / edit / delete / search, profile page with history
- Membership plans (name, duration, price)
- Assign memberships (end date auto-calculated, optional automatic payment record)
- Payments: record and list
- Attendance: check-in (only with active membership) and check-out
- Trainers management
- Built-in Django admin at `/admin/`

## Setup
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo      # creates demo data + login admin / admin123
python manage.py runserver
```
Open http://127.0.0.1:8000/ and log in with **admin / admin123**.

To start with an empty system, skip `seed_demo` and run `python manage.py createsuperuser` instead.

## Project structure
- `config/` - Django settings and root URLs
- `gym/` - the app (models, views, forms, templates)
- `gym/management/commands/seed_demo.py` - demo data generator

## Notes
For production, set `DEBUG = False`, change `SECRET_KEY`, and set `ALLOWED_HOSTS`.
