DJANGO_DIR = D:\practice\Web_Rating\rating_site
SERVER_DIR = D:\practice\Web_Rating\rating_site\backend


.PHONY: run
run:
	start cmd /K "cd /D $(DJANGO_DIR) && py manage.py runserver 8001"
	start cmd /K "cd /D $(SERVER_DIR) && uvicorn server:app --reload"

stop:
	@echo "Остановка всех серверов..."
	taskkill /IM "python.exe" /F