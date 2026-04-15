"""
Script de migración de base de datos.
Ejecutar UNA SOLA VEZ después de actualizar los modelos.

Uso:
  cd backend
  python migrate.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from app.database import engine
import app.models   # importar todos los modelos para que Base los registre


def migrar():
    print("Aplicando migraciones...")

    with engine.begin() as conn:

        # 1. Crear tabla departamentos (si no existe)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS departamentos (
                id         SERIAL PRIMARY KEY,
                nombre     VARCHAR(100) NOT NULL UNIQUE,
                activo     BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMPTZ DEFAULT now()
            )
        """))
        print("  ✅ Tabla 'departamentos' lista")

        # 2. Agregar departamento_id a profesores (si no existe)
        conn.execute(text("""
            ALTER TABLE profesores
                ADD COLUMN IF NOT EXISTS departamento_id INTEGER
                REFERENCES departamentos(id)
        """))
        print("  ✅ Columna 'departamento_id' en profesores")

        # 3. Agregar departamento_id a materias (si no existe)
        conn.execute(text("""
            ALTER TABLE materias
                ADD COLUMN IF NOT EXISTS departamento_id INTEGER
                REFERENCES departamentos(id)
        """))
        print("  ✅ Columna 'departamento_id' en materias")

        # 3b. Agregar solo_nivel a materias (si no existe)
        conn.execute(text("""
            ALTER TABLE materias
                ADD COLUMN IF NOT EXISTS solo_nivel INTEGER
        """))
        print("  ✅ Columna 'solo_nivel' en materias")

        # 4. Crear tabla M2M grupo_especialidades (si no existe)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS grupo_especialidades (
                grupo_id        INTEGER NOT NULL REFERENCES grupos(id),
                especialidad_id INTEGER NOT NULL REFERENCES especialidades(id),
                PRIMARY KEY (grupo_id, especialidad_id)
            )
        """))
        print("  ✅ Tabla 'grupo_especialidades' lista")

        # 5. Migrar datos existentes de especialidad_id → grupo_especialidades (si la columna existe)
        conn.execute(text("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='grupos' AND column_name='especialidad_id'
                ) THEN
                    INSERT INTO grupo_especialidades (grupo_id, especialidad_id)
                    SELECT id, especialidad_id
                    FROM grupos
                    WHERE especialidad_id IS NOT NULL
                    ON CONFLICT DO NOTHING;
                END IF;
            END $$;
        """))
        print("  ✅ Datos migrados a 'grupo_especialidades' (si había datos)")

        # 6. Eliminar columna especialidad_id de grupos (si existe)
        conn.execute(text("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='grupos' AND column_name='especialidad_id'
                ) THEN
                    ALTER TABLE grupos DROP COLUMN especialidad_id;
                END IF;
            END $$;
        """))
        print("  ✅ Columna 'especialidad_id' eliminada de grupos")

    print("\n✅ Migración completada exitosamente.")


if __name__ == "__main__":
    migrar()
