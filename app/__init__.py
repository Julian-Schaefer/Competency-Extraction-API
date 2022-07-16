import imp
from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint
from app.routes import routes

app = Flask(__name__, static_folder="../docs", static_url_path="/docs")
app.register_blueprint(routes)

SWAGGER_URL = "/api/docs"  # URL for exposing Swagger UI (without trailing '/')
API_DEFINITION_FILE = "../../docs/api_spec_swagger.yml"  # Our API Definition

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_DEFINITION_FILE,
)

app.register_blueprint(swaggerui_blueprint)
