import ipaddress

class Router:
    def __init__(self, name, local_subnet=None):
        self.name = name
        self.neighbors = []
        # Tabla de rutas: {Red: {'cost': saltos, 'next_hop': Router}}
        self.routing_table = {}
        
        if local_subnet:
            net = ipaddress.IPv4Network(local_subnet)
            self.routing_table[net] = {'cost': 0, 'next_hop': None}

    def connect(self, other_router):
        """Crea un enlace físico bidireccional entre routers."""
        if other_router not in self.neighbors:
            self.neighbors.append(other_router)
            other_router.neighbors.append(self)

    def send_updates_split_horizon(self):
        """Difunde la tabla de rutas a cada vecino aplicando Split Horizon."""
        for neighbor in self.neighbors:
            update_vector = {}
            
            for net, route in self.routing_table.items():
                # --- REGLA DE SPLIT HORIZON ---
                # Si aprendí a llegar a 'net' a través de ESTE 'neighbor',
                # OMITO la red en el reporte que le envío a él.
                if route['next_hop'] == neighbor:
                    continue
                
                update_vector[net] = route['cost']

            # Enviar el reporte filtrado al vecino
            neighbor.receive_update(from_router=self, vector=update_vector)

    def receive_update(self, from_router, vector):
        """Procesa el reporte de un vecino e incrementa la métrica de saltos."""
        for net, cost in vector.items():
            new_cost = cost + 1
            
            # Si descubrimos una red nueva o un camino con menor costo
            if net not in self.routing_table or new_cost < self.routing_table[net]['cost']:
                self.routing_table[net] = {'cost': new_cost, 'next_hop': from_router}
                print(f"  [{self.name}] ➔ Aprendió ruta hacia {net} vía [{from_router.name}] (Costo: {new_cost} saltos)")

    def route_packet(self, dest_ip, payload):
        """Una vez construida la tabla, enruta paquetes de datos."""
        dest = ipaddress.IPv4Address(dest_ip)
        best_route = None
        
        for net, route in self.routing_table.items():
            if dest in net:
                best_route = route
                break

        if best_route:
            next_hop = best_route['next_hop']
            if next_hop is None:
                print(f"[{self.name}] ✅ Entregado localmente en {dest_ip}.")
            else:
                print(f"[{self.name}] 🔀 Reenviando paquete a [{next_hop.name}] para alcanzar {dest_ip}")
                next_hop.route_packet(dest_ip, payload)
        else:
            print(f"[{self.name}] ❌ Sin ruta hacia {dest_ip}.")


# =====================================================================
# TOPOLOGÍA EN MALLA
# =====================================================================
#                  +---> [Router-Core] ---+
#                  |                      |
# [Router-Ventas] --+                      +---> [Router-IT]
#                  |                      |
#                  +---> [Router-Backup] -+

if __name__ == "__main__":
    # 1. Crear Routers y asignar subredes de origen
    ventas = Router("Router-Ventas", local_subnet="192.168.10.0/24")
    core = Router("Router-Core")
    backup = Router("Router-Backup")
    it = Router("Router-IT", local_subnet="192.168.20.0/24")

    # 2. Conectar enlaces en malla
    ventas.connect(core)
    ventas.connect(backup)
    core.connect(it)
    backup.connect(it)

    print("=== PASO 1: Descubrimiento de Rutas con Split Horizon ===")
    
    # Simular 2 rondas de actualización de tablas
    for ronda in range(1, 3):
        print(f"\n--- Ronda {ronda} ---")
        ventas.send_updates_split_horizon()
        core.send_updates_split_horizon()
        backup.send_updates_split_horizon()
        it.send_updates_split_horizon()

    print("\n=== PASO 2: Enrutamiento de un Paquete de Datos ===")
    # Ahora que las tablas se armaron sin bucles, enviamos tráfico normal
    ventas.route_packet("192.168.20.100", "Datos de prueba")