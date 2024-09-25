import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime, timedelta
import json


class CarreraResistenciaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Carrera de Resistencia 24H")
        self.pilotos = []
        self.datos_equipo = {}
        self.num_vuelta_global = 0
        self.inicio_vuelta = None
        self.vuelta_en_curso = False
        self.en_boxes = False
        self.incidencia_actual = None
        self.sesion_actual = None

        self.tiempo_vuelta_actual = tk.StringVar(value="00:00.000")
        self.tiempo_boxes_actual = tk.StringVar(value="00:00:00.000")
        self.piloto_actual = tk.StringVar(value="Selecciona un piloto")

        self.tiempos_vueltas_label = []

        self.incidencias = []  # Lista de incidencias activas

        self.create_widgets()

    def create_widgets(self):
        """Crear los widgets para la interfaz"""
        # Agregar widgets para los pilotos
        frame_pilotos = tk.Frame(self.root)
        frame_pilotos.pack(pady=10)
        self.entry_nombre_piloto = tk.Entry(frame_pilotos)
        self.entry_nombre_piloto.pack(side=tk.LEFT)
        btn_agregar_piloto = tk.Button(frame_pilotos, text="Agregar Piloto", command=self.agregar_piloto)
        btn_agregar_piloto.pack(side=tk.LEFT)

        # Inicializar OptionMenu con una selección por defecto
        self.lista_pilotos = tk.OptionMenu(self.root, self.piloto_actual, "Selecciona un piloto")
        self.lista_pilotos.pack(pady=10)

        # Botón para iniciar/finalizar vueltas
        self.btn_cronometro_vuelta = tk.Button(self.root, text="Iniciar Vuelta", command=self.cronometro_vuelta,
                                               bg="green", fg="white")
        self.btn_cronometro_vuelta.pack(pady=10)

        # Label para mostrar el tiempo de la vuelta actual
        self.lbl_tiempo_vuelta_actual = tk.Label(self.root, textvariable=self.tiempo_vuelta_actual,
                                                 font=("Helvetica", 16))
        self.lbl_tiempo_vuelta_actual.pack(pady=10)

        # Frame para mostrar las vueltas
        self.frame_vueltas = tk.Frame(self.root)
        self.frame_vueltas.pack(pady=10)

        # Título de columnas
        lbl_vuelta_title = tk.Label(self.frame_vueltas, text="Vuelta", width=10, font=("Helvetica", 12, "bold"))
        lbl_vuelta_title.grid(row=0, column=0)
        lbl_piloto_title = tk.Label(self.frame_vueltas, text="Piloto", width=20, font=("Helvetica", 12, "bold"))
        lbl_piloto_title.grid(row=0, column=1)
        lbl_tiempo_title = tk.Label(self.frame_vueltas, text="Tiempo", width=20, font=("Helvetica", 12, "bold"))
        lbl_tiempo_title.grid(row=0, column=2)
        lbl_diferencia_title = tk.Label(self.frame_vueltas, text="Diferencia", width=20, font=("Helvetica", 12, "bold"))
        lbl_diferencia_title.grid(row=0, column=3)
        lbl_indicador_title = tk.Label(self.frame_vueltas, text="Indicador", width=10, font=("Helvetica", 12, "bold"))
        lbl_indicador_title.grid(row=0, column=4)

        # Botón para guardar sesión
        btn_guardar_sesion = tk.Button(self.root, text="Guardar Sesión", command=self.guardar_sesion)
        btn_guardar_sesion.pack(pady=10)

        # Botón para abrir sesión
        btn_abrir_sesion = tk.Button(self.root, text="Abrir Sesión", command=self.abrir_sesion)
        btn_abrir_sesion.pack(pady=10)

        # Botón para gestionar incidencias
        self.btn_incidencia = tk.Button(self.root, text="Iniciar Incidencia", command=self.registrar_incidencia,
                                        bg="orange", fg="black")
        self.btn_incidencia.pack(pady=10)

        # Botón para finalizar incidencias (se desactiva hasta que una incidencia esté activa)
        self.btn_finalizar_incidencia = tk.Button(self.root, text="Finalizar Incidencia",
                                                  command=self.finalizar_incidencia, bg="red", fg="white",
                                                  state=tk.DISABLED)
        self.btn_finalizar_incidencia.pack(pady=10)

        # Botón para gestionar la entrada/salida de boxes
        self.btn_boxes = tk.Button(self.root, text="Entrar a Boxes", command=self.gestion_boxes, bg="blue", fg="white")
        self.btn_boxes.pack(pady=10)

        self.root.after(100, self.actualizar_tiempo)  # Actualización periódica del cronómetro

    def agregar_piloto(self):
        """Agregar un nuevo piloto al equipo."""
        nombre = self.entry_nombre_piloto.get()
        if nombre and nombre not in self.pilotos:
            self.pilotos.append(nombre)
            self.datos_equipo[nombre] = {"vueltas": [], "incidencias": [], "boxes": []}
            self.actualizar_lista_pilotos()
            self.entry_nombre_piloto.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "El nombre del piloto es inválido o ya existe.")

    def actualizar_lista_pilotos(self):
        """Actualizar el menú desplegable de pilotos."""
        menu = self.lista_pilotos["menu"]
        menu.delete(0, "end")
        for piloto in self.pilotos:
            menu.add_command(label=piloto, command=tk._setit(self.piloto_actual, piloto))

    def cronometro_vuelta(self):
        """Función de cronómetro para iniciar y finalizar vuelta con el mismo botón."""
        if not self.vuelta_en_curso:  # Si la vuelta no ha comenzado
            if self.piloto_actual.get() == "Selecciona un piloto":
                messagebox.showerror("Error", "Debes seleccionar un piloto para iniciar la vuelta.")
                return
            self.iniciar_vuelta()
        else:  # Si la vuelta está en curso, finalizarla
            self.finalizar_vuelta()

    def iniciar_vuelta(self):
        """Iniciar el cronómetro para una nueva vuelta."""
        self.inicio_vuelta = datetime.now()
        self.vuelta_en_curso = True
        self.btn_cronometro_vuelta.config(text="Finalizar Vuelta", bg="red", fg="white")

    def finalizar_vuelta(self):
        """Finalizar la vuelta y registrar el tiempo."""
        if self.inicio_vuelta is None:
            messagebox.showerror("Error", "No se ha iniciado ninguna vuelta.")
            return
        fin_vuelta = datetime.now()
        tiempo_vuelta = fin_vuelta - self.inicio_vuelta
        self.num_vuelta_global += 1
        self.datos_equipo[self.piloto_actual.get()]["vueltas"].append(tiempo_vuelta)
        self.mostrar_vuelta(self.num_vuelta_global, self.piloto_actual.get(), tiempo_vuelta)

        # Reiniciar cronómetro de vuelta
        self.inicio_vuelta = None
        self.tiempo_vuelta_actual.set("00:00.000")
        self.vuelta_en_curso = False
        self.btn_cronometro_vuelta.config(text="Iniciar Vuelta", bg="green", fg="white")

    def mostrar_vuelta(self, num_vuelta, piloto, tiempo_vuelta, tipo="Vuelta", tiempo_diferencia="", indicador=""):
        """Mostrar la vuelta en la interfaz."""
        fila = len(self.tiempos_vueltas_label) + 1
        lbl_vuelta = tk.Label(self.frame_vueltas, text=str(num_vuelta), width=10)
        lbl_vuelta.grid(row=fila, column=0)
        lbl_piloto = tk.Label(self.frame_vueltas, text=piloto, width=20)
        lbl_piloto.grid(row=fila, column=1)

        # Formatear tiempo en minutos, segundos y milésimas
        tiempo_formateado = self.formatear_tiempo(tiempo_vuelta)
        lbl_tiempo = tk.Label(self.frame_vueltas, text=tiempo_formateado, width=20)
        lbl_tiempo.grid(row=fila, column=2)

        # Mostrar la diferencia con la vuelta anterior y el indicador
        lbl_diferencia = tk.Label(self.frame_vueltas, text=tiempo_diferencia, width=20)
        lbl_diferencia.grid(row=fila, column=3)
        lbl_indicador = tk.Label(self.frame_vueltas, text=indicador, width=10)
        lbl_indicador.grid(row=fila, column=4)

        # Añadir la vuelta registrada a la lista de etiquetas
        self.tiempos_vueltas_label.append((lbl_vuelta, lbl_piloto, lbl_tiempo, lbl_diferencia, lbl_indicador))

    def formatear_tiempo(self, tiempo):
        """Formatear tiempo en minutos, segundos y milésimas."""
        total_segundos = int(tiempo.total_seconds())
        minutos, segundos = divmod(total_segundos, 60)
        milisegundos = int(tiempo.microseconds / 1000)
        return f"{minutos:02}:{segundos:02}.{milisegundos:03}"

    def calcular_diferencia(self, num_vuelta, piloto, tiempo_vuelta):
        """Calcular la diferencia con la vuelta anterior."""
        tiempo_anterior = self.datos_equipo[piloto]["vueltas"][-2] if len(
            self.datos_equipo[piloto]["vueltas"]) > 1 else timedelta(0)
        diferencia = tiempo_vuelta - tiempo_anterior

        if diferencia.total_seconds() < 0:
            return self.formatear_tiempo(abs(diferencia)), True  # Más rápida
        else:
            return self.formatear_tiempo(diferencia), False  # Más lenta

    def registrar_incidencia(self):
        """Registrar una incidencia mediante una ventana emergente."""

        def set_incidencia(tipo):
            self.incidencia_actual = {"tipo": tipo, "inicio_vuelta": self.num_vuelta_global,
                                      "inicio_hora": datetime.now()}
            self.datos_equipo[self.piloto_actual.get()]["incidencias"].append(self.incidencia_actual)
            incidencia_window.destroy()
            self.btn_finalizar_incidencia.config(state=tk.NORMAL)
            # Añadir al resumen la incidencia como un evento en la vuelta actual
            self.mostrar_vuelta(self.num_vuelta_global, self.piloto_actual.get(), timedelta(0),
                                tipo="Inicio de Incidencia")

        incidencia_window = tk.Toplevel(self.root)
        incidencia_window.title("Seleccionar Incidencia")
        for tipo in ["Safety Car", "Bandera Roja", "Bandera Amarilla", "Bandera Negra"]:
            btn = tk.Button(incidencia_window, text=tipo, command=lambda t=tipo: set_incidencia(t))
            btn.pack(pady=5)

    def finalizar_incidencia(self):
        """Finalizar la incidencia actual."""
        if not self.incidencia_actual:
            messagebox.showerror("Error", "No hay ninguna incidencia activa para finalizar.")
            return
        self.incidencia_actual["fin_vuelta"] = self.num_vuelta_global
        self.incidencia_actual["fin_hora"] = datetime.now()
        self.btn_finalizar_incidencia.config(state=tk.DISABLED)
        self.mostrar_incidencia(self.incidencia_actual)
        # Añadir al resumen el fin de la incidencia en la vuelta actual
        self.mostrar_vuelta(self.num_vuelta_global, self.piloto_actual.get(), timedelta(0), tipo="Fin de Incidencia")
        self.incidencia_actual = None

    def mostrar_incidencia(self, incidencia):
        """Mostrar la incidencia en la interfaz."""
        messagebox.showinfo("Incidencia Registrada",
                            f"Incidencia '{incidencia['tipo']}'\nInicio en vuelta: {incidencia['inicio_vuelta']}\nFin en vuelta: {incidencia['fin_vuelta']}")

    def gestion_boxes(self):
        """Registrar entrada o salida de boxes."""
        if not self.en_boxes:
            # Registrar entrada a boxes
            self.inicio_boxes = datetime.now()
            self.en_boxes = True
            self.btn_boxes.config(text="Salir de Boxes", bg="red")
            # Añadir al resumen la entrada a boxes
            self.mostrar_vuelta(self.num_vuelta_global, self.piloto_actual.get(), timedelta(0), tipo="Entrada a Boxes")
        else:
            # Registrar salida de boxes
            fin_boxes = datetime.now()
            tiempo_boxes = fin_boxes - self.inicio_boxes
            self.datos_equipo[self.piloto_actual.get()]["boxes"].append(tiempo_boxes)
            self.mostrar_tiempo_boxes(tiempo_boxes)
            self.en_boxes = False
            self.btn_boxes.config(text="Entrar a Boxes", bg="blue")
            # Añadir al resumen la salida de boxes con el tiempo total
            self.mostrar_vuelta(self.num_vuelta_global, self.piloto_actual.get(), tiempo_boxes, tipo="Salida de Boxes")

    def mostrar_tiempo_boxes(self, tiempo_boxes):
        """Mostrar el tiempo de boxes actual."""
        tiempo_formateado = str(tiempo_boxes)
        self.tiempo_boxes_actual.set(tiempo_formateado)
        messagebox.showinfo("Tiempo en Boxes", f"Tiempo en boxes: {tiempo_formateado}")

    def actualizar_tiempo(self):
        """Actualizar el tiempo en pantalla si la vuelta está en curso."""
        if self.vuelta_en_curso and self.inicio_vuelta:
            tiempo_actual = datetime.now() - self.inicio_vuelta
            self.tiempo_vuelta_actual.set(self.formatear_tiempo(tiempo_actual))
        self.root.after(100, self.actualizar_tiempo)

    def guardar_sesion(self):
        """Guardar la sesión actual en un archivo JSON."""
        self.sesion_actual = filedialog.asksaveasfilename(defaultextension=".json",
                                                          filetypes=[("JSON files", "*.json")])
        if self.sesion_actual:
            with open(self.sesion_actual, 'w') as f:
                json.dump({
                    "pilotos": self.pilotos,
                    "datos_equipo": self.datos_equipo,
                    "num_vuelta_global": self.num_vuelta_global,
                    "vuelta_en_curso": self.vuelta_en_curso,
                    "inicio_vuelta": self.inicio_vuelta.isoformat() if self.inicio_vuelta else None,
                }, f)

    def abrir_sesion(self):
        """Abrir una sesión guardada desde un archivo JSON."""
        self.sesion_actual = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if self.sesion_actual:
            with open(self.sesion_actual, 'r') as f:
                datos = json.load(f)
                self.pilotos = datos["pilotos"]
                self.datos_equipo = datos["datos_equipo"]
                self.num_vuelta_global = datos["num_vuelta_global"]
                self.vuelta_en_curso = datos["vuelta_en_curso"]
                self.inicio_vuelta = datetime.fromisoformat(datos["inicio_vuelta"]) if datos["inicio_vuelta"] else None
                self.actualizar_lista_pilotos()
                self.mostrar_vueltas_recuperadas()

    def mostrar_vueltas_recuperadas(self):
        """Mostrar las vueltas recuperadas en la interfaz."""
        for piloto in self.pilotos:
            for idx, tiempo in enumerate(self.datos_equipo[piloto]["vueltas"]):
                self.num_vuelta_global += 1
                self.mostrar_vuelta(self.num_vuelta_global, piloto, tiempo)


if __name__ == "__main__":
    root = tk.Tk()
    app = CarreraResistenciaApp(root)
    root.mainloop()
