import psycopg2
from datetime import datetime, timedelta

# Remember to replace these with your actual database credentials
DB_CONFIG = {
    'dbname': 'EXAM',
    'user': 'postgres',
    'password': '123456',
    'host': 'localhost'
}

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    return psycopg2.connect(**DB_CONFIG)

## ------------------ USER PROFILE (CRUD) ------------------ ##

def create_user(name, email, weight):
    """Adds a new user to the database."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (name, email, weight_kg) VALUES (%s, %s, %s) RETURNING user_id;", (name, email, weight))
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def get_user_profile(user_id):
    """Retrieves a user's profile information."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, email, weight_kg FROM users WHERE user_id = %s;", (user_id,))
    user_profile = cur.fetchone()
    cur.close()
    conn.close()
    return user_profile

def update_user_profile(user_id, name, email, weight):
    """Updates an existing user's profile."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE users SET name = %s, email = %s, weight_kg = %s WHERE user_id = %s;", (name, email, weight, user_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def delete_user(user_id):
    """Deletes a user and all their related data."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Deleting related data first to maintain referential integrity
        cur.execute("DELETE FROM exercises WHERE workout_id IN (SELECT workout_id FROM workouts WHERE user_id = %s);", (user_id,))
        cur.execute("DELETE FROM workouts WHERE user_id = %s;", (user_id,))
        cur.execute("DELETE FROM friendships WHERE user_id = %s OR friend_id = %s;", (user_id, user_id))
        cur.execute("DELETE FROM goals WHERE user_id = %s;", (user_id,))
        cur.execute("DELETE FROM users WHERE user_id = %s;", (user_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

## ------------------ WORKOUTS & EXERCISES (CRUD) ------------------ ##

def create_workout(user_id, date, duration):
    """Logs a new workout session."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO workouts (user_id, workout_date, duration_minutes) VALUES (%s, %s, %s) RETURNING workout_id;", (user_id, date, duration))
        workout_id = cur.fetchone()[0]
        conn.commit()
        return workout_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def add_exercise_to_workout(workout_id, exercise_name, reps, sets, weight_lifted):
    """Adds a specific exercise to a workout."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO exercises (workout_id, exercise_name, reps, sets, weight_lifted_kg) VALUES (%s, %s, %s, %s, %s);", (workout_id, exercise_name, reps, sets, weight_lifted))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def get_user_workouts(user_id):
    """Retrieves all workouts for a specific user."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT workout_id, workout_date, duration_minutes FROM workouts WHERE user_id = %s ORDER BY workout_date DESC;", (user_id,))
    workouts = cur.fetchall()
    cur.close()
    conn.close()
    return workouts

def get_workout_exercises(workout_id):
    """Retrieves all exercises for a specific workout."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT exercise_name, reps, sets, weight_lifted_kg FROM exercises WHERE workout_id = %s;", (workout_id,))
    exercises = cur.fetchall()
    cur.close()
    conn.close()
    return exercises

## ------------------ FRIENDSHIPS (CRUD) ------------------ ##

def add_friendship(user_id, friend_id):
    """Adds a friendship connection between two users."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO friendships (user_id, friend_id) VALUES (%s, %s);", (user_id, friend_id))
        cur.execute("INSERT INTO friendships (user_id, friend_id) VALUES (%s, %s);", (friend_id, user_id))
        conn.commit()
    except psycopg2.IntegrityError:
        # Handles cases where friendship already exists
        conn.rollback()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def get_friends_list(user_id):
    """Retrieves a list of friends for a user."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT u.user_id, u.name FROM users u JOIN friendships f ON u.user_id = f.friend_id WHERE f.user_id = %s;", (user_id,))
    friends = cur.fetchall()
    cur.close()
    conn.close()
    return friends

def remove_friendship(user_id, friend_id):
    """Removes a friendship connection."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM friendships WHERE (user_id = %s AND friend_id = %s) OR (user_id = %s AND friend_id = %s);", (user_id, friend_id, friend_id, user_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

## ------------------ GOALS (CRUD) ------------------ ##

def create_goal(user_id, description, target):
    """Creates a new fitness goal."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO goals (user_id, goal_description, target_value) VALUES (%s, %s, %s);", (user_id, description, target))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def get_user_goals(user_id):
    """Retrieves all goals for a specific user."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT goal_id, goal_description, target_value, current_value, is_completed FROM goals WHERE user_id = %s;", (user_id,))
    goals = cur.fetchall()
    cur.close()
    conn.close()
    return goals

def update_goal_progress(goal_id, new_value, is_completed):
    """Updates the progress of a goal."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE goals SET current_value = %s, is_completed = %s WHERE goal_id = %s;", (new_value, is_completed, goal_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()
    
def delete_goal(goal_id):
    """Deletes a goal."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM goals WHERE goal_id = %s;", (goal_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

## ------------------ BUSINESS INSIGHTS ------------------ ##

def get_leaderboard(user_id):
    """
    Retrieves a leaderboard of friends ranked by total workout minutes
    for the current week.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Get the start of the current week (e.g., Sunday or Monday)
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday()) # Monday as start of week

        cur.execute("""
            SELECT
                u.name,
                COALESCE(SUM(w.duration_minutes), 0) AS total_workout_minutes
            FROM users AS u
            JOIN friendships AS f ON u.user_id = f.friend_id
            LEFT JOIN workouts AS w ON u.user_id = w.user_id AND w.workout_date >= %s
            WHERE f.user_id = %s
            GROUP BY u.name
            ORDER BY total_workout_minutes DESC;
        """, (start_of_week, user_id))
        leaderboard_data = cur.fetchall()
        return leaderboard_data
    except Exception as e:
        raise e
    finally:
        cur.close()
        conn.close()

def get_user_workout_summary(user_id):
    """
    Provides a summary of a user's workout data using aggregate functions.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT
                COUNT(w.workout_id) AS total_workouts,
                SUM(w.duration_minutes) AS total_duration,
                AVG(w.duration_minutes) AS avg_duration,
                MIN(w.duration_minutes) AS min_duration,
                MAX(w.duration_minutes) AS max_duration
            FROM workouts AS w
            WHERE w.user_id = %s;
        """, (user_id,))
        summary_data = cur.fetchone()
        return summary_data
    except Exception as e:
        raise e
    finally:
        cur.close()
        conn.close()