import pickle
from tkinter import Tk
from tkinter import filedialog
from _thread import start_new_thread
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import mainthread, Clock
from kivy.properties import NumericProperty
from kivy.uix.screenmanager import Screen
from external_comm import UbidotsPublisher
from internal_comm import Listener, Publisher


class IoT(Screen):
    humidity = NumericProperty(0.0)
    temperature = NumericProperty(0.0)
    water_level = NumericProperty(0.0)
    

    def __init__(self, **kw):
        super().__init__(**kw)
        escuchador = Listener(self)
        try:
            start_new_thread(escuchador.start, ())
        except Exception as ex:
            print(f"Error: no se pudo iniciar el hilo. ex: {ex}")
            
        try:
            with open('image_path.pkl', 'rb') as f:
                image_path = pickle.load(f)
                self.ids.uploaded_image.source = image_path
        except Exception as ex:
            print(f"Error: no se pudo cargar la imagen. ex: {ex}")


    def uploadImage(self):
        root = Tk()
        root.withdraw()  
        filepath = filedialog.askopenfilename(filetypes=[('Image Files', '*.png *.jpg *.jpeg')])

        if filepath:
            self.ids.uploaded_image.source = filepath
            
            try:
                with open('image_path.pkl', 'wb') as f:
                    pickle.dump(filepath, f)
            except Exception as ex:
                print(f"Error: no se pudo guardar la imagen. ex: {ex}")

        root.destroy()
        
    def show_confirmation(self):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text='Seguro que deseas regar la planta?', color=[231/255, 237/255, 222/255, 1]))
        yes_button = Button(text='Yes', background_color=[28/255, 71/255, 35/255, 1], color=[231/255, 237/255, 222/255, 1])
        yes_button.bind(on_press=self.waterPlant)
        yes_button.bind(on_press=self.dismiss_popup)
        content.add_widget(yes_button)
        no_button = Button(text='No', background_color=[28/255, 71/255, 35/255, 1], color=[231/255, 237/255, 222/255, 1])
        no_button.bind(on_press=self.dismiss_popup)
        content.add_widget(no_button)

        self.confirmation_popup = Popup(title='Confirmation', content=content, size_hint=(None, None), size=('400dp', '200dp'), auto_dismiss=False)
        self.confirmation_popup.open()

    def dismiss_popup(self, instance):
        self.confirmation_popup.dismiss()
        
    def waterPlant(self, instance):
        print('Regando la planta')
        Publisher.send_message('aguita pa mi gente')
        UbidotsPublisher.send_message('regadita', 1)
        UbidotsPublisher.send_message('regadita', 0)

    @mainthread
    def procesarMensaje(self, topic, msg):
        print(f"recibido: {msg}. en topico: {topic}")
        if topic == 'water_level':
            self.water_level = float(msg)
            UbidotsPublisher.send_message('aguita', self.water_level)
        elif topic == 'humidity_temperature':
            humidity, temperature = msg.split(',')
            self.humidity = round((abs(2800 - float(humidity)) / 2800) * 100, 2) 
            self.temperature = float(temperature)
            UbidotsPublisher.send_message('humedadsita', self.humidity)
            UbidotsPublisher.send_message('temperaturita', self.temperature)
        elif topic == 'watered':
            UbidotsPublisher.send_message('regadita', 1)
            UbidotsPublisher.send_message('regadita', 0)
