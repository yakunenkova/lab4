import psycopg2
import traceback

try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="postgres",
        database="spa_db"
    )
    print("✅ Подключение УСПЕШНО!")
    conn.close()
except Exception as e:
    print("=" * 50)
    print("ПОЛНАЯ ОШИБКА:")
    print("=" * 50)
    traceback.print_exc()