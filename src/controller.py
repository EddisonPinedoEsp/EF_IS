from flask import Flask, jsonify
from data_handler import DataHandler
from flask import request

app = Flask(__name__)
data_handler = DataHandler()

class TaskController:
    def __init__(self, data_handler):
        self.data_handler = data_handler

@app.route('/dummy', methods=['GET'])
def dummy_endpoint():
    # Example dummy response
    return jsonify({"message": "This is a dummy endpoint!"})


@app.route('/usuarios', methods=['GET'])
def get_users():
    try:
        users = data_handler.get_all_users()
        if not users:
            return jsonify([]), 200  # Devolver lista vacía con status 200 en lugar de error 404
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/usuarios/<alias>', methods=['GET'])
def get_user_by_alias(alias):
    try:
        user = data_handler.get_user_by_atribute('alias',alias)
        if not user:
            return jsonify({"error": "User not found"}), 404
        return user
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/usuarios/<alias>/rides', methods=['GET'])
def get_rides_of_user(alias):
    try:
        rides = data_handler.get_rides_of_user(alias)
        if not rides:
            return jsonify({"error": "No rides found for user"}), 404
        return jsonify(rides)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/usuarios/<alias>/rides/<ride_id>', methods=['GET'])
def get_ride_details(alias, ride_id):
    try:
        ride = data_handler.get_ride_details(alias, int(ride_id))
        if not ride:
            return jsonify({"error": "Ride not found"}), 404
        return jsonify({"ride": ride})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/usuarios/<alias>/rides/<ride_id>/requestToJoin/<alias2>', methods=['POST'])
def request_to_join_ride(alias, ride_id, alias2):
    try:
        res = data_handler.request_to_join_ride(alias, int(ride_id), alias2)
        if not res:
            return jsonify({"error": "Participation request failed"}), 400
        return jsonify({"message": "Participation request successful"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/usuarios/<alias>/rides/<ride_id>/accept/<alias2>', methods=['POST'])
def accept_ride_request(alias, ride_id, alias2):
    try:
        res = data_handler.accept_ride_request(alias, int(ride_id), alias2)
        if not res:
            return jsonify({"error": "Participation request failed"}), 400
        return jsonify({"message": "Participation request successful"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/usuarios/<alias>/rides/<ride_id>/reject/<alias2>', methods=['POST'])
def reject_ride_request(alias, ride_id, alias2):
    try:
        res = data_handler.reject_ride_request(alias, int(ride_id), alias2)
        if not res:
            return jsonify({"error": "Participation request failed"}), 400
        return jsonify({"message": "Participation request successful"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/usuarios/<alias>/rides/<ride_id>/start', methods=['POST'])
def start_ride(alias, ride_id):
    try:
        res = data_handler.start_ride(alias, int(ride_id))
        if not res:
            return jsonify({"error": "Participation request failed"}), 400
        return jsonify({"message": "Participation request successful"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/usuarios/<alias>/rides/<ride_id>/end', methods=['POST'])
def end_ride(alias, ride_id):
    try:
        res = data_handler.end_ride(alias, int(ride_id))
        if not res:
            return jsonify({"error": "Participation request failed"}), 400
        return jsonify({"message": "Participation request successful"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/usuarios/<alias>/rides/<ride_id>/unloadParticipant', methods=['POST'])
def unload_participant(alias, ride_id):
    try:
        res = data_handler.unload_participant(alias, int(ride_id))
        if not res:
            return jsonify({"error": "Participation request failed"}), 400
        return jsonify({"message": "Participation request successful"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)