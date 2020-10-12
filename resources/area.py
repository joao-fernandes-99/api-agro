from flask_restful import Resource, reqparse
from models.area import area_information
from datasets.classification import prever
from datetime import date
import numpy as np
import psycopg2
import pandas as pd
import statistics
import json

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
        dict_condicao_dia = {}

        for y in array_dias:
            dict_temp_media_dia[y] = str(statistics.mean(list_temperatura_dia[y]))
            dict_humidade_media_dia[y] = str(statistics.mean(list_humidade_dia[y]))
            dict_uv_media_dia[y] = str(statistics.mean(list_uv_dia[y]))
            dict_condicao_dia[y] = prever(np.array([[min(list_temperatura_dia[y]), max(list_temperatura_dia[y]),
                                            min(list_humidade_dia[y]), max(list_humidade_dia[y]),
                                            min(list_uv_dia[y]), max(list_uv_dia[y])]])).replace("'","").replace("[","").replace("]","")
            
            
       
        periodo_temperatura = pd.Series(array_temperatura, index=array_index_temperatura)
        periodo_humidade = pd.Series(array_humidade, index=array_index_temperatura)
        periodo_uv = pd.Series(array_uv, index=array_index_temperatura)

        response = {}
        response['media_temp_dia'] = dict_temp_media_dia
        response['media_humi_dia'] = dict_humidade_media_dia
        response['media_uv_dia'] =  dict_uv_media_dia
        response['condicao_dia'] = dict_condicao_dia
        response['media_temp_periodo'] = str(periodo_temperatura.mean())
        response['media_humi_periodo'] = str(periodo_humidade.mean())
        response['media_uv_periodo'] = str(periodo_uv.mean())
        
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
        return {'response': response}

class Area(Resource):
    arguments = reqparse.RequestParser()
    arguments.add_argument('temp_ambiente', type=float, required=True, help="The Field 'temp_ambiente' is required")
    arguments.add_argument('humi_solo', type=float, required=True, help="The Field 'humi_solo' is required")
    arguments.add_argument('raio_uv', type=int, required=True, help="The Field 'raio_uv' is required")
    arguments.add_argument('data', required=False, help="The Field 'data' is required")
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
            dados['data'] = str(date.today())
            print(dados['data'])
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
