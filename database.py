import sqlite3
import datetime
import hashlib

DB_NAME = "bot_database.db"
DEFAULT_DAILY_LIMIT = 3
STREAK_BONUS_DAYS = 7
STREAK_BONUS_AMOUNT = 3

def get_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT DEFAULT '',
            username TEXT DEFAULT '',
            daily_balance INTEGER DEFAULT 2,
            total_docs_created INTEGER DEFAULT 0,
            last_reset_date TEXT DEFAULT '',
            joined_at TEXT DEFAULT '',
            is_banned INTEGER DEFAULT 0,
            streak_days INTEGER DEFAULT 0,
            last_active_date TEXT DEFAULT '',
            total_streak_bonus INTEGER DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            detail TEXT DEFAULT '',
            created_at TEXT DEFAULT ''
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            doc_hash TEXT DEFAULT '',
            rating INTEGER DEFAULT 0,
            comment TEXT DEFAULT '',
            created_at TEXT DEFAULT ''
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_hashes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_hash TEXT UNIQUE,
            user_id INTEGER,
            doc_type TEXT DEFAULT '',
            word_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT ''
        )
    """)
    
    # Yangi ustunlar eski DB uchun
    _add_column_if_not_exists(cursor, "users", "streak_days", "INTEGER DEFAULT 0")
    _add_column_if_not_exists(cursor, "users", "last_active_date", "TEXT DEFAULT ''")
    _add_column_if_not_exists(cursor, "users", "total_streak_bonus", "INTEGER DEFAULT 0")
    
    conn.commit()
    conn.close()


def _add_column_if_not_exists(cursor, table, column, col_type):
    """Agar ustun mavjud bo'lmasa qo'shish."""
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
    except sqlite3.OperationalError:
        pass  # Ustun allaqachon mavjud


def get_today_str():
    return datetime.date.today().isoformat()

def get_now_str():
    return datetime.datetime.now().isoformat(timespec='seconds')

def get_yesterday_str():
    return (datetime.date.today() - datetime.timedelta(days=1)).isoformat()


# ==================== FOYDALANUVCHI ====================

def register_user(user_id: int, first_name: str, username: str) -> bool:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    existing = cursor.fetchone()
    
    is_new = False
    
    if not existing:
        is_new = True
        cursor.execute(
            """INSERT INTO users 
               (user_id, first_name, username, daily_balance, total_docs_created, 
                last_reset_date, joined_at, streak_days, last_active_date) 
               VALUES (?, ?, ?, ?, 0, ?, ?, 0, ?)""",
            (user_id, first_name or '', username or '', DEFAULT_DAILY_LIMIT, 
             get_today_str(), get_now_str(), get_today_str())
        )
        log_activity(cursor, user_id, "joined", "organic")
    else:
        cursor.execute(
            "UPDATE users SET first_name = ?, username = ? WHERE user_id = ?",
            (first_name or '', username or '', user_id)
        )
    
    conn.commit()
    conn.close()
    return is_new

def log_activity(cursor, user_id: int, action: str, detail: str = ""):
    cursor.execute(
        "INSERT INTO activity_log (user_id, action, detail, created_at) VALUES (?, ?, ?, ?)",
        (user_id, action, detail, get_now_str())
    )


# ==================== STREAK TIZIMI ====================

def update_streak(user_id: int) -> dict:
    """Streak'ni yangilash va bonus tekshirish."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT streak_days, last_active_date FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return {"streak": 0, "bonus": 0, "new_bonus": False}
    
    today = get_today_str()
    yesterday = get_yesterday_str()
    last_active = user['last_active_date'] or ''
    streak = user['streak_days'] or 0
    
    bonus = 0
    new_bonus = False
    
    if last_active == today:
        # Bugun allaqachon yangilangan
        conn.close()
        return {"streak": streak, "bonus": 0, "new_bonus": False}
    elif last_active == yesterday:
        # Ketma-ket kun — streak oshadi
        streak += 1
    else:
        # Uzilish — qaytadan 1
        streak = 1
    
    # Bonus tekshirish
    if streak > 0 and streak % STREAK_BONUS_DAYS == 0:
        bonus = STREAK_BONUS_AMOUNT
        new_bonus = True
        cursor.execute(
            "UPDATE users SET daily_balance = daily_balance + ?, total_streak_bonus = total_streak_bonus + ? WHERE user_id = ?",
            (bonus, bonus, user_id)
        )
    
    cursor.execute(
        "UPDATE users SET streak_days = ?, last_active_date = ? WHERE user_id = ?",
        (streak, today, user_id)
    )
    
    conn.commit()
    conn.close()
    return {"streak": streak, "bonus": bonus, "new_bonus": new_bonus}


