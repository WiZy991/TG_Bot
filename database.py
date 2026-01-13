import aiosqlite

DB_NAME = "quiz.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS results (
                user_id INTEGER PRIMARY KEY,
                score INTEGER
            )
        """)
        await db.commit()

async def save_result(user_id: int, score: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR REPLACE INTO results (user_id, score) VALUES (?, ?)",
            (user_id, score),
        )
        await db.commit()

async def get_result(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT score FROM results WHERE user_id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()
        return row[0] if row else None
