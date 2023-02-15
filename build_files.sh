pip install -r requirements.txt

# Create the database
python manage.py makemigrations --noinput
python manage.py migrate --noinput

python manage.py collectstatic --noinput --clear
