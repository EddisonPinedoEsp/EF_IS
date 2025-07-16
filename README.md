# Sistema de Gestión de Rides UTEC


### Ejecutar la Aplicación
```bash
cd src
python controller.py
```

La aplicación se ejecutará en `http://localhost:5000`

### Ejecutar Pruebas Unitarias
```bash
# Ejecutar pruebas
python -m unittest src.test.unit_tests

# Ejecutar con coverage
python -m coverage run -m unittest src.test.unit_tests
python -m coverage report
```

## API Endpoints

### 1. Gestión de Usuarios

#### Obtener todos los usuarios
```http
GET /usuarios
```

#### Obtener usuario específico
```http
GET /usuarios/{alias}
```
**Ejemplo:**
```http
GET /usuarios/juan_driver
```

```
**Error (404):** Usuario no encontrado

#### Obtener rides de un usuario
```http
GET /usuarios/{alias}/rides
```
**Ejemplo:**
```http
GET /usuarios/juan_driver/rides
```

### 2. Gestión de Rides

#### Solicitar unirse a un ride
```http
POST /usuarios/{driver_alias}/rides/{ride_id}/requestToJoin/{passenger_alias}
```
**Ejemplo:**
```http
POST /usuarios/juan_driver/rides/1/requestToJoin/maria_user
```

**Error (400):** Solicitud fallida

#### Aceptar solicitud de ride
```http
POST /usuarios/{driver_alias}/rides/{ride_id}/accept/{passenger_alias}
```
**Ejemplo:**
```http
POST /usuarios/juan_driver/rides/1/accept/maria_user
```

#### Rechazar solicitud de ride
```http
POST /usuarios/{driver_alias}/rides/{ride_id}/reject/{passenger_alias}
```
**Ejemplo:**
```http
POST /usuarios/juan_driver/rides/1/reject/maria_user
```

## Modelos de Datos

### Usuario (User)
```json
{
    "id": 1,
    "alias": "juan_driver",
    "name": "Juan Pérez",
    "carPlate": "ABC-123",
    "rides": [1, 2]
}
```

### Ride
```json
{
    "id": 1,
    "rideDateAndTime": "2025-07-20 08:00",
    "finalAddress": "Universidad Central - Campus Norte",
    "allowedSpaces": 4,
    "rideDriver": 1,
    "status": "Ready",
    "participants": [2, 3]
}
```

### Participación en Ride (RideParticipation)
```json
{
    "id": 1,
    "confirmation": "15-07-25",
    "destination": "Universidad Central - Campus Norte",
    "occupiedSpaces": 2,
    "status": "Pendiente",
    "rideId": 1
}
```

## Estados del Sistema

### Estados de Ride
- **Ready**: Ride listo para recibir solicitudes
- **InProgress**: Ride en progreso
- **Completed**: Ride completado

### Estados de Participación
- **Pendiente**: Solicitud enviada, esperando respuesta
- **Aceptada**: Solicitud aceptada por el conductor
- **Rechazada**: Solicitud rechazada por el conductor

## Ejemplos de Uso

### 1. Consultar usuarios disponibles
```bash
curl -X GET http://localhost:5000/usuarios
```

### 2. Ver información de un usuario específico
```bash
curl -X GET http://localhost:5000/usuarios/juan_driver
```

### 3. Solicitar unirse a un ride
```bash
curl -X POST http://localhost:5000/usuarios/juan_driver/rides/1/requestToJoin/maria_user
```

### 4. Aceptar una solicitud (como conductor)
```bash
curl -X POST http://localhost:5000/usuarios/juan_driver/rides/1/accept/maria_user
```

## Validaciones Implementadas

- Solo se puede unir a un ride antes de que inicie (status "Ready")
- Solo el conductor puede aceptar/rechazar solicitudes
- Verificación de existencia de usuarios y rides
- Validación de espacios disponibles

## Códigos de Estado HTTP

- **200**: Operación exitosa
- **201**: Recurso creado exitosamente
- **400**: Error en la solicitud
- **404**: Recurso no encontrado
- **422**: Error de validación (para futuras implementaciones)
- **500**: Error interno del servidor

