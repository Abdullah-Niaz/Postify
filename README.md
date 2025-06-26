# 📝 Postify - A Django Blog Web App

Postify is a simple yet functional blog application built using Django. It allows users to write, categorize, and manage blog articles with features like comments, image uploads, user authentication, voting, and bookmarking.

## 🚀 Features

- User registration & login system
- Create, read, update, delete (CRUD) for blog posts
- Categorize articles using a many-to-many `Category` model
- Markdown-supported content editor
- Upload and display images
- Comment system
- Upvote / Downvote on articles
- Bookmark favorite articles
- Custom error pages (404, etc.)
- Clean and responsive UI using Bootstrap

## 🛠️ Tech Stack

- **Backend:** Django 4+
- **Frontend:** HTML, CSS, Bootstrap
- **Database:** SQLite (default) / PostgreSQL (for production)
- **Authentication:** Django's built-in auth system
- **Others:** `crispy-forms`, `python-dotenv`, `dj-database-url`

## 📦 Installation

1. **Clone the repo:**

   ```bash
   git clone https://github.com/yourusername/Postify.git
   cd Postify
   ```
````

2. **Create a virtual environment and activate it:**

   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   Create a `.env` file in the root directory:

   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///db.sqlite3
   ```

5. **Run migrations:**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Run the server:**

   ```bash
   python manage.py runserver
   ```

7. Visit:
   `http://127.0.0.1:8000/`

## 📂 Folder Structure

```
Postify/
├── blog/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/
│   └── static/
├── Postify/
│   ├── settings.py
│   └── urls.py
├── manage.py
├── .env
└── requirements.txt
```

## 🧪 TODO (Optional Enhancements)

- Rich text editor (e.g., CKEditor)
- Pagination on article list
- User profile pages
- REST API integration (Django REST Framework)
- Admin dashboard improvements

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

Happy blogging with Postify! 🚀
