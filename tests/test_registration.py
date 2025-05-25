import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users

@pytest.fixture(scope="module")
def setup_database():
    """Фикстура для настройки базы данных перед тестами и её очистки после."""
    create_db()
    yield
    try:
        os.remove('users.db')
    except PermissionError:
        pass

@pytest.fixture
def connection():
    """Фикстура для получения соединения с базой данных и его закрытия после теста."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()


def test_create_db(setup_database, connection):
    """Тест создания базы данных и таблицы пользователей."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "Таблица 'users' должна существовать в базе данных."

def test_add_new_user(setup_database, connection):
    """Тест добавления нового пользователя."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user, "Пользователь должен быть добавлен в базу данных."

def test_add_existing_user(setup_database):
    """Тест добавления пользователя с уже существующим логином."""
    add_user('duplicateuser', 'user1@example.com', 'pass1')
    result = add_user('duplicateuser', 'user2@example.com', 'pass2')
    assert result is False, "Нельзя добавить пользователя с существующим логином."

def test_authenticate_valid_user(setup_database):
    """Тест успешной аутентификации пользователя."""
    add_user('validuser', 'valid@example.com', 'securepass')
    result = authenticate_user('validuser', 'securepass')
    assert result, "Аутентификация должна пройти успешно с правильным логином и паролем."

def test_authenticate_invalid_username(setup_database):
    """Тест аутентификации несуществующего пользователя."""
    result = authenticate_user('nosuchuser', 'anyPassword')
    assert result is False, "Аутентификация должна провалиться для несуществующего пользователя."

def test_authenticate_wrong_password(setup_database):
    """Тест аутентификации с неправильным паролем."""
    add_user('wrongpassuser', 'wrong@example.com', 'correctpass')
    result = authenticate_user('wrongpassuser', 'incorrectpass')
    assert result is False, "Аутентификация должна провалиться с неправильным паролем."

def test_display_users(capsys, setup_database):
    """Тест отображения списка пользователей (проверка вывода в stdout)."""
    add_user('displayuser', 'display@example.com', 'pass')
    display_users()
    captured = capsys.readouterr()
    assert 'displayuser' in captured.out
    assert 'display@example.com' in captured.out
