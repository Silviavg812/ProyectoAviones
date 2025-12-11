"""
Gestión de pistas de aterrizaje/despegue.
"""

from __future__ import annotations
from typing import Dict, List, Optional

from src.models import Pista, Vuelo


class GestorPistas:
    """
    Gestiona las pistas disponibles en el aeropuerto.

    - pistas: diccionario id_pista -> Pista
    """

    def __init__(self) -> None:
        self.pistas: Dict[str, Pista] = {}

    # ------------------------------------------------------------------    
    # Altas y consultas
    # ------------------------------------------------------------------

    def añadir_pista(self, pista: Pista) -> None:
        """
        Añade una pista al sistema.
        """
        self.pistas[pista.id_pista] = pista

    def obtener_pistas_libres(self, tiempo_actual: int) -> List[Pista]:
        """
        Devuelve todas las pistas habilitadas y disponibles en este minuto.
        """
        return [
            p
            for p in self.pistas.values()
            if p.esta_disponible(tiempo_actual)
        ]

    # ------------------------------------------------------------------    
    # Asignación y liberación
    # ------------------------------------------------------------------

    def asignar_vuelo_a_pista(
        self, pista: Pista, vuelo: Vuelo, tiempo_actual: int
    ) -> None:
        """
        Asigna un vuelo a una pista concreta.
        """
        pista.asignar(vuelo, tiempo_actual)
        vuelo.pista_asignada = pista.id_pista

    def actualizar_pistas(self, tiempo_actual: int) -> List[str]:
        """
        Libera las pistas cuya operación termina en este minuto.

        Returns:
            Lista de id_vuelo que acaban de completar su operación.
        """
        completados: List[str] = []
        for pista in self.pistas.values():
            if (
                not pista.libre
                and pista.tiempo_liberacion is not None
                and pista.tiempo_liberacion <= tiempo_actual
            ):
                vuelo_id = pista.liberar(tiempo_actual)
                if vuelo_id:
                    completados.append(vuelo_id)
        return completados

    # ------------------------------------------------------------------    
    # Consultas de estado
    # ------------------------------------------------------------------

    def obtener_estado_pistas(self) -> List[dict]:
        """
        Devuelve información resumida de todas las pistas.
        """
        resultado: List[dict] = []
        for p in self.pistas.values():
            estado = "LIBRE" if p.libre else "OCUPADA"
            habilitada = "SÍ" if p.habilitada else "NO"
            resultado.append(
                {
                    "pista": p.id_pista,
                    "categoria": p.categoria,
                    "estado": estado,
                    "habilitada": habilitada,
                    "vuelo_actual": p.vuelo_actual or "-",
                    "liberacion_en": p.tiempo_liberacion if p.tiempo_liberacion else "-",
                    "operaciones": p.operaciones_totales,
                }
            )
        return resultado

    def contar_operaciones_totales(self) -> int:
        """
        Devuelve el número total de operaciones realizadas en todas las pistas.
        """
        return sum(p.operaciones_totales for p in self.pistas.values())
