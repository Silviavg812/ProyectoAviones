"""
Interfaz de usuario por consola para el simulador de aeropuerto.
"""

from __future__ import annotations
import os
from typing import Optional

from src import (
    GestorCSV,
    GestorLogs,
    GestorInformes,
    ControladorSimulacion,
    Vuelo,
)



class MenuPrincipal:
    """
    Menú de consola que permite controlar la simulación:

    1) Cargar datos (vuelos.csv, pistas.csv)
    2) Añadir vuelo manual
    3) Ver estado general
    4) Avanzar 1 minuto
    5) Avanzar N minutos
    6) Ver estado de pistas
    7) Ver estado de vuelos
    8) Generar informe.log
    9) Mostrar informe en pantalla
    10) Guardar estado y salir
    11) EMPEZAR RELOJ
    """

    def __init__(self, ruta_datos: str, ruta_logs: str) -> None:
        self.ruta_datos = ruta_datos
        self.ruta_logs = ruta_logs

        self.gestor_csv = GestorCSV()
        self.gestor_logs = GestorLogs(self.ruta_logs)

        self.controlador: Optional[ControladorSimulacion] = None
        self.vuelos_cargados: list[Vuelo] = []
        self.pistas_cargadas = []

    # ------------------------------------------------------------------    
    # Utilidades de interfaz
    # ------------------------------------------------------------------

    def _pausa(self) -> None:
        input("\nPulsa ENTER para continuar...")

    def _banner(self) -> None:
        print("\n" + "=" * 70)
        print("        SIMULADOR DE AEROPUERTO - DAM (ACCESO A DATOS)")
        print("=" * 70 + "\n")

    def _mostrar_menu(self) -> None:
        print("\n[MENÚ PRINCIPAL]")
        print("-" * 40)
        print("1. Cargar datos (vuelos.csv, pistas.csv)")
        print("2. Añadir vuelo manual")
        print("3. Ver estado general")
        print("4. Avanzar 1 minuto")
        print("5. Avanzar N minutos")
        print("6. Ver estado de pistas")
        print("7. Ver estado de vuelos")
        print("8. Generar informe.log")
        print("9. Mostrar informe en pantalla")
        print("10. Guardar estado y salir")
        print("11. EMPEZAR RELOJ")
        print("-" * 40)

    def _requiere_simulacion(self) -> bool:
        if self.controlador is None:
            print("\n[!] Primero debes cargar datos (opción 1).")
            return False
        return True

    # ------------------------------------------------------------------    
    # Opciones del menú
    # ------------------------------------------------------------------

    def opcion_cargar_datos(self) -> None:
        """
        Opción 1: Cargar vuelos.csv y pistas.csv, inicializar simulación.
        """
        print("\n[CARGA DE DATOS]")

        ruta_vuelos = os.path.join(self.ruta_datos, "vuelos.csv")
        ruta_pistas = os.path.join(self.ruta_datos, "pistas.csv")

        self.vuelos_cargados = self.gestor_csv.leer_vuelos(ruta_vuelos)
        self.pistas_cargadas = self.gestor_csv.leer_pistas(ruta_pistas)

        if not self.vuelos_cargados or not self.pistas_cargadas:
            print("\n[✗] No se han podido cargar vuelos o pistas.")
            return

        # Limpiar logs anteriores
        self.gestor_logs.limpiar_logs()

        # Crear controlador e inicializar sistema
        self.controlador = ControladorSimulacion(self.gestor_logs)
        self.controlador.inicializar_sistema(self.vuelos_cargados, self.pistas_cargadas)

        print(f"\n[✓] Vuelos cargados: {len(self.vuelos_cargados)}")
        print(f"[✓] Pistas cargadas: {len(self.pistas_cargadas)}")

    def opcion_añadir_vuelo(self) -> None:
        """
        Opción 2: Añadir un vuelo manualmente.
        """
        if not self._requiere_simulacion():
            return

        print("\n[AÑADIR VUELO MANUAL]")
        id_vuelo = input("ID del vuelo (ej: IB123): ").strip().upper()
        if not id_vuelo:
            print("[!] ID no válido.")
            return

        print("\nTipo de vuelo:")
        print("  1. ATERRIZAJE")
        print("  2. DESPEGUE")
        tipo_op = input("Selecciona (1/2): ").strip()
        tipo = "ATERRIZAJE" if tipo_op == "1" else "DESPEGUE"

        eta = None
        etd = None
        combustible = None

        try:
            if tipo == "ATERRIZAJE":
                eta = int(input("ETA (minuto simulado): ").strip())
                combustible = int(input("Combustible (minutos): ").strip())
            else:
                etd = int(input("ETD (minuto simulado): ").strip())
        except ValueError:
            print("[!] Valor numérico no válido.")
            return

        try:
            prioridad = int(input("Prioridad (0=normal,1=alta,2=emergencia): ").strip())
        except ValueError:
            print("[!] Prioridad no válida.")
            return

        vuelo = Vuelo(
            id_vuelo=id_vuelo,
            tipo=tipo,
            eta=eta,
            etd=etd,
            prioridad=prioridad,
            combustible=combustible,
        )

        self.vuelos_cargados.append(vuelo)
        self.controlador.gestor_vuelos.añadir_vuelo(vuelo)
        self.gestor_logs.registrar_en_cola(
            tiempo=self.controlador.tiempo_actual,
            id_vuelo=vuelo.id_vuelo,
            tipo_vuelo=vuelo.tipo,
        )

        print(f"\n[✓] Vuelo {id_vuelo} añadido a la simulación.")

    def opcion_ver_estado_general(self) -> None:
        """
        Opción 3: Ver resumen del estado global.
        """
        if not self._requiere_simulacion():
            return

        estado = self.controlador.obtener_estado_general()
        print("\n[ESTADO GENERAL]")
        print("-" * 40)
        print(f"Tiempo simulado: {estado['tiempo_actual']} min")
        print(f"Estado: {estado['estado']}")
        print(f"Pistas operativas: {estado['pistas_operativas']}")
        print(f"Vuelos en cola: {estado['vuelos']['en_cola']}")
        print(f"Vuelos en operación: {estado['vuelos']['en_operacion']}")
        print(f"Vuelos completados: {estado['vuelos']['completados']}")
        print(f"Total vuelos: {estado['vuelos']['total']}")

    def opcion_avanzar_1_minuto(self) -> None:
        """
        Opción 4: Avanzar 1 minuto de simulación.
        """
        if not self._requiere_simulacion():
            return

        self.controlador.avanzar_minuto()
        print(f"\n[✓] Avanzado a t={self.controlador.tiempo_actual}.")

    def opcion_avanzar_n_minutos(self) -> None:
        """
        Opción 5: Avanzar N minutos de simulación.
        """
        if not self._requiere_simulacion():
            return

        try:
            n = int(input("¿Cuántos minutos quieres avanzar?: ").strip())
        except ValueError:
            print("[!] Valor no válido.")
            return

        if n <= 0:
            print("[!] El número debe ser mayor que cero.")
            return

        self.controlador.avanzar_n_minutos(n)
        print(f"\n[✓] Avanzado a t={self.controlador.tiempo_actual}.")
        # ------------------------------------------------------------------
    # Modo reloj real en segundo plano
    # ------------------------------------------------------------------

    
            

    def opcion_ver_pistas(self) -> None:
        """
        Opción 6: Ver estado detallado de las pistas.
        """
        if not self._requiere_simulacion():
            return

        print("\n[ESTADO DE PISTAS]")
        print("-" * 60)
        estado = self.controlador.gestor_pistas.obtener_estado_pistas()
        for p in estado:
            print(
                f"Pista {p['pista']} ({p['categoria']}) "
                f"- Estado: {p['estado']} / Habilitada: {p['habilitada']}"
            )
            print(
                f"   Vuelo actual: {p['vuelo_actual']}  "
                f"Libera en: {p['liberacion_en']}  "
                f"Operaciones totales: {p['operaciones']}"
            )
            print("-" * 60)

    def opcion_ver_vuelos(self) -> None:
        """
        Opción 7: Ver estado detallado de los vuelos.
        """
        if not self._requiere_simulacion():
            return

        print("\n[ESTADO DE VUELOS]")
        print("-" * 80)
        estado = self.controlador.gestor_vuelos.obtener_estado_vuelos()
        for v in estado:
            print(
                f"{v['id']} | {v['tipo']:10} | Estado: {v['estado']:10} | "
                f"Prioridad: {v['prioridad']} | "
                f"Combustible: {str(v['combustible']) if v['combustible'] is not None else '-':3} | "
                f"Pista: {v['pista']}"
            )

    def opcion_generar_informe(self) -> None:
        """
        Opción 8: Generar informe.log con el resumen de la simulación.
        """
        if not self._requiere_simulacion():
            return

        ruta_informe = os.path.join(self.ruta_logs, "informe.log")
        GestorInformes.generar_informe(
            tiempo_actual=self.controlador.tiempo_actual,
            vuelos=self.controlador.gestor_vuelos.vuelos_activos.values(),
            pistas=self.controlador.gestor_pistas.pistas.values(),
            ruta_informe=ruta_informe,
        )
        print(f"\n[✓] Informe generado en {ruta_informe}.")

    def opcion_mostrar_informe(self) -> None:
        """
        Opción 9: Mostrar por pantalla el informe.log si existe.
        """
        ruta_informe = os.path.join(self.ruta_logs, "informe.log")
        GestorInformes.mostrar_informe(ruta_informe)

    def opcion_guardar_y_salir(self) -> bool:
        """
        Opción 10: Finalizar simulación, guardar estado y salir.
        """
        if self.controlador is not None:
            self.controlador.finalizar_simulacion()

            ruta_backup = os.path.join(self.ruta_datos, "vuelos_backup.csv")
            self.gestor_csv.guardar_vuelos(ruta_backup, self.vuelos_cargados)
            print(f"\n[✓] Estado de vuelos guardado en {ruta_backup}.")

        print("\nSaliendo del simulador...")
        return False

    def opcion_simulacion_automatica(self) -> None:
        """
        Opción 11: Inicia la simulación automática con reloj real.
        Cada 5 segundos reales = 1 minuto simulado.
        """
        if not self._requiere_simulacion():
            return

        print("\n[SIMULACIÓN AUTOMÁTICA]")
        print("Cada 5 segundos reales = 1 minuto simulado.")
        print("Pulsa Ctrl+C en la consola para detener la simulación.\n")

        # Llama al reloj real del controlador
        self.controlador.ejecutar_con_reloj_real(segundos_por_minuto=5.0)
    def opcion_iniciar_reloj_auto(self) -> None:
        """
        Opción 11: Inicia la simulación automática en segundo plano.
        """
        if not self._requiere_simulacion():
            return

        self.controlador.iniciar_reloj_real(segundos_por_minuto=5.0)
        print("\n[✓] Reloj automático iniciado (5 s reales = 1 min simulado).")
        print("Puedes seguir usando el menú; el tiempo seguirá avanzando.")

    def opcion_detener_reloj_auto(self) -> None:
        """
        Opción 12: Detiene la simulación automática en segundo plano.
        """
        if not self._requiere_simulacion():
            return

        self.controlador.detener_reloj_real()
        print("\n[✓] Reloj automático detenido.")
    # ------------------------------------------------------------------    
    # Bucle principal
    # ------------------------------------------------------------------

    def ejecutar(self) -> None:
        """
        Bucle principal del menú.
        """
        self._banner()

        seguir = True
        while seguir:
            self._mostrar_menu()
            opcion = input("Selecciona una opción (1-10): ").strip()

            if opcion == "1":
                self.opcion_cargar_datos()
            elif opcion == "2":
                self.opcion_añadir_vuelo()
            elif opcion == "3":
                self.opcion_ver_estado_general()
            elif opcion == "4":
                self.opcion_avanzar_1_minuto()
            elif opcion == "5":
                self.opcion_avanzar_n_minutos()
            elif opcion == "6":
                self.opcion_ver_pistas()
            elif opcion == "7":
                self.opcion_ver_vuelos()
            elif opcion == "8":
                self.opcion_generar_informe()
            elif opcion == "9":
                self.opcion_mostrar_informe()
            elif opcion == "10":
                seguir = self.opcion_guardar_y_salir()
            elif opcion == "11":
                self.opcion_iniciar_reloj_auto()
            else:
                print("\n[!] Opción no válida.")

            if seguir:
                self._pausa()
