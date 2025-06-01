import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import pickle

def redimensionar_imagen(imagen, nuevo_ancho=200):
    alto, ancho = imagen.shape[:2]
    nuevo_alto = int((nuevo_ancho / ancho) * alto)
    imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    imgresize = cv2.resize(imagen, (nuevo_ancho, nuevo_alto))
    f = np.zeros((nuevo_alto, 24))
    imgresize = np.concatenate((imgresize, f), axis=1)
    _, thresh = cv2.threshold(imgresize, 254, 255, cv2.THRESH_BINARY)
    final_filas, final_columnas = imgresize.shape
    return thresh, final_filas, final_columnas

def lista_bin_a_ent(lista_binarias):
    enteros = []
    for lista_binaria1 in lista_binarias:
        entero = 0
        ##es donde a lista_binaria 1 hacemos el reverso
        lista_binaria1.reverse()
        for bit in lista_binaria1:
            entero = (entero << 1) | bit
        enteros.append(int(entero))
    return enteros

def procesar_imagen(imagen, i_fila, final_columnas):
    hexf = []
    for y in range(i_fila):
        bina = []
        for x in range(final_columnas):
            bina.append(1) if imagen[y, x] <= 254 else bina.append(0)
        grupos = [bina[i:i + 8] for i in range(0, len(bina), 8)]
        entero = lista_bin_a_ent(grupos)
        hex1 = entero
        hexf.append(hex1)
    return hexf

class ImageLoaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CREACIÓN DE LA SECUENCIA")
        self.root.resizable(0, 0)
        #self.root.iconbitmap("icono.ico")
        self.root.geometry("650x550")


        self.image_paths = []
        self.processed_images = []
        self.resized_images = []

        self.create_widgets()

    def create_widgets(self):
        # Cargar imagen de fondo
        self.fondo = Image.open("imagen.png")
        self.fondo = self.fondo.resize((650, 550), Image.LANCZOS)
        self.fondo_photo = ImageTk.PhotoImage(self.fondo)

        # Crear un label para la imagen de fondo
        self.fondo_label = tk.Label(self.root, image=self.fondo_photo)
        self.fondo_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.nuevo_frame = tk.Frame(self.root, width=550, height=500, bg="gray45")
        self.nuevo_frame.place(x=50, y=25)

        self.button_frame = tk.Frame(self.nuevo_frame, width=540, height=490)
        self.button_frame.place(x=5, y=5)

        self.fondo2 = Image.open("fondo2.png")
        self.fondo2 = self.fondo2.resize((550, 500), Image.LANCZOS)
        self.fondo_photo2 = ImageTk.PhotoImage(self.fondo2)

        self.fondo_label2 = tk.Label(self.button_frame, image=self.fondo_photo2)
        self.fondo_label2.place(x=0, y=0, relwidth=1, relheight=1)

        self.path_frame = tk.Frame(self.nuevo_frame, width=165, height=175, bg="cyan4")
        self.path_frame.place(x=40, y=60)

        self.image_frame = tk.Frame(self.nuevo_frame, bd=2, relief=tk.SUNKEN, width=200, height=200)
        self.image_frame.place(x=280, y=110)
        self.fondo_frame = Image.open("fondo_img.jpeg")
        self.fondo_frame = self.fondo_frame.resize((200, 200), Image.LANCZOS)
        self.fondo_fondo = ImageTk.PhotoImage(self.fondo_frame)

        self.fondo_label1 = tk.Label(self.image_frame, image=self.fondo_fondo)
        self.fondo_label1.place(x=0, y=0, relwidth=1, relheight=1)

        self.load_button = tk.Button(self.button_frame, text="Cargar Imágenes", command=self.load_images)
        self.load_button.place(x=55, y=20)

        self.path_listbox = tk.Listbox(self.path_frame, selectmode=tk.SINGLE, width=25, height=10)
        self.path_listbox.place(x=5, y=5)
        self.path_listbox.bind('<ButtonRelease-1>', self.show_selected_image)

        self.add_button = tk.Button(self.button_frame, text="Agregar", command=self.add_image, height=1, width=8)
        self.add_button.place(x=180, y=20)

        self.added_image_frame = tk.Frame(self.nuevo_frame, width=165, height=175, bg="cyan4")
        self.added_image_frame.place(x=40, y=250)

        self.added_image_listbox = tk.Listbox(self.added_image_frame, selectmode=tk.SINGLE, width=25, height=10)
        self.added_image_listbox.place(x=5, y=5)
        self.added_image_listbox.image_list = []

        self.up_button = tk.Button(self.button_frame, text="Subir", command=self.move_up, height=1, width=8)
        self.up_button.place(x=267, y=20)

        self.down_button = tk.Button(self.button_frame, text="Bajar", command=self.move_down, height=1, width=8)
        self.down_button.place(x=355, y=20)

        self.delete_button = tk.Button(self.button_frame, text="Eliminar", command=self.delete_image, height=1, width=8)
        self.delete_button.place(x=440, y=20)

        self.save_frame = tk.Frame(self.nuevo_frame, width=195, height=28, bg="cyan4")
        self.save_frame.place(x=125, y=440)

        self.project_name_entry = tk.Entry(self.save_frame, width=30)
        self.project_name_entry.place(x=5, y=5)

        self.save_button = tk.Button(self.button_frame, text="Guardar Proyecto", command=self.save_project)
        self.save_button.place(x=325, y=435)


    def load_images(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.avif")])
        for file_path in file_paths:
            if file_path:
                image = cv2.imread(file_path)
                if image is not None:
                    self.image_paths.append(file_path)
                    self.path_listbox.insert(tk.END, file_path)
                else:
                    print(f"Error al cargar la imagen: {file_path}")

    def show_selected_image(self, event):
        selected_index = self.path_listbox.curselection()
        if selected_index:
            for widget in self.image_frame.winfo_children():
                widget.destroy()

            file_path = self.image_paths[selected_index[0]]
            image = Image.open(file_path)
            fixed_size = (200, 200)                                 # Tamaño fijo para las imágenes
            image = image.resize(fixed_size, Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)

            label = tk.Label(self.image_frame, image=photo, width=fixed_size[0], height=fixed_size[1])
            label.image = photo
            label.pack()

    def add_image(self):
        selected_index = self.path_listbox.curselection()
        if selected_index:
            file_path = self.image_paths[selected_index[0]]
            image = cv2.imread(file_path)

            resized_image, i_fila, final_columnas = redimensionar_imagen(image)
            self.resized_images.append((resized_image, i_fila, final_columnas))

            hexf = procesar_imagen(resized_image, i_fila, final_columnas)
            self.processed_images.append(hexf)

            resized_image_display = Image.fromarray(resized_image)
            resized_image_display = ImageTk.PhotoImage(resized_image_display)
            self.added_image_listbox.image_list.append(resized_image_display)
            self.added_image_listbox.insert(tk.END, f"Imagen {len(self.added_image_listbox.image_list)}")

    def move_up(self):
        selected_index = self.added_image_listbox.curselection()
        if selected_index and selected_index[0] > 0:
            item = self.added_image_listbox.get(selected_index)
            self.added_image_listbox.delete(selected_index)
            self.added_image_listbox.insert(selected_index[0] - 1, item)
            self.added_image_listbox.selection_set(selected_index[0] - 1)

            self.resized_images[selected_index[0]], self.resized_images[selected_index[0] - 1] = self.resized_images[selected_index[0] - 1], self.resized_images[selected_index[0]]

    def move_down(self):
        selected_index = self.added_image_listbox.curselection()
        if selected_index and selected_index[0] < self.added_image_listbox.size() - 1:
            item = self.added_image_listbox.get(selected_index)
            self.added_image_listbox.delete(selected_index)
            self.added_image_listbox.insert(selected_index[0] + 1, item)
            self.added_image_listbox.selection_set(selected_index[0] + 1)

            self.resized_images[selected_index[0]], self.resized_images[selected_index[0] + 1] = self.resized_images[selected_index[0] + 1], self.resized_images[selected_index[0]]

    def delete_image(self):
        selected_index = self.added_image_listbox.curselection()
        if selected_index:
            self.added_image_listbox.delete(selected_index)
            del self.resized_images[selected_index[0]]
            del self.processed_images[selected_index[0]]

    def save_project(self):
        project_name = self.project_name_entry.get()
        if project_name:
            data_programa_img = [self.image_paths, self.processed_images, self.resized_images]
            with open(f"{project_name}.pickle", "wb") as f:
                pickle.dump(data_programa_img, f)
            messagebox.showinfo("Guardar Proyecto", "El proyecto ha sido guardado exitosamente.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageLoaderApp(root)
    root.mainloop()
