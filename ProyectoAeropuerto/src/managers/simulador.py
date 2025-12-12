"""
Controlador principal de la simulación de aeropuerto.
"""

from __future__ import annotations
from typing import Iterable
import time
import threading

from src.managers.vuelos_manager import GestorVuelos
from src.managers.pistas_manager import GestorPistas
from src.models import Vuelo, Pista
from src.utils import GestorLogs


class ControladorSimulacion:
    """
    Orquesta la simulación:

    - Mantiene el tiempo simulado (minutos)
    - Actualiza pistas y vuelos
    - Aplica prioridades y emergencias
    - Registra eventos en los logs
    """
    def ejecutar_con_reloj_real(self, segundos_por_minuto: float = 5.0) -> None:
        """
        Modo automático: cada `segundos_por_minuto` segundos reales
        avanza 1 minuto simulado.
        """
        self.en_simulacion = True
        try:
            while self.en_simulacion:
                self.avanzar_minuto()
                time.sleep(segundos_por_minuto)
        except KeyboardInterrupt:
            # Permite parar con Ctrl+C si se ejecuta este modo
            self.finalizar_simulacion()
    
    def __init__(self, gestor_logs: GestorLogs) -> None:
        self.tiempo_actual: int = 0
        self.gestor_vuelos = GestorVuelos()
        self.gestor_pistas = GestorPistas()
        self.gestor_logs = gestor_logs
        self.en_simulacion: bool = False
        self._hilo_simulacion: threading.Thread | None = None
        self._stop_event = threading.Event()

    # ------------------------------------------------------------------
    # Inicialización
    # ------------------------------------------------------------------

    def inicializar_sistema(
        self, vuelos: Iterable[Vuelo], pistas: Iterable[Pista]
    ) -> None:
        """
        Carga vuelos y pistas en los gestores y registra la carga inicial.
        """
        vuelos = list(vuelos)
        pistas = list(pistas)

        for p in pistas:
            self.gestor_pistas.añadir_pista(p)

        self.gestor_logs.registrar_carga_inicial(
            tiempo=self.tiempo_actual,
            num_vuelos=len(vuelos),
            num_pistas=len(pistas),
        )

        for v in vuelos:
            self.gestor_vuelos.añadir_vuelo(v)
            self.gestor_logs.registrar_en_cola(
                tiempo=self.tiempo_actual,
                id_vuelo=v.id_vuelo,
                tipo_vuelo=v.tipo,
            )

        self.en_simulacion = True

    # ------------------------------------------------------------------
    # Avance del reloj
    # ------------------------------------------------------------------

    def _actualizar_emergencias(self) -> None:
        """
        Revisa vuelos de aterrizaje con combustible crítico y eleva prioridad.
        """
        for vuelo in self.gestor_vuelos.vuelos_activos.values():
            if vuelo.tipo != "ATERRIZAJE":
                continue
            if vuelo.tiene_combustible_critico() and vuelo.prioridad < 2:
                vuelo.prioridad = 2
                self.gestor_logs.registrar_emergencia(
                    tiempo=self.tiempo_actual,
                    id_vuelo=vuelo.id_vuelo,
                    prioridad=2,
                    motivo="combustible<=5",
                )

    def _asignar_vuelos_a_pistas(self) -> None:
        """
        Asigna vuelos a todas las pistas libres en este minuto.
        """
        pistas_libres = self.gestor_pistas.obtener_pistas_libres(self.tiempo_actual)

        for pista in pistas_libres:
            vuelo = self.gestor_vuelos.seleccionar_vuelo_para_pista(self.tiempo_actual)
            if vuelo is None:
                break

            self.gestor_pistas.asignar_vuelo_a_pista(pista, vuelo, self.tiempo_actual)
            self.gestor_vuelos.asignar_vuelo(vuelo.id_vuelo, self.tiempo_actual)

            self.gestor_logs.registrar_asignacion(
                tiempo=self.tiempo_actual,
                id_vuelo=vuelo.id_vuelo,
                id_pista=pista.id_pista,
                tipo_vuelo=vuelo.tipo,
            )

    def _consumir_combustible_en_cola(self) -> None:
        """
        Decrementa el combustible de los vuelos de aterrizaje que siguen en cola.
        """
        for vuelo in self.gestor_vuelos.vuelos_activos.values():
            if vuelo.tipo == "ATERRIZAJE" and vuelo.estado == "EN_COLA":
                if vuelo.combustible is not None and vuelo.combustible > 0:
                    vuelo.combustible -= 1

    def avanzar_minuto(self) -> bool:
        """
        Avanza un minuto en la simulación y actualiza todo el sistema.

        Devuelve:
            True si se avanza correctamente, False si la simulación ya está parada.
        """
        if not self.en_simulacion:
            return False

        # 1) Liberar pistas que terminan ahora
        completados = self.gestor_pistas.actualizar_pistas(self.tiempo_actual)
        for id_vuelo in completados:
            # Marcar vuelo como completado
            self.gestor_vuelos.completar_vuelo(id_vuelo, self.tiempo_actual)
            # Buscar una pista libre para registrar el log (simplificación)
            for pista in self.gestor_pistas.pistas.values():
                if pista.libre:
                    self.gestor_logs.registrar_completado(
                        tiempo=self.tiempo_actual,
                        id_vuelo=id_vuelo,
                        id_pista=pista.id_pista,
                    )
                    break

        # 2) Revisar emergencias por combustible
        self._actualizar_emergencias()

        # 3) Asignar vuelos a pistas libres
        self._asignar_vuelos_a_pistas()

        # 4) Consumir combustible de los que siguen en cola
        self._consumir_combustible_en_cola()

        # 5) Avanzar reloj
        self.tiempo_actual += 1
        return True

    def avanzar_n_minutos(self, n: int) -> None:
        """
        Avanza N minutos simulados (llamando a avanzar_minuto N veces).
        """
        for _ in range(n):
            if not self.avanzar_minuto():
                break
    def _bucle_reloj_real(self, segundos_por_minuto: float) -> None:
        """
        Bucle interno que avanza la simulación en segundo plano.
        """
        self.en_simulacion = True
        while not self._stop_event.is_set() and self.en_simulacion:
            self.avanzar_minuto()
            time.sleep(segundos_por_minuto)

    def iniciar_reloj_real(self, segundos_por_minuto: float = 5.0) -> None:
        """
        Inicia la simulación automática en un hilo aparte.
        """
        if self._hilo_simulacion and self._hilo_simulacion.is_alive():
            return  # ya está corriendo

        self._stop_event.clear()
        self._hilo_simulacion = threading.Thread(
            target=self._bucle_reloj_real,
            args=(segundos_por_minuto,),
            daemon=True,
        )
        self._hilo_simulacion.start()

    def detener_reloj_real(self) -> None:
        """
        Detiene el reloj real en segundo plano.
        """
        self._stop_event.set()
        self.en_simulacion = False
        if self._hilo_simulacion and self._hilo_simulacion.is_alive():
            self._hilo_simulacion.join(timeout=1.0)
    # ------------------------------------------------------------------
    # Finalización e información
    # ------------------------------------------------------------------


    def finalizar_simulacion(self) -> None:
        """
        Marca la simulación como finalizada y registra el fin en el log.
        """
        self.detener_reloj_real()
        total = len(self.gestor_vuelos.vuelos_completados)
        self.gestor_logs.registrar_fin_simulacion(
            tiempo=self.tiempo_actual,
            vuelos_atendidos=total,
        )


    def obtener_estado_general(self) -> dict:
        """
        Devuelve un resumen del estado global de la simulación.
        """
        return {
            "tiempo_actual": self.tiempo_actual,
            "estado": "EN_CURSO" if self.en_simulacion else "FINALIZADA",
            "vuelos": self.gestor_vuelos.contar_vuelos_por_estado(),
            "pistas_operativas": len(
                [p for p in self.gestor_pistas.pistas.values() if p.habilitada]
            ),
        }
        
