# Routing

## Descripción
Este proyecto implementa un sistema de enrutamiento para gestionar y optimizar rutas de manera eficiente.

## Características
- Sistema de enrutamiento inteligente
- Optimización de rutas
- Gestión de nodos y conexiones
- Visualización de rutas

## Requisitos
- Python 3.8 o superior
- Instalar mininet en la computadora donde se quiera usar el proyecto
- Dependencias listadas en `requirements.txt`

## Instalación
1. Clonar el repositorio:
```bash
git clone git@github.com:almaeq/routing.git
cd routing
```

2. Crear un entorno virtual (opcional pero recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
.\venv\Scripts\activate  # En Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso
El sistema implementa una red WAN con 6 sucursales utilizando Mininet. Para ejecutar el sistema:

1. Asegúrate de tener los permisos necesarios:
```bash
sudo chmod +x routing.py
```

2. Ejecuta el script principal:
```bash
sudo python routing.py
```

### Estructura de la Red
El sistema crea una red con las siguientes características:
- 1 Router Central (RC)
- 6 Routers de Sucursal (R1-R6)
- 6 Switches WAN (s1wan-s6wan)
- 6 Switches LAN (s1lan-s6lan)
- 6 Hosts (h1-h6)

#### Diagrama de la Red
![Diagrama del Router Central](Router%20central.jpg)

### Direccionamiento IP
- Redes LAN: 10.0.1.0/24 a 10.0.6.0/24
- Red WAN: 192.168.100.0/26
- Hosts: 10.0.X.100/24 (donde X es el número de sucursal)
- Gateways: 10.0.X.1/24

### Comandos Disponibles
Una vez que la red esté en funcionamiento, puedes usar los siguientes comandos en la CLI de Mininet:

1. Verificar conectividad entre hosts:
```bash
h1 ping h2
h1 ping h3
# etc...
```

2. Ver tablas de enrutamiento:
```bash
r1 route -n
rc route -n
```

3. Ver interfaces y direcciones IP:
```bash
r1 ip a
rc ip a
```

4. Probar conectividad entre sucursales:
```bash
h1 ping 10.0.2.100  # Ping desde sucursal 1 a sucursal 2
h1 ping 10.0.3.100  # Ping desde sucursal 1 a sucursal 3
```

### Salir del Sistema
Para detener la red y salir de la CLI de Mininet:
```bash
exit
```

### Notas Importantes
- El sistema requiere permisos de superusuario (sudo) para ejecutarse
- Se recomienda ejecutar en un entorno Linux
- La red se configura automáticamente al iniciar
- Las pruebas de conectividad se ejecutan automáticamente al inicio
