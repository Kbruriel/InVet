from dataclasses import dataclass
from typing import Union
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Id:
    """Value object para identificadores."""
    value: Union[str, UUID]
    
    def __post_init__(self):
        if isinstance(self.value, str):
            try:
                # Intentar convertir string a UUID
                object.__setattr__(self, 'value', UUID(self.value))
            except ValueError:
                raise ValueError("El identificador debe ser un UUID válido")
        elif not isinstance(self.value, UUID):
            raise TypeError("El identificador debe ser un UUID")
    
    def __str__(self) -> str:
        return str(self.value)
        
    def __repr__(self) -> str:
        return f"Id({str(self.value)})"