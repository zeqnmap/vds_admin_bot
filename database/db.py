import aiosqlite
from typing import List, Optional
from .models import Workshop, Project
from utils.logger_conf import setup_logger

logger = setup_logger(__name__)

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def create_tables(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('PRAGMA journal_mode=WAL')
            await db.execute('PRAGMA synchronous=NORMAL')
            await db.execute('PRAGMA cache_size=10000')
            await db.execute('PRAGMA temp_store=MEMORY')

            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS workshops (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    code TEXT UNIQUE NOT NULL
                )
            ''')

            await db.execute('''
                CREATE TABLE IF NOT EXISTS workshops_for_prod (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    code TEXT UNIQUE NOT NULL
                )
            ''')

            await db.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    workshop_code TEXT,
                    project_code TEXT,
                    master_fullname TEXT,
                    color TEXT,
                    report_type TEXT,
                    problem_type TEXT,
                    description TEXT,
                    photo_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            await db.execute('''
                    CREATE TABLE IF NOT EXISTS workshop_projects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        workshop_code TEXT NOT NULL,
                        project_name TEXT NOT NULL,
                        project_code TEXT NOT NULL,
                        UNIQUE(workshop_code, project_code)
                    )
                ''')

            await db.commit()
            await self._populate_initial_data(db)
            await self._populate_initial_data_prod(db)

    @classmethod
    async def _populate_initial_data(cls, db):
        workshops = [
            ('Цех сварки', 'welding'),
            ('Вспомогательный цех', 'auxiliary'),
            ('Заготовительный цех', 'preparatory'),
            ('Сборочный цех', 'assembly'),
            ('Цех RVI', 'rvi'),
            ('Продажи', 'sales'),
            ('КБ', 'kb'),
            ('Креатив', 'creative'),
            ('Логистика', 'logistics'),
            ('Монтаж', 'installation'),
        ]
        for name, code in workshops:
            await db.execute('INSERT OR IGNORE INTO workshops (name, code) VALUES (?, ?)', (name, code))
        await db.commit()

    @classmethod
    async def _populate_initial_data_prod(cls, db):
        workshops_prod = [
            ('Цех сварки', 'welding'),
            ('Вспомогательный цех', 'auxiliary'),
            ('Заготовительный цех', 'preparatory'),
            ('Сборочный цех', 'assembly'),
            ('Цех RVI', 'rvi')
        ]
        for name, code in workshops_prod:
            await db.execute('INSERT OR IGNORE INTO workshops_for_prod (name, code) VALUES (?, ?)', (name, code))
        await db.commit()

    async def add_user(self, user_id: int, username: Optional[str] = None):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
            await db.commit()

    async def get_workshops(self) -> List[Workshop]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT id, name, code FROM workshops ORDER BY id') as cursor:
                rows = await cursor.fetchall()
                return [Workshop(id=row['id'], name=row['name'], code=row['code']) for row in rows]

    async def get_workshops_prod(self) -> List[Workshop]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT id, name, code FROM workshops_for_prod ORDER BY id') as cursor:
                rows = await cursor.fetchall()
                return [Workshop(id=row['id'], name=row['name'], code=row['code']) for row in rows]

    async def get_projects(self) -> List[Project]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT id, name, code FROM projects ORDER BY id') as cursor:
                rows = await cursor.fetchall()
                return [Project(id=row['id'], name=row['name'], code=row['code']) for row in rows]

    async def save_report(self, **kwargs):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO reports (
                    user_id, workshop_code, project_code, master_fullname,
                    color, report_type, problem_type, description, photo_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                kwargs.get('user_id'),
                kwargs.get('workshop_code'),
                kwargs.get('project_code'),
                kwargs.get('master_fullname'),
                kwargs.get('color'),
                kwargs.get('report_type'),
                kwargs.get('problem_type'),
                kwargs.get('description'),
                kwargs.get('photo_path'),
            ))
            await db.commit()

    async def get_workshop_projects(self, workshop_code: str):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                    'SELECT project_name, project_code FROM workshop_projects WHERE workshop_code = ? ORDER BY project_name',
                    (workshop_code,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [{'name': row['project_name'], 'code': row['project_code']} for row in rows]

    async def add_workshop_project(self, workshop_code: str, project_name: str) -> bool:
        project_code = project_name.lower().replace(' ', '_')
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'INSERT INTO workshop_projects (workshop_code, project_name, project_code) VALUES (?, ?, ?)',
                    (workshop_code, project_name, project_code)
                )
                await db.commit()
                return True
        except aiosqlite.IntegrityError:
            return False

    async def delete_workshop_project(self, workshop_code: str, project_code: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'DELETE FROM workshop_projects WHERE workshop_code = ? AND project_code = ?',
                (workshop_code, project_code)
            )
            await db.commit()