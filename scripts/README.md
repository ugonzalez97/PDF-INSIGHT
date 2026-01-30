# Scripts de Mantenimiento

Esta carpeta contiene utilidades para gestionar y mantener la aplicación PDF-Insight.

## Scripts Disponibles

### 🗑️ reset_database.py
Elimina completamente la base de datos SQLite.

```bash
python scripts/reset_database.py
```

**Uso:** Cuando quieres empezar desde cero con una base de datos limpia.

⚠️ **ADVERTENCIA:** Esto eliminará todo el historial de PDFs procesados.

---

### 🧹 clean_data.py
Limpia los archivos extraídos (imágenes, texto, PDFs procesados).

```bash
python scripts/clean_data.py
```

**Opciones:**
- Limpiar solo imágenes y texto
- Limpiar todo (incluidos PDFs procesados)

**Uso:** Cuando quieres liberar espacio en disco manteniendo la base de datos intacta.

---

### 💾 backup_database.py
Crea una copia de seguridad timestamped de la base de datos.

```bash
python scripts/backup_database.py
```

**Uso:** Antes de hacer cambios importantes o regularmente para mantener backups.

Las copias se guardan en: `backups/pdf_insight_YYYYMMDD_HHMMSS.db`

---

### 🔄 move_pdfs_back.py
Mueve PDFs de `processed/` de vuelta a `pending/` para reprocesar.

```bash
python scripts/move_pdfs_back.py
```

**Uso:** Cuando has actualizado la lógica de procesamiento y quieres reprocesar archivos.

**Nota:** Usa esto junto con `reset_database.py` para un reprocesamiento completo.

---

## Flujos de Trabajo Comunes

### Reprocesar todo desde cero:
```bash
# 1. Hacer backup (opcional pero recomendado)
python scripts/backup_database.py

# 2. Resetear base de datos
python scripts/reset_database.py

# 3. Limpiar archivos extraídos
python scripts/clean_data.py  # Opción 2

# 4. Mover PDFs de vuelta
python scripts/move_pdfs_back.py

# 5. Reprocesar
python main.py
```

### Limpiar espacio manteniendo metadata:
```bash
# Limpiar solo imágenes y texto
python scripts/clean_data.py  # Opción 1
```

### Backup regular:
```bash
# Crear backup antes de cambios importantes
python scripts/backup_database.py
```
