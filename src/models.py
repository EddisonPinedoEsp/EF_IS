from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: Optional[int] = None
    alias: str
    name: str
    carPlate: str
    rides: list[int] = [] # Lista<RideParticipation>

class Ride(BaseModel):
    id: Optional[int] = None
    rideDateAndTime: str
    finalAddress: str
    allowedSpaces: int
    rideDriver: int # User
    status: str # Ready, InProgress, Done
    participants: list[int] = [] # Lista<RideParticipation>

class RideParticipation(BaseModel):
    id: Optional[int] = None
    confirmation: str
    destination: str
    occupiedSpaces: int
    status: str # Waiting, Rejected, Confirmed, Missing, NotMarked, In Progress, Done
    rideId: int
