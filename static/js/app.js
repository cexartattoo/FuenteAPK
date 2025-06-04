let elementoIdCounter = 0;
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
            'No se pudo conectar con la Raspberry Pi.\n\n' +
            'Verifica que:\n' +
            '• La Raspberry esté encendida\n' +
            '• Estés en la misma red Wi-Fi\n' +
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
document.head.appendChild(style);