# Verificación de modelos 
import sys
sys.path.insert(0, 'app')
try:
    from infrastructure.models.user import User
    from infrastructure.models.session import UserSession
    print("OK: Todos los modelos cargados correctamente")
except Exception as e:
    print(f"ERROR: {e}")