import ipaddress
import uuid

class Packet:
    def __init__(self, src_ip, dest_ip, payload, ttl=4):
        # Generamos un ID único por paquete para que los routers identifiquen duplicados
        self.id = str(uuid.uuid4())[:8]
        self.src_ip = ipaddress.IPv4Address(src_ip)
        self.dest_ip = ipaddress.IPv4Address(dest_ip)
        self.payload = payload
        self.ttl = ttl

    def __str__(self):
        return f"[ID:{self.id} | {self.src_ip} -> {self.dest_ip} | TTL:{self.ttl} | Datos: '{self.payload}']"


class Router:
    def __init__(self, name, local_subnets=None):
        self.name = name
        self.neighbors = []  # Lista de routers vecinos conectados directamente
        self.local_subnets = [ipaddress.IPv4Network(s) for s in (local_subnets or [])]
        self.seen_packets = set()  # Registro de memoria para evitar bucles e inundaciones infinitas

    def add_neighbor(self, router):
        """Conecta bidireccionalmente este router con otro."""
        if router not in self.neighbors:
            self.neighbors.append(router)
            router.neighbors.append(self)

    def flood_packet(self, packet, incoming_neighbor=None):
        """Implementación del algoritmo de Inundación (Flooding)."""

        # 1. CONTROL DE DUPLICADOS: Si ya procesamos este paquete antes, lo descartamos
        if packet.id in self.seen_packets:
            print(f"[{self.name}] 🔄 DUPLICADO IGNORADO: El paquete {packet.id} ya pasó por aquí.")
            return

        # Registrar el paquete en el historial local
        self.seen_packets.add(packet.id)
        print(f"[{self.name}] 📥 Recibido paquete: {packet}")

        # 2. VERIFICACIÓN DE DESTINO: ¿El paquete es para una de mis redes locales?
        for subnet in self.local_subnets:
            if packet.dest_ip in subnet:
                print(f"[{self.name}] ✅ ¡ÉXITO! El destino {packet.dest_ip} pertenece a mi red local ({subnet}). Paquete entregado.\n")
                return

        # 3. CONTROL DE TTL: Previene que paquetes extraviados circulen eternamente
        if packet.ttl <= 0:
            print(f"[{self.name}] ❌ TTL EXPIRADO: Paquete descartado.\n")
            return

        packet.ttl -= 1

        # 4. INUNDACIÓN (FLOODING): Copiar y enviar a TODOS los vecinos (menos al que nos lo mandó)
        targets = [n for n in self.neighbors if n != incoming_neighbor]
        print(f"[{self.name}] 🌊 INUNDANDO: Copiando paquete a {len(targets)} vecinos: {[t.name for t in targets]}")

        for neighbor in targets:
            neighbor.flood_packet(packet, incoming_neighbor=self)


# =====================================================================
# EJECUCIÓN DEL SIMULADOR
# =====================================================================
if __name__ == "__main__":
    # 1. Crear Routers y asignarles redes locales (si tienen)
    ventas = Router("Router-Ventas", local_subnets=["192.168.10.0/24"])
    core = Router("Router-Core")
    backup = Router("Router-Backup")
    it = Router("Router-IT", local_subnets=["192.168.20.0/24"])

    # 2. Crear enlaces físicos (Malla con caminos múltiples)
    ventas.add_neighbor(core)
    ventas.add_neighbor(backup)
    core.add_neighbor(it)
    backup.add_neighbor(it)

    print("=== INICIANDO INUNDACIÓN (Ventas -> IT) ===")
    
    # Enviar un paquete desde la red de Ventas hacia la red de IT
    p1 = Packet(
        src_ip="192.168.10.5", 
        dest_ip="192.168.20.100", 
        payload="Mensaje Broadcast por Inundación"
    )
    
    # Inicia la inundación desde Router-Ventas
    ventas.flood_packet(p1)