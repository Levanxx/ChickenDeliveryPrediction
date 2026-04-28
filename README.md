# ⚙️ Configuración del Entorno y Ejecución del Modelo

---

## 🧠 Requisitos previos

- 🐍 Python 3.8 o superior  
- 💻 Terminal (CMD, PowerShell, Bash, etc.)

---

## 🖥️ Configuración completa

```bash
##############################
# 🍎 macOS / 🐧 Linux
##############################

# Ir a la carpeta del proyecto
cd ruta/de/tu/proyecto

# Crear entorno virtual
python3 -m venv venv

# Activar entorno
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Si falla pip
python3 -m pip install -r requirements.txt


##############################
# 🪟 Windows (CMD)
##############################

# Ir a la carpeta del proyecto
cd ruta\de\tu\proyecto

# Crear entorno virtual
python -m venv venv

# Activar entorno
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Si falla pip
python -m pip install -r requirements.txt


##############################
# 🪟 Windows (PowerShell)
##############################

# Ir a la carpeta del proyecto
cd ruta\de\tu\proyecto

# Crear entorno virtual
python -m venv venv

# Activar entorno
venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r ml/requirements.txt

# Si falla pip
python -m pip install -r ml/requirements.txt


##############################
# 🚀 Extra
##############################

# Desactivar entorno virtual
deactivate
```


### Levantar API con FastAPI

uvicorn ml.api_model:app --reload --port 8000

### Abrir en navegador:
http://localhost:8000/docs
