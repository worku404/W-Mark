# W-Mark (Bookmarks)

A Django-based bookmarks application with user accounts, social auth, image management, and activity tracking.

## Features
- User registration and authentication
- Email-based login backend
- Google OAuth2 login
- Image uploads with thumbnailing
- Activity/actions tracking
- Django Debug Toolbar for development

## Project Structure
- `bookmarks/` — Django project root
  - `account/` — user management and authentication
  - `images/` — image upload and management
  - `actions/` — activity/actions tracking
  - `bookmarks/` — Django settings, URLs, WSGI/ASGI
  - `media/` — uploaded media (local dev)

## Requirements
Python 3.10+ recommended.

Install dependencies:

```bash
pip install -r bookmarks/requirements.txt
```

## Environment Variables
Create a `.env` file (or export environment variables) with:

```bash
GOOGLE_OAUTH2_KEY=your_google_oauth_key
GOOGLE_OAUTH2_SECRET=your_google_oauth_secret
```

## Running Locally

```bash
cd bookmarks
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then visit: http://127.0.0.1:8000

## Development Notes
- Debug toolbar is enabled in settings.
- SQLite is used by default.

## License
MIT
