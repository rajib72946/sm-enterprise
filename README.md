# Mobile Shop Web Application

A Flask-based web application for managing and showcasing mobile phones, with features for broadcasts and community posts.

## Features

- Mobile phone catalog with detailed specifications
- Admin dashboard for content management
- User authentication and authorization
- Broadcast announcements
- Community posts
- Image upload and management
- Responsive design

## Tech Stack

- Python 3.12
- Flask 3.0.0
- SQLAlchemy
- Bootstrap 5
- Gunicorn (Production server)
- PostgreSQL (Production database)
- SQLite (Development database)

## Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mobile-shop.git
cd mobile-shop
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
flask db upgrade
```

6. Run the development server:
```bash
flask run
```

## Deployment on Render

1. Push your code to GitHub
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Configure the following:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn wsgi:app`
   - Environment Variables:
     - `DATABASE_URL`
     - `SECRET_KEY`
     - `FLASK_ENV=production`

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
