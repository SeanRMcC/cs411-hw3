from contextlib import contextmanager
import re
import sqlite3

import pytest

from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    clear_meals,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats
)

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    @contextmanager
    def mock_get_db_connection():
        yield mock_conn
    
    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor

# Tests for create_meal

def test_create_meal(mock_cursor):
    """Test creating a new meal in the meals table"""

    create_meal(meal="Pad Tai", cuisine="Tai", price=10.0, difficulty="MED")

    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)                            
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]

    expected_arguments = ("Pad Tai", "Tai", 10.0, "MED")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}."

def test_create_meal_duplicate(mock_cursor):
    """Test creating a meal with a duplicate name (should raise an error)."""

    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meals.meal")

    with pytest.raises(ValueError, match="Meal with name 'Pad Tai' already exists"):
        create_meal(meal="Pad Tai", cuisine="Tai", price=10.0, difficulty="MED")

def test_create_meal_invalid_price():
    """Test error when trying to create a meal with an invalid price (non-positive price)"""

    with pytest.raises(ValueError, match="Invalid price: -2. Price must be a positive number."):
        create_meal(meal="Pad Tai", cuisine="Tai", price=-2, difficulty="MED")

    with pytest.raises(ValueError, match="Invalid price: invalid. Price must be a positive number."):
        create_meal(meal="Pad Tai", cuisine="Tai", price="invalid", difficulty="MED")

def test_create_meal_invalid_difficulty():
    """Test error when trying to create a meal with an invalid difficulty (not in LOW, MED, or HIGH)"""

    with pytest.raises(ValueError, match="Invalid difficulty level: HARD. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Pad Tai", cuisine="Tai", price=10.0, difficulty="HARD")

# Tests for clear_meals

def test_clear_meals(mock_cursor, mocker):
    """Test clearing the entire meals table (removes all meals)."""

    mocker.patch.dict("os.environ", {"SQL_CREATE_TABLE_PATH": "sql/create_meal_table.sql"})
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data="The body of the create statement"))

    clear_meals()

    mock_open.assert_called_once_with("sql/create_meal_table.sql", "r")

    mock_cursor.executescript.assert_called_once()

# Tests for delete_meal

def test_delete_meal(mock_cursor):
    """Test soft deleting a meal from the meals table by meal_id."""

    mock_cursor.fetchone.return_value = ([False])

    delete_meal(1)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")

    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."

def test_delete_meal_bad_id(mock_cursor):
    """Test error when trying to delete a non_existent meal."""

    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)

def test_delete_meal_already_deleted(mock_cursor):
    """Test error when trying to delete a song that's already marked as deleted."""

    mock_cursor.fetchone.return_value = ([True])

    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted"):
        delete_meal(999)

# Tests for get_meal_by_id

def test_get_meal_by_id(mock_cursor):
    """Test retrieving a meal by its id."""

    mock_cursor.fetchone.return_value = (1, "Pad Tai", "Tai", 10.0, "MED", False)

    result = get_meal_by_id(1)

    expected_result = Meal(1, "Pad Tai", "Tai", 10.0, "MED")

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]

    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_meal_by_id_bad_id(mock_cursor):
    """Test retrieving a meal by id with id that doesn't exist."""

    mock_cursor.fetchone.return_value = None
    
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)

# Tests for get_meal_by_name

def test_get_meal_by_name(mock_cursor):
    """Test retrieving a meal by its name."""

    mock_cursor.fetchone.return_value = (1, "Pad Tai", "Tai", 10.0, "MED", False)

    result = get_meal_by_name("Pad Tai")

    expected_result = Meal(1, "Pad Tai", "Tai", 10.0, "MED")

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]

    expected_arguments = ("Pad Tai",)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_meal_by_name_bad_name(mock_cursor):
    """Test retrieving a meal by a name that doesn't exist (should raise an error)."""

    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with name Chicken Tenders not found"):
        get_meal_by_name("Chicken Tenders")

# Test update_meal_stats 

def test_update_meal_stats_win(mock_cursor):
    """Test updating the stats of a meal after a win."""

    mock_cursor.fetchone.return_value = [False]

    meal_id = 1
    result = "win"
    update_meal_stats(meal_id, result)

    expected_query = normalize_whitespace("UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?")

    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_update_meal_stats_loss(mock_cursor):
    """Test updating the stats of a meal after a loss."""

    mock_cursor.fetchone.return_value = [False]

    meal_id = 1
    result = "loss"
    update_meal_stats(meal_id, result)

    expected_query = normalize_whitespace("UPDATE meals SET battles = battles + 1 WHERE id = ?")

    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_update_meal_stats_deleted_meal(mock_cursor):
    """Test updating the stats of a deleted meal (error should be raised)."""

    mock_cursor.fetchone.return_value = [True]

    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(1, "win")

    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM meals WHERE id = ?", (1,))

def test_update_meal_stats_bad_meal_id(mock_cursor):
    """Test updating the stats of a meal with an invalid meal_id (error should be raised)."""

    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        update_meal_stats(999, "win")

# Tests for get_leaderboard

def test_get_leaderboard(mock_cursor):
    """Test getting leaderboard with sort_by of wins."""

    mock_cursor.fetchall.return_value = [
        (1, "Pad Tai", "Tai", 10.0, "MED", 10, 9, .9),
        (2, "Lasagna", "Italian", 30, "MED", 5, 4, .8),
        (3, "Pizza", "New York", 5.0, "LOW", 20, 15, .75)
    ]

    actual_leaderboard = get_leaderboard()

    expected_leaderboard = [
        {"id": 1, "meal": "Pad Tai", "cuisine": "Tai", "price": 10.0, "difficulty": "MED", "battles": 10, "wins": 9, "win_pct": 90.0},
        {"id": 2, "meal": "Lasagna", "cuisine": "Italian", "price": 30, "difficulty": "MED", "battles": 5, "wins": 4, "win_pct": 80.0},
        {"id": 3, "meal": "Pizza", "cuisine": "New York", "price": 5.0, "difficulty": "LOW", "battles": 20, "wins": 15, "win_pct": 75.0}
    ]

    assert actual_leaderboard == expected_leaderboard, f"Expected {expected_leaderboard}, but got {actual_leaderboard}"

    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0
        ORDER BY wins DESC
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_leaderboard_win_pct(mock_cursor):
    """Test getting leaderboard with sort_by of win_pct."""

    get_leaderboard("win_pct")

    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0
        ORDER BY win_pct DESC
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_leaderboard_invalid_sort_by():
    """Tests getting leaderboard with invalid sort_by (error should be raises)."""

    with pytest.raises(ValueError, match="Invalid sort_by parameter: meal"):
        get_leaderboard("meal")