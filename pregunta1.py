from flask import Flask, jsonify, request
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

class RideStatus(Enum):
    READY = "ready"
    IN_PROGRESS = "inprogress"
    FINISHED = "finished"
    
class ParticipationStatus(Enum):
    WAITING = "waiting"
    REJECTED = "rejected"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "inprogress"
    COMPLETED = "completed"
    MISSING = "missing"
    NOT_MARKED = "notmarked"

class User:
    def __init__(self, alias: str, name: str, car_plate: Optional[str] = None):
        self.alias = alias
        self.name = name
        self.car_plate = car_plate  # None si no es conductor
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alias": self.alias,
            "name": self.name,
            "car_plate": self.car_plate
        }
        
    def is_driver(self) -> bool:
        return self.car_plate is not None

class RideParticipation:
    def __init__(self, participant: User, ride_id: int, destination: str, occupied_spaces: int):
        self.participant = participant
        self.ride_id = ride_id
        self.destination = destination
        self.occupied_spaces = occupied_spaces
        self.status = ParticipationStatus.WAITING
        self.confirmation = None  # será actualizado por el conductor
    
    def to_dict(self, include_stats: bool = False) -> Dict[str, Any]:
        result = {
            "confirmation": self.confirmation,
            "destination": self.destination,
            "occupiedSpaces": self.occupied_spaces,
            "status": self.status.value
        }
        
        if include_stats:
            # Obtener estadísticas de participación del usuario desde DataHandler
            stats = data_handler.get_user_ride_stats(self.participant.alias)
            participant_info = {
                "alias": self.participant.alias,
                "previousRidesTotal": stats["total"],
                "previousRidesCompleted": stats["completed"],
                "previousRidesMissing": stats["missing"],
                "previousRidesNotMarked": stats["not_marked"],
                "previousRidesRejected": stats["rejected"]
            }
            result["participant"] = participant_info
        else:
            result["participant"] = {"alias": self.participant.alias}
            
        return result
        
class Ride:
    def __init__(self, id: int, date_time: datetime, final_address: str, allowed_spaces: int, driver: User):
        self.id = id
        self.date_time = date_time
        self.final_address = final_address
        self.allowed_spaces = allowed_spaces
        self.driver = driver
        self.status = RideStatus.READY
        self.participations: List[RideParticipation] = []
    
    def available_spaces(self) -> int:
        occupied = sum(p.occupied_spaces for p in self.participations 
                      if p.status in [ParticipationStatus.CONFIRMED, ParticipationStatus.IN_PROGRESS])
        return self.allowed_spaces - occupied
    
    def to_dict(self, include_participants: bool = True, include_stats: bool = False) -> Dict[str, Any]:
        ride_dict = {
            "id": self.id,
            "rideDateAndTime": self.date_time.strftime("%Y/%m/%d %H:%M"),
            "finalAddress": self.final_address,
            "driver": self.driver.alias,
            "status": self.status.value,
            "allowedSpaces": self.allowed_spaces,
            "availableSpaces": self.available_spaces()
        }
        
        if include_participants:
            ride_dict["participants"] = [p.to_dict(include_stats) for p in self.participations]
        
        return ride_dict

