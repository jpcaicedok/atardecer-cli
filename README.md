# Atardecer CLI

Muestra en la terminal la salida y la puesta del sol de una ciudad o unas coordenadas. Hace el cálculo en local, sin API ni dependencias externas.

## Uso

Requiere Python 3.9 o superior. En Windows, instala también `tzdata` con `pip install tzdata`.

```bash
python atardecer.py bogota
python atardecer.py "Ciudad de México" --fecha 2026-12-21
python atardecer.py --lat 78.2 --lon 15.6 --tz Arctic/Longyearbyen
python atardecer.py --ciudades
```

Con `--lat` y `--lon`, la hora se muestra en UTC salvo que indiques `--tz`.

## Pruebas

```bash
python -m unittest
```

## Precisión

Usa las ecuaciones aproximadas de la NOAA, así que el resultado puede variar unos minutos. No tiene en cuenta la altitud ni el relieve.

## Licencia

MIT
