@echo off
echo ============================================
echo   E-Commerce API - Setup y arranque
echo ============================================

:: 1. Crear entorno virtual
echo.
echo [1/5] Creando entorno virtual...
python -m venv venv

:: 2. Activar entorno virtual
echo [2/5] Activando entorno virtual...
call venv\Scripts\activate.bat

:: 3. Instalar dependencias
echo [3/5] Instalando dependencias...
pip install -r requirements.txt

:: 4. Inicializar coleccion MongoDB
echo [4/5] Configurando coleccion MongoDB...
python mongo_setup.py

:: 5. Levantar servidor FastAPI
echo [5/5] Levantando servidor FastAPI...
echo.
echo  Swagger UI disponible en: http://localhost:8000/docs
echo  Presiona Ctrl+C para detener el servidor
echo.
uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause