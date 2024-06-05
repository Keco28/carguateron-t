# Ejemplo Kivy - Ubidots

Para simular el dispositivo se deben abrir dos terminales: una para  suscribirse al tópico `light_outbound` y simular la escucha de los mensajes provenientes del hub:

```
mosquitto_sub -t light_outbound
```
Y otra para publicar mensajes al tópico `light_inbound` y simular el envío de mensajes al hub:
```
mosquitto_pub -t light_inbound -m on
```
Para publicar mensajes en **Ubidots** directamente desde la terminal se puede usar el siguiente comando:

```
mosquitto_pub \
-h 'industrial.api.ubidots.com' \
-t '/v1.6/devices/{device}/{variable}' \
-u '{token} \
-p 1883 \
-q 1 \
-m '{"value": "1"}'
```

Se deben cambiar los valores entre llaves por los correspondientes desde la cuenta de Ubidots personal.