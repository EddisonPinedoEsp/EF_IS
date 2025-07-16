# Sistema de Gestión de Rides UTEC

## Ejecución

```bash
# Iniciar el servidor
python pregunta1.py
```

El servidor estará disponible en: http://localhost:5000

## Datos de prueba iniciales

El sistema se inicializa con los siguientes datos de prueba:

### Usuarios:
- **jperez**: Juan Pérez (conductor, placa: ABC-123)
- **lgomez**: Laura Gómez (pasajero)
- **acastro**: Alberto Castro (conductor, placa: XYZ-789)
- **mvega**: María Vega (pasajero)

### Rides:
- **ID**: 1
- **Conductor**: jperez
- **Fecha**: 2025/07/15 22:00
- **Dirección final**: Av Javier Prado 456, San Borja
- **Espacios permitidos**: 3
- **Participantes**: lgomez (en estado "waiting")

## Guía de Endpoints

### 1. Gestión de Usuarios

#### Listar todos los usuarios
```
GET /usuarios
```

**Ejemplo con curl:**
```bash
curl -X GET http://localhost:5000/usuarios
```

#### Obtener un usuario específico
```
GET /usuarios/{alias}
```

**Ejemplo con curl:**
```bash
curl -X GET http://localhost:5000/usuarios/jperez
```

#### Crear un nuevo usuario
```
POST /usuarios
```

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:5000/usuarios \
  -H "Content-Type: application/json" \
  -d '{
    "alias": "mrodriguez",
    "name": "Miguel Rodríguez",
    "car_plate": "DEF-456"
  }'
```

### 2. Gestión de Rides

#### Listar todos los rides activos
```
GET /rides
```

**Ejemplo con curl:**
```bash
curl -X GET http://localhost:5000/rides
```

#### Listar rides de un usuario específico
```
GET /usuarios/{alias}/rides
```

**Ejemplo con curl:**
```bash
curl -X GET http://localhost:5000/usuarios/jperez/rides
```

#### Obtener detalles de un ride específico
```
GET /usuarios/{alias}/rides/{ride_id}
```

**Ejemplo con curl:**
```bash
curl -X GET http://localhost:5000/usuarios/jperez/rides/1
```

#### Crear un nuevo ride
```
POST /usuarios/{alias}/rides
```

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:5000/usuarios/jperez/rides \
  -H "Content-Type: application/json" \
  -d '{
    "rideDateAndTime": "2025/07/16 18:30",
    "finalAddress": "Av. La Marina 2000, San Miguel",
    "allowedSpaces": 4
  }'
```

### 3. Gestión de Participaciones

#### Solicitar unirse a un ride
```
POST /usuarios/{conductor_alias}/rides/{ride_id}/requestToJoin/{participant_alias}
```

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:5000/usuarios/jperez/rides/1/requestToJoin/mvega \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Av. Benavides 1200, Miraflores",
    "occupiedSpaces": 1
  }'
```

#### Aceptar solicitud de participación
```
POST /usuarios/{conductor_alias}/rides/{ride_id}/accept/{participant_alias}
```

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:5000/usuarios/jperez/rides/1/accept/lgomez
```

#### Rechazar solicitud de participación
```
POST /usuarios/{conductor_alias}/rides/{ride_id}/reject/{participant_alias}
```

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:5000/usuarios/jperez/rides/1/reject/mvega
```

#### Iniciar un ride
```
POST /usuarios/{conductor_alias}/rides/{ride_id}/start
```

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:5000/usuarios/jperez/rides/1/start \
  -H "Content-Type: application/json" \
  -d '{
    "presentParticipants": ["lgomez"]
  }'
```

#### Marcar bajada de participante (lo hace el participante)
```
POST /usuarios/{participant_alias}/rides/{ride_id}/unloadParticipant
```

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:5000/usuarios/lgomez/rides/1/unloadParticipant
```

#### Terminar un ride (lo hace el conductor)
```
POST /usuarios/{conductor_alias}/rides/{ride_id}/end
```

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:5000/usuarios/jperez/rides/1/end
```

## Flujo de uso típico

1. **Crear un nuevo usuario conductor**
```bash
curl -X POST http://localhost:5000/usuarios \
  -H "Content-Type: application/json" \
  -d '{
    "alias": "rgarcia",
    "name": "Roberto García",
    "car_plate": "GHI-789"
  }'
```

2. **Crear un nuevo ride**
```bash
curl -X POST http://localhost:5000/usuarios/rgarcia/rides \
  -H "Content-Type: application/json" \
  -d '{
    "rideDateAndTime": "2025/07/20 19:00",
    "finalAddress": "Av. La Molina 1500, La Molina",
    "allowedSpaces": 3
  }'
```

3. **Solicitar unirse al ride (como lgomez)**
```bash
curl -X POST http://localhost:5000/usuarios/rgarcia/rides/2/requestToJoin/lgomez \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Av. Primavera 1340, Surco",
    "occupiedSpaces": 1
  }'
```

4. **Aceptar la solicitud**
```bash
curl -X POST http://localhost:5000/usuarios/rgarcia/rides/2/accept/lgomez
```

5. **Iniciar el ride**
```bash
curl -X POST http://localhost:5000/usuarios/rgarcia/rides/2/start \
  -H "Content-Type: application/json" \
  -d '{
    "presentParticipants": ["lgomez"]
  }'
```

6. **Marcar que un participante se ha bajado**
```bash
curl -X POST http://localhost:5000/usuarios/lgomez/rides/2/unloadParticipant
```

7. **Terminar el ride**
```bash
curl -X POST http://localhost:5000/usuarios/rgarcia/rides/2/end
```

## Códigos de respuesta

- **200**: Operación exitosa
- **404**: Recurso no encontrado (usuario o ride inexistente)
- **400**: Error en la solicitud (datos faltantes o incorrectos)
- **422**: Error de validación (violación de reglas de negocio)

## Validaciones importantes

- Solo se puede solicitar unirse a un ride con estado "ready"
- Solo se puede iniciar un ride cuando todas las solicitudes estén "confirmed" o "rejected"
- Solo se puede aceptar una solicitud por participante
- Solo se confirman participantes si hay espacios disponibles
- Si un participante no está presente al inicio del ride, se marca como "missing"
- Al iniciar el ride, se cambia el estado del ride y de los participantes a "inprogress"
- Si el conductor termina el ride y algún participante sigue en "inprogress",