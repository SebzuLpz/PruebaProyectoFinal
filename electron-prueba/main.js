const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');

// Definir rutas de archivos
const USERS_FILE = path.join(__dirname, 'data', 'users.json');
const INVENTORY_FILE = path.join(__dirname, 'data', 'inventory.json');

// Asegurar que el directorio data existe
if (!fs.existsSync(path.join(__dirname, 'data'))) {
    fs.mkdirSync(path.join(__dirname, 'data'));
}

// Función para leer datos
function readData(filePath) {
    try {
        if (fs.existsSync(filePath)) {
            return JSON.parse(fs.readFileSync(filePath, 'utf8'));
        }
        return {};
    } catch (error) {
        console.error(`Error reading file ${filePath}:`, error);
        return {};
    }
}

// Función para escribir datos
function writeData(filePath, data) {
    try {
        fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
    } catch (error) {
        console.error(`Error writing file ${filePath}:`, error);
    }
}

// Inicializar usuarios por defecto si no existen
const defaultUsers = {
    admin: {
        username: 'admin',
        passwordHash: crypto.createHash('sha256').update('admin123').digest('hex'),
        isAdmin: true
    },
    user: {
        username: 'user',
        passwordHash: crypto.createHash('sha256').update('user123').digest('hex'),
        isAdmin: false
    }
};

if (!fs.existsSync(USERS_FILE)) {
    writeData(USERS_FILE, defaultUsers);
}

if (!fs.existsSync(INVENTORY_FILE)) {
    writeData(INVENTORY_FILE, {});
}

function hashPassword(password) {
    return crypto.createHash('sha256').update(password).digest('hex');
}

function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 1000,
        height: 700,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    mainWindow.loadFile('index.html');
    mainWindow.removeMenu();
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// IPC handlers para operaciones de base de datos
ipcMain.handle('login', (event, { username, password }) => {
    const users = readData(USERS_FILE);
    const user = users[username];
    
    if (!user) {
        return { success: false, message: 'Usuario no encontrado' };
    }
    
    if (user.passwordHash === hashPassword(password)) {
        return { 
            success: true, 
            message: 'Inicio de sesión exitoso',
            isAdmin: user.isAdmin
        };
    }
    
    return { success: false, message: 'Contraseña incorrecta' };
});

ipcMain.handle('get-inventory', () => {
    return readData(INVENTORY_FILE);
});

ipcMain.handle('add-product', (event, product) => {
    const inventory = readData(INVENTORY_FILE);
    

    // Verificar si el usuario es admin antes de permitir la operación
    if (!isAdmin) {
        return { success: false, message: 'No tiene permisos para realizar esta operación' };
    }

    const productId = crypto
        .createHash('md5')
        .update(`${product.colegio}${product.tipoUniforme}${product.prenda}${product.talla}`)
        .digest('hex');
        

    if (inventory[productId]) {
        return { success: false, message: 'El producto ya existe' };
    }
    
    inventory[productId] = { ...product, id: productId };
    writeData(INVENTORY_FILE, inventory);
    return { success: true, message: 'Producto agregado exitosamente' };
});

ipcMain.handle('update-stock', (event, { productId, cantidad, tipo }) => {
    const inventory = readData(INVENTORY_FILE);
    const product = inventory[productId];
    
    if (!product) {
        return { success: false, message: 'Producto no encontrado' };
    }
    
    if (tipo === 'ENTRADA') {
        product.cantidad += parseInt(cantidad);
    } else if (tipo === 'SALIDA') {
        if (product.cantidad < cantidad) {
            return { success: false, message: 'Stock insuficiente' };
        }
        product.cantidad -= parseInt(cantidad);
    }
    
    inventory[productId] = product;
    writeData(INVENTORY_FILE, inventory);
    return { 
        success: true, 
        message: `Stock actualizado. Nuevo stock: ${product.cantidad}` 
    };
});

ipcMain.handle('delete-product', (event, productId) => {
    const inventory = readData(INVENTORY_FILE);
    
    if (!inventory[productId]) {
        return { success: false };
    }
    
    delete inventory[productId];
    writeData(INVENTORY_FILE, inventory);
    
    return { success: true };
});
