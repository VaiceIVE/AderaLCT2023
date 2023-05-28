from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from mongoService import Save, Get, Getall, Delete
from docConvertor import create_xls, create_csv 
from fastapi.responses import StreamingResponse
from IResult import IResult
from ICriteria import ICriteria
from catboost import CatBoostClassifier
import requests
from tempfile import NamedTemporaryFile
import pandas as pd
from datetime import date
from pullenti_wrapper.langs import (
    set_langs,
    RU
)
set_langs([RU])
from pullenti_wrapper.processor import (
    Processor,
    GEO,
    ADDRESS
)
from pullenti_wrapper.referent import Referent
addr = []
def display_shortcuts(referent, level=0):
    tmp = {}
    a = ""
    b = ""
    for key in referent.__shortcuts__:
        value = getattr(referent, key)
        if value in (None, 0, -1):
            continue
        if isinstance(value, Referent):
            display_shortcuts(value, level + 1)
        else:
            if key == 'type':
                a = value 
            if key == 'name':
                b = value
                # print('ok', value)
            if key == 'house':
                a = "дом"
                b = value
                tmp[a] = b
            if key == 'flat':
                a = "квартира"
                b = value
                # print('ok', value)
                tmp[a] = b
            if key == 'corpus':
                    a = "корпус"
                    b = value
                    tmp[a] = b
    tmp[a] = b
    addr.append(tmp)



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=
    [
        "http://127.0.0.1:5173",
        "http://178.170.192.87:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get('/base')
def analyze_basic():

    model = CatBoostClassifier()

    model.load_model('./model/catboost_model2t.bin')

    with NamedTemporaryFile() as tmp:
        data = requests.get('http://178.170.192.87:8004/permanent/normalized_data.csv')

        open(tmp.name, 'wb').write(data.content)

        input_data = pd.read_csv(tmp.name, encoding='utf8')

        print(input_data)

        input_data = input_data.drop("Unnamed: 0", axis=1)

        result = model.predict(input_data)

        print(result)

        result = pd.concat([pd.DataFrame(result), input_data], axis=1)

    issues_data = []

    print(result.info())

    for index, row in result.iterrows():
        issues_data.append({'adress': row['Адрес'], 'workname': [row[0]]})

    analysis_result = {'result': issues_data, 'type': 'base', 'criterias': [''], 'date': str(date.today()).replace('-', '.')}

    print(analysis_result)
    """
    mock_result = {'result': [
        {'adress': 'улица Красковская, дом 121А', 'workname': ['Ремонт освещения', 'Сбивание сосулек'],"stats": {"Год постройки МКД": 1950, "Район": "Измайлово"}, "priority": "Срочная работа"},
        {'adress': 'улица Владимирская, дом 12', 'workname': ['Замена лестницы', 'Замена крыльца'],  "stats": {"Год постройки МКД": 1960, "Район": "Внуково"},"priority": "Плановая работа"},
        {'adress': 'улица Кусковская, дом 1', 'workname': ['Замена крыльца', 'Ремонт освещения'],  "stats": {"Год постройки МКД": 1970, "Район": "Сколково"},"priority": "Плановая работа"},
        {'adress': 'улица Бойцовая, дом 11', 'workname': ['Сбивание сосулек', 'Замена лестницы'],  "stats": {"Год постройки МКД": 1980, "Район": "Мытищи"},"priority": "Срочная работа"}
    ], 'type': 'base', 'criterias': ['МКД', 'Капитальный ремонт'], 'date': '03.08.2003'}

    
    id = Save(mock_result)
    return {'result': [
        {'adress': 'улица Красковская, дом 121А', 'workname': ['Ремонт освещения', 'Сбивание сосулек'],"stats": {"Год постройки МКД": 1950, "Район": "Измайлово"}, "priority": "Срочная работа"},
        {'adress': 'улица Владимирская, дом 12', 'workname': ['Замена лестницы', 'Замена крыльца'],  "stats": {"Год постройки МКД": 1960, "Район": "Внуково"},"priority": "Плановая работа"},
        {'adress': 'улица Кусковская, дом 1', 'workname': ['Замена крыльца', 'Ремонт освещения'],  "stats": {"Год постройки МКД": 1970, "Район": "Сколково"},"priority": "Плановая работа"},
        {'adress': 'улица Бойцовая, дом 11', 'workname': ['Сбивание сосулек', 'Замена лестницы'],  "stats": {"Год постройки МКД": 1980, "Район": "Мытищи"},"priority": "Срочная работа"}
    ], 'type': 'base', '_id' : id}
    """
    return analysis_result



@app.get('/worktypes')
def get_worktypes():
    return ['Капитальный ремонт']

@app.get('/objcategories')
def get_object_categories():
    return ['Многоквартирный дом']

@app.get('/xlsbyid/{id}/{name}')
def get_xls_report_by_analysis_id(id, name):
    result = Get(id)
    if result == False:
        return "No such item"
    return StreamingResponse(create_xls(result), headers={'Content-Disposition': f'attachment; filename="{name}.xls"'.encode('utf-8').decode('unicode-escape')}, media_type="application/vnd.ms-excel")

@app.get('/xlsxbyid/{id}/{name}')
def get_xlsx_report_by_analysis_id(id, name):
    result = Get(id)
    if result == False:
        return "No such item"
    return StreamingResponse(create_xls(result), headers={'Content-Disposition': f'attachment; filename="{name}.xlsx"'.encode('utf-8').decode('unicode-escape')}, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.get('/csvbyid/{id}/{name}')
def get_xlsx_report_by_analysis_id(id, name):
    result = Get(id)

    return StreamingResponse(create_csv(result), headers={'Content-Disposition': f'attachment; filename="{name}.csv"'.encode('utf-8').decode('unicode-escape')}, media_type="application/vnd.ms-excel")

@app.get('/history')
def get_history():
    results = Getall()

    print(results)
    response = list()

    for result in results:
        response.append({"type": result['type'], "date": result['date'], "criterias": result['criterias'], 'id': str(result['_id']) })

    return response

@app.get('/analyze/{id}')
def get_analyze_by_id(id):
    
    result = Get(id)

    return result

@app.post('/analyze/update')
def update_analysis_data(result: IResult):
    Delete(result.id)
    id = Save(result.ToDict())
    return id

@app.post('/advanced')
def update_analysis_data(criterias: ICriteria):
    objtype = criterias.obj
    worktype = criterias.work
    dates = criterias.date


    mock_result = {'result': [
        {'adress': 'улица Красковская, дом 121А', 'workname': ['Ремонт освещения', 'Сбивание сосулек'],"stats": {"Год постройки МКД": 1950, "Район": "Измайлово"}, "priority": "Срочная работа"},
        {'adress': 'улица Владимирская, дом 12', 'workname': ['Замена лестницы', 'Замена крыльца'],  "stats": {"Год постройки МКД": 1960, "Район": "Внуково"},"priority": "Плановая работа"},
        {'adress': 'улица Кусковская, дом 1', 'workname': ['Замена крыльца', 'Ремонт освещения'],  "stats": {"Год постройки МКД": 1970, "Район": "Сколково"},"priority": "Плановая работа"},
        {'adress': 'улица Бойцовая, дом 11', 'workname': ['Сбивание сосулек', 'Замена лестницы'],  "stats": {"Год постройки МКД": 1980, "Район": "Мытищи"},"priority": "Срочная работа"}
    ], 'type': 'criterizedDB', 'criterias': [objtype, worktype, dates], 'date': '03.08.2003'}

    
    id = Save(mock_result)
    return {'result': [
        {'adress': 'улица Красковская, дом 121А', 'workname': ['Ремонт освещения', 'Сбивание сосулек'],"stats": {"Год постройки МКД": 1950, "Район": "Измайлово"}, "priority": "Срочная работа"},
        {'adress': 'улица Владимирская, дом 12', 'workname': ['Замена лестницы', 'Замена крыльца'],  "stats": {"Год постройки МКД": 1960, "Район": "Внуково"},"priority": "Плановая работа"},
        {'adress': 'улица Кусковская, дом 1', 'workname': ['Замена крыльца', 'Ремонт освещения'],  "stats": {"Год постройки МКД": 1970, "Район": "Сколково"},"priority": "Плановая работа"},
        {'adress': 'улица Бойцовая, дом 11', 'workname': ['Сбивание сосулек', 'Замена лестницы'],  "stats": {"Год постройки МКД": 1980, "Район": "Мытищи"},"priority": "Срочная работа"}
    ], 'type': 'criterizedDB', 'criterias': [objtype, worktype, dates], 'date': '03.08.2003', "_id": id}

@app.get('/updatedata')
def update_houses_data():
    processor = Processor([GEO, ADDRESS])
    houses_data = pd.read_excel('Storage/houses.xlsx')
    houses_data.info()
    houses_data = houses_data[houses_data.NAME != None]
    houses_data.info()    
    testset = houses_data.head(10)
    print(testset)
    for text in testset.loc[:, "NAME"]:
        result = processor(str(text))
        if result.matches:
            referent = result.matches[0].referent
            display_shortcuts(referent)
            print(addr)
        addr.clear()
    return 0
    
    