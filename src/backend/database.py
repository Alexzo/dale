"""
Simple database for storing game data.
"""

import sqlite3
import os
from typing import Dict, Any, List
from datetime import datetime

class GameDatabase:
    """Simple SQLite database for game data."""
    
    def __init__(self, db_path: str = "game_data.db"):
        """Initialize the database."""
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Initialize the database tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
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
            
            conn.commit()
            
    def save_game_session(self, game_data: Dict[str, Any]) -> int:
        """Save a game session to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
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
            
            session_id = cursor.lastrowid or 0
            
            # Check if this is a high score
            self._check_and_save_high_score(cursor, game_data, timestamp)
            
            conn.commit()
            return session_id
            
    def _check_and_save_high_score(self, cursor, game_data: Dict[str, Any], timestamp: str):
        """Check if the score qualifies as a high score and save it."""
        score = game_data['score']
        wave_reached = game_data['wave_reached']
        
        # Get current high scores count
        cursor.execute('SELECT COUNT(*) FROM high_scores')
        high_score_count = cursor.fetchone()[0]
        
        if high_score_count < 10:
            # Less than 10 high scores, automatically add
            cursor.execute('''
                INSERT INTO high_scores (score, wave_reached, timestamp)
                VALUES (?, ?, ?)
            ''', (score, wave_reached, timestamp))
        else:
            # Check if score beats the lowest high score
            cursor.execute('SELECT MIN(score) FROM high_scores')
            lowest_score = cursor.fetchone()[0]
            
            if score > lowest_score:
                # Remove the lowest score
                cursor.execute('DELETE FROM high_scores WHERE score = ? LIMIT 1', (lowest_score,))
                # Add the new high score
                cursor.execute('''
                    INSERT INTO high_scores (score, wave_reached, timestamp)
                    VALUES (?, ?, ?)
                ''', (score, wave_reached, timestamp))
                
    def get_high_scores(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the top high scores."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
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
                    'timestamp': row[3]
                })
                
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
            
            return {
                'total_games': total_games,
                'average_score': round(avg_score, 2),
                'highest_wave': highest_wave,
                'total_enemies_killed': total_enemies_killed,
                'total_time_played': round(total_time_played, 2)
            } 