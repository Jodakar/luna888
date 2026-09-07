#!/bin/bash
cd /var/www/luna888
source venv/bin/activate
export PYTHONPATH=/var/www/luna888:$PYTHONPATH
export DATABASE_URL="postgresql://luna_user:LunaPass2026@localhost:5432/luna_db"
export REDIS_URL="redis://localhost:6379/0"
echo "✅ Окружение активировано!"
echo "📁 Проект: /var/www/luna888"
echo "🐍 Python: $(python3 --version)"
echo "📦 Библиотек: $(pip freeze | wc -l)"
