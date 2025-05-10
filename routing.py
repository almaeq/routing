#!/usr/bin/env python
# Implementación generalizada para una red WAN con 6 sucursales

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

def myNetwork():
    """
    Implementación de una red WAN con 6 sucursales
    """
    suc_count = 6  # Número fijo de sucursales
    
    net = Mininet(topo=None,
                    build=False,
                    ipBase='10.0.0.0/8')

    info('*** Adding controller\n')
    
    info('*** Add switches\n')
    
    # Crear switches WAN y LAN para cada sucursal
    wan_switches = []
    lan_switches = []
    
    for i in range(1, suc_count + 1):
        wan_sw = net.addSwitch(f's{i}wan', cls=OVSKernelSwitch, failMode='standalone')
        lan_sw = net.addSwitch(f's{i}lan', cls=OVSKernelSwitch, failMode='standalone')
        wan_switches.append(wan_sw)
        lan_switches.append(lan_sw)
    
    # Crear router central y routers de sucursales
    rc = net.addHost('rc', cls=Node, ip='0.0.0.0')
    rc.cmd('sysctl -w net.ipv4.ip_forward=1')
    
    routers = []
    for i in range(1, suc_count + 1):
        r = net.addHost(f'r{i}', cls=Node, ip='0.0.0.0')
        r.cmd('sysctl -w net.ipv4.ip_forward=1')
        routers.append(r)
    
    info('*** Add hosts\n')
    hosts = []
    for i in range(1, suc_count + 1):
        h = net.addHost(f'h{i}', cls=Host, ip=f'10.0.{i}.100/24', defaultRoute=f'via 10.0.{i}.1')
        hosts.append(h)
    
    info('*** Add links\n')
    # Conectar router central a todos los switches WAN
    for i in range(suc_count):
        net.addLink(rc, wan_switches[i])
    
    # Conectar cada router de sucursal a su switch LAN y WAN correspondiente
    for i in range(suc_count):
        net.addLink(routers[i], lan_switches[i])
        net.addLink(routers[i], wan_switches[i])
    
    # Conectar cada host a su switch LAN correspondiente
    for i in range(suc_count):
        net.addLink(hosts[i], lan_switches[i])
    
    info('*** Starting network\n')
    net.build()
    
    info('*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()
    
    info('*** Starting switches\n')
    for i in range(suc_count):
        wan_switches[i].start([])
        lan_switches[i].start([])
    
    info('*** Post configure switches and hosts\n')
    
    # Definir direcciones IP para los enlaces WAN
    # Para router de sucursal: primera IP utilizable (.1, .9, .17, .25, .33, .41)
    # Para router central: última IP utilizable (.6, .14, .22, .30, .38, .46)
    wan_ips_routers = ['192.168.100.1/29', '192.168.100.9/29', '192.168.100.17/29', 
                        '192.168.100.25/29', '192.168.100.33/29', '192.168.100.41/29']
    
    wan_ips_rc = ['192.168.100.6/29', '192.168.100.14/29', '192.168.100.22/29', 
                    '192.168.100.30/29', '192.168.100.38/29', '192.168.100.46/29']
    
    # Configurar direcciones IP
    info('*** Address/ando-arrancando\n')
    
    # Configurar IPs en interfaces de router central (RC)
    for i in range(suc_count):
        rc.cmd(f'ip a a {wan_ips_rc[i]} dev rc-eth{i}')
    
    # Configurar IPs en interfaces de routers de sucursales
    for i in range(suc_count):
        routers[i].cmd(f'ip a a 10.0.{i+1}.1/24 dev r{i+1}-eth0')
        routers[i].cmd(f'ip a a {wan_ips_routers[i]} dev r{i+1}-eth1')
    
    # Configuración de rutas
    info('*** Rute/ando-ando\n')
    
    # Extraer sólo la IP (sin la máscara) para usar en las rutas
    def strip_mask(ip_with_mask):
        return ip_with_mask.split('/')[0]
    
    # Configurar rutas en routers de sucursales
    for i in range(suc_count):
        # Ruta para alcanzar todas las redes 10.0.0.0/21 y 192.168.100.0/26 a través del router central
        rc_ip = strip_mask(wan_ips_rc[i])
        routers[i].cmd(f'ip r a 10.0.0.0/21 via {rc_ip}')
        routers[i].cmd(f'ip r a 192.168.100.0/26 via {rc_ip}')
    
    # Configurar rutas en router central
    for i in range(suc_count):
        # Ruta para alcanzar cada red LAN de sucursal a través del router correspondiente
        router_ip = strip_mask(wan_ips_routers[i])
        rc.cmd(f'ip r a 10.0.{i+1}.0/24 via {router_ip}')
    
    # Pruebas de conectividad
    info('*** Testing connectivity between hosts\n')
    
    # Probar ping desde h1 a todos los demás hosts
    for i in range(1, suc_count):
        output = hosts[0].cmd(f'ping -W0.5 -qc1 10.0.{i+1}.100 && echo ==PASS== || echo ==FAIL==')
        info(f'Ping from h1 to h{i+1}: {output}')
    
    # Mostrar tablas de enrutamiento
    info('*** Router Central (RC) Routing Table:\n')
    info(rc.cmd('route -n'))
    
    info('*** Router R1 Routing Table:\n')
    info(routers[0].cmd('route -n'))
    
    # Imprimir un resumen del direccionamiento
    info('\n*** Network Addressing Summary ***\n')
    info('Router Central (RC):\n')
    for i in range(suc_count):
        info(f'  Interface rc-eth{i}: {wan_ips_rc[i]}\n')
    
    info('\nBranch Routers:\n')
    for i in range(suc_count):
        info(f'  R{i+1} WAN Interface: {wan_ips_routers[i]}\n')
        info(f'  R{i+1} LAN Interface: 10.0.{i+1}.1/24\n')
    
    info('\nHosts:\n')
    for i in range(suc_count):
        info(f'  H{i+1}: 10.0.{i+1}.100/24 (Gateway: 10.0.{i+1}.1)\n')
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    myNetwork() 