# 🗓️ Sistema de Horarios — CTP Heredia

Sistema web para la **gestión y generación automática de horarios académicos** del Colegio Técnico Profesional de Heredia. Genera horarios semanales respetando la estructura de bloques del CTP, las restricciones de especialidades técnicas y los días permitidos por materia, usando programación por restricciones (OR-Tools CP-SAT).

> Proyecto desarrollado como Trabajo Comunal Universitario (TCU).

---

## 📋 Índice

- [Características](#-características)
- [Stack tecnológico](#-stack-tecnológico)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Instalación local](#-instalación-local)
- [Variables de entorno](#-variables-de-entorno)
- [Despliegue](#-despliegue)
- [Estructura de horarios del CTP](#-estructura-de-horarios-del-ctp)
- [API — Endpoints principales](#-api--endpoints-principales)

---

## ✨ Características

- **Generación automática de horarios** mediante el solver CP-SAT de Google OR-Tools
- Respeta bloques de 3 lecciones (A/B/C/D) y horarios split para grupos técnicos
- Manejo de pistas paralelas: grupos con dos especialidades técnicas simultáneas
- **Edición manual** de sesiones con verificación de conflictos en tiempo real
- Exportación del horario a **PDF** y **Excel**
- Autenticación con JWT y recuperación de contraseña por e-mail (OTP)
- CRUD completo de especialidades, materias y grupos
- Interfaz responsive con Tailwind CSS

---

## 🛠️ Stack tecnológico

### Backend
| Tecnología | Uso |
|---|---|
| **Python 3.12** | Lenguaje principal |
| **FastAPI 0.111** | Framework REST |
| **SQLAlchemy 2.0** | ORM |
| **PostgreSQL** | Base de datos |
| **Alembic 1.13** | Migraciones |
| **OR-Tools 9.15** | Solver CP-SAT para la generación de horarios |
| **ReportLab 4.2** | Generación de PDF en el servidor |
| **python-jose** | Tokens JWT |
| **Passlib + bcrypt** | Hashing de contraseñas |

### Frontend
| Tecnología | Uso |
|---|---|
| **React 19** | Framework UI |
| **Vite 8** | Bundler |
| **Tailwind CSS 3** | Estilos |
| **TanStack Query 5** | Fetching y caché de datos |
| **Axios** | Cliente HTTP |
| **jsPDF + autotable** | Exportación a PDF en el cliente |
| **SheetJS (xlsx)** | Exportación a Excel |
| **React Router 7** | Enrutamiento |

---

## 📁 Estructura del proyecto

```
sistema-horarios/
├── backend/
│   ├── app/
│   │   ├── algorithm/
│   │   │   └── generador.py      # Motor de generación (CP-SAT)
│   │   ├── models/               # Modelos SQLAlchemy
│   │   │   ├── grupo.py
│   │   │   ├── materia.py
│   │   │   ├── horario.py
│   │   │   ├── especialidad.py
│   │   │   └── usuario.py
│   │   ├── routers/              # Endpoints FastAPI
│   │   │   ├── auth.py
│   │   │   ├── especialidades.py
│   │   │   ├── materias.py
│   │   │   ├── grupos.py
│   │   │   └── horarios.py
│   │   ├── services/             # Lógica de negocio
│   │   ├── schemas/              # Modelos Pydantic
│   │   ├── main.py               # Punto de entrada FastAPI
│   │   ├── database.py           # Configuración DB
│   │   ├── auth.py               # JWT helpers
│   │   └── config.py             # Variables de entorno
│   ├── requirements.txt
│   └── .python-version
│
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── Horarios.jsx      # Visualización y generación de horarios
    │   │   ├── Grupos.jsx
    │   │   ├── Materias.jsx
    │   │   ├── Especialidades.jsx
    │   │   ├── Dashboard.jsx
    │   │   └── Login.jsx
    │   ├── components/           # Componentes reutilizables
    │   ├── api/axios.js          # Instancia Axios configurada
    │   ├── context/AuthContext.jsx
    │   └── utils/exportHorario.js
    ├── package.json
    └── vercel.json
```

---

## 🚀 Instalación local

### Requisitos previos

- Python 3.12
- Node.js 20+
- PostgreSQL 15+

### Backend

```bash
# 1. Clonar el repositorio
git clone https://github.com/<tu-usuario>/sistema-horarios.git
cd sistema-horarios/backend

# 2. Crear y activar entorno virtual
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores (ver sección siguiente)

# 5. Ejecutar el servidor
uvicorn app.main:app --reload --port 8000
```

La API estará disponible en `http://localhost:8000`.  
Documentación interactiva: `http://localhost:8000/docs`

### Frontend

```bash
cd ../frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

La app estará en `http://localhost:5173`.

---

## 🔐 Variables de entorno

Crea el archivo `backend/.env` con las siguientes variables:

```env
# Base de datos PostgreSQL
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/horarios_db

# Seguridad JWT
SECRET_KEY=tu_clave_secreta_muy_larga
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# CORS — URLs del frontend separadas por coma
ALLOWED_ORIGINS=http://localhost:5173

# Correo para recuperación de contraseña (opcional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_correo@gmail.com
SMTP_PASSWORD=tu_app_password
SMTP_FROM=tu_correo@gmail.com
```

**Usuario admin por defecto** (se crea automáticamente al iniciar):
- Email: `admin@ctp.ed.cr`
- Contraseña: `Admin1234`

> ⚠️ Cambia la contraseña del admin inmediatamente en producción.

---

## ☁️ Despliegue

| Servicio | Plataforma |
|---|---|
| **Backend** | [Render](https://render.com) — Web Service con Python 3.12 |
| **Frontend** | [Vercel](https://vercel.com) — con `vercel.json` para SPA routing |
| **Base de datos** | [Render PostgreSQL](https://render.com/docs/databases) |

### Render (Backend)

1. Crear un **Web Service** apuntando a la carpeta `backend/`
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Agregar las variables de entorno en el dashboard de Render

### Vercel (Frontend)

1. Importar el repositorio en Vercel
2. Configurar el **Root Directory** como `frontend`
3. Build command: `npm run build` | Output: `dist`
4. Agregar la variable `VITE_API_URL` apuntando al backend de Render

---

## 📅 Estructura de horarios del CTP

El horario semanal se organiza en **12 lecciones por día**, divididas en 4 bloques:

| Bloque | Lecciones | Horario |
|--------|-----------|---------|
| **A** | 1 – 2 – 3 | 7:00 – 9:00 |
| Recreo | — | 9:00 – 9:20 |
| **B** | 4 – 5 – 6 | 9:20 – 11:20 |
| Almuerzo | — | 11:20 – 12:00 |
| **C** | 7 – 8 – 9 | 12:00 – 2:00 |
| Recreo | — | 2:00 – 2:20 |
| **D** | 10 – 11 – 12 | 2:20 – 4:20 |

### Tipos de horario por grupo

- **`general`** (grupos 5–10 de cada nivel): sin restricción de días.
- **`split_10`** (10.° técnico): materias técnicas en Lun, Mar y Mié AM; académicas el resto.
- **`split_11`** / **`split_12`**: materias técnicas solo en Lun y Mar.

### Algoritmo de generación

El motor usa el solver **CP-SAT** de Google OR-Tools:

1. **Carga de datos** — grupos, materias, especialidades y días permitidos.
2. **Creación de variables** — una variable booleana por posible sesión `(grupo, materia, día, lección_inicio)`.
3. **Restricciones**:
   - R1: máximo 1 materia por lección dentro de cada pista (académica o técnica).
   - R2: conteo exacto de sesiones semanales por materia.
   - R3: grupos "gemelos" (misma especialidad) no comparten slots de especialidad.
4. **Objetivo suave** — minimiza la dispersión de sesiones pequeñas para concentrarlas en menos días.
5. **Guardado** — las sesiones encontradas se persisten en la base de datos (reemplaza el horario automático anterior, conserva ediciones manuales).

---

## 🔌 API — Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/auth/login` | Autenticación, retorna JWT |
| `POST` | `/auth/recuperar-contrasena` | Solicitar OTP por correo |
| `GET` | `/especialidades/` | Listar especialidades |
| `GET` | `/materias/` | Listar materias |
| `GET` | `/grupos/` | Listar grupos |
| `GET` | `/horarios/grupo/{id}` | Horario de un grupo |
| `POST` | `/horarios/generar` | **Lanzar generación automática** |
| `PATCH` | `/horarios/leccion/{id}` | Editar una sesión manualmente |

Documentación completa disponible en `/docs` (Swagger UI) al correr el servidor.

---

## 📄 Licencia

Este proyecto es de carácter académico — TCU universitario. Todos los derechos reservados.