class DataHandler:
    def __init__(self):
        self.users: Dict[str, User] = {}  # alias -> User
        self.rides: Dict[int, Ride] = {}  # id -> Ride
        self.next_ride_id = 1
        
    def add_user(self, user: User) -> None:
        self.users[user.alias] = user
        
    def get_user(self, alias: str) -> Optional[User]:
        return self.users.get(alias)
        
    def get_all_users(self) -> List[User]:
        return list(self.users.values())
    
    def create_ride(self, date_time: datetime, final_address: str, allowed_spaces: int, driver: User) -> Ride:
        ride = Ride(self.next_ride_id, date_time, final_address, allowed_spaces, driver)
        self.rides[ride.id] = ride
        self.next_ride_id += 1
        return ride
    
    def get_ride(self, ride_id: int) -> Optional[Ride]:
        return self.rides.get(ride_id)
    
    def get_user_rides(self, alias: str) -> List[Ride]:
        return [ride for ride in self.rides.values() if ride.driver.alias == alias]
        
    def get_active_rides(self) -> List[Ride]:
        return [ride for ride in self.rides.values() if ride.status != RideStatus.FINISHED]
    
    def get_user_ride_stats(self, alias: str) -> Dict[str, int]:
        """Obtener estadísticas de participación en rides para un usuario específico"""
        stats = {
            "total": 0,
            "completed": 0,
            "missing": 0,
            "not_marked": 0,
            "rejected": 0
        }
        
        for ride in self.rides.values():
            for participation in ride.participations:
                if participation.participant.alias == alias:
                    stats["total"] += 1
                    
                    if participation.status == ParticipationStatus.COMPLETED:
                        stats["completed"] += 1
                    elif participation.status == ParticipationStatus.MISSING:
                        stats["missing"] += 1
                    elif participation.status == ParticipationStatus.NOT_MARKED:
                        stats["not_marked"] += 1
                    elif participation.status == ParticipationStatus.REJECTED:
                        stats["rejected"] += 1
        
        return stats

# Creamos una instancia global del DataHandler
data_handler = DataHandler()

# Inicializamos algunos datos para pruebas
def init_test_data():
    # Crear algunos usuarios
    user1 = User("jperez", "Juan Pérez", "ABC-123")
    user2 = User("lgomez", "Laura Gómez", None)
    user3 = User("acastro", "Alberto Castro", "XYZ-789")
    user4 = User("mvega", "María Vega", None)
    
    for user in [user1, user2, user3, user4]:
        data_handler.add_user(user)
    
    # Crear un ride para pruebas
    ride_date = datetime.strptime("2025/07/15 22:00", "%Y/%m/%d %H:%M")
    ride = data_handler.create_ride(
        ride_date, 
        "Av Javier Prado 456, San Borja", 
        3, 
        user1
    )
    
    # Añadir una solicitud de participación
    participation = RideParticipation(user2, ride.id, "Av Aramburú 245, Surquillo", 1)
    ride.participations.append(participation)

# Crear la aplicación Flask
app = Flask(__name__)

# Inicializar datos de prueba
init_test_data()

# Endpoints de la API

@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    """Retorna la lista de todos los usuarios"""
    usuarios = [user.to_dict() for user in data_handler.get_all_users()]
    return jsonify(usuarios)

@app.route('/usuarios/<string:alias>', methods=['GET'])
def get_usuario(alias):
    """Retorna los datos de un usuario específico"""
    usuario = data_handler.get_user(alias)
    if not usuario:
        return jsonify({"error": f"Usuario con alias {alias} no encontrado"}), 404
    
    return jsonify(usuario.to_dict())

@app.route('/usuarios/<string:alias>/rides', methods=['GET'])
def get_usuario_rides(alias):
    """Retorna los datos de los rides creados por el usuario"""
    usuario = data_handler.get_user(alias)
    if not usuario:
        return jsonify({"error": f"Usuario con alias {alias} no encontrado"}), 404
    
    rides = data_handler.get_user_rides(alias)
    return jsonify([ride.to_dict(include_participants=False) for ride in rides])

@app.route('/usuarios/<string:alias>/rides/<int:ride_id>', methods=['GET'])
def get_usuario_ride(alias, ride_id):
    """Retorna los datos del ride incluyendo los participantes y las estadísticas"""
    usuario = data_handler.get_user(alias)
    if not usuario:
        return jsonify({"error": f"Usuario con alias {alias} no encontrado"}), 404
    
    ride = data_handler.get_ride(ride_id)
    if not ride:
        return jsonify({"error": f"Ride con id {ride_id} no encontrado"}), 404
    
    if ride.driver.alias != alias:
        return jsonify({"error": f"El ride con id {ride_id} no pertenece al usuario {alias}"}), 404
    
    return jsonify({"ride": ride.to_dict(include_stats=True)})

