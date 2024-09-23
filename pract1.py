import sys
import glob
import serial
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from ttkthemes import ThemedTk

# Función que nos la lista de puertos seriales
def obtener_puertos_disponibles():
    if sys.platform.startswith('win'):
        puertos = [f'COM{i + 1}' for i in range(256)]
    elif sys.platform.startswith(('linux', 'cygwin')):
        puertos = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        puertos = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Plataforma no compatible')

    puertos_validos = []
    for puerto in puertos:
        try:
            s = serial.Serial(puerto)
            s.close()
            puertos_validos.append(puerto)
        except (OSError, serial.SerialException):
            pass
    return puertos_validos

# Inicialización de variable global para conexión serial
conexion_serial = None

# Función para establecer conexión con el puerto seleccionado
def conectar_serial():
    global conexion_serial
    puerto = puerto_combobox.get()
    baud_rate = baud_combobox.get()

    if puerto and baud_rate:
        try:
            conexion_serial = serial.Serial(puerto, int(baud_rate), timeout=1)
            estado_led.config(image=img_led_verde)
            messagebox.showinfo("Estado", "Conexión establecida correctamente")
        except serial.SerialException as e:
            estado_led.config(image=img_led_rojo)
            messagebox.showerror("Error", f"Fallo al conectar: {e}")
    else:
        messagebox.showerror("Error", "Seleccione un puerto y una velocidad correcta")

# Función para encender el LED
def activar_led():
    if conexion_serial:
        try:
            conexion_serial.write(b'1')
            messagebox.showinfo("LED", "El LED ha sido encendido")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo encender el LED: {e}")
    else:
        messagebox.showerror("Error", "No se ha establecido una conexión serial")

# Función para apagar el LED
def desactivar_led():
    if conexion_serial:
        try:
            conexion_serial.write(b'0')
            messagebox.showinfo("LED", "El LED ha sido apagado")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo apagar el LED: {e}")
    else:
        messagebox.showerror("Error", "No se ha establecido una conexión serial")

# Configurar el valor del PWM
def ajustar_pwm():
    if conexion_serial:
        try:
            pwm_valor = int(pwm_entrada.get())
            if 0 <= pwm_valor <= 255:
                conexion_serial.write(f'P{pwm_valor}'.encode())
                messagebox.showinfo("PWM", f"PWM ajustado a: {pwm_valor}")
            else:
                messagebox.showerror("Error", "El valor PWM debe estar entre 0 y 255")
        except ValueError:
            messagebox.showerror("Error", "Debe ingresar un número válido")
    else:
        messagebox.showerror("Error", "No hay conexión serial")

# Convertir el valor de DAC
def establecer_dac():
    if conexion_serial:
        try:
            dac_valor = int(dac_entrada.get())
            if 0 <= dac_valor <= 255:
                conexion_serial.write(f'D{dac_valor}'.encode())
                messagebox.showinfo("DAC", f"DAC ajustado a: {dac_valor}")
            else:
                messagebox.showerror("Error", "El valor DAC debe estar entre 0 y 255")
        except ValueError:
            messagebox.showerror("Error", "Debe ingresar un número válido")
    else:
        messagebox.showerror("Error", "No hay conexión serial")

# Manejo de opciones para habilitar/deshabilitar campos
def gestionar_opciones():
    seleccion = opciones_spinbox.get()
    entrada_valor1.config(state="normal")
    btn_incrementar.config(state="normal")
    dac_entrada.config(state="normal")
    btn_dac.config(state="normal")
    pwm_entrada.config(state="normal")
    btn_pwm.config(state="normal")

    if seleccion == "1":
        dac_entrada.config(state="disabled")
        btn_dac.config(state="disabled")
        pwm_entrada.config(state="disabled")
        btn_pwm.config(state="disabled")
    elif seleccion == "2":
        entrada_valor1.config(state="disabled")
        btn_incrementar.config(state="disabled")
        pwm_entrada.config(state="disabled")
        btn_pwm.config(state="disabled")
    elif seleccion == "3":
        entrada_valor1.config(state="disabled")
        btn_incrementar.config(state="disabled")
        dac_entrada.config(state="disabled")
        btn_dac.config(state="disabled")

# Incrementar valor en entrada
def incrementar(entrada, etiqueta_resultado):
    try:
        valor_actual = int(entrada.get())
        nuevo_valor = valor_actual + 1
        etiqueta_resultado.config(text=f"Nuevo valor: {nuevo_valor}")
    except ValueError:
        messagebox.showerror("Error", "Por favor, ingrese un número válido")

