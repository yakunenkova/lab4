import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from alembic.config import Config
from alembic import command
from app.core.database import Base
from app.models.service import Service

# Создаём таблицу напрямую (минуя Alembic)
engine = create_engine("postgresql://postgres:postgres@127.0.0.1:5432/spa_db")
Base.metadata.create_all(bind=engine)
print("✅ Таблицы созданы!")