import ipaddress

class Packet:
    def __init__(self, src_ip, dest_ip, payload, ttl=5):
        self.src_ip = ipaddress.IPv4Address(src_ip)
        self.dest_ip = ipaddress.IPv4Address(dest_ip)
        self.payload = payload
        self.ttl = ttl  # Time to Live: evita bucles infinitos en la red

    def __str__(self):
        return f"[Paquete: {self.src_ip} -> {self.dest_ip} | TTL: {self.ttl} | Datos: '{self.payload}']"


class Router:
    def __init__(self, name):
        self.name = name
        self.routing_table = []

    def add_route(self, dest_subnet, next_router=None, description="Entrega Directa"):
        """Añade una ruta estática a la tabla de enrutamiento."""
        network = ipaddress.IPv4Network(dest_subnet)
        self.routing_table.append({
            'network': network,
            'next_router': next_router,
            'description': description
        })

    def route_packet(self, packet):
        """Procesa y reenvía el paquete al siguiente router en la cadena."""
        print(f"[{self.name}] Recibido: {packet}")

        # 1. Validar Time to Live (TTL)
        if packet.ttl <= 0:
            print(f"[{self.name}] ERROR: TTL expirado. Paquete descartado.")
            return

        packet.ttl -= 1
        best_match = None
        max_prefix_len = -1
        selected_route = None

        # 2. Algoritmo Longest Prefix Match (Coincidencia de prefijo más largo)
        for route in self.routing_table:
            if packet.dest_ip in route['network']:
                if route['network'].prefixlen > max_prefix_len:
                    max_prefix_len = route['network'].prefixlen
                    best_match = route['network']
                    selected_route = route

        # 3. Decisión de Reenvío
        if selected_route:
            next_router = selected_route['next_router']
            if next_router is None:
                # El destino está en la red local de este router
                print(f"[{self.name}] ÉXITO: Destino en red local ({best_match}). Paquete entregado a {packet.dest_ip}.\n")
            else:
                # El paquete debe saltar al siguiente router
                print(f"[{self.name}] REENVIANDO: Coincidencia con {best_match} -> Salto hacia [{next_router.name}]")
                next_router.route_packet(packet)
        else:
            print(f"[{self.name}] ERROR: Sin ruta hacia {packet.dest_ip}. Paquete descartado.\n")


# =====================================================================
# CONSTRUCCIÓN DE LA RED Y TABLAS DE ENRUTAMIENTO
# =====================================================================
if __name__ == "__main__":
    # 1. Instanciar Routers
    core = Router("Router-Core")
    ventas = Router("Router-Ventas")
    it = Router("Router-IT")
    sucursal = Router("Router-Sucursal")
    isp = Router("Router-ISP")

    # 2. Configurar Tablas de Enrutamiento

    # --- Router Core ---
    core.add_route("192.168.10.0/24", next_router=ventas)
    core.add_route("192.168.20.0/24", next_router=it)
    core.add_route("10.1.0.0/16", next_router=sucursal)
    core.add_route("0.0.0.0/0", next_router=isp, description="Ruta por Defecto")

    # --- Router Ventas ---
    ventas.add_route("192.168.10.0/24", next_router=None)  # Red local
    ventas.add_route("0.0.0.0/0", next_router=core, description="Default Gateway")

    # --- Router IT ---
    it.add_route("192.168.20.0/24", next_router=None)  # Red local
    it.add_route("0.0.0.0/0", next_router=core, description="Default Gateway")

    # --- Router Sucursal ---
    sucursal.add_route("10.1.0.0/16", next_router=None)  # Red local
    sucursal.add_route("0.0.0.0/0", next_router=core, description="Default Gateway")

    # --- Router ISP ---
    isp.add_route("0.0.0.0/0", next_router=None, description="Internet")


    # =====================================================================
    # PRUEBAS DE TRÁFICO
    # =====================================================================
    print("=== PRUEBA 1: Tráfico Inter-Departamento (Ventas -> IT) ===")
    p1 = Packet(src_ip="192.168.10.15", dest_ip="192.168.20.50", payload="Reporte Financiero")
    ventas.route_packet(p1)

    print("=== PRUEBA 2: Tráfico a Sede Remota (IT -> Sucursal) ===")
    p2 = Packet(src_ip="192.168.20.5", dest_ip="10.1.45.12", payload="Actualización Servidor")
    it.route_packet(p2)

    print("=== PRUEBA 3: Tráfico a Internet (Ventas -> Web Externa) ===")
    p3 = Packet(src_ip="192.168.10.15", dest_ip="8.8.8.8", payload="Consulta DNS")
    ventas.route_packet(p3)