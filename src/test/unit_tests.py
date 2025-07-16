from src.data_handler import DataHandler

def test_get_user_by_alias_1():
    # Test with a valid user alias
    data = DataHandler()
    data.users = [
        {"id": 1, "alias": "testuser", "nombre": "Test"}]
    result = data.get_user_by_alias("testuser")
    assert result == {"id": 1, "alias": "testuser", "nombre": "Test"}

def test_get_user_by_alias_2():
    # Test with an invalid user alias
    data = DataHandler()
    data.users = []
    result = data.get_user_by_alias("testuser")
    assert result is None

def test_get_user_by_alias_3():
    # Test with an empty user alias
    data = DataHandler()
    data.users = [{"id": 1, "alias": "testuser", "nombre": "Test"}]
    result = data.get_user_by_alias("test")
    assert result is None

def test_get_user_by_alias_4():
    # Test with a user alias that has special characters
    data = DataHandler()
    data.users = [{"id": 1, "alias": "testuser", "nombre": "Test"}]
    result = data.get_user_by_alias("")
    assert result is None

def test_create_user_1():
    # Test creating a user with valid data
    data = DataHandler()
    new_user = {"contacto": "newuser", "nombre": "New User"}
    data.create_user(new_user)
    assert len(data.users) == 1
    assert data.users[0]['alias'] == "newuser"
    assert data.users[0]['nombre'] == "New User"

def test_create_user_2():
    # Test creating a user with missing fields
    data = DataHandler()
    new_user = {}
    data.create_user(new_user)
    assert len(data.users) == 0

def test_create_user_3():
    # Test creating a user with an existing alias
    data = DataHandler()
    data.users = [{"id": 1, "alias": "existinguser", "nombre": "Existing User"}]
    new_user = {"contacto": "existinguser"}
    data.create_user(new_user)
    assert len(data.users) == 1  # Should not create a duplicate user
    assert data.users[0]['alias'] == "existinguser"

def test_create_user_4():
    # Test creating a user with an empty alias
    data = DataHandler()
    new_user = {"contacto": "", "nombre": ""}
    data.create_user(new_user)
    assert len(data.users) == 0

def test_create_task_1():
    # Test creating a task with valid data
    data = DataHandler()
    new_task = {"nombre": "New Task", "descripcion": "Task Description", "usuario": "testuser", "rol": "Infraestructura"}
    data.users = [{"id": 1, "alias": "testuser", "nombre": "Test User"}]
    res = data.create_task(new_task)
    assert res is not None
    assert len(data.tasks) == 1
    assert data.tasks[0]['nombre'] == "New Task"
    assert data.tasks[0]['descripcion'] == "Task Description"
    assert data.tasks[0]['usuario'] == 1

def test_create_task_2():
    # Test creating a task with missing fields
    data = DataHandler()
    new_task = {"nombre": "Incomplete Task"}
    res = data.create_task(new_task)
    assert res is None
    assert len(data.tasks) == 0


def test_create_task_3():
    # Test creating a task with an invalid role
    data = DataHandler()
    new_task = {"nombre": "Invalid Role Task", "descripcion": "Task Description", "usuario": "testuser", "rol": "InvalidRole"}
    data.users = [{"id": 1, "alias": "testuser", "nombre": "Test User"}]
    res = data.create_task(new_task)
    assert res is None
    assert len(data.tasks) == 0

def test_create_task_4():
    # Test creating a task with an empty user alias
    data = DataHandler()
    new_task = {"nombre": "Empty User Task", "descripcion": "Task Description", "usuario": "", "rol": "Infraestructura"}
    res = data.create_task(new_task)
    assert res is None
    assert len(data.tasks) == 0

def test_update_state_task_1():
    # Test updating task state with valid data
    data = DataHandler()
    data.tasks = [{"id": 1, "estado": "Nueva"}]
    new_state = {"estado": "En Progreso"}
    res = data.update_task_state(1, new_state['estado'])
    assert res is not None
    assert res['estado'] == "Completado"

def test_update_state_task_2():
    # Test updating task state with an invalid task ID
    data = DataHandler()
    data.tasks = [{"id": 1, "estado": "Nueva"}]
    new_state = {"estado": "En Progreso"}
    res = data.update_task_state('2', new_state['estado'])
    assert res is None
    assert data.tasks[0]['estado'] == "Nueva"

def test_update_state_task_3():
    # Test updating task state with an not existing state
    data = DataHandler()
    data.tasks = [{"id": 1, "estado": "Nueva"}]
    new_state = {"estado": "InvalidState"}
    res = data.update_task_state(1, new_state['estado'])
    assert res is None
    assert data.tasks[0]['estado'] == "Nueva"

def test_update_state_task_4():
    # Test updating task state with an invalid state
    data = DataHandler()
    data.tasks = [{"id": 1, "estado": "Nueva"}]
    new_state = {"estado": "Finalizada"}
    res = data.update_task_state(1, new_state['estado'])
    assert res is None
    assert data.tasks[0]['estado'] == "Nueva"

def test_create_assignment_1():
    # Test creating an assignment with valid data
    data = DataHandler()
    data.tasks = [{"id": 1, "nombre": "Test Task"}]
    new_assignment = {"usuario": "testuser", "rol": "Analisis"}
    data.users = [{"id": 1, "alias": "testuser", "nombre": "Test User"}]
    res = data.create_assignment(1, new_assignment)
    assert res is not None
    assert len(data.asignaciones) == 1
    assert data.asignaciones[0]['usuarioAsignado'] == 1