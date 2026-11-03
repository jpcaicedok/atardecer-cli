# Atardecer CLI

Muestra en la terminal la salida y la puesta del sol de una ciudad o unas coordenadas. Hace el cálculo en local, sin API ni dependencias externas.

## Uso

Requiere Python 3.9 o superior. En Windows, instala también `tzdata` con `pip install tzdata`.

```bash
python atardecer.py bogota
python atardecer.py "Ciudad de México" --fecha 2026-12-21
python atardecer.py --lat 78.2 --lon 15.6 --tz Arctic/Longyearbyen
python atardecer.py --ciudades
python atardecer.py bogota --json
```

Con `--lat` y `--lon`, la hora se muestra en UTC salvo que indiques `--tz`.

Además de las horas, el programa muestra cuánto dura el día. Con `--json`, el resultado sale listo para usarlo en scripts:

```json
{"fecha": "2026-11-03", "zona": "America/Bogota", "estado": "normal", "salida": "2026-11-03T05:41-05:00", "puesta": "2026-11-03T17:38-05:00", "duracion_minutos": 717}
```

En regiones polares, `estado` puede ser `dia-polar` o `noche-polar`, y entonces no se incluyen las horas.

## Pruebas

```bash
python -m unittest
```

## Precisión

Usa las ecuaciones aproximadas de la NOAA, así que el resultado puede variar unos minutos. No tiene en cuenta la altitud ni el relieve.

## Licencia

MIT
