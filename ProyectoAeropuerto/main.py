#!/usr/bin/env python3
"""
SIMULADOR DE AEROPUERTO - DAM

Punto de entrada de la aplicación de consola que gestiona:
- Pistas de aterrizaje y despegue
- Vuelos (aterrizaje / despegue) con prioridades
- Reloj simulado y flujo de tráfico aéreo
- Registro de eventos en logs e informes

Requisitos del enunciado:
- Cargar datos desde vuelos.csv y pistas.csv
- Menú de consola para controlar la simulación
- Generar eventos en eventos.log e informe.log
"""

import os
import sys


def configurar_rutas_base() -> tuple[str, str]:
    """
    Calcula y devuelve las rutas base de datos y logs.

    Returns:
        (ruta_datos, ruta_logs): rutas absolutas a carpetas data/ y logs/
    """
    raiz = os.path.dirname(os.path.abspath(__file__))
    ruta_datos = os.path.join(raiz, "data")
    ruta_logs = os.path.join(raiz, "logs")

    # Asegurar que existen las carpetas necesarias
    os.makedirs(ruta_datos, exist_ok=True)
    os.makedirs(ruta_logs, exist_ok=True)

    return ruta_datos, ruta_logs


def main() -> None:
    """
    Punto de entrada principal de la aplicación.

    - Configura las rutas de datos y logs.
    - Añade el paquete src al sys.path.
    - Lanza el menú de consola.
    """
    # Añadir src al path de importación
    raiz = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(raiz, "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    # Importar aquí para evitar problemas si src no existe aún
    from interfaz_menu import MenuPrincipal  # type: ignore

    ruta_datos, ruta_logs = configurar_rutas_base()

    menu = MenuPrincipal(ruta_datos=ruta_datos, ruta_logs=ruta_logs)
    menu.ejecutar()


if __name__ == "__main__":
    main()
