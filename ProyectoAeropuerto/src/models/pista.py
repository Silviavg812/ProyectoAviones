"""
Modelo de datos para representar una pista de aterrizaje/despegue.
"""

from __future__ import annotations
from typing import Optional


class Pista:
    """
    Representa una pista del aeropuerto.

    Atributos principales (según enunciado):
    - id_pista: identificador de pista (R1, R2, ...)
    - categoria: corta, estandar, larga
    - tiempo_uso: minutos que permanece ocupada por operación
    - habilitada: 1=operativa, 0=fuera de servicio
    """

    def __init__(
        self,
        id_pista: str,
        categoria: str,
        tiempo_uso: int,
        habilitada: int = 1,
    ) -> None:
        self.id_pista: str = id_pista
        self.categoria: str = categoria
        self.tiempo_uso: int = tiempo_uso
        self.habilitada: int = habilitada

        # Estado dinámico en la simulación
        self.libre: bool = True
        self.vuelo_actual: Optional[str] = None
        self.tiempo_liberacion: Optional[int] = None
        self.operaciones_totales: int = 0

    def __repr__(self) -> str:
        estado = "LIBRE" if self.libre else f"OCUPADA ({self.vuelo_actual})"
        return f"{self.id_pista} ({self.categoria}, {estado})"

    # ---- Lógica de uso de pista -------------------------------------------

    def asignar(self, vuelo, tiempo_actual: int) -> None:
        """
        Asigna un vuelo a la pista durante tiempo_uso minutos.
        """
        self.libre = False
        self.vuelo_actual = vuelo.id_vuelo
        self.tiempo_liberacion = tiempo_actual + self.tiempo_uso
        self.operaciones_totales += 1

    def liberar(self, tiempo_actual: int) -> Optional[str]:
        """
        Libera la pista y devuelve el id del vuelo que la ocupaba.
        """
        vuelo_liberado = self.vuelo_actual
        self.libre = True
        self.vuelo_actual = None
        self.tiempo_liberacion = None
        return vuelo_liberado

    def esta_disponible(self, tiempo_actual: int) -> bool:
        """
        Indica si la pista está operativa y libre en este momento.
        """
        if not self.habilitada:
            return False

        if self.libre:
            return True

        if self.tiempo_liberacion is not None and tiempo_actual >= self.tiempo_liberacion:
            return True

        return False

    # ---- Serialización a/desde CSV ----------------------------------------

    def to_dict(self) -> dict:
        """
        Convierte la pista a diccionario compatible con CSV.
        """
        return {
            "id_pista": self.id_pista,
            "categoria": self.categoria,
            "tiempo_uso": self.tiempo_uso,
            "habilitada": self.habilitada,
        }

    @staticmethod
    def from_dict(data: dict) -> "Pista":
        """
        Crea una Pista desde un diccionario (leído de CSV).
        """
        return Pista(
            id_pista=data["id_pista"],
            categoria=data["categoria"],
            tiempo_uso=int(data["tiempo_uso"]),
            habilitada=int(data["habilitada"]),
        )
