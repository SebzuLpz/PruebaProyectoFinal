//renderer.js


const { ipcRenderer } = require('electron');

// DOM Elements
const loginForm = document.querySelector('.login-form');
const loginContainer = document.getElementById('login-container');
const mainContainer = document.getElementById('main-container');
const loginBtn = document.getElementById('login-btn');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const addProductBtn = document.getElementById('add-product-btn');
const updateStockBtn = document.getElementById('update-stock-btn');
const logoutBtn = document.getElementById('logout-btn');

// Configuración inicial
const prendas = {
    "Uniforme Diario": ["Camisa", "Pantalón", "Falda", "Suéter"],
    "Uniforme Deportivo": ["Camiseta", "Pantaloneta", "Sudadera", "Chaqueta"]
};
let isLoggingIn = false;

let isAdmin = false;

// Función para resetear el formulario de login
//function resetLoginForm() {
//    usernameInput.value = '';
//    passwordInput.value = '';
//    usernameInput.disabled = false;
//    passwordInput.disabled = false;
//    loginBtn.disabled = false;

    //document.getElementById('new-colegio')?.value = '';
    //document.getElementById('new-cantidad')?.value = '';
    //document.getElementById('update-cantidad')?.value = '';

//}

// Función para resetear el formulario de login
//function resetLoginForm() {
//    //loginForm.reset(); // Usar reset() del formulario
//    usernameInput.disabled = false;
//    passwordInput.disabled = false;
//    loginBtn.disabled = false;
//    
//    // Limpiar otros formularios
//    document.getElementById('new-colegio')?.value = '';
//    document.getElementById('new-cantidad')?.value = '';
//    document.getElementById('update-cantidad')?.value = '';
//}


//function resetLoginForm() {
//    // Limpiar valores
//    usernameInput.value = '';
//    passwordInput.value = '';
//    
//    // Habilitar inputs
//    usernameInput.disabled = false;
//    passwordInput.disabled = false;
//    loginBtn.disabled = false;
//    
//    // Remover cualquier clase que pueda estar causando problemas
//    usernameInput.classList.remove('disabled');
//    passwordInput.classList.remove('disabled');
//}

// Función resetLoginForm



// Función para mostrar errores
//function showError(message) {
//    
//    usernameInput.disabled = false;
//    passwordInput.disabled = false;
//    loginBtn.disabled = false;
//    alert(message);
//}


function showError(message) {
    const errorDiv = document.getElementById('error-message');
    const hidden1 = document.createElement('div');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
    
    // Habilitar los inputs
    usernameInput.disabled = false;
    passwordInput.disabled = false;
    loginBtn.disabled = false;
    
    // Ocultar el mensaje de error después de 3 segundos
    setTimeout(() => {
        errorDiv.classList.add('hidden');
        setTimeout(() => {
            errorDiv.removeChild(hidden1);
        }, 400); // tiempo de la animación
    },3000);


}

// Login functionality
loginBtn.addEventListener('click', async (e) => {
    e.preventDefault();

    //if (isLoggingIn) return; // Prevenir múltiples intentos

    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    loginForm.reset();
    usernameInput.value = '';
    passwordInput.value = '';
    
    

    if (!username || !password) {
        showError('Por favor complete todos los campos');
        return;
    }

    try {
        isLoggingIn = true;
        loginBtn.disabled = false; // Solo deshabilitamos el botón

        const response = await ipcRenderer.invoke('login', { username, password });
        
        if (response.success) {
            isAdmin = response.isAdmin;
            loginContainer.classList.add('hidden');
            mainContainer.classList.remove('hidden');
            
            addProductBtn.classList.add('hidden'); // Primero ocultar para todos
            if (isAdmin) {
                addProductBtn.classList.remove('hidden'); // Mostrar solo si es admin
            }

            
            await loadInventory();
            await updateColegiosList();
            
            // Limpiar los campos sin deshabilitarlos
            usernameInput.value = '';
            passwordInput.value = '';
        } else {
            showError(response.message);
        }
    } catch (error) {
        console.error('Error during login:', error);
        showError('Error al iniciar sesión. Por favor intente nuevamente.');
    } finally {
        isLoggingIn = true;
        loginBtn.disabled = false;
    }
});


