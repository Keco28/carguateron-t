import paho.mqtt.publish as publish
import paho.mqtt.client as mqttc

OUTBOUND_TOPIC = "water_button"
WATER_LEVEL_TOPIC = "water_level"
HUMIDIY_TEMPERATURE_TOPIC = "humidity_temperature"
WATERED_TOPIC = "watered"
BROKER_URL = "localhost"
BROKER_PORT = 1883    


class Publisher:

    @staticmethod
    def send_message(message):
        try:
            print(OUTBOUND_TOPIC, message, BROKER_URL)
            publish.single(OUTBOUND_TOPIC, message, hostname=BROKER_URL,
                           port=BROKER_PORT)
        except Exception as ex:
            print(f"Error enviando mensaje ex: {ex}")


class Listener:

    def __init__(self, observador):
        self.client = mqttc.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.observador = observador
        try:
            self.client.connect(BROKER_URL, BROKER_PORT, 60)
        except ConnectionRefusedError:
            print("Sin conexión al broker")

    def start(self):
        print("Looping")
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print("Conectado ", str(rc))
        client.subscribe(WATER_LEVEL_TOPIC)
        client.subscribe(HUMIDIY_TEMPERATURE_TOPIC)
        client.subscribe(WATERED_TOPIC)

    def on_message(self, client, userdata, msg):
        print(f"recibido: {msg}")
        print(f"Mensaje recibido: {msg.payload.decode('utf-8')}")
        print(f"topico: {msg.topic}")
        print(f"-----------------")
        
        self.observador.procesarMensaje(msg.topic, msg.payload.decode('utf-8'))
