# Tests para PDF-Insight

Suite de tests completa para la aplicación PDF-Insight usando pytest.

## Estructura de Tests

```
tests/
├── __init__.py              # Inicialización del paquete de tests
├── conftest.py              # Fixtures compartidas y configuración
├── test_config.py           # Tests del módulo de configuración
├── test_database.py         # Tests de operaciones de base de datos
├── test_file_manager.py     # Tests de gestión de archivos
├── test_pdf_processor.py    # Tests del procesador de PDFs
├── test_integration.py      # Tests de integración end-to-end
└── README.md                # Esta documentación
```

## Instalación de Dependencias

Instala las dependencias de testing:

```bash
pip install -r requirements.txt
```

Esto instalará:
- `pytest` - Framework de testing
- `pytest-cov` - Cobertura de código
- `pytest-mock` - Mocking para tests

## Ejecutar Tests

### Ejecutar todos los tests

```bash
pytest
```

### Ejecutar tests con salida verbose

```bash
pytest -v
```

### Ejecutar un archivo de test específico

```bash
pytest tests/test_database.py
pytest tests/test_file_manager.py
```

### Ejecutar una función de test específica

```bash
pytest tests/test_database.py::test_database_initialization
```

### Ejecutar tests con cobertura

```bash
pytest --cov=src --cov-report=html
```

Esto generará un reporte de cobertura en `htmlcov/index.html`.

### Ver cobertura en terminal

```bash
pytest --cov=src --cov-report=term-missing
```

### Ejecutar solo tests rápidos (excluir tests marcados como lentos)

```bash
pytest -m "not slow"
```

### Ejecutar solo tests de integración

```bash
pytest tests/test_integration.py -v
```

## Fixtures Disponibles

Las fixtures están definidas en `conftest.py` y están disponibles para todos los tests:

### `temp_dir`
Directorio temporal que se limpia automáticamente después del test.

```python
def test_example(temp_dir):
    file_path = temp_dir / "test.txt"
    file_path.write_text("test")
    assert file_path.exists()
```

### `temp_data_dirs`
Estructura completa de directorios de datos (pending, processed, images, text, logs).

```python
def test_example(temp_data_dirs):
    assert temp_data_dirs['pending'].exists()
    assert temp_data_dirs['processed'].exists()
```

### `temp_db_path`
Ruta a una base de datos temporal.

```python
def test_example(temp_db_path):
    db = Database(temp_db_path)
    assert temp_db_path.exists()
```

### `sample_pdf_metadata`
Metadata de ejemplo para un PDF.

```python
def test_example(sample_pdf_metadata):
    assert sample_pdf_metadata['filename'] == 'test.pdf'
    assert sample_pdf_metadata['num_pages'] == 5
```

### `create_sample_pdf`
Factory fixture para crear archivos PDF de prueba.

```python
def test_example(create_sample_pdf):
    pdf = create_sample_pdf("my_test.pdf", "content")
    assert pdf.exists()
```

## Tipos de Tests

### Tests Unitarios

Prueban funciones y métodos individuales de forma aislada:
- `test_config.py` - Configuración y directorios
- `test_database.py` - Operaciones CRUD de base de datos
- `test_file_manager.py` - Operaciones de archivos
- `test_pdf_processor.py` - Funciones de procesamiento

### Tests de Integración

Prueban el flujo completo de la aplicación:
- `test_integration.py` - Workflows completos de procesamiento

## Cobertura de Código

Para ver qué partes del código están cubiertas por tests:

```bash
# Generar reporte HTML
pytest --cov=src --cov-report=html

# Abrir en navegador
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html      # macOS
```

## Buenas Prácticas

### Nombrar Tests

- Usa nombres descriptivos: `test_database_handles_duplicate_filenames`
- Prefijo con `test_` para que pytest los detecte
- Agrupa tests relacionados en clases

### Estructura de Test

Sigue el patrón AAA (Arrange, Act, Assert):

```python
def test_example():
    # Arrange - Configurar el test
    db = Database(temp_db_path)
    metadata = {...}
    
    # Act - Ejecutar la acción
    pdf_id = db.add_pdf(metadata)
    
    # Assert - Verificar el resultado
    assert pdf_id > 0
    assert db.pdf_exists(metadata['filename'])
```

### Usar Fixtures

Reutiliza configuración común con fixtures:

```python
@pytest.fixture
def configured_database(temp_db_path):
    db = Database(temp_db_path)
    # Setup adicional
    return db

def test_with_fixture(configured_database):
    # Usa la fixture
    assert configured_database.db_path.exists()
```

## Configuración Adicional

### pytest.ini

Crea un archivo `pytest.ini` en la raíz del proyecto para configuración personalizada:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
```

## Comandos Útiles

```bash
# Tests con output de print statements
pytest -s

# Detener en el primer fallo
pytest -x

# Ejecutar el último test que falló
pytest --lf

# Mostrar los tests más lentos
pytest --durations=10

# Ejecutar tests en paralelo (requiere pytest-xdist)
pytest -n auto
```

## Recursos

- [Documentación de pytest](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
