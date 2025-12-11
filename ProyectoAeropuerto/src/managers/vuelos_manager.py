"""
Gestión de vuelos y colas de aterrizaje / despegue.
"""

from __future__ import annotations
from collections import deque
from typing import Deque, Dict, List, Optional

from src.models import Vuelo


class GestorVuelos:
    """
    Gestiona los vuelos activos y las colas de aterrizaje / despegue.

    - cola_aterrizaje: vuelos pendientes de aterrizar
    - cola_despegue: vuelos pendientes de despegar
    - vuelos_activos: todos los vuelos cargados en memoria
    """

    def __init__(self) -> None:
        self.cola_aterrizaje: Deque[Vuelo] = deque()
        self.cola_despegue: Deque[Vuelo] = deque()
        self.vuelos_activos: Dict[str, Vuelo] = {}
        self.vuelos_completados: List[Vuelo] = []

    # ------------------------------------------------------------------    
    # Altas y colas
    # ------------------------------------------------------------------

    def añadir_vuelo(self, vuelo: Vuelo) -> None:
        """
        Añade un vuelo al sistema y lo coloca en la cola correspondiente.
        """
        self.vuelos_activos[vuelo.id_vuelo] = vuelo

        if vuelo.tipo == "ATERRIZAJE":
            self.cola_aterrizaje.append(vuelo)
        else:
            self.cola_despegue.append(vuelo)

    # ------------------------------------------------------------------    
    # Selección de vuelo prioritario
    # ------------------------------------------------------------------

    def _obtener_vuelo_prioritario(self, cola: Deque[Vuelo], tiempo_actual: int) -> Optional[Vuelo]:
        """
        Devuelve el vuelo con mayor prioridad dentro de una cola.

        Criterios (en orden):
        1) Mayor prioridad (2 = emergencia)
        2) Aterrizajes con combustible crítico (<= 5)
        3) Mayor atraso respecto a ETA/ETD
        4) Desempate alfabético por id_vuelo
        """
        if not cola:
            return None

        vuelos = list(cola)

        def clave(v: Vuelo):
            prioridad = v.prioridad
            combustible_critico = 1 if v.tiene_combustible_critico() else 0
            previsto = v.get_tiempo_previsto() or 0
            atraso = max(0, tiempo_actual - previsto)
            return (
                prioridad,          # prioridad (2 > 1 > 0)
                combustible_critico,  # combustible crítico
                atraso,             # mayor atraso
                v.id_vuelo          # alfabético
            )

        vuelos.sort(key=clave, reverse=True)
        return vuelos[0]

    def seleccionar_vuelo_para_pista(self, tiempo_actual: int) -> Optional[Vuelo]:
        """
        Selecciona el siguiente vuelo a asignar a una pista libre.

        Política:
        - Intentar primero aterrizajes (seguridad)
        - Si no hay, usar vuelos de despegue
        """
        vuelo = self._obtener_vuelo_prioritario(self.cola_aterrizaje, tiempo_actual)
        if vuelo is not None:
            return vuelo

        return self._obtener_vuelo_prioritario(self.cola_despegue, tiempo_actual)

    # ------------------------------------------------------------------    
    # Cambio de estado
    # ------------------------------------------------------------------

    def asignar_vuelo(self, id_vuelo: str, tiempo_actual: int) -> None:
        """
        Marca un vuelo como ASIGNADO y lo saca de la cola.
        """
        vuelo = self.vuelos_activos.get(id_vuelo)
        if vuelo is None:
            return

        vuelo.estado = "ASIGNADO"
        vuelo.tiempo_inicio = tiempo_actual

        if vuelo in self.cola_aterrizaje:
            self.cola_aterrizaje.remove(vuelo)
        if vuelo in self.cola_despegue:
            self.cola_despegue.remove(vuelo)

    def completar_vuelo(self, id_vuelo: str, tiempo_actual: int) -> None:
        """
        Marca un vuelo como COMPLETADO.
        """
        vuelo = self.vuelos_activos.get(id_vuelo)
        if vuelo is None:
            return

        vuelo.estado = "COMPLETADO"
        vuelo.tiempo_fin = tiempo_actual
        if vuelo not in self.vuelos_completados:
            self.vuelos_completados.append(vuelo)

    # ------------------------------------------------------------------    
    # Consultas de estado
    # ------------------------------------------------------------------

    def obtener_estado_vuelos(self) -> List[dict]:
        """
        Devuelve una lista con información resumida de todos los vuelos.
        """
        resultado: List[dict] = []
        for v in self.vuelos_activos.values():
            resultado.append(
                {
                    "id": v.id_vuelo,
                    "tipo": v.tipo,
                    "estado": v.estado,
                    "prioridad": v.prioridad,
                    "combustible": v.combustible,
                    "pista": v.pista_asignada or "-",
                }
            )
        return resultado

    def contar_vuelos_por_estado(self) -> dict:
        """
        Devuelve un resumen de cuántos vuelos hay en cada estado.
        """
        en_cola = len(self.cola_aterrizaje) + len(self.cola_despegue)
        en_operacion = len(
            [v for v in self.vuelos_activos.values() if v.estado == "ASIGNADO"]
        )
        completados = len(self.vuelos_completados)

        return {
            "en_cola": en_cola,
            "en_operacion": en_operacion,
            "completados": completados,
            "total": len(self.vuelos_activos),
        }
