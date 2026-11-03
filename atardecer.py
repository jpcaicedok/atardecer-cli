#!/usr/bin/env python3
"""Calcula la salida y la puesta del sol sin depender de ninguna API."""

import argparse
import math
import sys
import unicodedata
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

CIUDADES = {
    "bogota": (4.711, -74.072, "America/Bogota"),
    "medellin": (6.244, -75.581, "America/Bogota"),
    "cali": (3.452, -76.532, "America/Bogota"),
    "barranquilla": (10.964, -74.796, "America/Bogota"),
    "cartagena": (10.391, -75.479, "America/Bogota"),
    "lima": (-12.046, -77.043, "America/Lima"),
    "quito": (-0.180, -78.468, "America/Guayaquil"),
    "ciudad-de-mexico": (19.433, -99.133, "America/Mexico_City"),
    "buenos-aires": (-34.604, -58.382, "America/Argentina/Buenos_Aires"),
    "santiago": (-33.449, -70.669, "America/Santiago"),
    "madrid": (40.417, -3.704, "Europe/Madrid"),
}


def normalizar(nombre):
    """Convierte 'Bogotá' o 'Ciudad de México' en su clave de CIUDADES."""
    sin_tildes = unicodedata.normalize("NFKD", nombre)
    sin_tildes = "".join(c for c in sin_tildes if not unicodedata.combining(c))
    return sin_tildes.strip().lower().replace(" ", "-")


def calcular_sol(fecha, lat, lon):
    """Devuelve (salida, puesta) en UTC, o el texto 'dia-polar' / 'noche-polar'.

    Usa las ecuaciones aproximadas de la NOAA Global Monitoring Laboratory.
    """
    if not -90 <= lat <= 90:
        raise ValueError("La latitud debe estar entre -90 y 90")
    if not -180 <= lon <= 180:
        raise ValueError("La longitud debe estar entre -180 y 180")

    dia = fecha.timetuple().tm_yday
    g = 2 * math.pi / 365 * (dia - 1)
    ecuacion_tiempo = 229.18 * (
        0.000075
        + 0.001868 * math.cos(g)
        - 0.032077 * math.sin(g)
        - 0.014615 * math.cos(2 * g)
        - 0.040849 * math.sin(2 * g)
    )
    declinacion = (
        0.006918
        - 0.399912 * math.cos(g)
        + 0.070257 * math.sin(g)
        - 0.006758 * math.cos(2 * g)
        + 0.000907 * math.sin(2 * g)
        - 0.002697 * math.cos(3 * g)
        + 0.00148 * math.sin(3 * g)
    )

    phi = math.radians(lat)
    cos_ha = math.cos(math.radians(90.833)) / (
        math.cos(phi) * math.cos(declinacion)
    ) - math.tan(phi) * math.tan(declinacion)

    if cos_ha < -1:
        return "dia-polar"
    if cos_ha > 1:
        return "noche-polar"

    ha = math.degrees(math.acos(cos_ha))
    medianoche = datetime(fecha.year, fecha.month, fecha.day, tzinfo=timezone.utc)
    salida = medianoche + timedelta(minutes=720 - 4 * (lon + ha) - ecuacion_tiempo)
    puesta = medianoche + timedelta(minutes=720 - 4 * (lon - ha) - ecuacion_tiempo)
    return salida, puesta


def crear_parser():
    parser = argparse.ArgumentParser(
        description="Muestra la salida y la puesta del sol."
    )
    parser.add_argument("ciudad", nargs="?", help="por ejemplo: bogota o 'Ciudad de México'")
    parser.add_argument("--lat", type=float, help="latitud en grados")
    parser.add_argument("--lon", type=float, help="longitud en grados")
    parser.add_argument("--tz", help="zona horaria IANA, por ejemplo America/Bogota")
    parser.add_argument("--fecha", type=date.fromisoformat, help="AAAA-MM-DD (por defecto, hoy)")
    parser.add_argument("--ciudades", action="store_true", help="lista las ciudades incluidas")
    return parser


def resolver_lugar(args):
    """Devuelve (lat, lon, zona horaria) a partir de los argumentos."""
    if args.ciudad:
        clave = normalizar(args.ciudad)
        if clave not in CIUDADES:
            raise ValueError(f"Ciudad desconocida: {args.ciudad}. Usa --ciudades para ver la lista.")
        lat, lon, zona = CIUDADES[clave]
        return lat, lon, args.tz or zona
    if args.lat is None or args.lon is None:
        raise ValueError("Indica una ciudad o bien --lat y --lon.")
    return args.lat, args.lon, args.tz or "UTC"


def main(argv=None):
    parser = crear_parser()
    args = parser.parse_args(argv)

    if args.ciudades:
        print("\n".join(sorted(CIUDADES)))
        return 0

    try:
        lat, lon, zona = resolver_lugar(args)
        tz = ZoneInfo(zona)
        fecha = args.fecha or datetime.now(tz).date()
        resultado = calcular_sol(fecha, lat, lon)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    if isinstance(resultado, str):
        texto = "El sol no se pone hoy." if resultado == "dia-polar" else "El sol no sale hoy."
        print(f"{fecha}: {texto}")
        return 0

    salida, puesta = resultado
    print(f"Fecha:  {fecha} ({zona})")
    print(f"Salida: {salida.astimezone(tz):%H:%M}")
    print(f"Puesta: {puesta.astimezone(tz):%H:%M}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
