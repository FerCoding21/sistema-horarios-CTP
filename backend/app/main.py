from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, SessionLocal
import app.models
from app.routers import especialidades, materias, grupos, auth, horarios
from app.auth    import hashear_password
from app.models.usuario import Usuario
from app.config  import settings

app = FastAPI(
    title="Sistema de Horarios CTP Heredia",
    description="API para gestión y generación automática de horarios académicos",
    version="2.0.0"
)

# ALLOWED_ORIGINS acepta varias URLs separadas por coma
_origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(especialidades.router)
app.include_router(materias.router)
app.include_router(grupos.router)
app.include_router(horarios.router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    print("✅ Conexión a base de datos exitosa")

    db = SessionLocal()
    try:
        admin = db.query(Usuario).filter(Usuario.rol == "admin").first()
        if not admin:
            admin_inicial = Usuario(
                nombre        = "Administrador",
                email         = "admin@ctp.ed.cr",
                password_hash = hashear_password("Admin1234"),
                rol           = "admin"
            )
            db.add(admin_inicial)
            db.commit()
            print("✅ Usuario admin creado: admin@ctp.ed.cr / Admin1234")
    finally:
        db.close()

@app.get("/")
def root():
    return {"sistema": "Horarios CTP Heredia", "version": "2.0.0", "status": "activo"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
