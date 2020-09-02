from flask_restful import Resource, reqparse
from models.users import UserModel
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import create_access_token, jwt_required, get_raw_jwt
from blacklist import BLACKLIST

atributos = reqparse.RequestParser()
atributos.add_argument('user_login', type=str, required=True, help="The field 'login' cannot be left blank")
atributos.add_argument('user_senha', type=str, required=True, help="The Field 'senha' cannot be left blank")

class UserLogin(Resource):

    @classmethod
    def post(cls):
        #1° captura os parametros passados
        dados = atributos.parse_args()

        #2° realiza a busca no banco postress utilizado o USER_LOGIN como parametro
        user = UserModel.find_by_login(dados['user_login'])

        #3° Realiza a validação dos dados informados
        if user and safe_str_cmp(user.user_senha, dados['user_senha']):
            #4 caso seja encontrado é criado um token do tipo JWT para o usuario
            token_de_acesso = create_access_token(identity=user.user_id)
            #5 é retornado o token de acesso
            return {'acess_token': token_de_acesso}, 200
        return {'Message': 'The username or password is incorrect'}, 401
        
class UserLogout(Resource):

    @jwt_required
    def post(self):
        jwt_id = get_raw_jwt()['jti']
        BLACKLIST.add(jwt_id)
        return {'message': 'Logged Out Successfully'}, 200


