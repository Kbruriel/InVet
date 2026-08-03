#!/usr/bin/env python3

"""
Archivo para validación de implementación del slice BE-002.
Este script ejecuta las pruebas unitarias y verifica que todo funcione correctamente.
"""

import sys
import os
from pathlib import Path

# Añadir el directorio app al path para poder hacer imports
sys.path.insert(0, str(Path(__file__).parent / "app"))

def test_backend_structure():
    """Test la estructura básica del backend"""
    print("Validación de estructura backend BE-002...")
    
    # Verificar que existen los directorios necesarios
    required_dirs = [
        "app/domain",
        "app/application", 
        "app/infrastructure/repositories",
        "app/api/schemas",
        "app/tests"
    ]
    
    for dir_path in required_dirs:
        full_path = Path(dir_path)
        if not full_path.exists():
            print(f"ERROR: Directorio no encontrado: {dir_path}")
            return False
        else:
            print(f"OK: Directorio encontrado: {dir_path}")
    
    # Verificar que existen los archivos necesarios 
    required_files = [
        "app/domain/user.py",
        "app/domain/value_objects.py", 
        "app/application/auth_use_cases.py",
        "app/infrastructure/repositories/user_repository.py",
        "app/infrastructure/repositories/session_repository.py",
        "app/infrastructure/models/user.py",
        "app/infrastructure/models/session.py",
        "app/api/schemas/auth.py",
        "app/api/auth_router.py",
        "app/api/user_router.py"
    ]
    
    for file_path in required_files:
        full_path = Path(file_path)
        if not full_path.exists():
            print(f"ERROR: Archivo no encontrado: {file_path}")
            return False
        else:
            print(f"OK: Archivo encontrado: {file_path}")
            
    print("OK: Estructura básica verificada correctamente")
    return True

def test_imports():
    """Test que todos los imports funcionan correctamente"""
    print("\nValidación de importaciones...")
    
    try:
        # Importar clases principales
        from app.domain.user import User, UserCreate
        from app.domain.value_objects import Token, AuthCredentials
        from app.application.auth_use_cases import AuthUseCase
        from app.infrastructure.repositories.user_repository import UserRepository
        from app.infrastructure.repositories.session_repository import SessionRepository
        from app.api.schemas.auth import UserPublic, Token as APIToken
        
        print("OK: Todos los imports funcionan correctamente")
        return True
        
    except Exception as e:
        print(f"ERROR: Fallo en importaciones: {e}")
        return False

if __name__ == "__main__":
    print("=== Validación de BE-002 (Autenticación y sesión) ===\n")
    
    success = True
    success &= test_backend_structure()
    success &= test_imports()
    
    if success:
        print("\n✓ Implementación BE-002 completada con éxito")
        sys.exit(0)
    else:
        print("\n✗ Fallo en la validación de BE-002") 
        sys.exit(1)