// Permitir usar Enter para iniciar sesión
passwordInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        loginBtn.click();
    }
});

function resetLoginForm() {
    loginForm.reset();  // Resetear el formulario completo
    document.querySelectorAll('input, select, button').forEach(element => {
        element.disabled = false;  // Asegurar que todos los elementos estén habilitados
    });
    isLoggingIn = false;
}


// Resetear modales
function resetModal(modalId) {
    const modal = document.getElementById(modalId);
    const inputs = modal.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.disabled = false;
        if (input.type === 'radio') {
            input.checked = input.defaultChecked;
        } else {
            input.value = '';
        }
    });
}


// Logout functionality
logoutBtn.addEventListener('click', () => {
    mainContainer.classList.add('hidden');
    loginContainer.classList.remove('hidden');
    
    // Ocultar el botón de agregar producto
    addProductBtn.classList.add('hidden');

    // Resetear todos los formularios
    document.querySelectorAll('form').forEach(form => form.reset());
    
    // Resetear y habilitar todos los inputs y selects
    document.querySelectorAll('input, select').forEach(element => {
        element.disabled = false;
        if (element.type !== 'radio') {
            element.value = '';
        }
    });
    
    // Resetear modales
    resetModal('add-product-modal');
    resetModal('update-stock-modal');
    
    isAdmin = false;
    isLoggingIn = false;
});

// Cargar inventario
async function loadInventory() {
    try {
        const inventory = await ipcRenderer.invoke('get-inventory');
        updateProductsTable(Object.values(inventory));
    } catch (error) {
        console.error('Error loading inventory:', error);
        alert('Error al cargar el inventario');
    }
}

// Actualizar tabla de productos
//function updateProductsTable(products) {
//    const tbody = document.getElementById('products-body');
//    tbody.innerHTML = '';
//    products.forEach(product => {
//        const row = document.createElement('tr');
//        row.innerHTML = `
//            <td>${product.colegio}</td>
//            <td>${product.tipoUniforme}</td>
//            <td>${product.prenda}</td>
//            <td>${product.talla}</td>
//            <td>${product.cantidad}</td>
//        `;
//        tbody.appendChild(row);
//    });
//}