@app.route('/usuarios/<string:driver_alias>/rides/<int:ride_id>/requestToJoin/<string:participant_alias>', methods=['POST'])
def request_to_join_ride(driver_alias, ride_id, participant_alias):
    """Solicitar unirse a un ride"""
    driver = data_handler.get_user(driver_alias)
    if not driver:
        return jsonify({"error": f"Conductor con alias {driver_alias} no encontrado"}), 404
    
    participant = data_handler.get_user(participant_alias)
    if not participant:
        return jsonify({"error": f"Participante con alias {participant_alias} no encontrado"}), 404
    
    ride = data_handler.get_ride(ride_id)
    if not ride:
        return jsonify({"error": f"Ride con id {ride_id} no encontrado"}), 404
    
    if ride.driver.alias != driver_alias:
        return jsonify({"error": f"El ride con id {ride_id} no pertenece al usuario {driver_alias}"}), 404
    
    # Validación: solo unirse a un ride con estado ready
    if ride.status != RideStatus.READY:
        return jsonify({"error": "Solo se puede solicitar unirse a un ride que esté en estado ready"}), 422
    
    # Validación: verificar si el participante ya ha solicitado unirse a este ride
    for participation in ride.participations:
        if participation.participant.alias == participant_alias:
            return jsonify({"error": f"El usuario {participant_alias} ya ha solicitado unirse a este ride"}), 422
    
    # Datos del request
    data = request.get_json() or {}
    destination = data.get("destination")
    occupied_spaces = data.get("occupiedSpaces")
    
    if not destination or not occupied_spaces:
        return jsonify({"error": "Se requiere destino y número de espacios ocupados"}), 400
    
    # Validar que hay suficientes espacios
    if occupied_spaces > ride.available_spaces():
        return jsonify({"error": f"No hay suficientes espacios disponibles. Disponibles: {ride.available_spaces()}"}), 422
    
    # Crear la participación
    participation = RideParticipation(participant, ride_id, destination, occupied_spaces)
    ride.participations.append(participation)
    
    return jsonify({"message": "Solicitud de unirse al ride enviada correctamente"})

@app.route('/usuarios/<string:driver_alias>/rides/<int:ride_id>/accept/<string:participant_alias>', methods=['POST'])
def accept_participant(driver_alias, ride_id, participant_alias):
    """Aceptar la solicitud de un participante para unirse al ride"""
    driver = data_handler.get_user(driver_alias)
    if not driver:
        return jsonify({"error": f"Conductor con alias {driver_alias} no encontrado"}), 404
    
    ride = data_handler.get_ride(ride_id)
    if not ride:
        return jsonify({"error": f"Ride con id {ride_id} no encontrado"}), 404
    
    if ride.driver.alias != driver_alias:
        return jsonify({"error": f"El ride con id {ride_id} no pertenece al usuario {driver_alias}"}), 404
    
    # Validación: solo aceptar participantes en un ride con estado ready
    if ride.status != RideStatus.READY:
        return jsonify({"error": "Solo se pueden aceptar participantes en un ride que esté en estado ready"}), 422
    
    # Buscar la participación del participante
    found = False
    for participation in ride.participations:
        if participation.participant.alias == participant_alias:
            found = True
            
            # Validar que la participación está en estado waiting
            if participation.status != ParticipationStatus.WAITING:
                return jsonify({"error": f"La solicitud del participante {participant_alias} no está en estado waiting"}), 422
            
            # Validar que hay suficientes espacios
            if participation.occupied_spaces > ride.available_spaces():
                return jsonify({"error": f"No hay suficientes espacios disponibles. Disponibles: {ride.available_spaces()}"}), 422
            
            # Aceptar la participación
            participation.status = ParticipationStatus.CONFIRMED
            participation.confirmation = datetime.now()
            break
    
    if not found:
        return jsonify({"error": f"No se encontró una solicitud del participante {participant_alias} para este ride"}), 404
    
    return jsonify({"message": f"Solicitud del participante {participant_alias} aceptada correctamente"})

