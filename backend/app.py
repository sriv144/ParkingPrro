"""Local development entrypoint.

Production imports ``parkingpro.wsgi:app`` through Gunicorn. Keeping this small
wrapper preserves ``python app.py`` for contributors without exposing Flask's
debugger in deployed environments.
"""

from parkingpro import create_app

if __name__ == "__main__":
    create_app("development").run(debug=False)
