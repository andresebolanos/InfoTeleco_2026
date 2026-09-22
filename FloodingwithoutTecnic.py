import sys

# Reducimos el límite de recursión de Python para capturar el error rápidamente
sys.setrecursionlimit(60)

class BrokenRouter:
    def __init__(self, name):
        self.name = name
        self.neighbors = []

    def add_neighbor(self, router):
        if router not in self.neighbors:
            self.neighbors.append(router)
            router.neighbors.append(self)

    def flood_uncontrolled(self, packet_data):
        print(f"[{self.name}] 🌊 Reenviando paquete '{packet_data}' a {len(self.neighbors)} vecinos...")
        
        # SIN TTL, SIN HISTORIAL DE PAQUETES, SIN FILTRAR ORIGEN
        for neighbor in self.neighbors:
            neighbor.flood_uncontrolled(packet_data)


if __name__ == "__main__":
    # Creamos un ciclo cerrado (Anillo/Triángulo): A -> B -> C -> A
    router_a = BrokenRouter("Router-A")
    router_b = BrokenRouter("Router-B")
    router_c = BrokenRouter("Router-C")

    router_a.add_neighbor(router_b)
    router_b.add_neighbor(router_c)
    router_c.add_neighbor(router_a)

    print("=== INICIANDO INUNDACIÓN SIN CONTROL (Provocando Bucle) ===")
    try:
        router_a.flood_uncontrolled("Datos Críticos")
    except RecursionError:
        print("\n💥 ¡COLAPSO DE LA RED! (RecursionError)")
        print("Explicación: El paquete quedó atrapado girando infinitamente en el ciclo A -> B -> C -> A.")