class Subtarea:
    def __init__(self, descripcion, bloquea=False):
        self.descripcion = descripcion
        self.bloquea = bloquea
        self.responsable = None
        self.completada = False

    def __repr__(self):
        return f"<Subtarea {self.descripcion} - Responsable: {self.responsable.nombre if self.responsable else 'Sin asignar'}>"


class Tarea:
    def __init__(self, id, titulo, tipo, cliente, urgencia, fecha_limite):
        self.id = id
        self.titulo = titulo
        self.tipo = tipo
        self.cliente = cliente
        self.urgencia = urgencia
        self.fecha_limite = fecha_limite
        self.subtareas = []  # se llenará luego con lógica de asignación

    def __repr__(self):
        return f"<Tarea {self.titulo} - Cliente: {self.cliente} - Urgencia: {self.urgencia}>"


class Usuario:
    def __init__(self, nombre, rol, carga=0, bloqueos=None):
        self.nombre = nombre
        self.rol = rol
        self.carga = carga
        self.bloqueos = bloqueos if bloqueos else []
        self.tareas_asignadas = []

    def __repr__(self):
        return f"<Usuario {self.nombre} - Rol: {self.rol} - Carga: {self.carga}>"
