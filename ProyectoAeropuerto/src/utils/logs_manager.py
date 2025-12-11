"""
Gestión de logs de eventos e informes de simulación.
"""

from __future__ import annotations
import os
from typing import Iterable

from src.models import Vuelo, Pista


class GestorLogs:
    """
    Gestor de escritura de eventos en eventos.log.
    """

    def __init__(self, directorio_logs: str) -> None:
        self.directorio = directorio_logs
        os.makedirs(self.directorio, exist_ok=True)
        self.ruta_eventos = os.path.join(self.directorio, "eventos.log")
        self.ruta_informe = os.path.join(self.directorio, "informe.log")

    # ------------------------------------------------------------------    
    # Utilidad interna
    # ------------------------------------------------------------------

    def _escribir_linea(self, linea: str) -> None:
        with open(self.ruta_eventos, mode="a", encoding="utf-8") as f:
            f.write(linea + "\n")

    def limpiar_logs(self) -> None:
        """
        Elimina eventos.log e informe.log si existen.
        """
        for ruta in (self.ruta_eventos, self.ruta_informe):
            if os.path.exists(ruta):
                os.remove(ruta)

    # ------------------------------------------------------------------    
    # Eventos específicos
    # ------------------------------------------------------------------

    def registrar_carga_inicial(self, tiempo: int, num_vuelos: int, num_pistas: int) -> None:
        linea = f"[t={tiempo}] CARGA_INICIAL vuelos={num_vuelos} pistas={num_pistas}"
        self._escribir_linea(linea)

    def registrar_en_cola(self, tiempo: int, id_vuelo: str, tipo_vuelo: str) -> None:
        linea = f"[t={tiempo}] EN_COLA id_vuelo={id_vuelo} tipo={tipo_vuelo}"
        self._escribir_linea(linea)

    def registrar_asignacion(self, tiempo: int, id_vuelo: str, id_pista: str, tipo_vuelo: str) -> None:
        linea = (
            f"[t={tiempo}] ASIGNACION id_vuelo={id_vuelo} "
            f"pista={id_pista} tipo={tipo_vuelo}"
        )
        self._escribir_linea(linea)

    def registrar_completado(self, tiempo: int, id_vuelo: str, id_pista: str) -> None:
        linea = f"[t={tiempo}] COMPLETADO id_vuelo={id_vuelo} pista={id_pista}"
        self._escribir_linea(linea)

    def registrar_emergencia(self, tiempo: int, id_vuelo: str, prioridad: int, motivo: str) -> None:
        linea = (
            f"[t={tiempo}] EMERGENCIA id_vuelo={id_vuelo} "
            f"prioridad={prioridad} motivo={motivo}"
        )
        self._escribir_linea(linea)

    def registrar_fin_simulacion(self, tiempo: int, vuelos_atendidos: int) -> None:
        linea = f"[t={tiempo}] FIN_SIMULACION vuelos_atendidos={vuelos_atendidos}"
        self._escribir_linea(linea)


class GestorInformes:
    """
    Genera y muestra informe.log a partir del estado de la simulación.
    """

    @staticmethod
    def generar_informe(
        tiempo_actual: int,
        vuelos: Iterable[Vuelo],
        pistas: Iterable[Pista],
        ruta_informe: str,
    ) -> None:
        """
        Crea informe.log con resumen de la simulación.
        """
        vuelos = list(vuelos)
        pistas = list(pistas)

        completados = [v for v in vuelos if v.estado == "COMPLETADO"]

        # Tiempo medio de espera (t_inicio - ETA/ETD, solo si es positivo)
        tiempos_espera = []
        for v in completados:
            previsto = v.get_tiempo_previsto()
            if previsto is not None and v.tiempo_inicio is not None:
                espera = v.tiempo_inicio - previsto
                if espera >= 0:
                    tiempos_espera.append(espera)

        tiempo_medio_espera = (
            sum(tiempos_espera) / len(tiempos_espera) if tiempos_espera else 0.0
        )

        # Emergencias gestionadas
        emergencias = [v for v in completados if v.es_emergencia()]

        # Uso de pistas
        uso_pistas = [f"{p.id_pista}={p.operaciones_totales} operaciones" for p in pistas]

        lineas = []
        lineas.append("RESUMEN")
        lineas.append(f"- Tiempo simulado (min): {tiempo_actual}")
        lineas.append(f"- Vuelos atendidos: {len(completados)}")
        lineas.append(f"- Tiempo medio de espera (min): {tiempo_medio_espera:.1f}")
        lineas.append(f"- Uso de pistas: {', '.join(uso_pistas)}")
        lineas.append(f"- Emergencias gestionadas: {len(emergencias)}")
        lineas.append("- Detalle de vuelos completados:")

        for v in completados:
            if v.tiempo_inicio is None or v.tiempo_fin is None:
                continue
            extra = ", EMERGENCIA" if v.es_emergencia() else ""
            lineas.append(
                f"   • {v.id_vuelo}  ({v.tipo}{extra})  "
                f"t_inicio={v.tiempo_inicio}  t_fin={v.tiempo_fin}"
            )

        with open(ruta_informe, mode="w", encoding="utf-8") as f:
            f.write("\n".join(lineas))

    @staticmethod
    def mostrar_informe(ruta_informe: str) -> None:
        """
        Muestra por pantalla el contenido de informe.log, si existe.
        """
        if not os.path.exists(ruta_informe):
            print("[GestorInformes] No existe informe.log todavía.")
            return

        print("\n" + "=" * 60)
        with open(ruta_informe, mode="r", encoding="utf-8") as f:
            print(f.read())
        print("=" * 60 + "\n")
