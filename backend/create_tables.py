from basedatos import engine, Base
from models.task import Task
from models.client import Client
from models.alert import Alert
from models.suggestion import Suggestion
from models.user import User

print("Creando tablas...")
Base.metadata.create_all(bind=engine)
print("Tablas creadas correctamente.")