# Configuración de la interfaz gráfica
ventana = ThemedTk(theme="breeze")
ventana.geometry("1000x1000")
ventana.title("Interfaz Serial de Control")

# Crear las pestañas
notebook = ttk.Notebook(ventana)
pestana_conexion = ttk.Frame(notebook)
pestana_control = ttk.Frame(notebook)
pestana_opciones = ttk.Frame(notebook)

notebook.add(pestana_conexion, text="Tab1")
notebook.add(pestana_control, text="Tab2")
notebook.add(pestana_opciones, text="Tab3")
notebook.pack(expand=1, fill="both")

# Imágenes para los estados del LED
img_led_verde = ImageTk.PhotoImage(Image.open("ledverde.png").resize((60, 60)))
img_led_rojo = ImageTk.PhotoImage(Image.open("ledrojo.png").resize((60, 60)))

# --- TAB 1 de conexión ---
lbl_puerto = ttk.Label(pestana_conexion, text="Elegir puerto Serial:")
lbl_puerto.grid(row=0, column=0, padx=10, pady=10)
puerto_combobox = ttk.Combobox(pestana_conexion, values=obtener_puertos_disponibles() or ["No se encontraron puertos"])
puerto_combobox.grid(row=0, column=1, padx=10, pady=10)

lbl_baud = ttk.Label(pestana_conexion, text="Baud Rate:")
lbl_baud.grid(row=0, column=2, padx=10, pady=10)
baud_combobox = ttk.Combobox(pestana_conexion, values=["9600", "115200", "19200", "57600"])
baud_combobox.grid(row=0, column=3, padx=10, pady=10)

btn_conectar = ttk.Button(pestana_conexion, text="Conectar", command=conectar_serial)
btn_conectar.grid(row=1, column=1, columnspan=4, padx=10, pady=10)

estado_led = ttk.Label(pestana_conexion, image=img_led_rojo)
estado_led.grid(row=1, column=4, padx=10, pady=10)

btn_led_on = ttk.Button(pestana_conexion, text="Encender LED", command=activar_led)
btn_led_on.grid(row=2, column=2, padx=10, pady=10)

btn_led_off = ttk.Button(pestana_conexion, text="Apagar LED", command=desactivar_led)
btn_led_off.grid(row=2, column=4, padx=10, pady=10)

# --- TAB2 de control ---
opciones_spinbox = ttk.Spinbox(pestana_control, from_=1, to=3)
opciones_spinbox.grid(row=0, column=0, padx=10, pady=10)

btn_confirmar_opcion = ttk.Button(pestana_control, text="Seleccionar Opción", command=gestionar_opciones)
btn_confirmar_opcion.grid(row=0, column=1, padx=10, pady=10)

# Opción 1: Incrementar valor
lbl_opcion1 = ttk.Label(pestana_control, text="Valor a Incrementar:")
lbl_opcion1.grid(row=1, column=0, padx=10, pady=10)

entrada_valor1 = ttk.Entry(pestana_control)
entrada_valor1.grid(row=1, column=1, padx=10, pady=10)

etiqueta_resultado = ttk.Label(pestana_control, text="Resultado:")
etiqueta_resultado.grid(row=1, column=2, padx=10, pady=10)

btn_incrementar = ttk.Button(pestana_control, text="Incrementar", command=lambda: incrementar(entrada_valor1, etiqueta_resultado))
btn_incrementar.grid(row=1, column=3, padx=10, pady=10)

# Opción 2: Configuración de DAC
lbl_dac = ttk.Label(pestana_control, text="DAC (0-255):")
lbl_dac.grid(row=2, column=0, padx=10, pady=10)

dac_entrada = ttk.Entry(pestana_control)
dac_entrada.grid(row=2, column=1, padx=10, pady=10)

btn_dac = ttk.Button(pestana_control, text="Ajustar DAC", command=establecer_dac)
btn_dac.grid(row=2, column=2, padx=10, pady=10)

# Opción 3: Configuración de PWM
lbl_pwm = ttk.Label(pestana_control, text="PWM (0-255):")
lbl_pwm.grid(row=3, column=0, padx=10, pady=10)

pwm_entrada = ttk.Entry(pestana_control)
pwm_entrada.grid(row=3, column=1, padx=10, pady=10)

btn_pwm = ttk.Button(pestana_control, text="Ajustar PWM", command=ajustar_pwm)
btn_pwm.grid(row=3, column=2, padx=10, pady=10)

# Iniciar la aplicación
ventana.mainloop()