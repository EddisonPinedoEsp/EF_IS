import unittest
import json
import os
import tempfile
from unittest.mock import patch, mock_open
from src.data_handler import DataHandler

class TestDataHandler(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.data_handler = DataHandler()
        
        # Datos de prueba
        self.test_users = [
            {
                "id": 1,
                "alias": "test_driver",
                "name": "Test Driver",
                "carPlate": "TEST-123",
                "rides": []
            },
            {
                "id": 2,
                "alias": "test_passenger",
                "name": "Test Passenger",
                "carPlate": "TEST-456",
                "rides": []
            }
        ]
        
        self.test_rides = [
            {
                "id": 1,
                "rideDateAndTime": "2025-07-20 08:00",
                "finalAddress": "Universidad Central",
                "allowedSpaces": 3,
                "rideDriver": 1,
                "status": "Ready",
                "participants": []
            }
        ]
        
        self.test_participations = []

    def test_get_user_by_attribute_success(self):
        """Caso de éxito: Obtener usuario por alias existente"""
        with patch.object(self.data_handler, 'load_users'):
            self.data_handler.users = self.test_users
            
            result = self.data_handler.get_user_by_attribute('alias', 'test_driver')
            
            self.assertIsNotNone(result)
            self.assertEqual(result['alias'], 'test_driver')
            self.assertEqual(result['name'], 'Test Driver')

    def test_get_user_by_attribute_not_found(self):
        """Caso de error: Usuario no encontrado"""
        with patch.object(self.data_handler, 'load_users'):
            self.data_handler.users = self.test_users
            
            result = self.data_handler.get_user_by_attribute('alias', 'nonexistent_user')
            
            self.assertIsNone(result)

    def test_request_to_join_ride_success(self):
        """Caso de éxito: Solicitud exitosa para unirse a un ride"""
        with patch.object(self.data_handler, 'load_users'), \
             patch.object(self.data_handler, 'load_rides'), \
             patch.object(self.data_handler, 'load_ride_participations'), \
             patch.object(self.data_handler, 'save_rides'), \
             patch.object(self.data_handler, 'save_ride_participations'):
            
            self.data_handler.users = self.test_users.copy()
            self.data_handler.rides = self.test_rides.copy()
            self.data_handler.ride_participations = []
            
            result = self.data_handler.request_to_join_ride('test_driver', 1, 'test_passenger')
            
            self.assertIsNotNone(result)
            self.assertEqual(result['rideId'], 1)
            self.assertEqual(result['status'], 'Pendiente')
            self.assertEqual(result['destination'], 'Universidad Central')

    def test_request_to_join_ride_user_not_found(self):
        """Caso de error: Usuario no encontrado en solicitud de ride"""
        with patch.object(self.data_handler, 'load_users'), \
             patch.object(self.data_handler, 'load_rides'), \
             patch.object(self.data_handler, 'load_ride_participations'):
            
            self.data_handler.users = self.test_users.copy()
            self.data_handler.rides = self.test_rides.copy()
            self.data_handler.ride_participations = []
            
            result = self.data_handler.request_to_join_ride('nonexistent_user', 1, 'test_passenger')
            
            self.assertIsNone(result)

    def test_request_to_join_ride_ride_not_found(self):
        """Caso de error: Ride no encontrado"""
        with patch.object(self.data_handler, 'load_users'), \
             patch.object(self.data_handler, 'load_rides'), \
             patch.object(self.data_handler, 'load_ride_participations'):
            
            self.data_handler.users = self.test_users.copy()
            self.data_handler.rides = self.test_rides.copy()
            self.data_handler.ride_participations = []
            
            result = self.data_handler.request_to_join_ride('test_driver', 999, 'test_passenger')
            
            self.assertIsNone(result)

    def test_accept_ride_request_invalid_driver(self):
        """Caso de error: Conductor inválido al aceptar solicitud"""
        with patch.object(self.data_handler, 'load_users'), \
             patch.object(self.data_handler, 'load_rides'), \
             patch.object(self.data_handler, 'load_ride_participations'):
            
            test_ride = self.test_rides[0].copy()
            test_ride['participants'] = [2] 
            
            self.data_handler.users = self.test_users.copy()
            self.data_handler.rides = [test_ride]
            self.data_handler.ride_participations = []
        
            result = self.data_handler.accept_ride_request('test_passenger', 1, 'test_passenger')
            
            self.assertIsNone(result)

    def test_generate_new_id_empty_list(self):
        """Caso de éxito: Generar ID para lista vacía"""
        result = self.data_handler.generate_new_id([])
        self.assertEqual(result, 1)

    def test_generate_new_id_with_existing_items(self):
        """Caso de éxito: Generar nuevo ID con elementos existentes"""
        test_data = [
            {"id": 1, "name": "item1"},
            {"id": 3, "name": "item2"},
            {"id": 2, "name": "item3"}
        ]
        result = self.data_handler.generate_new_id(test_data)
        self.assertEqual(result, 4)

if __name__ == '__main__':
    unittest.main()