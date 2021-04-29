set COMPOSE_CONVERT_WINDOWS_PATHS=1
docker-compose -p project_oauth up -d --build
pause
docker-compose -p project_oauth down
