# app.py - Servidor Flask para Raspberry Pi
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
import glob
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

# Configuración
UPLOAD_FOLDER = 'uploads'
ICONOS_FOLDER = 'static/iconos'
CONFIG_FILE = 'configuracion_actual.json'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Variable para controlar si es la primera imagen de una nueva sesión
primera_imagen_sesion = True

# Crear directorios necesarios
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ICONOS_FOLDER, exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('templates', exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def limpiar_uploads():
    """Elimina todos los archivos del directorio uploads"""
    try:
        files = glob.glob(os.path.join(UPLOAD_FOLDER, '*'))
        for file in files:
            if os.path.isfile(file):
                os.remove(file)
        print(f"Limpiados {len(files)} archivos del directorio uploads")
    except Exception as e:
        print(f"Error al limpiar uploads: {e}")


def cargar_configuracion_actual():
    """Carga la configuración actual si existe"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error al cargar configuración: {e}")
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/subir-imagen', methods=['POST'])
def subir_imagen():
    global primera_imagen_sesion
    try:
        # Si es la primera imagen de una nueva sesión, limpiar uploads
        if primera_imagen_sesion:
            limpiar_uploads()
            primera_imagen_sesion = False

        if 'imagen' not in request.files:
            return jsonify({'success': False, 'error': 'No se encontró archivo'})

        file = request.files['imagen']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No se seleccionó archivo'})

        if file and allowed_file(file.filename):
            # Mantener el nombre original
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            return jsonify({
                'success': True,
                'filename': filename,
                'message': 'Imagen subida exitosamente'
            })
        else:
            return jsonify({'success': False, 'error': 'Formato de archivo no permitido'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/configuracion', methods=['POST'])
def recibir_configuracion():
    global primera_imagen_sesion
    try:
        secuencia = request.get_json()

        # Resetear la bandera para la próxima sesión
        primera_imagen_sesion = True

        # Procesar la secuencia para manejar nombres de archivo de imágenes
        secuencia_procesada = []

        for elemento in secuencia:
            elemento_procesado = elemento.copy()

            # Si el elemento es de tipo imagen y tiene imagen_nombre
            if (elemento.get('tipo') == 'imagen' and
                    'imagen_nombre' in elemento and
                    elemento['imagen_nombre']):

                # Buscar el archivo en uploads que coincida
                imagen_nombre = elemento['imagen_nombre']
                archivo_encontrado = None

                # Buscar archivos en uploads
                for archivo in os.listdir(UPLOAD_FOLDER):
                    if os.path.isfile(os.path.join(UPLOAD_FOLDER, archivo)):
                        archivo_encontrado = archivo
                        break

                if archivo_encontrado:
                    elemento_procesado['archivo'] = archivo_encontrado
                    print(f"Imagen {imagen_nombre} asociada con archivo {archivo_encontrado}")
                else:
                    print(f"Advertencia: No se encontró archivo para imagen {imagen_nombre}")
                    elemento_procesado['archivo'] = None

            secuencia_procesada.append(elemento_procesado)

        # Guardar configuración actual (sobrescribir la anterior)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(secuencia_procesada, f, indent=2, ensure_ascii=False)

        print("Configuración recibida y procesada:", secuencia_procesada)

        # Aquí puedes agregar la lógica para procesar la secuencia
        # Por ejemplo, controlar GPIO, mostrar en pantalla, etc.

        return jsonify({
            'success': True,
            'message': 'Configuración recibida exitosamente',
            'elementos': len(secuencia_procesada)
        })
    except Exception as e:
        print(f"Error en configuración: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/configuracion', methods=['GET'])
def obtener_configuracion():
    """Endpoint para obtener la configuración actual"""
    try:
        config = cargar_configuracion_actual()
        if config:
            return jsonify({
                'success': True,
                'configuracion': config,
                'total_elementos': len(config)
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No se encontró configuración'
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/limpiar', methods=['POST'])
def limpiar_todo():
    """Endpoint para limpiar todos los archivos y configuración"""
    global primera_imagen_sesion
    try:
        # Limpiar uploads
        limpiar_uploads()

        # Eliminar configuración actual
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)

        # Resetear bandera
        primera_imagen_sesion = True

        return jsonify({
            'success': True,
            'message': 'Archivos y configuración limpiados exitosamente'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/estado', methods=['GET'])
def obtener_estado():
    """Endpoint para obtener el estado actual del sistema"""
    try:
        # Contar archivos en uploads
        uploads_files = len([f for f in os.listdir(UPLOAD_FOLDER)
                             if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))])

        # Verificar si existe configuración
        config_exists = os.path.exists(CONFIG_FILE)

        config_info = None
        if config_exists:
            config = cargar_configuracion_actual()
            if config:
                config_info = {
                    'total_elementos': len(config),
                    'elementos_con_imagen': len([e for e in config
                                                 if e.get('tipo') == 'imagen' and e.get('archivo')])
                }

        return jsonify({
            'success': True,
            'uploads_count': uploads_files,
            'config_exists': config_exists,
            'config_info': config_info,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    '''
        print("=== Servidor Flask Iniciado ===")
        print(f"Directorio de uploads: {UPLOAD_FOLDER}")
        print(f"Archivo de configuración: {CONFIG_FILE}")
        print("Endpoints disponibles:")
        print("  GET  /                    - Página principal")
        print("  POST /subir-imagen       - Subir imagen")
        print("  POST /configuracion      - Recibir configuración")
        print("  GET  /configuracion      - Obtener configuración actual")
        print("  GET  /uploads/<filename> - Acceder a archivos subidos")
        print("  POST /limpiar           - Limpiar archivos y configuración")
        print("  GET  /estado            - Obtener estado del sistema")
        print("===============================")
    '''
    # Ejecutar en todas las interfaces para acceso por IP
    app.run(host='0.0.0.0', port=5000, debug=True)