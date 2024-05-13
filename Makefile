migrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

app:
	django-admin startapp $(word 2, $(MAKECMDGOALS))

up:
	powershell -Command "(Get-Content spotify/credentials.py -Raw) -replace 'REDIRECT_URL = .+', 'REDIRECT_URL = \"http://127.0.0.1:8000/spotify/redirect\"' | Set-Content spotify/credentials.py -NoNewline"
	python manage.py runserver

local:
	powershell -Command "(Get-Content spotify/credentials.py -Raw) -replace 'REDIRECT_URL = .+', 'REDIRECT_URL = \"http://192.168.0.23:8000/spotify/redirect\"' | Set-Content spotify/credentials.py -NoNewline"
	python manage.py runserver 192.168.0.23:8000

shell:
	python manage.py shell