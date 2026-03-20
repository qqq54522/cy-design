@echo off
echo Stopping all services...
docker compose -f docker-compose.yml -f docker-compose.dev.yml down 2>nul
docker compose -f docker-compose.yml -f docker-compose.prod.yml down 2>nul
echo.
echo All services stopped.
pause
