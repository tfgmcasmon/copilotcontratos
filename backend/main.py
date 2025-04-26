from flask import Flask
from flask_cors import CORS

# Importar Blueprints
from api.autocomplete_routes import autocomplete_bp
from api.verification_routes import data_verification_bp
from api.chatlegal_routes import chatlegal_bp
from api.healthcheck import healthcheck_bp
from gestor_tareas.router import gestor_tareas_bp  
from api.legalchat_routes import legalchat_bp
from api.contract_context_routes import contract_context_bp
from api.legal_verifier_routes import legalcheck_bp

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

    # Registrar blueprints
    app.register_blueprint(autocomplete_bp)
    app.register_blueprint(data_verification_bp)
    #app.register_blueprint(chatlegal_bp)
    app.register_blueprint(healthcheck_bp)
    app.register_blueprint(gestor_tareas_bp, url_prefix="/gestor_tareas")
    app.register_blueprint(legalchat_bp)
    app.register_blueprint(contract_context_bp)
    app.register_blueprint(legalcheck_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    print("Servidor Flask corriendo en http://127.0.0.1:8080")
    app.run(host="127.0.0.1", port=8080, debug=True)
