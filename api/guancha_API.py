from flask import Flask
from flask import Blueprint
from api.configuration.config import config
from flask_sqlalchemy import SQLAlchemy
from api.resource.official import official_bp
from flasgger import Swagger

app = Flask(__name__)


app.config.from_object(config['develop_config'])
config['develop_config'].init_app(app)
#app.config['JSON_AS_ASCII'] = False


app.register_blueprint(official_bp)

swagger = Swagger(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
