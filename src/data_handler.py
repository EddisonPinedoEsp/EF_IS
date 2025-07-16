import json
from datetime import datetime
from dateutil.relativedelta import relativedelta

class DataHandler:
    def __init__(self, filename='data.json'):
        self.filename = filename
        self.rides = []
        self.users = []
        self.ride_participations = []
        self.load_data()

    def save_data(self):
        data = {
            'rides': self.rides,
            'users': self.users,
            'ride_participations': self.ride_participations
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f)

    def load_data(self):
        self.load_users()
        self.load_rides()
        self.load_ride_participations()

    def load_users(self, path='src/data/users.json'):
        try:
            with open(path, 'r') as f:
                self.users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.users = []

    def save_users(self, path='src/data/users.json'):
        with open(path, 'w') as f:
            json.dump(self.users, f)

    def load_rides(self, path='src/data/rides.json'):
        try:
            with open(path, 'r') as f:
                self.rides = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.rides = []

    def save_rides(self, path='src/data/rides.json'):
        with open(path, 'w') as f:
            json.dump(self.rides, f)

    def load_ride_participations(self, path='src/data/rideParticipations.json'):
        try:
            with open(path, 'r') as f:
                self.ride_participations = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.ride_participations = []
    
    def save_ride_participations(self, path='src/data/rideParticipations.json'):
        with open(path, 'w') as f:
            json.dump(self.ride_participations, f)

    def generate_new_id(self, data_list):
        if not data_list:
            return 1
        return max(item['id'] for item in data_list) + 1

    def get_user_by_attribute(self, attribute, value):
        self.load_users()
        for user in self.users:
            if user.get(attribute) == value:
                return user
        return None

    def get_user_by_atribute(self, attribute, value):
        return self.get_user_by_attribute(attribute, value)

    def get_ride_by_attribute(self, attribute, value):
        self.load_rides()
        for ride in self.rides:
            if ride.get(attribute) == value:
                return ride
        return None

    def get_ride_participation_by_attribute(self, attribute, value):
        self.load_ride_participations()
        for participation in self.ride_participations:
            if participation.get(attribute) == value:
                return participation
        return None

    def get_all_users(self):
        self.load_users()
        return self.users
    
    def get_rides_of_user(self, alias):
        self.load_users()
        self.load_rides()

        user = self.get_user_by_atribute('alias', alias)
        if not user:
            return None
        
        return user.get('rides', [])

    def get_ride_details(self, alias, value):
        self.load_rides()
        self.load_ride_participations()
        
        ride = self.get_ride_by_attribute('id', value)
        if not ride:
            return None
        
        driver = self.get_user_by_atribute('id', ride['rideDriver'])
        if not driver:
            return None
        driver_alias = driver['alias']
        
        participants = []
        for participant_id in ride['participants']:
            participant = self.get_user_by_atribute('id', participant_id)
            if not participant:
                continue
                
            participation = None
            for part in self.ride_participations:
                if part['rideId'] == value:
                    participation = part
                    break
            
            if not participation:
                participation = {
                    'confirmation': None,
                    'destination': ride['finalAddress'],
                    'occupiedSpaces': 1,
                    'status': 'waiting'
                }
            
            previousRidesTotal = 0
            previousRidesCompleted = 0
            previousRidesMissing = 0
            previousRidesNotMarked = 0
            previousRidesRejected = 0
            
            for ride_participation_id in participant['rides']:
                ride_participation = self.get_ride_participation_by_attribute('id', ride_participation_id)
                if ride_participation:
                    status = ride_participation.get('status', '')
                    if status == 'Pendiente':
                        previousRidesTotal += 1
                    elif status == 'Aceptada':
                        previousRidesCompleted += 1
                    elif status == 'Missing':
                        previousRidesMissing += 1
                    elif status == 'NotMarked':
                        previousRidesNotMarked += 1
                    elif status == 'Rechazada':
                        previousRidesRejected += 1

            user_data = {
                'confirmation': participation.get('confirmation', None),
                'participant': {
                    'alias': participant['alias'],
                    "previousRidesTotal": previousRidesTotal,
                    "previousRidesCompleted": previousRidesCompleted,
                    "previousRidesMissing": previousRidesMissing,
                    "previousRidesNotMarked": previousRidesNotMarked,
                    "previousRidesRejected": previousRidesRejected
                },
                'destination': participation.get('destination', ''),
                'occupiedSpaces': participation.get('occupiedSpaces', 0),
                'status': participation.get('status', 'waiting'),
            }

            participants.append(user_data)

        res = {
            "id": ride['id'],
            "rideDateAndTime": ride['rideDateAndTime'],
            "finalAddress": ride['finalAddress'],
            "driver": driver_alias,
            "status": ride['status'],
            "participants": participants
        }
        return res
        
    def request_to_join_ride(self, alias, ride_id, alias2):
        self.load_users()
        self.load_rides()
        self.load_ride_participations()

        driver = self.get_user_by_atribute('alias', alias)
        passenger = self.get_user_by_atribute('alias', alias2)
        if not driver or not passenger:
            return None
        
        ride = self.get_ride_by_attribute('id', ride_id)
        if not ride:
            return None
        
        if ride['rideDriver'] != driver['id']:
            return None
        
        if passenger['id'] in ride['participants']:
            return None
        
        ride['participants'].append(passenger['id'])

        new_participation_id = self.generate_new_id(self.ride_participations)
        new_ride_participation = {
            "id": new_participation_id,
            "confirmation": datetime.now().strftime('%d-%m-%y'),
            "destination": ride['finalAddress'],
            "occupiedSpaces": len(ride['participants']),
            "status": "Pendiente",
            "rideId": ride_id
        }
        
        passenger['rides'].append(new_participation_id)

        self.ride_participations.append(new_ride_participation)
        self.save_rides()
        self.save_ride_participations()
        self.save_users()

        return new_ride_participation
    
    def accept_ride_request(self, alias, ride_id, alias2):
        self.load_users()
        self.load_rides()
        self.load_ride_participations()

        driver = self.get_user_by_atribute('alias', alias)
        passenger = self.get_user_by_atribute('alias', alias2)
        if not driver or not passenger:
            return None
        
        ride = self.get_ride_by_attribute('id', ride_id)
        if not ride or ride['rideDriver'] != driver['id'] or passenger['id'] not in ride['participants']:
            return None
        
        for participation in self.ride_participations:
            if participation['rideId'] == ride_id and participation['id'] in passenger['rides']:
                participation['status'] = 'Aceptada'
                self.save_ride_participations()
                return participation

        return None
    
    def reject_ride_request(self, alias, ride_id, alias2):
        self.load_users()
        self.load_rides()
        self.load_ride_participations()

        driver = self.get_user_by_atribute('alias', alias)
        passenger = self.get_user_by_atribute('alias', alias2)
        if not driver or not passenger:
            return None
    
        ride = self.get_ride_by_attribute('id', ride_id)
        if not ride or ride['rideDriver'] != driver['id'] or passenger['id'] not in ride['participants']:
            return None
        
        for participation in self.ride_participations:
            if participation['rideId'] == ride_id and participation['id'] in passenger['rides']:
                participation['status'] = 'Rechazada'
                self.save_ride_participations()
                return participation

        return None
    
    def start_ride(self, alias, ride_id):
        self.load_users()
        self.load_rides()
        self.load_ride_participations()

        driver = self.get_user_by_atribute('alias', alias)
        if not driver:
            return None
        
        ride = self.get_ride_by_attribute('id', ride_id)
        if not ride or ride['rideDriver'] != driver['id']:
            return None
        
        ride['status'] = 'En Progreso'
        self.save_rides()
        
        return {"message": "Ride started successfully", "ride": ride}
    
    def end_ride(self, alias, ride_id):
        self.load_users()
        self.load_rides()
        self.load_ride_participations()

        driver = self.get_user_by_atribute('alias', alias)
        if not driver:
            return None
        
        ride = self.get_ride_by_attribute('id', ride_id)
        if not ride or ride['rideDriver'] != driver['id']:
            return None
        
        ride['status'] = 'Finalizada'
        self.save_rides()
        
        return {"message": "Ride ended successfully", "ride": ride}
    
    def unload_participant(self, alias, ride_id):
        self.load_users()
        self.load_rides()
        self.load_ride_participations()

        user = self.get_user_by_atribute('alias', alias)
        if not user:
            return None
        
        for participation_id in user['rides']:
            participation = self.get_ride_participation_by_attribute('id', participation_id)
            if participation and participation['rideId'] == ride_id:
                user['rides'].remove(participation_id)
                
                self.ride_participations.remove(participation)
                
                ride = self.get_ride_by_attribute('id', ride_id)
                if ride and user['id'] in ride['participants']:
                    ride['participants'].remove(user['id'])
                    self.save_rides()
                
                self.save_users()
                self.save_ride_participations()
                return {"message": "Participant unloaded successfully"}

        return None