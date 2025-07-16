import json
from datetime import datetime
from dateutil.relativedelta import relativedelta

class DataHandler:
    def __init__(self, filename='data.json'):
        self.filename = filename
        self.tasks = []
        self.users = []
        self.asignaciones = []
        self.load_data()

    def save_data(self):
        data = {
            'tasks': self.tasks,
            'users': self.users
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f)

    def load_data(self):
        self.load_usuarios()
        self.load_tareas()
        self.load_asignaciones()
    
    def load_users(self, path='src/data/usuarios.json'):
        try:
            with open(path, 'r') as f:
                self.users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.users = []

    def save_users(self, path='src/data/usuarios.json'):
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

    def load_ride_participations(self, path='src/data/ride_participations.json'):
        try:
            with open(path, 'r') as f:
                self.ride_participations = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.ride_participations = []
    
    def save_ride_participations(self, path='src/data/ride_participations.json'):
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

    def get_users(self):
        self.load_users()
        return self.users
    
    def get_rides_of_user(self, alias):
        self.load_users()
        self.load_rides()

        user = self.get_user_by_atribute('alias', alias)
        if not user:
            return None
        
        return user.get('rides', [])

    def request_to_join_ride(self, alias, ride_id, alias2):
        self.load_users()
        self.load_rides()
        self.load_ride_participations()

        user1 = self.get_user_by_atribute('alias', alias)
        user2 = self.get_user_by_atribute('alias', alias2)
        if not user1 or not user2:
            return None
        
        ride = self.get_ride_by_attribute('id', ride_id)
        if not ride:
            return None
        
        ride['rideDriver'] = user1['id']
        ride['participants'].append(user2['id'])

        new_participation_id = self.generate_new_id(self.ride_participations)
        new_ride_participation = {
            "id": new_participation_id,
            "confirmation": datetime.now().strftime('%d-%m-%y'),
            "destination": ride['finalAddress'],
            "occupiedSpaces": len(ride['participants']),
            "status": "Pendiente",
            "rideId": ride_id
        }
        user1['rides'].append(new_participation_id)

        self.ride_participations.append(new_ride_participation)
        self.save_rides()
        self.save_ride_participations()

        return new_ride_participation
    
    def accept_ride_request(self, alias, ride_id, alias2):
        self.load_users()
        self.load_rides()
        self.load_ride_participations()

        user1 = self.get_user_by_atribute('alias', alias)
        user2 = self.get_user_by_atribute('alias', alias2)
        if not user1 or not user2:
            return None
    
        ride = self.get_ride_by_attribute('id', ride_id)
        if not ride or ride['rideDriver'] != user1['id'] or user2['id'] not in ride['participants']:
            return None
        
        for rides in self.users['rides']:
            if rides['rideId'] == ride_id:
                rides['status'] = 'Aceptada'
                self.save_rides()
                return rides

        return None
    
    def reject_ride_request(self, alias, ride_id, alias2):
        self.load_users()
        self.load_rides()
        self.load_ride_participations()

        user1 = self.get_user_by_atribute('alias', alias)
        user2 = self.get_user_by_atribute('alias', alias2)
        if not user1 or not user2:
            return None
    
        ride = self.get_ride_by_attribute('id', ride_id)
        if not ride or ride['rideDriver'] != user1['id'] or user2['id'] not in ride['participants']:
            return None
        
        for rides in self.users['rides']:
            if rides['rideId'] == ride_id:
                rides['status'] = 'Rechazada'
                self.save_rides()
                return rides

        return None