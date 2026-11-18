# Postify Dense Repository Map (Token-Optimized)

```yaml
project: Postify (Django Blog Web Application)
config:
  settings: Postify/settings.py (INSTALLED_APPS: blog, accounts, crispy_forms, crispy_bootstrap5)
  urls: Postify/urls.py (routes: /, /accounts/, /admin/)
  dependencies: requirements.txt (Django, crispy-bootstrap5, django-crispy-forms, django-multiselectfield, markdown2, Pillow, whitenoise, python-dotenv, dj-database-url, psycopg2-binary)

apps:
  accounts:
    models: Django User
    urls: accounts/urls.py (register: /accounts/register/)
    views: accounts/views.py (register)
    templates: accounts/templates/ (base.html, registration/login.html, register.html)
    static: accounts/static/accounts/ (css/login.css)

  blog:
    models:
      Article: [owner, title, desc, artImage, content, category, created, bookmarks, upvote, downvote]
      Comment: [owner, article, created, content]
    urls: blog/urls.py
      views:
        - GET  /                     -> index (feed + search `?q=`)
        - GET/POST /add              -> add (create post)
        - GET  /categories           -> categories (list)
        - GET  /category/<name>      -> category (filtered posts)
        - GET  /articles/<id>        -> singleArt (post detail + markdown + comments)
        - GET  /bookmarks            -> bookmarks (saved posts)
        - GET/POST /update/<id>      -> update (edit post)
      apis:
        - POST /save/<id>            -> save (toggle bookmark)
        - PUT  /vote/<id>            -> voting (toggle upvote)
        - POST /delete/<id>          -> delete (owner only)
        - POST /articles/comment/<id> -> addComment (AJAX comment)
    templates: blog/templates/
      - layout.html (base navbar + footer + snackbar)
      - index.html (feed with postcard cards)
      - singleArt.html (article detail + markdown2 render + AJAX comments)
      - add.html (crispy form for create/update)
      - categories.html (category grid)
      - category.html (category filtered feed)
      - bookmarks.html (bookmarked articles)
      - 404.html (custom error page)
    static: blog/static/blog/
      - js/main.js (AJAX voting, bookmarking, deletion with SweetAlert, comment posting)
      - css/ (layout.css, index.css, singleArt.css, add.css, category.css, bookmarks.css, 404.css, editorial_admin.css)
    commands: blog/management/commands/feed_dummy_articles.py (seed realistic technical articles, discussions, votes)
```