@app.route('/usuarios/<string:driver_alias>/rides/<int:ride_id>/reject/<string:participant_alias>', methods=['POST'])
def reject_participant(driver_alias, ride_id, participant_alias):
    """Rechazar la solicitud de un participante para unirse al ride"""
    driver = data_handler.get_user(driver_alias)
    if not driver:
        return jsonify({"error": f"Conductor con alias {driver_alias} no encontrado"}), 404
    
    ride = data_handler.get_ride(ride_id)
    if not ride:
        return jsonify({"error": f"Ride con id {ride_id} no encontrado"}), 404
    
    if ride.driver.alias != driver_alias:
        return jsonify({"error": f"El ride con id {ride_id} no pertenece al usuario {driver_alias}"}), 404
    
    # Validación: solo rechazar participantes en un ride con estado ready
    if ride.status != RideStatus.READY:
        return jsonify({"error": "Solo se pueden rechazar participantes en un ride que esté en estado ready"}), 422
    
    # Buscar la participación del participante
    found = False
    for participation in ride.participations:
        if participation.participant.alias == participant_alias:
            found = True
            
            # Validar que la participación está en estado waiting
            if participation.status != ParticipationStatus.WAITING:
                return jsonify({"error": f"La solicitud del participante {participant_alias} no está en estado waiting"}), 422
            
            # Rechazar la participación
            participation.status = ParticipationStatus.REJECTED
            break
    
    if not found:
        return jsonify({"error": f"No se encontró una solicitud del participante {participant_alias} para este ride"}), 404
    
    return jsonify({"message": f"Solicitud del participante {participant_alias} rechazada correctamente"})

@app.route('/usuarios/<string:driver_alias>/rides/<int:ride_id>/start', methods=['POST'])
def start_ride(driver_alias, ride_id):
    """Iniciar un ride"""
    driver = data_handler.get_user(driver_alias)
    if not driver:
        return jsonify({"error": f"Conductor con alias {driver_alias} no encontrado"}), 404
    
    ride = data_handler.get_ride(ride_id)
    if not ride:
        return jsonify({"error": f"Ride con id {ride_id} no encontrado"}), 404
    
    if ride.driver.alias != driver_alias:
        return jsonify({"error": f"El ride con id {ride_id} no pertenece al usuario {driver_alias}"}), 404
    
    # Validación: solo iniciar un ride con estado ready
    if ride.status != RideStatus.READY:
        return jsonify({"error": "Solo se puede iniciar un ride que esté en estado ready"}), 422
    
    # Datos del request - participantes presentes al iniciar el ride
    data = request.get_json() or {}
    present_participants = data.get("presentParticipants", [])
    
    # Validación: todas las solicitudes deben estar confirmed o rejected
    for participation in ride.participations:
        if participation.status not in [ParticipationStatus.CONFIRMED, ParticipationStatus.REJECTED]:
            return jsonify({"error": f"Todas las solicitudes deben estar confirmadas o rechazadas antes de iniciar el ride"}), 422
    
    # Cambiar el estado del ride a in_progress
    ride.status = RideStatus.IN_PROGRESS
    
    # Actualizar el estado de los participantes
    for participation in ride.participations:
        if participation.status == ParticipationStatus.CONFIRMED:
            if participation.participant.alias in present_participants:
                participation.status = ParticipationStatus.IN_PROGRESS
            else:
                participation.status = ParticipationStatus.MISSING
    
    return jsonify({"message": "Ride iniciado correctamente"})

@app.route('/usuarios/<string:driver_alias>/rides/<int:ride_id>/end', methods=['POST'])
def end_ride(driver_alias, ride_id):
    """Terminar un ride"""
    driver = data_handler.get_user(driver_alias)
    if not driver:
        return jsonify({"error": f"Conductor con alias {driver_alias} no encontrado"}), 404
    
    ride = data_handler.get_ride(ride_id)
    if not ride:
        return jsonify({"error": f"Ride con id {ride_id} no encontrado"}), 404
    
    if ride.driver.alias != driver_alias:
        return jsonify({"error": f"El ride con id {ride_id} no pertenece al usuario {driver_alias}"}), 404
    
    # Validación: solo terminar un ride con estado in_progress
    if ride.status != RideStatus.IN_PROGRESS:
        return jsonify({"error": "Solo se puede terminar un ride que esté en estado in_progress"}), 422
    
    # Cambiar el estado del ride a finished
    ride.status = RideStatus.FINISHED
    
    # Actualizar el estado de los participantes
    for participation in ride.participations:
        if participation.status == ParticipationStatus.IN_PROGRESS:
            participation.status = ParticipationStatus.NOT_MARKED
    
    return jsonify({"message": "Ride terminado correctamente"})

