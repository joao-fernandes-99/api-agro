#Importação de bibliotecas para o funcionamento da api
from flask import Flask, jsonify
from flask_restful import Api
from resources.area import Area, ProcessInformation
from resources.users import UserLogin, UserLogout
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from blacklist import BLACKLIST

app = Flask(__name__)
#Condigurações iniciais do banco de dados MONGODB
app.config['MONGODB_SETTINGS'] = {
    'db' : 'plant'
}

#Configurações iniciais do banco de dados Postgress
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres+psycopg2://postgres:1234@localhost/plant'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#configurações iniciais do JWT
app.config['JWT_SECRET_KEY'] = 'DontTellAnyone'
app.config['JWT_BLACKLIST_ENABLED'] = True
#iniciando o cors
CORS(app)
#iniciando a api
api = Api(app)
#iniciando o JWT
jwt = JWTManager(app)

@jwt.token_in_blacklist_loader
def verifica_blacklist(token):
    return token['jti'] in BLACKLIST

@jwt.revoked_token_loader
def token_de_acesso_invalidado():
    return jsonify({'Message' : 'You have benn Logged out.'}), 401

#End Points Configurados
api.add_resource(Area, '/area/<string:name_area>')
api.add_resource(ProcessInformation, '/process')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')


if __name__ == '__main__':
    from mon_engine import db_mon
    from sql_alchemy import banco
    banco.init_app(app)
    db_mon.init_app(app)
    app.run(debug=True, host="192.168.1.105", port=5000)