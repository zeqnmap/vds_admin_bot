import sqlite3

DB_PATH = "production_database.db"


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT code FROM workshops")
    workshops = [row[0] for row in cur.fetchall()]

    if not workshops:
        print("❌ Таблица workshops пуста или не найдена. Запустите бота хотя бы раз.")
        conn.close()
        return

    projects = [
        ("Лукойл", "Лукойл"),]

    count = 0
    for ws in workshops:
        for name, code in projects:
            try:
                cur.execute(
                    "INSERT OR IGNORE INTO workshop_projects (workshop_code, project_name, project_code) VALUES (?, ?, ?)",
                    (ws, name, code),
                )
                if cur.rowcount:
                    count += 1
            except Exception as e:
                print(f"Ошибка")

    conn.commit()
    conn.close()
    print(f"Добавлено проектов: {count} (уникальные пары workshop+project).")


if __name__ == "__main__":
    main()