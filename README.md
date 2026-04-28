## ⚙️ Configuración del entorno y ejecución del modelo

---

### 🧠 Requisitos previos

- Python 3.8 o superior  
- Terminal (CMD, PowerShell, Bash, etc.)

---

## 🖥️ Crear y activar entorno virtual

### 🍎 macOS / 🐧 Linux

```bash
# Ir a la carpeta del proyecto
cd ruta/de/tu/proyecto

# Crear entorno virtual
python3 -m venv venv

# Activar entorno
source venv/bin/activate
---

### 🪟 Windows
```cmd
# Ir a la carpeta del proyecto
cd ruta\de\tu\proyecto

# Crear entorno virtual
python -m venv venv

# Activar entorno
venv\Scripts\activate
###🪟 Windows
```PowerShell
# Ir a la carpeta del proyecto
cd ruta\de\tu\proyecto

# Crear entorno virtual
python -m venv venv
---
# Activar entorno
venv\Scripts\Activate.ps1
📦 Instalar dependencias
pip install -r requirements.txt
Si ocurre un error con pip:
python -m pip install -r requirements.txt