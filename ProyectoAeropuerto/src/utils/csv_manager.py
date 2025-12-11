"""
Utilidades para lectura y escritura de CSV (vuelos y pistas).
"""

from __future__ import annotations
import csv
import os
from typing import List

from src.models import Vuelo, Pista


class GestorCSV:
    """
    Gestor estático para manejar ficheros CSV de vuelos y pistas.
    """

    # ------------------------------------------------------------------    
    # Lectura
    # ------------------------------------------------------------------

    @staticmethod
    def leer_vuelos(ruta_archivo: str) -> List[Vuelo]:
        """
        Lee vuelos desde un fichero vuelos.csv y devuelve una lista de Vuelo.

        Formato esperado (cabecera):
        id_vuelo,tipo,eta,etd,prioridad,combustible,estado
        """
        vuelos: List[Vuelo] = []

        if not os.path.exists(ruta_archivo):
            print(f"[GestorCSV] Archivo no encontrado: {ruta_archivo}")
            return vuelos

        try:
            with open(ruta_archivo, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    vuelo = Vuelo.from_dict(row)
                    vuelos.append(vuelo)
        except Exception as e:
            print(f"[GestorCSV] Error leyendo vuelos: {e}")

        return vuelos

    @staticmethod
    def leer_pistas(ruta_archivo: str) -> List[Pista]:
        """
        Lee pistas desde un fichero pistas.csv y devuelve una lista de Pista.

        Formato esperado (cabecera):
        id_pista,categoria,tiempo_uso,habilitada
        """
        pistas: List[Pista] = []

        if not os.path.exists(ruta_archivo):
            print(f"[GestorCSV] Archivo no encontrado: {ruta_archivo}")
            return pistas

        try:
            with open(ruta_archivo, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    pista = Pista.from_dict(row)
                    pistas.append(pista)
        except Exception as e:
            print(f"[GestorCSV] Error leyendo pistas: {e}")

        return pistas

    # ------------------------------------------------------------------    
    # Escritura
    # ------------------------------------------------------------------

    @staticmethod
    def guardar_vuelos(ruta_archivo: str, vuelos: List[Vuelo]) -> None:
        """
        Guarda una lista de vuelos en un CSV (por ejemplo, estado final).
        """
        try:
            with open(ruta_archivo, mode="w", newline="", encoding="utf-8") as f:
                fieldnames = [
                    "id_vuelo",
                    "tipo",
                    "eta",
                    "etd",
                    "prioridad",
                    "combustible",
                    "estado",
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for vuelo in vuelos:
                    writer.writerow(vuelo.to_dict())
        except Exception as e:
            print(f"[GestorCSV] Error guardando vuelos: {e}")

    @staticmethod
    def guardar_pistas(ruta_archivo: str, pistas: List[Pista]) -> None:
        """
        Guarda una lista de pistas en un CSV.
        """
        try:
            with open(ruta_archivo, mode="w", newline="", encoding="utf-8") as f:
                fieldnames = ["id_pista", "categoria", "tiempo_uso", "habilitada"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for pista in pistas:
                    writer.writerow(pista.to_dict())
        except Exception as e:
            print(f"[GestorCSV] Error guardando pistas: {e}")
