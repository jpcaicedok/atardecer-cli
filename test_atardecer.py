import contextlib
import io
import json
import unittest
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from atardecer import CIUDADES, calcular_sol, formatear_duracion, main, normalizar


class PruebasSol(unittest.TestCase):
    def test_bogota_tiene_dia_de_unas_doce_horas(self):
        lat, lon, _ = CIUDADES["bogota"]
        salida, puesta = calcular_sol(date(2026, 3, 20), lat, lon)
        horas = (puesta - salida).total_seconds() / 3600
        self.assertAlmostEqual(horas, 12.1, delta=0.2)

    def test_bogota_hora_local_razonable(self):
        lat, lon, zona = CIUDADES["bogota"]
        salida, puesta = calcular_sol(date(2026, 6, 21), lat, lon)
        tz = ZoneInfo(zona)
        self.assertEqual(salida.astimezone(tz).hour, 5)
        self.assertEqual(puesta.astimezone(tz).hour, 18)

    def test_madrid_verano_mas_largo_que_invierno(self):
        lat, lon, _ = CIUDADES["madrid"]
        s1, p1 = calcular_sol(date(2026, 6, 21), lat, lon)
        s2, p2 = calcular_sol(date(2026, 12, 21), lat, lon)
        self.assertGreater(p1 - s1, p2 - s2)

    def test_dia_y_noche_polar(self):
        self.assertEqual(calcular_sol(date(2026, 6, 21), 78.2, 15.6), "dia-polar")
        self.assertEqual(calcular_sol(date(2026, 12, 21), 78.2, 15.6), "noche-polar")

    def test_coordenadas_invalidas(self):
        with self.assertRaises(ValueError):
            calcular_sol(date(2026, 1, 1), 91, 0)
        with self.assertRaises(ValueError):
            calcular_sol(date(2026, 1, 1), 0, 181)


class PruebasCLI(unittest.TestCase):
    def test_normalizar_quita_tildes_y_espacios(self):
        self.assertEqual(normalizar("Ciudad de México"), "ciudad-de-mexico")
        self.assertEqual(normalizar(" Bogotá "), "bogota")

    def test_ciudad_desconocida_devuelve_error(self):
        self.assertEqual(main(["atlantida"]), 2)

    def test_sin_lugar_devuelve_error(self):
        self.assertEqual(main([]), 2)

    def test_formatear_duracion(self):
        inicio = datetime(2026, 1, 1, 6, 0)
        self.assertEqual(formatear_duracion(inicio, inicio + timedelta(hours=12, minutes=3)), "12 h 03 min")

    def ejecutar_json(self, *argumentos):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            self.assertEqual(main([*argumentos, "--json"]), 0)
        return json.loads(salida.getvalue())

    def test_json_normal(self):
        datos = self.ejecutar_json("bogota", "--fecha", "2026-11-03")
        self.assertEqual(datos["estado"], "normal")
        self.assertEqual(datos["zona"], "America/Bogota")
        self.assertAlmostEqual(datos["duracion_minutos"], 717, delta=5)
        self.assertTrue(datos["salida"].startswith("2026-11-03T05:"))

    def test_json_dia_polar(self):
        datos = self.ejecutar_json("--lat", "78.2", "--lon", "15.6", "--fecha", "2026-06-21")
        self.assertEqual(datos["estado"], "dia-polar")
        self.assertNotIn("salida", datos)

    def test_ciudad_valida(self):
        self.assertEqual(main(["bogota", "--fecha", "2026-11-03"]), 0)


if __name__ == "__main__":
    unittest.main()
