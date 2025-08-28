web: python manage.py collectstatic --noinput --clear && gunicorn letterflow.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --preload