function updateProductsTable(products) {
    const tbody = document.getElementById('products-body');
    tbody.innerHTML = '';

    products.forEach(product => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${product.colegio}</td>
            <td>${product.tipoUniforme}</td>
            <td>${product.prenda}</td>
            <td>${product.talla}</td>
            <td>${product.cantidad}${
                isAdmin ? 
                `<button class="delete-btn" data-id="${product.id}" 
                    data-colegio="${product.colegio}"
                    data-tipo="${product.tipoUniforme}"
                    data-prenda="${product.prenda}"
                    data-talla="${product.talla}">
                    Eliminar
                    </button>` : 
                ''
            }</td>
        `;
        tbody.appendChild(row);
    });

    // Añadir event listeners para los botones de eliminar
    if (isAdmin) {
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', showDeleteConfirmation);
        });
    }
}




// Actualizar lista de colegios
async function updateColegiosList() {
    try {
        const inventory = await ipcRenderer.invoke('get-inventory');
        const colegios = new Set(Object.values(inventory).map(p => p.colegio));
        
        const colegioSelect = document.getElementById('filter-colegio');
        const updateColegioSelect = document.getElementById('update-colegio');
        
        [colegioSelect, updateColegioSelect].forEach(select => {
            if (select) {
                const currentValue = select.value;
                select.innerHTML = '<option value="">Seleccionar Colegio</option>';
                colegios.forEach(colegio => {
                    const option = document.createElement('option');
                    option.value = colegio;
                    option.textContent = colegio;
                    select.appendChild(option);
                });
                select.value = currentValue;
            }
        });
    } catch (error) {
        console.error('Error updating colegios list:', error);
    }
}




// Event listeners para modales

document.querySelectorAll('.modal-close').forEach(button => {
    button.addEventListener('click', () => {
        const modal = button.closest('.modal');
        modal.classList.add('hidden');
        resetModal(modal.id);
    });
});

//document.querySelectorAll('.modal-close').forEach(button => {
//    button.addEventListener('click', () => {
//        // Ocultar todos los modales
//        document.querySelectorAll('.modal').forEach(modal => {
//            modal.classList.add('hidden');
//            
//            // Rehabilitar y limpiar todos los inputs dentro del modal
//            modal.querySelectorAll('input').forEach(input => {
//                input.value = '';
//                input.disabled = false;
//                input.classList.remove('disabled');
//            });
//            
//            // Rehabilitar y limpiar todos los selects dentro del modal
//            modal.querySelectorAll('select').forEach(select => {
//                select.value = '';
//                select.disabled = false;
//                select.classList.remove('disabled');
//            });
//        });
//    });
//});


// Mostrar modal de agregar producto
addProductBtn.addEventListener('click', () => {
    document.getElementById('add-product-modal').classList.remove('hidden');
    updatePrendasList('new-tipo', 'new-prenda');
});

// Mostrar modal de actualizar stock
updateStockBtn.addEventListener('click', () => {
    document.getElementById('update-stock-modal').classList.remove('hidden');
    updatePrendasList('update-tipo', 'update-prenda');
    updateTallasSelect('update-talla'); // Actualizar lista de tallas
});

// Actualizar lista de prendas según el tipo de uniforme
function updatePrendasList(tipoSelectId, prendaSelectId) {
    const tipoSelect = document.getElementById(tipoSelectId);
    const prendaSelect = document.getElementById(prendaSelectId);
    const selectedTipo = tipoSelect.value;

    prendaSelect.innerHTML = '<option value="">Seleccionar Prenda</option>';
    prendas[selectedTipo].forEach(prenda => {
        const option = document.createElement('option');
        option.value = prenda;
        option.textContent = prenda;
        prendaSelect.appendChild(option);
    });
}

// Inicializar lista de prendas
updatePrendasList('new-tipo', 'new-prenda');
updatePrendasList('update-tipo', 'update-prenda');



document.getElementById('new-tipo').addEventListener('change', () => {
    updatePrendasList('new-tipo', 'new-prenda');
    updateTallasSelect('new-talla');
});

document.getElementById('update-tipo').addEventListener('change', () => {
    updatePrendasList('update-tipo', 'update-prenda');
    updateTallasSelect('update-talla');
});

// Al cargar la página, inicializar las tallas
document.addEventListener('DOMContentLoaded', () => {
    updateTallasSelect('filter-talla');
    updateTallasSelect('new-talla');
    updateTallasSelect('update-talla');
});

// Función para actualizar las tallas disponibles
function updateTallasSelect(selectId) {
    const tallas = ["4", "6", "8", "10", "12", "14", "16", "S", "M", "L", "XL"];
    const select = document.getElementById(selectId);
    select.innerHTML = '<option value="">Seleccionar Talla</option>';
    tallas.forEach(talla => {
        const option = document.createElement('option');
        option.value = talla;
        option.textContent = talla;
        select.appendChild(option);
    });
}

// Event listeners para cambios en tipo de uniforme
document.getElementById('new-tipo').addEventListener('change', () => {
    updatePrendasList('new-tipo', 'new-prenda');
});

document.getElementById('update-tipo').addEventListener('change', () => {
    updatePrendasList('update-tipo', 'update-prenda');
});

// Guardar nuevo producto
document.getElementById('save-product-btn').addEventListener('click', async () => {
    const product = {
        colegio: document.getElementById('new-colegio').value,
        tipoUniforme: document.getElementById('new-tipo').value,
        prenda: document.getElementById('new-prenda').value,
        talla: document.getElementById('new-talla').value,
        cantidad: parseInt(document.getElementById('new-cantidad').value)
    };

    try {
        const response = await ipcRenderer.invoke('add-product', product);
        if (response.success) {
            showNotification(response.message);
            document.getElementById('add-product-modal').classList.add('hidden');
            loadInventory();
            updateColegiosList();
        } else {
            showNotification(response.message);
        }
    } catch (error) {
        console.error('Error adding product:', error);
        showNotification('Error al agregar producto');
    }
});

// Actualizar stock
document.getElementById('save-update-btn').addEventListener('click', async () => {

    const productId = require('crypto')
        .createHash('md5')
        .update(
            `${document.getElementById('update-colegio').value}` +
            `${document.getElementById('update-tipo').value}` +
            `${document.getElementById('update-prenda').value}` +
            `${document.getElementById('update-talla').value}`
        )
        .digest('hex');

    const updateData = {
        productId,
        cantidad: document.getElementById('update-cantidad').value,
        tipo: document.querySelector('input[name="tipo-mov"]:checked').value
    };

    try {
        const response = await ipcRenderer.invoke('update-stock', updateData);
        if (response.success) {
            showNotification(response.message);
            document.getElementById('update-stock-modal').classList.add('hidden');
            loadInventory();
        } else {
            showNotification(response.message);
        }
    } catch (error) {
        console.error('Error updating stock:', error);
        showNotification('Error al actualizar stock');
    }
});

// Event listeners para filtros
['filter-colegio', 'filter-tipo', 'filter-prenda', 'filter-talla'].forEach(filterId => {
    document.getElementById(filterId).addEventListener('change', async () => {
        try {
            const inventory = await ipcRenderer.invoke('get-inventory');
            let filteredProducts = Object.values(inventory);

            const filters = {
                colegio: document.getElementById('filter-colegio').value,
                tipoUniforme: document.getElementById('filter-tipo').value,
                prenda: document.getElementById('filter-prenda').value,
                talla: document.getElementById('filter-talla').value
            };

            Object.keys(filters).forEach(key => {
                if (filters[key]) {
                    filteredProducts = filteredProducts.filter(product => 
                        product[key] === filters[key]
                    );
                }
            });

            updateProductsTable(filteredProducts);
        } catch (error) {
            console.error('Error filtering products:', error);
        }
    });
});


function showNotification(message, duration = 3000) {
    const container = document.getElementById('notification-container');
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    
    container.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('hiding');
        setTimeout(() => {
            container.removeChild(notification);
        }, 300); // tiempo de la animación
    }, duration);
}





function showDeleteConfirmation(event) {
    const btn = event.currentTarget;
    const modal = document.getElementById('delete-confirm-modal');
    
    // Guardar el ID del producto en el botón de confirmar
    document.getElementById('confirm-delete-btn').dataset.productId = btn.dataset.id;
    
    // Mostrar detalles del producto
    document.getElementById('delete-colegio').textContent = btn.dataset.colegio;
    document.getElementById('delete-tipo').textContent = btn.dataset.tipo;
    document.getElementById('delete-prenda').textContent = btn.dataset.prenda;
    document.getElementById('delete-talla').textContent = btn.dataset.talla;
    
    modal.classList.remove('hidden');
}

document.getElementById('confirm-delete-btn').addEventListener('click', async function() {
    const productId = this.dataset.productId;
    
    try {
        const response = await ipcRenderer.invoke('delete-product', productId);
        if (response.success) {
            document.getElementById('delete-confirm-modal').classList.add('hidden');
            showNotification('Producto eliminado exitosamente'); // Usando tu función de notificación
            await loadInventory();
            await updateColegiosList();
        } else {
            showNotification('Error: No se pudo eliminar el producto'); // Para errores
        }
    } catch (error) {
        console.error('Error deleting product:', error);
        showNotification('Error al eliminar el producto'); // Para excepciones
    }
});