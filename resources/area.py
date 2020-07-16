from flask_restful import Resource, reqparse
from models.area import area_information
import psycopg2
import pandas as pd
import statistics

path_params = reqparse.RequestParser()
path_params.add_argument('data_inicio', type=str, required=True, help="The argument 'data_inicio' is required")
path_params.add_argument('data_fim', type=str, required=True,  help="The argument 'data_fim' is required")
path_params.add_argument('area', type=str, required=True,  help="The argument 'area' is required")


class ProcessInformation(Resource):
    def get(self):
        conn = psycopg2.connect(host="localhost", database="plant", user="postgres", password="1234")
        cur = conn.cursor()

        dados = path_params.parse_args()
        tupla = tuple([dados[chave] for chave in dados])
        
        sql = 'SELECT * FROM area_information where data>= %s and CAST(data as date) <= %s and name = %s'
        cur.execute(sql,tupla)
        result = cur.fetchall()
        
        array_temperatura = []
        array_humidade = []
        array_uv = []
        array_index_temperatura = []
        array_dias = []
        for line in result:
            array_temperatura.append(line[1])
            array_humidade.append(line[2])
            array_uv.append(line[3])
            array_index_temperatura.append(str(line[4]).replace(" ","|"))
            array_dias.append(str(line[4]).split()[0])

#-----------------------------------#-------------------------------------------------#
#TRECHO DO CÓDIGO RESPONSAVEL POR AGRUPAR AS TEMPERATURAS POR DIA
        array_dias = sorted(set(array_dias))
        auxiliar_temperatura = []
        auxiliar_humidade = []
        auxiliar_uv = []
        
        array = []
        list_humidade = []
        list_uv = []

        i = 0
        j = 0

        while (i < len(array_dias)):
            while(j < len(array_index_temperatura)):
                if array_dias[i] == array_index_temperatura[j].split("|")[0]:
                    auxiliar_temperatura.append(array_temperatura[j])
                    auxiliar_humidade.append(array_humidade[j])
                    auxiliar_uv.append(array_uv[j]) 
                j+=1    
            if len(auxiliar_temperatura) != 0:        
                array.append(auxiliar_temperatura)
                list_humidade.append(auxiliar_humidade)
                list_uv.append(auxiliar_uv)

                auxiliar_temperatura = [] 
                auxiliar_humidade = []
                auxiliar_uv = []
            i = i + 1
            j = 0

        list_temperatura_dia = pd.Series(array, index=array_dias)
        list_humidade_dia = pd.Series(list_humidade, index=array_dias)
        list_uv_dia = pd.Series(list_uv, index=array_dias)


        dict_temp_media_dia = {}
        dict_humidade_media_dia = {}
        dict_uv_media_dia = {}

        for y in array_dias:
            dict_temp_media_dia[y] = statistics.mean(list_temperatura_dia[y])
            dict_humidade_media_dia [y] = statistics.mean(list_humidade_dia[y])
            dict_uv_media_dia [y] = statistics.mean(list_uv_dia[y])

        print(dict_temp_media_dia)
        print(dict_humidade_media_dia)
        print(dict_uv_media_dia)
#----------------------------#-------------------------------------------------#      
       # print(array_dias)
        #Utilizado para pegar a media da temperatura em todo o pediodo
        '''    
        temperatura = pd.Series(array_temperatura, index=array_index_temperatura)
        print("media: " + str(temperatura.mean()))
        '''
        
        '''
        lista_resultado = []
        for linha in result:
            lista_resultado.append({
                'id' : linha[0],
                'temp_ambiente' : linha[1],
                'humi_solo' : linha[2],
                'raio_uv' : linha[3],
                'data' : linha[4],
                'name' : linha[5]

            })
        '''

       
        return {'message': 'OK'}, 200

class Area(Resource):
    arguments = reqparse.RequestParser()
    arguments.add_argument('temp_ambiente', type=float, required=True, help="The Field 'temp_ambiente' is required")
    arguments.add_argument('humi_solo', type=int, required=True, help="The Field 'humi_solo' is required")
    arguments.add_argument('raio_uv', type=int, required=True, help="The Field 'raio_uv' is required")
    arguments.add_argument('data', required=True, help="The Field 'data' is required")
    arguments.add_argument('name')


    def get(self, name_area):
        area = area_information.find_area(name_area)
        if area:
            return area.json()
        return {'message': 'Are hot Found'}, 404


    def put(self, name_area):
        dados = Area.arguments.parse_args()
        area = area_information.find_area(name_area)
        if area:
            area.update_area(**dados)
            tupla = tuple([dados[chave] for chave in dados])
            conn = psycopg2.connect(host="localhost", database="plant", user="postgres", password="1234")
            cur = conn.cursor()
            print(tupla)
            cur.execute('INSERT INTO area_information(temp_ambiente, humi_solo, raio_uv, data, name) VALUES(%s,%s,%s,%s,%s);', tupla)
            conn.commit()
            conn.close()
            try:
               area.save_area()
               return {'message': 'Paremetros atualizados com sucesso!'}, 200
            except Exception as ex:
                return {'message': 'An internal error ocurred trying to update area.' + str(ex)}, 500
        return {'message':'This Area dont Exist'}, 404
