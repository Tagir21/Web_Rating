# make only for windows

DJANGO_DIR = D:\practice\Web_Rating\rating_site
SERVER_DIR = D:\practice\Web_Rating\rating_site\backend


.PHONY: run
run:
	start "Django Server" cmd /K "cd /D $(DJANGO_DIR) && py manage.py runserver 8001"
	start "BD Server" cmd /K "cd /D $(SERVER_DIR) && uvicorn server:app --reload"

stop:
	@echo "Остановка всех серверов..."
	taskkill /FI "WINDOWTITLE eq Django Server*" /IM "cmd.exe" /F
	taskkill /FI "WINDOWTITLE eq BD Server*" /IM "cmd.exe" /F
	taskkill /IM "python.exe" /F