@app.route('/usuarios/<string:participant_alias>/rides/<int:ride_id>/unloadParticipant', methods=['POST'])
def unload_participant(participant_alias, ride_id):
    """Bajar del ride (lo hace el participante)"""
    participant = data_handler.get_user(participant_alias)
    if not participant:
        return jsonify({"error": f"Participante con alias {participant_alias} no encontrado"}), 404
    
    ride = data_handler.get_ride(ride_id)
    if not ride:
        return jsonify({"error": f"Ride con id {ride_id} no encontrado"}), 404
    
    # Validación: solo descargar participantes de un ride con estado in_progress
    if ride.status != RideStatus.IN_PROGRESS:
        return jsonify({"error": "Solo se puede bajar de un ride que esté en estado in_progress"}), 422
    
    # Buscar la participación del participante
    found = False
    for participation in ride.participations:
        if participation.participant.alias == participant_alias:
            found = True
            
            # Validar que la participación está en estado in_progress
            if participation.status != ParticipationStatus.IN_PROGRESS:
                return jsonify({"error": f"El participante {participant_alias} no está en el ride o su estado no es in_progress"}), 422
            
            # Marcar la participación como completada
            participation.status = ParticipationStatus.COMPLETED
            break
    
    if not found:
        return jsonify({"error": f"No se encontró una participación del usuario {participant_alias} en este ride"}), 404
    
    return jsonify({"message": f"El participante {participant_alias} se ha bajado correctamente del ride"})

@app.route('/rides', methods=['GET'])
def get_rides():
    """Retorna la lista de todos los rides activos"""
    rides = data_handler.get_active_rides()
    return jsonify([ride.to_dict(include_participants=False) for ride in rides])

@app.route('/usuarios/<string:driver_alias>/rides', methods=['POST'])
def create_ride(driver_alias):
    """Crear un nuevo ride"""
    driver = data_handler.get_user(driver_alias)
    if not driver:
        return jsonify({"error": f"Usuario con alias {driver_alias} no encontrado"}), 404
    
    # Validar que el usuario sea conductor
    if not driver.is_driver():
        return jsonify({"error": f"El usuario {driver_alias} no es conductor (no tiene matrícula de coche)"}), 422
    
    # Obtener datos del request
    data = request.get_json() or {}
    date_time_str = data.get("rideDateAndTime")
    final_address = data.get("finalAddress")
    allowed_spaces = data.get("allowedSpaces")
    
    if not date_time_str or not final_address or not allowed_spaces:
        return jsonify({"error": "Se requieren fecha y hora, dirección final y espacios permitidos"}), 400
    
    try:
        date_time = datetime.strptime(date_time_str, "%Y/%m/%d %H:%M")
    except ValueError:
        return jsonify({"error": "Formato de fecha y hora incorrecto. Use YYYY/MM/DD HH:MM"}), 400
    
    # Crear el ride
    ride = data_handler.create_ride(date_time, final_address, allowed_spaces, driver)
    
    return jsonify({"message": "Ride creado correctamente", "ride": ride.to_dict()})

# Agregar endpoint para crear un nuevo usuario
@app.route('/usuarios', methods=['POST'])
def create_usuario():
    """Crear un nuevo usuario"""
    data = request.get_json() or {}
    alias = data.get("alias")
    name = data.get("name")
    car_plate = data.get("car_plate")
    
    if not alias or not name:
        return jsonify({"error": "Se requieren alias y nombre"}), 400
    
    # Verificar si el usuario ya existe
    if data_handler.get_user(alias):
        return jsonify({"error": f"Ya existe un usuario con el alias {alias}"}), 422
    
    # Crear el usuario
    usuario = User(alias, name, car_plate)
    data_handler.add_user(usuario)
    
    return jsonify({"message": "Usuario creado correctamente", "usuario": usuario.to_dict()})

if __name__ == '__main__':
    app.run(debug=True)

