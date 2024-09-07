import sqlite3

DB_PATH = "user_data.db"


class DatabaseUtils:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def _connect(self):
        """Connects to the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        return conn

    def add_cache(self, user_id, guild_id, category_id, tags=[]):
        """Adds a new cache (guild and category) for a user with optional tags."""
        conn = self._connect()
        cursor = conn.cursor()

        # Insert user if not already in users table
        cursor.execute(
            """
            INSERT OR IGNORE INTO users (user_id) VALUES (?)
        """,
            (user_id,),
        )

        # Insert cache (guild and category) for the user
        cursor.execute(
            """
            INSERT INTO caches (user_id, guild_id, category_id)
            VALUES (?, ?, ?)
        """,
            (user_id, guild_id, category_id),
        )
        cache_id = cursor.lastrowid

        # Insert tags if provided
        for tag in tags:
            cursor.execute(
                """
                INSERT INTO tags (cache_id, tag)
                VALUES (?, ?)
            """,
                (cache_id, tag),
            )

        conn.commit()
        conn.close()

    def update_tags(self, user_id, guild_id, category_id, new_tags):
        """Updates the tags for a given cache of a user identified by guild and category."""  # noqa E501
        conn = self._connect()
        cursor = conn.cursor()

        # Find the cache ID
        cursor.execute(
            """
            SELECT id FROM caches
            WHERE user_id = ? AND guild_id = ? AND category_id = ?
        """,
            (user_id, guild_id, category_id),
        )
        cache = cursor.fetchone()

        if cache:
            cache_id = cache[0]

            # Delete old tags
            cursor.execute(
                """
                DELETE FROM tags WHERE cache_id = ?
            """,
                (cache_id,),
            )

            # Insert new tags
            for tag in new_tags:
                cursor.execute(
                    """
                    INSERT INTO tags (cache_id, tag)
                    VALUES (?, ?)
                """,
                    (cache_id, tag),
                )

            conn.commit()
        else:
            print("Cache not found for the given user, guild, and category.")

        conn.close()

    def get_caches_for_user(self, user_id):
        """Retrieves all caches and their tags for a given user."""
        conn = self._connect()
        cursor = conn.cursor()

        # Fetch all caches for the user
        cursor.execute(
            """
            SELECT id, guild_id, category_id FROM caches WHERE user_id = ?
        """,
            (user_id,),
        )
        caches = cursor.fetchall()

        result = []
        for cache_id, guild_id, category_id in caches:
            # Fetch tags for each cache
            cursor.execute(
                """
                SELECT tag FROM tags WHERE cache_id = ?
            """,
                (cache_id,),
            )
            tags = [row[0] for row in cursor.fetchall()]
            result.append(
                {"guild_id": guild_id, "category_id": category_id, "tags": tags}
            )

        conn.close()
        return result

    def get_cache(self, user_id, guild_id, category_id):
        """Retrieves a specific cache (guild and category) and its tags for a given user."""  # noqa E501
        conn = self._connect()
        cursor = conn.cursor()

        # Fetch the cache for the user with the specified guild and category
        cursor.execute(
            """
            SELECT id FROM caches
            WHERE user_id = ? AND guild_id = ? AND category_id = ?
        """,
            (user_id, guild_id, category_id),
        )
        cache = cursor.fetchone()

        if cache:
            cache_id = cache[0]

            # Fetch tags for the cache
            cursor.execute(
                """
                SELECT tag FROM tags WHERE cache_id = ?
            """,
                (cache_id,),
            )
            tags = [row[0] for row in cursor.fetchall()]

            conn.close()

            return {"guild_id": guild_id, "category_id": category_id, "tags": tags}
        else:
            conn.close()
            return None

    def delete_cache(self, user_id, guild_id, category_id):
        """Deletes a cache and its tags for a specific user, guild, and category."""
        conn = self._connect()
        cursor = conn.cursor()

        # Find the cache ID
        cursor.execute(
            """
            SELECT id FROM caches
            WHERE user_id = ? AND guild_id = ? AND category_id = ?
        """,
            (user_id, guild_id, category_id),
        )
        cache = cursor.fetchone()

        if cache:
            cache_id = cache[0]

            # Delete tags for the cache
            cursor.execute(
                """
                DELETE FROM tags WHERE cache_id = ?
            """,
                (cache_id,),
            )

            # Delete the cache
            cursor.execute(
                """
                DELETE FROM caches WHERE id = ?
            """,
                (cache_id,),
            )

            conn.commit()
        else:
            print("Cache not found for the given user, guild, and category.")

        conn.close()

    def reset(self):
        conn = self._connect()
        cursor = conn.cursor()

        # Drop the tables
        cursor.execute("DROP TABLE IF EXISTS tags")
        cursor.execute("DROP TABLE IF EXISTS caches")
        cursor.execute("DROP TABLE IF EXISTS users")

        # Recreate the tables
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY
        )
        """
        )

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS caches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            guild_id INTEGER,
            category_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        """
        )

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cache_id INTEGER,
            tag TEXT,
            FOREIGN KEY (cache_id) REFERENCES caches (id)
        )
        """
        )

        conn.commit()
        conn.close()
        print("All data has been cleared, and the tables have been reset.")
