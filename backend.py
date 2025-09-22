from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import threading
import time

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

evento_actual = None
VALID_API_KEY = '5A5N04L3R7'
TIMER_SEGUNDOS = 120
timer = None

def limpiar_evento():
    """Borra el evento actual automáticamente después del tiempo definido"""
    global evento_actual, timer
    evento_actual = None
    timer = None
    print("⏰ Evento eliminado automáticamente tras 120 segundos.")
    socketio.emit('evento_eliminado', {"status": "El evento ha sido eliminado automáticamente."})

@app.route('/', methods=['GET'])
def raiz():
    return jsonify({"status": "Servidor activo."})

@app.route('/evento', methods=['GET'])
def obtener_evento():
    return jsonify({"evento": evento_actual})

@app.route('/evento', methods=['POST'])
def recibir_evento():
    global evento_actual, timer
    try:
        data = request.get_json()
        print(f"📩 Datos recibidos: {data}")

        if data.get('api_key') != VALID_API_KEY:
            print("❌ API Key inválida.")
            return jsonify({"error": "API Key inválida"}), 403

        # Validar que venga el formato correcto
        if "earthquakeLiveEventData" not in data:
            return jsonify({"error": "Formato inválido, falta 'earthquakeLiveEventData'."}), 400

        # Reemplazar el evento actual con el nuevo
        evento_actual = data["earthquakeLiveEventData"]
        print(f"🌍 Nuevo evento activo: {evento_actual}")

        # Emitir a los clientes el nuevo evento
        socketio.emit('nuevo_evento', evento_actual)

        # Reiniciar el temporizador de 120 segundos
        if timer and timer.is_alive():
            timer.cancel()
        timer = threading.Timer(TIMER_SEGUNDOS, limpiar_evento)
        timer.start()

        return jsonify({"status": "Evento recibido y activado."})

    except Exception as e:
        print(f"❌ Error procesando el evento: {e}")
        return jsonify({"error": "Error procesando el evento."}), 500

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
