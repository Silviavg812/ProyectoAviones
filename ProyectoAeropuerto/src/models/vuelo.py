"""
Modelo de datos para representar un vuelo en el simulador.
"""

from __future__ import annotations
from typing import Optional


class Vuelo:
    """
    Representa un vuelo dentro del sistema de simulación.

    Atributos principales (según enunciado):
    - id_vuelo: identificador único (p.ej. IB123)
    - tipo: "ATERRIZAJE" o "DESPEGUE"
    - eta: minuto simulado previsto de llegada (solo aterrizajes)
    - etd: minuto simulado previsto de salida (solo despegues)
    - prioridad: 0=normal, 1=alta, 2=emergencia
    - combustible: minutos de autonomía (solo aterrizajes)
    - estado: EN_COLA, ASIGNADO, COMPLETADO, CANCELADO
    """

    def __init__(
        self,
        id_vuelo: str,
        tipo: str,
        eta: Optional[int] = None,
        etd: Optional[int] = None,
        prioridad: int = 0,
        combustible: Optional[int] = None,
        estado: str = "EN_COLA",
    ) -> None:
        self.id_vuelo: str = id_vuelo
        self.tipo: str = tipo.upper()
        self.eta: Optional[int] = eta if self.tipo == "ATERRIZAJE" else None
        self.etd: Optional[int] = etd if self.tipo == "DESPEGUE" else None
        self.prioridad: int = prioridad
        self.combustible: Optional[int] = (
            combustible if self.tipo == "ATERRIZAJE" else None
        )
        self.estado: str = estado

        # Campos adicionales útiles para la simulación
        self.pista_asignada: Optional[str] = None
        self.tiempo_inicio: Optional[int] = None
        self.tiempo_fin: Optional[int] = None

    def __repr__(self) -> str:
        previsto = self.get_tiempo_previsto()
        return f"{self.id_vuelo} ({self.tipo}, t={previsto}, p={self.prioridad})"

    # ---- Lógica de dominio -------------------------------------------------

    def get_tiempo_previsto(self) -> Optional[int]:
        """
        Devuelve el tiempo previsto (ETA o ETD) según el tipo de vuelo.
        """
        return self.eta if self.tipo == "ATERRIZAJE" else self.etd

    def es_emergencia(self) -> bool:
        """
        Indica si el vuelo está marcado como emergencia (prioridad 2).
        """
        return self.prioridad == 2

    def tiene_combustible_critico(self) -> bool:
        """
        Indica si el vuelo de aterrizaje está en combustible crítico (<= 5).
        """
        if self.tipo != "ATERRIZAJE":
            return False
        if self.combustible is None:
            return False
        return self.combustible <= 5

    # ---- Serialización a/desde CSV ----------------------------------------

    def to_dict(self) -> dict:
        """
        Convierte el vuelo a un diccionario compatible con CSV.
        """
        return {
            "id_vuelo": self.id_vuelo,
            "tipo": self.tipo,
            "eta": self.eta if self.eta is not None else "",
            "etd": self.etd if self.etd is not None else "",
            "prioridad": self.prioridad,
            "combustible": self.combustible if self.combustible is not None else "",
            "estado": self.estado,
        }

    @staticmethod
    def from_dict(data: dict) -> "Vuelo":
        """
        Crea un Vuelo desde un diccionario (leído de CSV).
        """
        eta = int(data["eta"]) if data.get("eta") else None
        etd = int(data["etd"]) if data.get("etd") else None
        combustible = int(data["combustible"]) if data.get("combustible") else None

        return Vuelo(
            id_vuelo=data["id_vuelo"],
            tipo=data["tipo"],
            eta=eta,
            etd=etd,
            prioridad=int(data["prioridad"]),
            combustible=combustible,
            estado=data.get("estado", "EN_COLA"),
        )
