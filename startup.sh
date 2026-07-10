#!/bin/bash
# Comando de arranque que Azure App Service usa para levantar la app.
# En el portal de Azure: Configuración > Configuración general > Comando de inicio:
#   startup.sh
gunicorn --bind=0.0.0.0 --timeout 600 wsgi:app