def get_streak(user_id: int) -> int:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT streak_days FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user['streak_days'] if user else 0


def get_leaderboard(limit: int = 10) -> list:
    """Top foydalanuvchilar (hujjatlar soni bo'yicha)."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT user_id, first_name, total_docs_created, streak_days 
           FROM users ORDER BY total_docs_created DESC LIMIT ?""",
        (limit,)
    )
    users = cursor.fetchall()
    conn.close()
    return [dict(u) for u in users]


def get_user_rank(user_id: int) -> int:
    """Foydalanuvchining reytingdagi o'rni."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) as rank FROM users WHERE total_docs_created > (SELECT COALESCE(total_docs_created, 0) FROM users WHERE user_id = ?)",
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return (row['rank'] + 1) if row else 0


# ==================== LIMIT ====================

def _reset_daily_if_needed(cursor, user: dict, user_id: int) -> int:
    balance = user['daily_balance']
    last_reset = user['last_reset_date']
    today = get_today_str()
    
    if last_reset != today:
        balance = DEFAULT_DAILY_LIMIT
        cursor.execute(
            "UPDATE users SET daily_balance = ?, last_reset_date = ? WHERE user_id = ?",
            (balance, today, user_id)
        )
    return balance

def check_and_deduct_limit(user_id: int) -> tuple:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT daily_balance, last_reset_date, is_banned FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return (False, 0)
    
    if user['is_banned']:
        conn.close()
        return (False, 0)
    
    balance = _reset_daily_if_needed(cursor, user, user_id)
    
    if balance > 0:
        cursor.execute(
            "UPDATE users SET daily_balance = daily_balance - 1, total_docs_created = total_docs_created + 1 WHERE user_id = ?",
            (user_id,)
        )
        log_activity(cursor, user_id, "doc_created", f"balance_before={balance}")
        conn.commit()
        conn.close()
        return (True, balance - 1)
    else:
        conn.commit()
        conn.close()
        return (False, 0)

def get_user_balance(user_id: int) -> int:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT daily_balance, last_reset_date FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return 0
    
    balance = _reset_daily_if_needed(cursor, user, user_id)
    conn.commit()
    conn.close()
    return balance


# ==================== FEEDBACK TIZIMI ====================

def save_feedback(user_id: int, doc_hash: str, rating: int, comment: str = ""):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO feedback (user_id, doc_hash, rating, comment, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, doc_hash, rating, comment, get_now_str())
    )
    conn.commit()
    conn.close()

def get_feedback_stats() -> dict:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total, AVG(rating) as avg_rating FROM feedback")
    row = cursor.fetchone()
    conn.close()
    return {
        "total": row['total'] if row else 0,
        "avg_rating": round(row['avg_rating'], 1) if row and row['avg_rating'] else 0,
    }


# ==================== HUJJAT HASH ====================

def generate_doc_hash(text: str, user_id: int) -> str:
    """Hujjat uchun unikal hash yaratish."""
    raw = f"{text[:500]}_{user_id}_{get_now_str()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

def save_doc_hash(doc_hash: str, user_id: int, doc_type: str, word_count: int):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO document_hashes (doc_hash, user_id, doc_type, word_count, created_at) VALUES (?, ?, ?, ?, ?)",
            (doc_hash, user_id, doc_type, word_count, get_now_str())
        )
    except sqlite3.IntegrityError:
        pass
    conn.commit()
    conn.close()

def verify_doc_hash(doc_hash: str) -> dict:
    """Hash bo'yicha hujjatni tekshirish."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT doc_hash, user_id, doc_type, word_count, created_at FROM document_hashes WHERE doc_hash = ?",
        (doc_hash,)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


# ==================== STATISTIKA ====================

def get_user_stats() -> dict:
    conn = get_conn()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as cnt FROM users")
    total_users = cursor.fetchone()['cnt']
    
    today = get_today_str()
    cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE last_reset_date = ?", (today,))
    today_active = cursor.fetchone()['cnt']
    
    cursor.execute("SELECT SUM(total_docs_created) as total FROM users")
    row = cursor.fetchone()
    total_docs = row['total'] if row['total'] else 0
    
    conn.close()
    return {
        "total_users": total_users,
        "today_active": today_active,
        "total_docs": total_docs,
    }

def get_all_users_list(limit: int = 50) -> list:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT user_id, first_name, username, daily_balance, total_docs_created, joined_at 
           FROM users ORDER BY rowid DESC LIMIT ?""",
        (limit,)
    )
    users = cursor.fetchall()
    conn.close()
    return [dict(u) for u in users]

def get_all_user_ids() -> list:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE is_banned = 0")
    user_ids = [row['user_id'] for row in cursor.fetchall()]
    conn.close()
    return user_ids
