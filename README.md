# OpenMeteo

## Prueba técnica: Open-Meteo Weather

---

## Instalación Básica

`pip install -r requirementsBasics.txt`

### Arrancar

`python backend/main.py --reload`

Si no funciona por librerias probar la instalación avanzada

## Instalación Avanzada

`pip install -r requirementsFull.txt`

### Arrancar

`python backend/main.py --reload`

---

# Uso de la api

```
Entrar en 127.0.0.1:8000 abrir el weather_data y hacer el post de load_weather con su ciudad y fechas correspondientes para que se guarde en la BD Local.

Una vez guardada esa consulta en la BD Local los demas métodos funcionaran consultando la BD.

Se pueden añadir mas datos volviendo a lanzar el post de load_weather con su ciudad y fechas correspondientes.

Mediante load_weather podemos consultar todos los datos guardados de una ciudad con los cuales interacturan los endpoint de los stats.
```
