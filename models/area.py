from mon_engine import db_mon
from datasets.classification import prever
import numpy as np

class area_information(db_mon.DynamicDocument):
   
    temp_ambiente = db_mon.FloatField()
    humi_solo = db_mon.FloatField()
    raio_uv = db_mon.IntField()
    data = db_mon.StringField()
    name = db_mon.StringField()

    def json(self):
        condicao = prever(np.array([[self.temp_ambiente,self.temp_ambiente,self.humi_solo,self.humi_solo,self.raio_uv,self.raio_uv]]))
        return {
            
            'temp_ambiente' : self.temp_ambiente,
            'humi_solo' : self.humi_solo,
            'raio_uv' : self.raio_uv,
            'data' : self.data,
            'name': self.name,
            'condicao': condicao.replace("'","").replace("[","").replace("]","")
        }
    
    @classmethod
    def find_area(cls, name):
        area = cls.objects(name=name).first()
        if area:
            return area
        return None 

    def update_area(self, temp_ambiente, humi_solo, raio_uv, data, name):
        self.temp_ambiente = temp_ambiente
        self.humi_solo = humi_solo
        self.raio_uv = raio_uv
        self.data = data

    
    def save_area(self):
        self.save()
        


