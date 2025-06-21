"""
Simple database for storing game data and character progression.
"""

import sqlite3
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

class GameDatabase:
    """Simple SQLite database for game data and character progression."""
    
    def __init__(self, db_path: str = "game_data.db"):
        """Initialize the database."""
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Initialize the database tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create character progression table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS character_progression (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL DEFAULT 'Thranduil',
                    level INTEGER NOT NULL DEFAULT 1,
                    current_exp INTEGER NOT NULL DEFAULT 0,
                    total_exp INTEGER NOT NULL DEFAULT 0,
                    games_played INTEGER NOT NULL DEFAULT 0,
                    total_enemies_killed INTEGER NOT NULL DEFAULT 0,
                    total_waves_completed INTEGER NOT NULL DEFAULT 0,
                    total_towers_built INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # Create game sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    wave_reached INTEGER NOT NULL,
                    enemies_killed INTEGER NOT NULL,
                    towers_built INTEGER NOT NULL,
                    allies_summoned INTEGER NOT NULL,
                    time_elapsed REAL NOT NULL
                )
            ''')
            
            # Create high scores table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS high_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT DEFAULT 'Player',
                    score INTEGER NOT NULL,
                    wave_reached INTEGER NOT NULL,
                    timestamp TEXT NOT NULL
                )
            ''')
            
            # Create saved games table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS saved_games (
                    id INTEGER PRIMARY KEY,
                    character_name TEXT NOT NULL,
                    character_level INTEGER NOT NULL,
                    save_timestamp TEXT NOT NULL,
                    game_state TEXT NOT NULL,
                    wave_number INTEGER NOT NULL,
                    score INTEGER NOT NULL,
                    essence INTEGER NOT NULL,
                    castle_health INTEGER NOT NULL,
                    time_elapsed REAL NOT NULL
                )
            ''')
            
            # Migrate existing tables - add missing columns
            self._migrate_database_schema(cursor)
            
            # Initialize character if it doesn't exist
            cursor.execute('SELECT COUNT(*) FROM character_progression')
            if cursor.fetchone()[0] == 0:
                now = datetime.now().isoformat()
                cursor.execute('''
                    INSERT INTO character_progression 
                    (id, name, level, current_exp, total_exp, games_played, 
                     total_enemies_killed, total_waves_completed, total_towers_built,
                     created_at, updated_at)
                    VALUES (1, 'Thranduil', 1, 0, 0, 0, 0, 0, 0, ?, ?)
                ''', (now, now))
            
            conn.commit()
            
    def _migrate_database_schema(self, cursor):
        """Migrate existing database schema to add missing columns."""
        try:
            # Check and add missing columns to game_sessions table
            cursor.execute("PRAGMA table_info(game_sessions)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'exp_gained' not in columns:
                cursor.execute('ALTER TABLE game_sessions ADD COLUMN exp_gained INTEGER NOT NULL DEFAULT 0')
                print("✅ Added exp_gained column to game_sessions table")
                
            if 'character_level_start' not in columns:
                cursor.execute('ALTER TABLE game_sessions ADD COLUMN character_level_start INTEGER NOT NULL DEFAULT 1')
                print("✅ Added character_level_start column to game_sessions table")
                
            if 'character_level_end' not in columns:
                cursor.execute('ALTER TABLE game_sessions ADD COLUMN character_level_end INTEGER NOT NULL DEFAULT 1')
                print("✅ Added character_level_end column to game_sessions table")
                
        except Exception as e:
            print(f"⚠️  Migration warning for game_sessions: {e}")
            
        try:
            # Check and add missing columns to high_scores table
            cursor.execute("PRAGMA table_info(high_scores)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'character_level' not in columns:
                cursor.execute('ALTER TABLE high_scores ADD COLUMN character_level INTEGER NOT NULL DEFAULT 1')
                print("✅ Added character_level column to high_scores table")
                
        except Exception as e:
            print(f"⚠️  Migration warning for high_scores: {e}")
            
        try:
            # Check and add missing columns to character_progression table
            cursor.execute("PRAGMA table_info(character_progression)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'name' not in columns:
                cursor.execute('ALTER TABLE character_progression ADD COLUMN name TEXT DEFAULT "Thranduil"')
                print("✅ Added name column to character_progression table")
                
        except Exception as e:
            print(f"⚠️  Migration warning for character_progression: {e}")
            
    def get_character_data(self) -> Dict[str, Any]:
        """Get current character progression data."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, level, current_exp, total_exp, games_played,
                       total_enemies_killed, total_waves_completed, total_towers_built
                FROM character_progression WHERE id = 1
            ''')
            
            row = cursor.fetchone()
            if row:
                return {
                    'name': row[0],
                    'level': row[1],
                    'current_exp': row[2],
                    'total_exp': row[3],
                    'games_played': row[4],
                    'total_enemies_killed': row[5],
                    'total_waves_completed': row[6],
                    'total_towers_built': row[7]
                }
            else:
                # Fallback if no character data exists
                return {
                    'name': 'Thranduil',
                    'level': 1,
                    'current_exp': 0,
                    'total_exp': 0,
                    'games_played': 0,
                    'total_enemies_killed': 0,
                    'total_waves_completed': 0,
                    'total_towers_built': 0
                }
    
    def add_character_exp(self, exp_amount: int) -> Dict[str, Any]:
        """Add EXP to character and handle level ups. Returns level up info."""
        from ..game.constants import get_exp_requirement_for_level
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get current character data
            cursor.execute('''
                SELECT level, current_exp, total_exp FROM character_progression WHERE id = 1
            ''')
            
            row = cursor.fetchone()
            if not row:
                return {'level_up': False, 'old_level': 1, 'new_level': 1}
                
            current_level, current_exp, total_exp = row
            old_level = current_level
            
            # Add EXP
            new_current_exp = current_exp + exp_amount
            new_total_exp = total_exp + exp_amount
            
            # Check for level ups
            new_level = current_level
            while True:
                exp_needed = get_exp_requirement_for_level(new_level + 1)
                if new_current_exp >= exp_needed and exp_needed > 0:
                    new_current_exp -= exp_needed
                    new_level += 1
                else:
                    break
            
            # Update database
            cursor.execute('''
                UPDATE character_progression 
                SET level = ?, current_exp = ?, total_exp = ?, updated_at = ?
                WHERE id = 1
            ''', (new_level, new_current_exp, new_total_exp, datetime.now().isoformat()))
            
            conn.commit()
            
            return {
                'level_up': new_level > old_level,
                'old_level': old_level,
                'new_level': new_level,
                'levels_gained': new_level - old_level,
                'exp_gained': exp_amount
            }
    
    def update_character_stats(self, enemies_killed: int = 0, waves_completed: int = 0, 
                             towers_built: int = 0, games_played: int = 0):
        """Update character statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE character_progression 
                SET total_enemies_killed = total_enemies_killed + ?,
                    total_waves_completed = total_waves_completed + ?,
                    total_towers_built = total_towers_built + ?,
                    games_played = games_played + ?,
                    updated_at = ?
                WHERE id = 1
            ''', (enemies_killed, waves_completed, towers_built, games_played, 
                  datetime.now().isoformat()))
            
            conn.commit()
            
    def save_game_session(self, game_data: Dict[str, Any]) -> int:
        """Save a game session to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            # Get character level info within the same connection
            cursor.execute('''
                SELECT name, level, current_exp, total_exp, games_played,
                       total_enemies_killed, total_waves_completed, total_towers_built
                FROM character_progression WHERE id = 1
            ''')
            
            row = cursor.fetchone()
            if row:
                char_data = {
                    'name': row[0],
                    'level': row[1],
                    'current_exp': row[2],
                    'total_exp': row[3],
                    'games_played': row[4],
                    'total_enemies_killed': row[5],
                    'total_waves_completed': row[6],
                    'total_towers_built': row[7]
                }
            else:
                char_data = {
                    'name': 'Thranduil',
                    'level': 1,
                    'current_exp': 0,
                    'total_exp': 0,
                    'games_played': 0,
                    'total_enemies_killed': 0,
                    'total_waves_completed': 0,
                    'total_towers_built': 0
                }
            
            character_level_start = game_data.get('character_level_start', char_data['level'])
            character_level_end = char_data['level']
            exp_gained = game_data.get('exp_gained', 0)
            
            # Try to insert with new columns first
            try:
                cursor.execute('''
                    INSERT INTO game_sessions 
                    (timestamp, score, wave_reached, enemies_killed, towers_built, 
                     allies_summoned, time_elapsed, exp_gained, character_level_start, character_level_end)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    timestamp,
                    game_data['score'],
                    game_data['wave_reached'],
                    game_data['enemies_killed'],
                    game_data['towers_built'],
                    game_data['allies_summoned'],
                    game_data['time_elapsed'],
                    exp_gained,
                    character_level_start,
                    character_level_end
                ))
            except sqlite3.OperationalError as e:
                if "no column named" in str(e):
                    # Fallback to old schema if new columns don't exist
                    print(f"⚠️  Using fallback save method: {e}")
                    cursor.execute('''
                        INSERT INTO game_sessions 
                        (timestamp, score, wave_reached, enemies_killed, towers_built, allies_summoned, time_elapsed)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        timestamp,
                        game_data['score'],
                        game_data['wave_reached'],
                        game_data['enemies_killed'],
                        game_data['towers_built'],
                        game_data['allies_summoned'],
                        game_data['time_elapsed']
                    ))
                else:
                    raise  # Re-raise if it's a different error
            
            session_id = cursor.lastrowid or 0
            
            # Update character stats within the same connection
            cursor.execute('''
                UPDATE character_progression 
                SET total_enemies_killed = total_enemies_killed + ?,
                    total_waves_completed = total_waves_completed + ?,
                    total_towers_built = total_towers_built + ?,
                    games_played = games_played + ?,
                    updated_at = ?
                WHERE id = 1
            ''', (game_data['enemies_killed'], game_data['wave_reached'], 
                  game_data['towers_built'], 1, datetime.now().isoformat()))
            
            # Check if this is a high score
            self._check_and_save_high_score(cursor, game_data, timestamp, char_data)
            
            conn.commit()
            return session_id
            
    def _check_and_save_high_score(self, cursor, game_data: Dict[str, Any], timestamp: str, char_data: Dict[str, Any]):
        """Check if the score qualifies as a high score and save it."""
        score = game_data['score']
        wave_reached = game_data['wave_reached']
        character_level = char_data['level']
        character_name = char_data['name']
        
        # Get current high scores count
        cursor.execute('SELECT COUNT(*) FROM high_scores')
        high_score_count = cursor.fetchone()[0]
        
        if high_score_count < 10:
            # Less than 10 high scores, automatically add
            try:
                cursor.execute('''
                    INSERT INTO high_scores (player_name, score, wave_reached, character_level, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (character_name, score, wave_reached, character_level, timestamp))
            except sqlite3.OperationalError as e:
                if "no column named" in str(e):
                    # Fallback to old schema
                    print(f"⚠️  Using fallback high score save: {e}")
                    cursor.execute('''
                        INSERT INTO high_scores (player_name, score, wave_reached, timestamp)
                        VALUES (?, ?, ?, ?)
                    ''', (character_name, score, wave_reached, timestamp))
                else:
                    raise
        else:
            # Check if score beats the lowest high score
            cursor.execute('SELECT MIN(score) FROM high_scores')
            lowest_score = cursor.fetchone()[0]
            
            if score > lowest_score:
                # Remove the lowest score
                cursor.execute('DELETE FROM high_scores WHERE score = ? LIMIT 1', (lowest_score,))
                # Add the new high score
                try:
                    cursor.execute('''
                        INSERT INTO high_scores (player_name, score, wave_reached, character_level, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (character_name, score, wave_reached, character_level, timestamp))
                except sqlite3.OperationalError as e:
                    if "no column named" in str(e):
                        # Fallback to old schema
                        print(f"⚠️  Using fallback high score save: {e}")
                        cursor.execute('''
                            INSERT INTO high_scores (player_name, score, wave_reached, timestamp)
                            VALUES (?, ?, ?, ?)
                        ''', (character_name, score, wave_reached, timestamp))
                    else:
                        raise
                
    def get_high_scores(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the top high scores."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    SELECT player_name, score, wave_reached, character_level, timestamp
                    FROM high_scores
                    ORDER BY score DESC, wave_reached DESC
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                
                high_scores = []
                for row in rows:
                    high_scores.append({
                        'player_name': row[0],
                        'score': row[1],
                        'wave_reached': row[2],
                        'character_level': row[3],
                        'timestamp': row[4]
                    })
                    
            except sqlite3.OperationalError as e:
                if "no column named" in str(e):
                    # Fallback to old schema without character_level
                    print(f"⚠️  Using fallback high scores query: {e}")
                    cursor.execute('''
                        SELECT player_name, score, wave_reached, timestamp
                        FROM high_scores
                        ORDER BY score DESC, wave_reached DESC
                        LIMIT ?
                    ''', (limit,))
                    
                    rows = cursor.fetchall()
                    
                    high_scores = []
                    for row in rows:
                        high_scores.append({
                            'player_name': row[0],
                            'score': row[1],
                            'wave_reached': row[2],
                            'character_level': 1,  # Default value for old records
                            'timestamp': row[3]
                        })
                else:
                    raise
                
            return high_scores
            
    def get_game_stats(self) -> Dict[str, Any]:
        """Get overall game statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total games played
            cursor.execute('SELECT COUNT(*) FROM game_sessions')
            total_games = cursor.fetchone()[0]
            
            # Average score
            cursor.execute('SELECT AVG(score) FROM game_sessions')
            avg_score = cursor.fetchone()[0] or 0
            
            # Highest wave reached
            cursor.execute('SELECT MAX(wave_reached) FROM game_sessions')
            highest_wave = cursor.fetchone()[0] or 0
            
            # Total enemies killed
            cursor.execute('SELECT SUM(enemies_killed) FROM game_sessions')
            total_enemies_killed = cursor.fetchone()[0] or 0
            
            # Total time played
            cursor.execute('SELECT SUM(time_elapsed) FROM game_sessions')
            total_time_played = cursor.fetchone()[0] or 0
            
            # Character progression stats
            char_data = self.get_character_data()
            
            return {
                'total_games': total_games,
                'average_score': round(avg_score, 2),
                'highest_wave': highest_wave,
                'total_enemies_killed': total_enemies_killed,
                'total_time_played': round(total_time_played, 2),
                'character_level': char_data['level'],
                'character_total_exp': char_data['total_exp']
            }
    
    def update_character_name(self, name: str):
        """Update character name."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE character_progression 
                SET name = ?, updated_at = ?
                WHERE id = 1
            ''', (name, datetime.now().isoformat()))
            
            conn.commit()
            
    def save_game_state(self, game_state_data: Dict[str, Any]) -> bool:
        """Save a game state that can be resumed later."""
        import json
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get character info
                char_data = self.get_character_data()
                
                # Convert game state to JSON
                game_state_json = json.dumps(game_state_data['game_state'])
                
                # Save or update the saved game (only keep one save per character)
                cursor.execute('''
                    INSERT OR REPLACE INTO saved_games 
                    (id, character_name, character_level, save_timestamp, game_state, 
                     wave_number, score, essence, castle_health, time_elapsed)
                    VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    char_data['name'],
                    char_data['level'],
                    datetime.now().isoformat(),
                    game_state_json,
                    game_state_data['wave_number'],
                    game_state_data['score'],
                    game_state_data['essence'],
                    game_state_data['castle_health'],
                    game_state_data['time_elapsed']
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"❌ Failed to save game: {e}")
            return False
            
    def load_saved_game(self) -> Optional[Dict[str, Any]]:
        """Load the saved game state if it exists."""
        import json
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT character_name, character_level, save_timestamp, game_state,
                           wave_number, score, essence, castle_health, time_elapsed
                    FROM saved_games WHERE id = 1
                ''')
                
                row = cursor.fetchone()
                if row:
                    game_state = json.loads(row[3])
                    
                    return {
                        'character_name': row[0],
                        'character_level': row[1],
                        'save_timestamp': row[2],
                        'game_state': game_state,
                        'wave_number': row[4],
                        'score': row[5],
                        'essence': row[6],
                        'castle_health': row[7],
                        'time_elapsed': row[8]
                    }
                    
        except Exception as e:
            print(f"❌ Failed to load saved game: {e}")
            
        return None
        
    def has_saved_game(self) -> bool:
        """Check if there's a saved game available."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM saved_games WHERE id = 1')
                count = cursor.fetchone()[0]
                
                return count > 0
                
        except Exception as e:
            print(f"❌ Failed to check for saved game: {e}")
            return False
            
    def get_saved_game_info(self) -> Optional[Dict[str, Any]]:
        """Get basic info about the saved game for display purposes."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT character_name, character_level, save_timestamp, 
                           wave_number, score, essence, castle_health, time_elapsed
                    FROM saved_games WHERE id = 1
                ''')
                
                row = cursor.fetchone()
                if row:
                    return {
                        'character_name': row[0],
                        'character_level': row[1],
                        'save_timestamp': row[2],
                        'wave_number': row[3],
                        'score': row[4],
                        'essence': row[5],
                        'castle_health': row[6],
                        'time_elapsed': row[7]
                    }
                    
        except Exception as e:
            print(f"❌ Failed to get saved game info: {e}")
            
        return None
        
    def delete_saved_game(self) -> bool:
        """Delete the saved game."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM saved_games WHERE id = 1')
                conn.commit()
                
                return True
                
        except Exception as e:
            print(f"❌ Failed to delete saved game: {e}")
            return False 