import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from uuid import uuid4

from app.domain.consulta_medica import ConsultaMedica
from app.application.consulta_medica_use_cases import (
    CrearConsultaMedicaUseCase,
    ObtenerConsultaMedicaUseCase,
    ListarConsultasPorMascotaUseCase
)
from app.infrastructure.repositories.consulta_medica_repository import ConsultaMedicaSQLAlchemyRepository
from app.domain.value_objects import Id


def test_creacion_consulta_medica_valida():
    """Test de creación válida de consulta médica."""
    # Datos de prueba
    cita_id = Id(uuid4())
    mascota_id = Id(uuid4())
    veterinario_id = Id(uuid4())
    
    # Crear consulta
    consulta = ConsultaMedica(
        id=Id(uuid4()),
        cita_id=cita_id,
        mascota_id=mascota_id,
        veterinario_id=veterinario_id,
        fecha_consulta=datetime.now(),
        diagnostico="Diagnóstico de prueba",
        tratamiento="Tratamiento de prueba"
    )
    
    # Verificar que se creó correctamente
    assert consulta.id is not None
    assert consulta.cita_id == cita_id
    assert consulta.mascota_id == mascota_id
    assert consulta.veterinario_id == veterinario_id
    assert consulta.diagnostico == "Diagnóstico de prueba"
    assert consulta.tratamiento == "Tratamiento de prueba"


def test_creacion_consulta_medica_sin_diagnostico():
    """Test de creación inválida sin diagnóstico."""
    with pytest.raises(ValueError, match="El diagnóstico no puede estar vacío"):
        ConsultaMedica(
            id=Id(uuid4()),
            cita_id=Id(uuid4()),
            mascota_id=Id(uuid4()),
            veterinario_id=Id(uuid4()),
            fecha_consulta=datetime.now(),
            diagnostico="",  # Empty
            tratamiento="Tratamiento de prueba"
        )


def test_creacion_consulta_medica_sin_tratamiento():
    """Test de creación inválida sin tratamiento."""
    with pytest.raises(ValueError, match="El tratamiento no puede estar vacío"):
        ConsultaMedica(
            id=Id(uuid4()),
            cita_id=Id(uuid4()),
            mascota_id=Id(uuid4()),
            veterinario_id=Id(uuid4()),
            fecha_consulta=datetime.now(),
            diagnostico="Diagnóstico de prueba",
            tratamiento=""  # Empty
        )


def test_crear_consulta_medica_use_case():
    """Test del caso de uso de crear consulta médica."""
    
    # Mock del repositorio
    mock_repository = Mock()
    
    # Configurar el comportamiento del repositorio
    mock_consulta = ConsultaMedica(
        id=Id(uuid4()),
        cita_id=Id(uuid4()),
        mascota_id=Id(uuid4()),
        veterinario_id=Id(uuid4()),
        fecha_consulta=datetime.now(),
        diagnostico="Diagnóstico de prueba",
        tratamiento="Tratamiento de prueba"
    )
    
    mock_repository.crear_consulta.return_value = mock_consulta
    
    # Crear el caso de uso
    use_case = CrearConsultaMedicaUseCase(mock_repository)
    
    # Ejecutar el caso de uso con datos válidos
    dto = {
        "cita_id": Id(uuid4()),
        "mascota_id": Id(uuid4()),
        "veterinario_id": Id(uuid4()),
        "fecha_consulta": datetime.now(),
        "diagnostico": "Diagnóstico de prueba",
        "tratamiento": "Tratamiento de prueba"
    }
    
    result = use_case.execute(dto)
    
    # Verificar resultados
    assert result == mock_consulta
    mock_repository.crear_consulta.assert_called_once()


def test_obtener_consulta_medica_use_case():
    """Test del caso de uso de obtener consulta médica."""
    
    # Mock del repositorio
    mock_repository = Mock()
    
    # Configurar el comportamiento del repositorio
    mock_consulta = ConsultaMedica(
        id=Id(uuid4()),
        cita_id=Id(uuid4()),
        mascota_id=Id(uuid4()),
        veterinario_id=Id(uuid4()),
        fecha_consulta=datetime.now(),
        diagnostico="Diagnóstico de prueba",
        tratamiento="Tratamiento de prueba"
    )
    
    mock_repository.obtener_por_id.return_value = mock_consulta
    
    # Crear el caso de uso
    use_case = ObtenerConsultaMedicaUseCase(mock_repository)
    
    # Ejecutar el caso de uso
    result = use_case.execute(Id(uuid4()))
    
    # Verificar resultados
    assert result == mock_consulta
    mock_repository.obtener_por_id.assert_called_once()


def test_listar_consultas_por_mascota_use_case():
    """Test del caso de uso de listar consultas por mascota."""
    
    # Mock del repositorio
    mock_repository = Mock()
    
    # Configurar el comportamiento del repositorio
    mock_consultas = [
        ConsultaMedica(
            id=Id(uuid4()),
            cita_id=Id(uuid4()),
            mascota_id=Id(uuid4()),
            veterinario_id=Id(uuid4()),
            fecha_consulta=datetime.now(),
            diagnostico="Diagnóstico 1",
            tratamiento="Tratamiento 1"
        ),
        ConsultaMedica(
            id=Id(uuid4()),
            cita_id=Id(uuid4()),
            mascota_id=Id(uuid4()),
            veterinario_id=Id(uuid4()),
            fecha_consulta=datetime.now(),
            diagnostico="Diagnóstico 2",
            tratamiento="Tratamiento 2"
        )
    ]
    
    mock_repository.listar_por_mascota.return_value = mock_consultas
    
    # Crear el caso de uso
    use_case = ListarConsultasPorMascotaUseCase(mock_repository)
    
    # Ejecutar el caso de uso
    result = use_case.execute(Id(uuid4()))
    
    # Verificar resultados
    assert result == mock_consultas
    mock_repository.listar_por_mascota.assert_called_once()


def test_creacion_consulta_medica_con_validacion():
    """Test de creación con validaciones adecuadas."""
    
    with pytest.raises(ValueError, match="El diagnóstico no puede estar vacío"):
        ConsultaMedica(
            id=Id(uuid4()),
            cita_id=Id(uuid4()),
            mascota_id=Id(uuid4()),
            veterinario_id=Id(uuid4()),
            fecha_consulta=datetime.now(),
            diagnostico="   ",  # Solo espacios
            tratamiento="Tratamiento"
        )
        
    with pytest.raises(ValueError, match="El tratamiento no puede estar vacío"):
        ConsultaMedica(
            id=Id(uuid4()),
            cita_id=Id(uuid4()),
            mascota_id=Id(uuid4()),
            veterinario_id=Id(uuid4()),
            fecha_consulta=datetime.now(),
            diagnostico="Diagnóstico",
            tratamiento="   " # Solo espacios
        )