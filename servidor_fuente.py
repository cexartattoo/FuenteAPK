# app.py - Servidor Flask para Raspberry Pi
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

# Configuración
UPLOAD_FOLDER = 'uploads'
ICONOS_FOLDER = 'static/iconos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Crear directorios necesarios
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ICONOS_FOLDER, exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('templates', exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/subir-imagen', methods=['POST'])
def subir_imagen():
    try:
        if 'imagen' not in request.files:
            return jsonify({'success': False, 'error': 'No se encontró archivo'})

        file = request.files['imagen']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No se seleccionó archivo'})

        if file and allowed_file(file.filename):
            # Generar nombre único
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)

            return jsonify({
                'success': True,
                'filename': unique_filename,
                'message': 'Imagen subida exitosamente'
            })
        else:
            return jsonify({'success': False, 'error': 'Formato de archivo no permitido'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/configuracion', methods=['POST'])
def recibir_configuracion():
    try:
        secuencia = request.get_json()

        # Guardar configuración en archivo JSON
        config_file = f"configuracion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(config_file, 'w') as f:
            json.dump(secuencia, f, indent=2)

        print("Configuración recibida:", secuencia)

        # Aquí puedes agregar la lógica para procesar la secuencia
        # Por ejemplo, controlar GPIO, mostrar en pantalla, etc.

        return jsonify({
            'success': True,
            'message': 'Configuración recibida exitosamente',
            'elementos': len(secuencia)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)





def crear_archivos_web():
    # Crear archivo HTML
    html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Control de Fuente</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Control de Fuente</h1>
        </div>

        <div class="lista-elementos" id="listaElementos">
            <!-- Los elementos se agregan aquí dinámicamente -->
        </div>

        <div class="botones-principales">
            <button class="boton-accion" onclick="seleccionarImagen()">
                <span class="icono">🖼️</span>
            </button>
            <button class="boton-accion" onclick="agregarElemento('reloj')">
                <span class="icono">🕐</span>
            </button>
            <button class="boton-accion" onclick="agregarElemento('fecha')">
                <span class="icono">📅</span>
            </button>
            <button class="boton-accion boton-enviar" onclick="enviarConfiguracion()">
                <span class="icono">📤</span>
            </button>
        </div>
    </div>

    <!-- Input oculto para selección de archivos -->
    <input type="file" id="inputImagen" accept="image/*" style="display: none;" onchange="procesarImagen(this)">

    <!-- Modal para mensajes -->
    <div id="modal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="cerrarModal()">&times;</span>
            <h3 id="modalTitulo"></h3>
            <p id="modalMensaje"></p>
        </div>
    </div>

    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
</body>
</html>"""

    # Crear archivo CSS
    css_content = """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Roboto', Arial, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: #333;
}

.container {
    max-width: 360px;
    margin: 0 auto;
    background: white;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 0 20px rgba(0,0,0,0.1);
}

.header {
    background: #4CAF50;
    color: white;
    padding: 20px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header h1 {
    font-size: 24px;
    font-weight: 300;
}

.lista-elementos {
    flex: 1;
    padding: 10px;
    overflow-y: auto;
    max-height: calc(100vh - 180px);
}

.elemento {
    background: white;
    border-radius: 8px;
    margin-bottom: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    overflow: hidden;
    position: relative;
    transition: all 0.3s ease;
    border-left: 4px solid #4CAF50;
    height: 80px;
}

.elemento.dragging {
    opacity: 0.7;
    transform: scale(1.02);
    z-index: 1000;
}

.elemento-contenido {
    display: flex;
    align-items: center;
    padding: 10px 12px;
    height: 100%;
    transition: transform 0.3s ease;
}

.elemento-contenido.swipe-left {
    transform: translateX(-80px);
}

.elemento-icono {
    width: 45px;
    height: 45px;
    margin-right: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f8f9fa;
    border-radius: 6px;
    font-size: 20px;
    flex-shrink: 0;
}

.elemento-icono img {
    width: 35px;
    height: 35px;
    object-fit: cover;
    border-radius: 4px;
}

.elemento-inputs {
    flex: 1;
    display: flex;
    gap: 8px;
    align-items: center;
}

.input-grupo {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.input-label {
    font-size: 10px;
    color: #666;
    margin-bottom: 2px;
    font-weight: 500;
    text-align: center;
}

.input-campo {
    width: 100%;
    max-width: 60px;
    height: 32px;
    padding: 4px 6px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 12px;
    text-align: center;
    transition: border-color 0.3s ease;
}

.input-campo:focus {
    outline: none;
    border-color: #4CAF50;
    box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.drag-handle {
    width: 30px;
    height: 45px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #999;
    cursor: grab;
    font-size: 16px;
    margin-left: 8px;
    flex-shrink: 0;
    background: #f8f9fa;
    border-radius: 4px;
    transition: all 0.3s ease;
}

.drag-handle:hover {
    background: #e9ecef;
    color: #666;
}

.drag-handle:active {
    cursor: grabbing;
    background: #dee2e6;
}

.boton-eliminar {
    position: absolute;
    right: -80px;
    top: 0;
    bottom: 0;
    width: 80px;
    background: linear-gradient(135deg, #f44336, #d32f2f);
    color: white;
    border: none;
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.1);
}

.boton-eliminar:hover {
    background: linear-gradient(135deg, #d32f2f, #b71c1c);
}

.boton-eliminar:active {
    transform: scale(0.95);
}

.elemento.swipe-active .boton-eliminar {
    right: 0;
    box-shadow: -2px 0 8px rgba(0,0,0,0.2);
}

.botones-principales {
    display: flex;
    justify-content: space-around;
    padding: 20px 10px;
    background: white;
    border-top: 1px solid #eee;
    box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
}

.boton-accion {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    border: none;
    background: #4CAF50;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.boton-accion:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(76, 175, 80, 0.4);
}

.boton-accion:active {
    transform: translateY(0);
}

.boton-enviar {
    background: #FF9800;
    box-shadow: 0 4px 12px rgba(255, 152, 0, 0.3);
}

.boton-enviar:hover {
    box-shadow: 0 6px 16px rgba(255, 152, 0, 0.4);
}

.icono {
    font-size: 24px;
}

/* Modal */
.modal {
    display: none;
    position: fixed;
    z-index: 2000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.5);
}

.modal-content {
    background-color: white;
    margin: 20% auto;
    padding: 20px;
    border-radius: 8px;
    width: 80%;
    max-width: 300px;
    position: relative;
    animation: modalSlideIn 0.3s ease;
}

@keyframes modalSlideIn {
    from {
        transform: translateY(-50px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.close {
    position: absolute;
    right: 15px;
    top: 10px;
    font-size: 24px;
    cursor: pointer;
    color: #999;
}

.close:hover {
    color: #333;
}

/* Estados de carga */
.loading {
    opacity: 0.6;
    pointer-events: none;
}

.success {
    border-left-color: #4CAF50;
}

.error {
    border-left-color: #f44336;
}

/* Responsive */
@media (max-width: 400px) {
    .container {
        max-width: 100%;
    }

    .elemento {
        height: 75px;
    }

    .elemento-contenido {
        padding: 8px 10px;
    }

    .elemento-icono {
        width: 40px;
        height: 40px;
        margin-right: 10px;
    }

    .elemento-icono img {
        width: 30px;
        height: 30px;
    }

    .input-campo {
        max-width: 50px;
        height: 28px;
        font-size: 11px;
    }

    .input-label {
        font-size: 9px;
    }

    .drag-handle {
        width: 25px;
        height: 40px;
        font-size: 14px;
        margin-left: 6px;
    }

    .botones-principales {
        padding: 15px 5px;
    }

    .boton-accion {
        width: 50px;
        height: 50px;
    }
}"""

    # Crear archivo JavaScript
    js_content = """let elementoIdCounter = 0;
let draggedElement = null;
let swipeStartX = 0;
let currentSwipedElement = null;

// Agregar elemento a la lista
function agregarElemento(tipo, rutaImagen = null) {
    const lista = document.getElementById('listaElementos');
    const elementoId = 'elemento_' + (++elementoIdCounter);

    const elemento = document.createElement('div');
    elemento.className = 'elemento';
    elemento.id = elementoId;
    elemento.setAttribute('data-tipo', tipo);
    elemento.setAttribute('data-imagen', rutaImagen || '');

    let iconoContent = '';
    switch(tipo) {
        case 'reloj':
            iconoContent = '<span style="font-size: 24px;">🕐</span>';
            break;
        case 'fecha':
            iconoContent = '<span style="font-size: 24px;">📅</span>';
            break;
        default:
            if (rutaImagen) {
                iconoContent = `<img src="${rutaImagen}" alt="Imagen personalizada">`;
            } else {
                iconoContent = '<span style="font-size: 24px;">🖼️</span>';
            }
    }

    elemento.innerHTML = `
        <div class="elemento-contenido">
            <div class="elemento-icono">
                ${iconoContent}
            </div>
            <div class="elemento-inputs">
                <div class="input-grupo">
                    <label class="input-label">Segundos</label>
                    <input type="number" class="input-campo tiempo-input" value="1" min="1">
                </div>
                <div class="input-grupo">
                    <label class="input-label">Repeticiones</label>
                    <input type="number" class="input-campo repeticiones-input" value="1" min="1">
                </div>
            </div>
            <div class="drag-handle" onmousedown="iniciarDrag(event, '${elementoId}')" ontouchstart="iniciarDrag(event, '${elementoId}')">
                ⋮⋮
            </div>
        </div>
        <button class="boton-eliminar" onclick="eliminarElemento('${elementoId}')">
            ✕
        </button>
    `;

    // Agregar eventos de swipe
    elemento.addEventListener('touchstart', iniciarSwipe);
    elemento.addEventListener('touchmove', moverSwipe);
    elemento.addEventListener('touchend', terminarSwipe);

    lista.appendChild(elemento);
    mostrarMensaje('Elemento agregado', `Se agregó elemento de tipo: ${tipo}`);
}

// Seleccionar imagen
function seleccionarImagen() {
    document.getElementById('inputImagen').click();
}

// Procesar imagen seleccionada
function procesarImagen(input) {
    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            // Crear elemento con preview de la imagen
            agregarElemento('imagen', e.target.result);

            // Subir imagen al servidor
            subirImagen(file);
        };
        reader.readAsDataURL(file);
    }
}

// Subir imagen al servidor
function subirImagen(file) {
    const formData = new FormData();
    formData.append('imagen', file);

    fetch('/subir-imagen', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Imagen subida:', data.filename);
        } else {
            mostrarMensaje('Error', 'No se pudo subir la imagen: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarMensaje('Error', 'Error de conexión al subir imagen');
    });
}

// Eliminar elemento
function eliminarElemento(elementoId) {
    const elemento = document.getElementById(elementoId);
    if (elemento) {
        elemento.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            elemento.remove();
        }, 300);
    }
}

// Sistema de Drag & Drop
function iniciarDrag(event, elementoId) {
    event.preventDefault();
    draggedElement = document.getElementById(elementoId);
    draggedElement.classList.add('dragging');

    const moveHandler = (e) => moverDrag(e);
    const upHandler = () => terminarDrag(moveHandler, upHandler);

    document.addEventListener('mousemove', moveHandler);
    document.addEventListener('mouseup', upHandler);
    document.addEventListener('touchmove', moveHandler);
    document.addEventListener('touchend', upHandler);
}

function moverDrag(event) {
    if (!draggedElement) return;

    const touch = event.touches ? event.touches[0] : event;
    const y = touch.clientY;

    // Encontrar el elemento sobre el que estamos
    const elementos = Array.from(document.querySelectorAll('.elemento:not(.dragging)'));
    let targetElement = null;

    elementos.forEach(el => {
        const rect = el.getBoundingClientRect();
        if (y > rect.top && y < rect.bottom) {
            targetElement = el;
        }
    });

    if (targetElement) {
        const lista = document.getElementById('listaElementos');
        const rect = targetElement.getBoundingClientRect();
        const middle = rect.top + rect.height / 2;

        if (y < middle) {
            lista.insertBefore(draggedElement, targetElement);
        } else {
            lista.insertBefore(draggedElement, targetElement.nextSibling);
        }
    }
}

function terminarDrag(moveHandler, upHandler) {
    if (draggedElement) {
        draggedElement.classList.remove('dragging');
        draggedElement = null;
    }

    document.removeEventListener('mousemove', moveHandler);
    document.removeEventListener('mouseup', upHandler);
    document.removeEventListener('touchmove', moveHandler);
    document.removeEventListener('touchend', upHandler);
}

// Sistema de Swipe para mostrar botón eliminar
function iniciarSwipe(event) {
    swipeStartX = event.touches[0].clientX;
    currentSwipedElement = event.currentTarget;
}

function moverSwipe(event) {
    if (!currentSwipedElement) return;

    const currentX = event.touches[0].clientX;
    const diff = swipeStartX - currentX;

    if (diff > 5) { // Swipe hacia la izquierda (más sensible)
        const contenido = currentSwipedElement.querySelector('.elemento-contenido');
        const maxSwipe = 80;
        const swipeAmount = Math.min(diff, maxSwipe);

        contenido.style.transform = `translateX(-${swipeAmount}px)`;

        if (diff > 30) { // Umbral más bajo para activar
            currentSwipedElement.classList.add('swipe-active');
        } else {
            currentSwipedElement.classList.remove('swipe-active');
        }
    } else if (diff < -10) { // Swipe hacia la derecha para cerrar
        const contenido = currentSwipedElement.querySelector('.elemento-contenido');
        contenido.style.transform = 'translateX(0)';
        currentSwipedElement.classList.remove('swipe-active');
    }
}

function terminarSwipe(event) {
    if (!currentSwipedElement) return;

    const contenido = currentSwipedElement.querySelector('.elemento-contenido');
    const isActive = currentSwipedElement.classList.contains('swipe-active');

    if (isActive) {
        // Mantener el botón eliminar visible
        contenido.style.transform = 'translateX(-80px)';
        contenido.style.transition = 'transform 0.3s ease';

        // Agregar evento para cerrar al tocar fuera
        setTimeout(() => {
            const cerrarSwipe = (e) => {
                if (!currentSwipedElement.contains(e.target)) {
                    contenido.style.transform = 'translateX(0)';
                    currentSwipedElement.classList.remove('swipe-active');
                    document.removeEventListener('touchstart', cerrarSwipe);
                    document.removeEventListener('click', cerrarSwipe);
                }
            };
            document.addEventListener('touchstart', cerrarSwipe);
            document.addEventListener('click', cerrarSwipe);
        }, 100);
    } else {
        // Volver a la posición original
        contenido.style.transform = 'translateX(0)';
        contenido.style.transition = 'transform 0.3s ease';
    }

    // Limpiar la transición después de la animación
    setTimeout(() => {
        if (contenido) contenido.style.transition = '';
    }, 300);

    currentSwipedElement = null;
}

// Enviar configuración
function enviarConfiguracion() {
    const elementos = document.querySelectorAll('.elemento');
    const secuencia = [];

    elementos.forEach(elemento => {
        const tipo = elemento.getAttribute('data-tipo');
        const imagen = elemento.getAttribute('data-imagen');
        const tiempo = elemento.querySelector('.tiempo-input').value;
        const repeticiones = elemento.querySelector('.repeticiones-input').value;

        secuencia.push({
            tipo: tipo,
            imagen_nombre: imagen ? 'imagen_' + Date.now() : null,
            tiempo: tiempo || '1',
            repeticiones: repeticiones || '1'
        });
    });

    if (secuencia.length === 0) {
        mostrarMensaje('Aviso', 'Agrega al menos un elemento antes de enviar');
        return;
    }

    // Enviar configuración
    fetch('/configuracion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(secuencia)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarMensaje('Éxito', `Configuración enviada correctamente. ${data.elementos} elementos procesados.`);
        } else {
            mostrarMensaje('Error', 'Error al enviar configuración: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarMensaje('Error de conexión', 
            'No se pudo conectar con la Raspberry Pi.\\n\\n' +
            'Verifica que:\\n' +
            '• La Raspberry esté encendida\\n' +
            '• Estés en la misma red Wi-Fi\\n' +
            '• El servidor esté ejecutándose'
        );
    });
}

// Sistema de modales
function mostrarMensaje(titulo, mensaje) {
    document.getElementById('modalTitulo').textContent = titulo;
    document.getElementById('modalMensaje').textContent = mensaje;
    document.getElementById('modal').style.display = 'block';
}

function cerrarModal() {
    document.getElementById('modal').style.display = 'none';
}

// Cerrar modal al hacer clic fuera
window.onclick = function(event) {
    const modal = document.getElementById('modal');
    if (event.target === modal) {
        cerrarModal();
    }
}

// Animación de salida para elementos eliminados
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(-100%);
        }
    }
`;
document.head.appendChild(style);"""

    # Escribir archivos
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    os.makedirs('static/css', exist_ok=True)
    with open('static/css/style.css', 'w', encoding='utf-8') as f:
        f.write(css_content)

    os.makedirs('static/js', exist_ok=True)
    with open('static/js/app.js', 'w', encoding='utf-8') as f:
        f.write(js_content)

if __name__ == '__main__':
    # Crear archivos HTML y CSS
    crear_archivos_web()
    # Ejecutar en todas las interfaces para acceso por IP
    app.run(host='0.0.0.0', port=5000, debug=True)