from sql_alchemy import banco

class UserModel(banco.Model):
    __tablename__ = 'users'

    user_id = banco.Column(banco.Integer, primary_key=True)
    user_login = banco.Column(banco.String(40))
    user_senha = banco.Column(banco.String(40))

    def __init__(self, user_login, user_senha):
        self.user_login = user_login
        self.user_senha = user_senha

    def json(self):
        return{
            'user_id' : self.user_id,
            'user_login': self.user_login
        }

    @classmethod
    def find_by_login(cls, user_login):
        user = cls.query.filter_by(user_login=user_login).first()
        if user:
            return user
        return None
