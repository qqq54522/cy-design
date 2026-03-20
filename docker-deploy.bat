@echo off
echo ========================================
echo    Lingqiao Creative Hub - PRODUCTION
echo ========================================
echo.
echo Building and deploying all services (production)...
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
echo.
echo ========================================
echo   Hub:        http://localhost:5180
echo   Platform:   http://localhost:8100/health
echo   Content:    http://localhost:5174
echo   KV:         http://localhost:5175/kv
echo   Emoji:      http://localhost:5176
echo ========================================
echo.
echo View logs:  docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f
echo Stop all:   docker-stop.bat
echo.
pause
