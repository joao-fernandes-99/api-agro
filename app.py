from flask import Flask
from flask_restful import Api
from resources.area import Area, ProcessInformation


app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db' : 'plant'
}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)

api.add_resource(Area, '/area/<string:name_area>')
api.add_resource(ProcessInformation, '/process')



if __name__ == '__main__':
    from mon_engine import db_mon
    db_mon.init_app(app)
    app.run(debug=True)