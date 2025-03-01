//main.js
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const mysql = require('mysql');
const crypto = require('crypto');

// Configuración de la conexión a la base de datos
const dbConfig = {
    host: 'localhost',
    user: 'root',
    password: 'root',
    database: 'ritmichell_db'
};

// Función para conectar a la base de datos
function createConnection() {
    const connection = mysql.createConnection(dbConfig);
    connection.connect(err => {
        if (err) {
            console.error('Error connecting to database:', err.code);
            console.error('Fatal:', err.fatal);
        }
    });
    return connection;
}

function hashPassword(password) {
    return crypto.createHash('sha256').update(password).digest('hex');
}

function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 1000,
        height: 700,
        icon: __dirname + '/images/Ritmichell.ico',
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

// IPC handlers para operaciones con la base de datos
ipcMain.handle('login', async (event, { username, password }) => {
    const connection = createConnection();
    
    try {
        const [rows] = await new Promise((resolve, reject) => {
            connection.query(
                'SELECT * FROM users WHERE username = ?', 
                [username],
                (error, results) => {
                    if (error) reject(error);
                    else resolve([results]);
                }
            );
        });

        if (rows.length === 0) {
            return { success: false, message: 'Usuario no encontrado' };
        }
        
        const user = rows[0];
        const hashedPassword = hashPassword(password);
        
        if (user.password_hash === hashedPassword) {
            return { 
                success: true, 
                message: 'Inicio de sesión exitoso',
                isAdmin: user.is_admin === 1
            };
        }
        
        return { success: false, message: 'Contraseña incorrecta' };
    } catch (error) {
        console.error('Error en login:', error);
        return { success: false, message: 'Error en la base de datos' };
    } finally {
        connection.end();
    }
});

ipcMain.handle('get-inventory', async () => {
    const connection = createConnection();
    
    try {
        const [rows] = await new Promise((resolve, reject) => {
            connection.query(
                'SELECT * FROM inventory',
                (error, results) => {
                    if (error) reject(error);
                    else resolve([results]);
                }
            );
        });
        
        // Convertir array de resultados a objeto con id como clave (igual al formato anterior)
        const inventory = {};
        rows.forEach(product => {
            inventory[product.id] = {
                id: product.id,
                colegio: product.colegio,
                tipoUniforme: product.tipo_uniforme,
                prenda: product.prenda,
                talla: product.talla,
                cantidad: product.cantidad
            };
        });
        
        return inventory;
    } catch (error) {
        console.error('Error getting inventory:', error);
        return {};
    } finally {
        connection.end();
    }
});

ipcMain.handle('add-product', async (event, product) => {
    const connection = createConnection();
    
    try {
        // Generar ID del producto
        const productId = crypto
            .createHash('md5')
            .update(`${product.colegio}${product.tipoUniforme}${product.prenda}${product.talla}`)
            .digest('hex');
        
        // Verificar si el producto ya existe
        const [existingProducts] = await new Promise((resolve, reject) => {
            connection.query(
                'SELECT * FROM inventory WHERE id = ?',
                [productId],
                (error, results) => {
                    if (error) reject(error);
                    else resolve([results]);
                }
            );
        });
        
        if (existingProducts.length > 0) {
            return { success: false, message: 'El producto ya existe' };
        }
        
        // Insertar nuevo producto
        await new Promise((resolve, reject) => {
            connection.query(
                'INSERT INTO inventory (id, colegio, tipo_uniforme, prenda, talla, cantidad) VALUES (?, ?, ?, ?, ?, ?)',
                [productId, product.colegio, product.tipoUniforme, product.prenda, product.talla, product.cantidad],
                (error) => {
                    if (error) reject(error);
                    else resolve();
                }
            );
        });
        
        return { success: true, message: 'Producto agregado exitosamente' };
    } catch (error) {
        console.error('Error adding product:', error);
        return { success: false, message: 'Error en la base de datos' };
    } finally {
        connection.end();
    }
});

ipcMain.handle('update-stock', async (event, { productId, cantidad, tipo }) => {
    const connection = createConnection();
    
    try {
        // Obtener producto actual
        const [products] = await new Promise((resolve, reject) => {
            connection.query(
                'SELECT * FROM inventory WHERE id = ?',
                [productId],
                (error, results) => {
                    if (error) reject(error);
                    else resolve([results]);
                }
            );
        });
        
        if (products.length === 0) {
            return { success: false, message: 'Producto no encontrado' };
        }
        
        const product = products[0];
        let newCantidad = product.cantidad;
        
        if (tipo === 'ENTRADA') {
            newCantidad += parseInt(cantidad);
        } else if (tipo === 'SALIDA') {
            if (product.cantidad < cantidad) {
                return { success: false, message: 'Stock insuficiente' };
            }
            newCantidad -= parseInt(cantidad);
        }
        
        // Actualizar stock
        await new Promise((resolve, reject) => {
            connection.query(
                'UPDATE inventory SET cantidad = ? WHERE id = ?',
                [newCantidad, productId],
                (error) => {
                    if (error) reject(error);
                    else resolve();
                }
            );
        });
        
        return { 
            success: true, 
            message: `Stock actualizado. Nuevo stock: ${newCantidad}` 
        };
    } catch (error) {
        console.error('Error updating stock:', error);
        return { success: false, message: 'Error en la base de datos' };
    } finally {
        connection.end();
    }
});

ipcMain.handle('delete-product', async (event, productId) => {
    const connection = createConnection();
    
    try {
        await new Promise((resolve, reject) => {
            connection.query(
                'DELETE FROM inventory WHERE id = ?',
                [productId],
                (error, results) => {
                    if (error) reject(error);
                    else resolve(results);
                }
            );
        });
        
        return { success: true };
    } catch (error) {
        console.error('Error deleting product:', error);
        return { success: false };
    } finally {
        connection.end();
    }
});


// Add these handlers to the bottom of your main.js file

// Handler to get all costs
ipcMain.handle('get-costs', async () => {
    const connection = createConnection();
    
    try {
        const [rows] = await new Promise((resolve, reject) => {
            connection.query(
                'SELECT * FROM costs ORDER BY month DESC',
                (error, results) => {
                    if (error) reject(error);
                    else resolve([results]);
                }
            );
        });
        
        return rows;
    } catch (error) {
        console.error('Error getting costs:', error);
        return [];
    } finally {
        connection.end();
    }
});

// Handler to add a new cost
ipcMain.handle('add-cost', async (event, costData) => {
    const connection = createConnection();
    
    try {
        await new Promise((resolve, reject) => {
            connection.query(
                'INSERT INTO costs (colegio, tipo_uniforme, month, amount, description) VALUES (?, ?, ?, ?, ?)',
                [
                    costData.colegio, 
                    costData.tipoUniforme, 
                    costData.month, 
                    costData.amount, 
                    costData.description
                ],
                (error) => {
                    if (error) reject(error);
                    else resolve();
                }
            );
        });
        
        return { success: true, message: 'Costo registrado exitosamente' };
    } catch (error) {
        console.error('Error adding cost:', error);
        return { success: false, message: 'Error en la base de datos' };
    } finally {
        connection.end();
    }
});