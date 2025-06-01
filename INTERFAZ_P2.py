import tkinter as tk
from tkinter import filedialog
from threading import Thread, Event
from time import sleep
import pickle
from PIL import Image, ImageTk
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import copy
import numpy as np

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # Use chip GPIO numbering


SDI1, SDI2, SDI3, SDI4, SDI5, SDI6, SDI7= 12, 1, 7, 8, 25, 24, 23
SRCLK = 27
RCLK  = 22 
OE = 17

GPIO.setup(SDI1, GPIO.OUT, initial=GPIO.HIGH) # Set pin 11 to be an output pin and set initial value to low
GPIO.setup(SDI2, GPIO.OUT, initial=GPIO.HIGH) # Set pin 11 to be an output pin and set initial value to low
GPIO.setup(SDI3, GPIO.OUT, initial=GPIO.HIGH) # Set pin 11 to be an output pin and set initial value to low
GPIO.setup(SDI4, GPIO.OUT, initial=GPIO.HIGH) # Set pin 11 to be an output pin and set initial value to low
GPIO.setup(SDI5, GPIO.OUT, initial=GPIO.HIGH) # Set pin 11 to be an output pin and set initial value to low
GPIO.setup(SDI6, GPIO.OUT, initial=GPIO.HIGH) # Set pin 11 to be an output pin and set initial value to low
GPIO.setup(SDI7, GPIO.OUT, initial=GPIO.HIGH) # Set pin 11 to be an output pin and set initial value to low

GPIO.setup(SRCLK, GPIO.OUT, initial=GPIO.HIGH) 
GPIO.setup(RCLK, GPIO.OUT, initial=GPIO.HIGH) 

def Send_Data_74HC595(value):
    #--------Shift out 8 bits----------------------- 
    flag_SR=0 #4
    for data in range(0,4):       
        for bit in range(0, 8):
            GPIO.output(SDI1, 0x80 & ~(value[data] << bit))
            GPIO.output(SDI2, 0x80 & ~(value[4+data] << bit))
            GPIO.output(SDI3, 0x80 & ~(value[8+data] << bit))
            GPIO.output(SDI4, 0x80 & ~(value[12+data] << bit))
            GPIO.output(SDI5, 0x80 & ~(value[16+data] << bit))
            GPIO.output(SDI6, 0x80 & ~(value[20+data] << bit))
            GPIO.output(SDI7, 0x80 & ~(value[24+data] << bit))
            #GPIO.output(SDI2[4+flag_SR], 0x80 & (value << bit))
            GPIO.output(SRCLK, GPIO.LOW)
            sleep(0.0001)
            GPIO.output(SRCLK, GPIO.HIGH)
            sleep(0.0001)
            #print(data)
    #-------Transfer shifted bits to output---------    
    GPIO.output(RCLK, GPIO.LOW)
    sleep(0.001)
    GPIO.output(RCLK, GPIO.HIGH)
    sleep(0.001)
    #-----------------------------------------------

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Ejecución")
        self.root.resizable(0, 0)
        #self.root.iconbitmap("icono.ico")
        self.root.geometry("450x500")

        self.fondo = Image.open("imagen.png")
        self.fondo = self.fondo.resize((450, 500), Image.LANCZOS)
        self.fondo_photo = ImageTk.PhotoImage(self.fondo)

        # Crear un label para la imagen de fondo
        self.fondo_label = tk.Label(self.root, image=self.fondo_photo)
        self.fondo_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Crear botones
        self.load_button = tk.Button(root, text="Cargar Archivo", command=self.load_file, height=1, width=12)
        self.start_button = tk.Button(root, text="Inicio", command=self.start, state=tk.DISABLED, height=1, width=12)
        self.pause_button = tk.Button(root, text="Pausa", command=self.pause, state=tk.DISABLED, height=1, width=12)
        self.stop_button = tk.Button(root, text="Stop", command=self.stop, state=tk.DISABLED, height=1, width=12)

        # Crear etiquetas
        self.label_imagenes = tk.Label(root, text="Imagen: 0", height=1, width=10, font=('Helvetica', 12))

        # Crear un frame para la imagen
        self.image_frame = tk.Frame(self.root, bd=2, relief=tk.SUNKEN, width=200, height=200)
        self.image_frame.place(x=125, y=50)
        self.nueva_imagen = Image.open("fondo_img.jpeg")
        self.nueva_imagen = self.nueva_imagen.resize((200, 200), Image.LANCZOS)
        self.image_image = ImageTk.PhotoImage(self.nueva_imagen)

        self.image_label = tk.Label(self.image_frame, image=self.image_image)
        self.image_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Colocar botones, etiquetas y frame en la ventana
        self.load_button.pack(pady=10)
        self.start_button.pack(pady=10)
        self.pause_button.pack(pady=10)
        self.stop_button.pack(pady=10)
        self.label_imagenes.pack(pady=10)
        self.image_frame.pack(pady=10)

        self.stop_event = Event()
        self.pause_event = Event()
        self.thread = None
        self.obj = None

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Pickle files", "*.pickle")])
        if file_path:
            with open(file_path, "rb") as f:
                self.obj = pickle.load(f)
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)

    def start(self):
        if self.thread is None or not self.thread.is_alive():
            self.stop_event.clear()
            self.pause_event.clear()
            self.thread = Thread(target=self.run)
            self.thread.start()
        else:
            self.pause_event.clear()  # Reanuda el hilo si está pausado

    def pause(self):
        self.pause_event.set()  # Pone en pausa la ejecución

    def stop(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join()
            self.thread = None

    def run(self):
        if self.obj is None:
            return  # No hacer nada si el archivo no está cargado

        while not self.stop_event.is_set():
            for imagenes in range(0, len(self.obj[1])):
                if self.stop_event.is_set():
                    break
                while self.pause_event.is_set():
                    if self.stop_event.is_set():
                        break
                    sleep(0.001)  # Verificar cada 100 ms si se ha detenido o reanudado
                if self.stop_event.is_set():
                    break

                # Actualizar la etiqueta con el valor actual de 'imagenes'
                self.label_imagenes.config(text=f"Imagen: {imagenes}")

                # Mostrar la imagen actual en el layout aparte
                self.update_image(self.obj[2][imagenes][0])

                #print(imagenes)
                for filas in self.obj[1][imagenes]:
                    #print(filas)
                    sleep(0.0005)  # Pausa de 20 milisegundos

    def update_image(self, image_data):
        # Convertir los datos de imagen a un objeto PIL Image
        image = Image.fromarray(np.array(image_data, dtype='uint8'))
        image = image.resize((200, 200))  # Ajustar el tamaño de la imagen si es necesario
        image_tk = ImageTk.PhotoImage(image)

        # Actualizar la etiqueta de la imagen
        self.image_label.config(image=image_tk)
        self.image_label.image = image_tk  # Guardar una referencia para evitar que se recoja basura

if __name__ == "__main__":
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()