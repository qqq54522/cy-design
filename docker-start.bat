@echo off
echo ========================================
echo    Lingqiao Creative Hub - DEV MODE
echo ========================================
echo.
echo Building and starting all services (development)...
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
echo.
echo ========================================
echo   Hub:        http://localhost:5180
echo   Platform:   http://localhost:8100/health
echo   Content:    http://localhost:5174
echo   KV:         http://localhost:5175/kv
echo   Emoji:      http://localhost:5176
echo ========================================
echo.
echo View logs:  docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f
echo Stop all:   docker-stop.bat
echo.
timeout /t 8 /nobreak >nul
start http://localhost:5180
pause
