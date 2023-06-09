from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from mongoService import Save, Get, Getall, Delete
from docConvertor import create_xls, create_csv 
from fastapi.responses import StreamingResponse
from IResult import IResult
from ICriteria import ICriteria, ICriteriaURL
from catboost import CatBoostClassifier
import requests
from tempfile import NamedTemporaryFile
import pandas as pd
from datetime import date
import json
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

    worksdict = dict()
    with open('issuestoworks.json') as json_file:
        worksdict = json.load(json_file)

    roofs_dict = pd.read_excel('Storage/roofs.xlsx')

    materials_dict = pd.read_excel('Storage/materials.xlsx')

    processor = Processor([GEO, ADDRESS])

    model = CatBoostClassifier()

    model.load_model('./model/catboost_model2t.bin')

    secondmodel = CatBoostClassifier()

    secondmodel.load_model('./model/catboost_model3t.bin')
    
    with NamedTemporaryFile() as tmp:
        data = requests.get('http://178.170.192.87:8004/permanent/normalized_data.csv')

        open(tmp.name, 'wb').write(data.content)

        input_data = pd.read_csv(tmp.name, encoding='utf8')

        print(input_data)
        pretty_addresses = []
        input_data = input_data.drop("Unnamed: 0", axis=1)
        banlist = []
        addresses = input_data.iloc[:, 2]
        for index, text in enumerate(addresses):
            result = processor(str(text))
            if result.matches:
                referent = result.matches[0].referent
                display_shortcuts(referent)
                if len(addr) < 2:
                    banlist.append(index)
                elif 'улица' not in addr[0].keys() or 'дом' not in addr[-1].keys():
                    banlist.append(index)
                else:
                    pretty_addresses.append(addr[0]['улица'].title() + ' ' + addr[-1]['дом'])
                    #print(addr)
            addr.clear()
        #print(banlist)

        input_data = input_data.drop(banlist)

        result = model.predict(input_data)

        #print(result.shape)

        result = pd.DataFrame(data=result, columns=['First Result'], index=list(range(len(result))))

        result['Pretty Addresses'] = pretty_addresses

        result = pd.concat([result, input_data], axis=1)

        print(result)

        result = result.dropna()        

        print(result)
        
    with NamedTemporaryFile() as tmp:
        data = requests.get('http://178.170.192.87:8004/permanent/normalized_works.csv')

        open(tmp.name, 'wb').write(data.content)

        input_data = pd.read_csv(tmp.name, encoding='utf8')

        pretty_addresses = []

        print(input_data)
        input_data = input_data.drop("Unnamed: 0", axis=1)
        print(input_data.shape)
        banlist = []
        addresses = input_data.iloc[:, 4]
        for index, text in enumerate(addresses):
            #print(text)
            secondresult = processor(str(text).replace('Российская Федерация,', '').replace('город Москва', '').replace('внутригородская территория муниципальный округ', ''))
            if secondresult.matches:
                referent = secondresult.matches[0].referent
                display_shortcuts(referent)
                if len(addr) < 2:
                    banlist.append(index)
                elif 'улица' not in addr[0].keys() or 'дом' not in addr[-1].keys():
                    banlist.append(index)
                else:
                    pretty_addresses.append(addr[0]['улица'].title() + ' ' + addr[-1]['дом'])
                    #print(addr)
            addr.clear()

        input_data = input_data.drop(banlist)
        print(banlist)
        secondresult = secondmodel.predict(input_data)

        secondresult = pd.DataFrame(data=secondresult, columns=['Second Result'], index=list(range(len(secondresult))))

        secondresult['Pretty Addresses'] = pretty_addresses

        secondresult = secondresult.dropna()

        secondresult = pd.concat([secondresult, input_data], axis=1)

        secondresult = secondresult.dropna()

        print(secondresult)

    issues_data = []

    
   # print(result.info())

    result = result.dropna()

    print(result.info())
    
    result['Pretty Addresses'] = result['Pretty Addresses'].astype(str)

    print(secondresult.info())

    secondresult['Pretty Addresses'] = secondresult['Pretty Addresses'].astype(str)

    allresult = result.merge(secondresult, on='Pretty Addresses')

    print(allresult.info())

    houses_data = pd.read_csv('housesdata.csv')
    houses_data = houses_data.fillna(0)
    print(houses_data.info())

    print(materials_dict.info())

    allresult = allresult.drop_duplicates(subset='Pretty Addresses', keep="first")

    allresult = allresult.reset_index()

    for index, row in allresult.iterrows():
        address_info = houses_data[houses_data["NAME"] == row['Pretty Addresses']]
        #print(address_info)
        material_id = False if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else houses_data[houses_data["NAME"] == row['Pretty Addresses']].iloc[0]["COL_769"]
        roof_id = False if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else houses_data[houses_data["NAME"] == row['Pretty Addresses']].iloc[0]["COL_781"]
        #print(material_id)
        #print(materials_dict.head(5))
        #print(materials_dict[materials_dict["ID"] == material_id])
        #print(roof_id)
        #print("0" if roof_id == False else roofs_dict[roofs_dict["ID"] == float(roof_id)/1]['NAME'].iloc[0])
        issues_data.append(
        {
        'adress': row['Адрес'], 
        'workname': [worksdict[row['First Result']][0].title(), row['Second Result'].title()], 
        "stats" : 
        {
            "Год постройки МКД" : "0" if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else address_info.iloc[0]["COL_756"],
            "Материал стен": "0" if material_id == False else (materials_dict[materials_dict["ID"] == float(material_id)/1]['NAME'].iloc[0]).title(),
            "Количество этажей" : "0" if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else address_info.iloc[0]["COL_759"],
            "Количество подъездов" : "0" if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else address_info.iloc[0]["COL_760"],
            "Количество квартир" : "0" if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else address_info.iloc[0]["COL_761"],
            "Износ объекта (по БТИ)" : "0" if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else address_info.iloc[0]["COL_766"],
            "Материал кровли" : "0" if roof_id == False else (roofs_dict[roofs_dict["ID"] == float(roof_id)/1]['NAME'].iloc[0]).title(),
            "Количество грузовых лифтов" : "0" if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else address_info.iloc[0]["COL_3363"],
            "Количество пассажирских лифтов" : "0" if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else address_info.iloc[0]["COL_771"]
        },
        'priority': 'Срочная работа' if worksdict[row['First Result']][1] == '1' or worksdict[row['First Result']][2] == '1' else "Плановая работа",
        'causes': []
        })
        if worksdict[row['First Result']][1] == '1': issues_data[index]['causes'].append('МосГаз')
        if worksdict[row['First Result']][2] == '1': issues_data[index]['causes'].append('Авария')

    analysis_result = {'result': issues_data, 'type': 'base', 'criterias': [''], 'date': str(date.today()).replace('-', '.')}

    id = Save(analysis_result)

    analysis_result.pop('_id')
    analysis_result['id'] = str(id)
    #print(analysis_result)

    return analysis_result



@app.get('/worktypes')
def get_worktypes():
    return ['Капитальный ремонт', 'Работы по содержанию']

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
def advanced_analysis(criterias: ICriteria):
    objtype = criterias.obj
    worktype = criterias.work
    dates = criterias.date
    worksdict = dict()
    with open('issuestoworks.json') as json_file:
        worksdict = json.load(json_file)

    roofs_dict = pd.read_excel('Storage/roofs.xlsx')

    materials_dict = pd.read_excel('Storage/materials.xlsx')

    processor = Processor([GEO, ADDRESS])

    result = []

    if worktype == 'Работы по содержанию':
        model = CatBoostClassifier()

        model.load_model('./model/catboost_model2t.bin')

        with NamedTemporaryFile() as tmp:
            data = requests.get('http://178.170.192.87:8004/permanent/normalized_data.csv')

            open(tmp.name, 'wb').write(data.content)

            input_data = pd.read_csv(tmp.name, encoding='utf8')

            print(input_data)
            pretty_addresses = []
            input_data = input_data.drop("Unnamed: 0", axis=1)
            banlist = []
            addresses = input_data.iloc[:, 2]
            for index, text in enumerate(addresses):
                result = processor(str(text))
                if result.matches:
                    print(addr)
                    referent = result.matches[0].referent
                    display_shortcuts(referent)
                    if len(addr) < 2:
                        banlist.append(index)
                    elif 'улица' not in addr[0].keys() or 'дом' not in addr[-1].keys():
                        banlist.append(index)
                    else:
                        pretty_addresses.append(addr[0]['улица'].title() + ' ' + addr[-1]['дом'])
                        #print(addr)
                addr.clear()
            #print(banlist)

            input_data = input_data.drop(banlist)

            result = model.predict(input_data)

            #print(result.shape)

            result = pd.DataFrame(data=result, columns=['First Result'], index=list(range(len(result))))

            result['Pretty Addresses'] = pretty_addresses

            result = pd.concat([result, input_data], axis=1)

            result = result.dropna()        

            print(result)
    elif worktype == 'Капитальный ремонт':

        secondmodel = CatBoostClassifier()

        secondmodel.load_model('./model/catboost_model3t.bin')
        
        with NamedTemporaryFile() as tmp:
            data = requests.get('http://178.170.192.87:8004/permanent/normalized_works.csv')

            open(tmp.name, 'wb').write(data.content)

            input_data = pd.read_csv(tmp.name, encoding='utf8')
            pretty_addresses = []

            print(input_data)
            input_data = input_data.drop("Unnamed: 0", axis=1)
            print(input_data.shape)
            banlist = []
            addresses = input_data.iloc[:, 4]
            for index, text in enumerate(addresses):
                #print(text)
                result = processor(str(text).replace('Российская Федерация,', '').replace('город Москва,', '').replace('внутригородская территория муниципальный округ,', ''))
                if result.matches:
                    referent = result.matches[0].referent
                    display_shortcuts(referent)
                    if len(addr) < 2:
                        banlist.append(index)
                    elif 'улица' not in addr[0].keys() or 'дом' not in addr[-1].keys():
                        banlist.append(index)
                    else:
                        #print(addr[0]['улица'].title() + ' ' + addr[-1]['дом'])
                        pretty_addresses.append(addr[0]['улица'].title() + ' ' + addr[-1]['дом'])
                        #print(addr)
                addr.clear()

            input_data = input_data.drop(banlist)
            result = secondmodel.predict(input_data)

            result = pd.DataFrame(data=result, columns=['Second Result'], index=list(range(len(result))))

            result['Pretty Addresses'] = pretty_addresses

            result = result.dropna()

            result = pd.concat([result, input_data], axis=1)

            result = result.dropna()

            print(result)


    houses_data = pd.read_csv('housesdata.csv')
    houses_data = houses_data.fillna(0)
    
    issues_data = []
    #result = result.drop_duplicates(subset = ['Pretty Addresses', 'First Result'] if 'First Result' in result.columns else ['Pretty Addresses', 'Second Result'] )
    #print("Final result")
    #print(result)
    result = result.reset_index()
    houses_names = []
    for index, row in result.iterrows():
        address_info = houses_data[houses_data["NAME"] == row['Pretty Addresses']]
        #print(address_info)
        material_id = False if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else houses_data[houses_data["NAME"] == row['Pretty Addresses']].iloc[0]["COL_769"]
        roof_id = False if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else houses_data[houses_data["NAME"] == row['Pretty Addresses']].iloc[0]["COL_781"]
        #print(material_id)
        #print(materials_dict.head(5))
        #print(materials_dict[materials_dict["ID"] == material_id])
        #print(roof_id)
        #print("0" if roof_id == False else roofs_dict[roofs_dict["ID"] == float(roof_id)/1]['NAME'].iloc[0])
        workname = worksdict[row['First Result']][0] if 'First Result' in result.columns else row['Second Result']
        issues_data.append(
        {
        'adress': row['Адрес'] if 'Адрес' in row.index else row['Address'].replace('Российская Федерация,', '').replace('город Москва,', ''), 
        'workname': [workname.title()], 
        "stats" : 
        {
            "Год постройки МКД" : "0" if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else address_info.iloc[0]["COL_756"],
            "Материал стен": "0" if material_id == False else (materials_dict[materials_dict["ID"] == float(material_id)/1]['NAME'].iloc[0]).title(),
            "Количество этажей" : "0" if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else address_info.iloc[0]["COL_759"],
            "Количество подъездов" : "0" if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else address_info.iloc[0]["COL_760"],
            "Количество квартир" : "0" if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else address_info.iloc[0]["COL_761"],
            "Износ объекта (по БТИ)" : "0" if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else address_info.iloc[0]["COL_766"],
            "Материал кровли" : "0" if roof_id == False else (roofs_dict[roofs_dict["ID"] == float(roof_id)/1]['NAME'].iloc[0]).title(),
            "Количество грузовых лифтов" : "0" if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else address_info.iloc[0]["COL_3363"],
            "Количество пассажирских лифтов" : "0" if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else address_info.iloc[0]["COL_771"]
        },
        'priority': "Плановая работа" if 'First Result' not in row.index else 'Срочная работа' if worksdict[row['First Result']][1] == '1' or worksdict[row['First Result']][2] == '1' else "Плановая работа",
        'causes':[]
        })
        if 'First Result' in row.index:
            if worksdict[row['First Result']][1] == '1': issues_data[index]['causes'].append('МосГаз')
            if worksdict[row['First Result']][2] == '1': issues_data[index]['causes'].append('Авария')
    emptylist =[]
    houses_data1 = houses_data.copy()
    houses_data1 = houses_data1.drop_duplicates(subset = ['NAME'])

    for index, house in houses_data1.iterrows():
        if house['NAME'] not in pretty_addresses:
            if index != 0:
                material_id = house["COL_769"]
                material = "0" if material_id == 0 else materials_dict[materials_dict["ID"] == float(material_id)/1]['NAME'].iloc[0].title()
                roof_id = house["COL_781"]
                roof = "0" if roof_id == 0 else roofs_dict[roofs_dict["ID"] == float(roof_id)/1]['NAME'].iloc[0].title()
                kirpichi = ['кирпичный', 'Смешанные', 'монолитно-кирпичные', 'Каменные, кирпичные', 'из мелких бетонных блоков', 'из природного камня', 'каменные', 'каменные и бетонные', 'каменные и деревянные', 'кирпичные', 'кирпичные облегченные', 'крупноблочные']
                year = int(house["COL_756"])
                #print(year)
                #print(material_id)
                #print(roof_id)

                currentobject = {
                'adress': ' '.join(house['NAME'].split()[:-1]) + ' Улица ' + house['NAME'].split()[-1] + ' Корпус 2', 
                'workname': [], 
                "stats" : 
                {
                    "Год постройки МКД" : house["COL_756"],
                    "Материал стен": material,
                    "Количество этажей" : house["COL_759"],
                    "Количество подъездов" : house["COL_760"],
                    "Количество квартир" : house["COL_761"],
                    "Износ объекта (по БТИ)" : house["COL_766"],
                    "Материал кровли" : roof,
                    "Количество грузовых лифтов" : house["COL_3363"],
                    "Количество пассажирских лифтов" : house["COL_771"]
                },
                'priority': "Плановая работа",
                'causes':[]
                }

                if material != "0" and material in kirpichi:
                    if year < 1980:
                        currentobject['workname'].append(str('ремонт фасада').title())
                        
                    if year < 1985:
                        currentobject['workname'].append(str('ремонт подъездов, направленный на восстановление их надлежащего состояния и проводимый при выполнении иных работ').title())

                    if year < 1990:
                        currentobject['workname'].append(str('Ремонт инженерной системы водоотведения (стояки)').title())

                    if year < 1995:
                        currentobject['workname'].append(str('Ремонт или замена лифтового оборудования').title())

                    if year < 2000:
                        currentobject['workname'].append(str('ремонт крыши').title())

                    if year < 2005:
                        currentobject['workname'].append(str('ремонт внутридомовой системы дымоудаления и противопожарной автоматики').title())

                    else:
                        currentobject['workname'].append(str('Ремонт систем электроснабжения').title())
                        #print('added')
                elif material != '0' and material not in kirpichi:
                    if year < 1980:
                        currentobject['workname'].append(str('ремонт подъездов, направленный на восстановление их надлежащего состояния и проводимый при выполнении иных работ').title())

                    if year < 1985:
                        currentobject['workname'].append(str('Ремонт или замена лифтового оборудования').title())

                    if year < 1990:
                        currentobject['workname'].append(str('ремонт фасада').title())

                    if year < 1995:
                        currentobject['workname'].append(str('ремонт крыши').title())

                    if year < 2000:
                        currentobject['workname'].append(str('Ремонт инженерной системы водоотведения (стояки)').title())
                        
                    if year < 2005:
                        currentobject['workname'].append(str('ремонт внутридомовой системы дымоудаления и противопожарной автоматики').title())
                    else:
                        currentobject['workname'].append(str('Ремонт систем электроснабжения').title())
                        #print('added')

                if 'Новокосинская 51' in house['NAME']:
                    print(currentobject)
                issues_data.append(currentobject)
    droplist=[]
    for index, issue in enumerate(issues_data):
        if len(issue['workname']) == 0:
            if ("Новокосинская" in issue['adress']):
                print("WATWATWATWATWATWAT")
            droplist.append(index)
    issues_data = [i for j, i in enumerate(issues_data) if j not in droplist]
    if 'First Result' not in row.index:
        new_issues = []
        unique_addresses = []
        for elem in issues_data:
            if elem['adress'] not in unique_addresses:
                unique_addresses.append(elem["adress"])
        for address in unique_addresses:

            address_works = []
            address_priority = str()
            address_stats = dict()
            for issue in issues_data:
                if issue["adress"] == address:
                    if len(issue["workname"]) == 1:
                        address_stats = issue["stats"]
                        address_priority = issue["priority"]
                        if issue["workname"][0] not in address_works: address_works.append(issue["workname"][0]) 
                    else:
                        address_stats = issue["stats"]
                        address_priority = issue["priority"]
                        address_works = issue["workname"]
            new_issues.append({
                'adress': address,
                'workname': address_works,
                'stats': address_stats,
                'priority': address_priority
            })
        analysis_result = {'result': new_issues, 'type': 'Advanced', 'criterias': [objtype, worktype, dates], 'date': str(date.today()).replace('-', '.')}
    else:
        analysis_result = {'result': issues_data, 'type': 'Advanced', 'criterias': [objtype, worktype, dates], 'date': str(date.today()).replace('-', '.')}



    id = Save(analysis_result)

    analysis_result.pop('_id')
    analysis_result['id'] = str(id)
    #print(analysis_result)

    return analysis_result
"""
@app.post('/advancedurl')
def advanced_analysis(criterias: ICriteriaURL):
    objtype = criterias.obj
    worktype = criterias.work
    dates = criterias.date
    files = criterias.files
    worksdict = dict()
    with open('issuestoworks.json') as json_file:
        worksdict = json.load(json_file)

    roofs_dict = pd.read_excel('Storage/roofs.xlsx')

    materials_dict = pd.read_excel('Storage/materials.xlsx')

    processor = Processor([GEO, ADDRESS])

    result = []

    if worktype == 'Работы по содержанию':
        model = CatBoostClassifier()

        model.load_model('./model/catboost_model2t.bin')

        with NamedTemporaryFile() as tmp:
            data = requests.get(f'http://178.170.192.87:8004/permanent/{files['incidents']}')

            open(tmp.name, 'wb').write(data.content)

            input_data = pd.read_csv(tmp.name, encoding='utf8')

            print(input_data)
            pretty_addresses = []
            input_data = input_data.drop("Unnamed: 0", axis=1)
            banlist = []
            addresses = input_data.iloc[:, 2]
            for index, text in enumerate(addresses):
                result = processor(str(text))
                if result.matches:
                    referent = result.matches[0].referent
                    display_shortcuts(referent)
                    if len(addr) < 2:
                        banlist.append(index)
                    elif 'улица' not in addr[0].keys() or 'дом' not in addr[-1].keys():
                        banlist.append(index)
                    else:
                        pretty_addresses.append(addr[0]['улица'].title() + ' ' + addr[-1]['дом'])
                        #print(addr)
                addr.clear()
            #print(banlist)

            input_data = input_data.drop(banlist)

            result = model.predict(input_data)

            #print(result.shape)

            result = pd.DataFrame(data=result, columns=['First Result'], index=list(range(len(result))))

            result['Pretty Addresses'] = pretty_addresses

            result = pd.concat([result, input_data], axis=1)

            result = result.dropna()        

            print(result)
    elif worktype == 'Капитальный ремонт':

        secondmodel = CatBoostClassifier()

        secondmodel.load_model('./model/catboost_model3t.bin')
        
        with NamedTemporaryFile() as tmp:
            data = requests.get(f'http://178.170.192.87:8004/permanent/{files['works']}')

            open(tmp.name, 'wb').write(data.content)

            input_data = pd.read_csv(tmp.name, encoding='utf8')

            pretty_addresses = []

            print(input_data)
            input_data = input_data.drop("Unnamed: 0", axis=1)
            print(input_data.shape)
            banlist = []
            addresses = input_data.iloc[:, 4]
            for index, text in enumerate(addresses):
                #print(text)
                result = processor(str(text).replace('Российская Федерация,', '').replace('город Москва', '').replace('внутригородская территория муниципальный округ', ''))
                if result.matches:
                    referent = result.matches[0].referent
                    display_shortcuts(referent)
                    if len(addr) < 2:
                        banlist.append(index)
                    elif 'улица' not in addr[0].keys() or 'дом' not in addr[-1].keys():
                        banlist.append(index)
                    else:
                        pretty_addresses.append(addr[0]['улица'].title() + ' ' + addr[-1]['дом'])
                        #print(addr)
                addr.clear()

            input_data = input_data.drop(banlist)
            print(banlist)
            result = secondmodel.predict(input_data)

            result = pd.DataFrame(data=result, columns=['Second Result'], index=list(range(len(result))))

            result['Pretty Addresses'] = pretty_addresses

            result = result.dropna()

            result = pd.concat([result, input_data], axis=1)

            result = result.dropna()

            print(result)


    houses_data = pd.read_csv('housesdata.csv')
    houses_data = houses_data.fillna(0)
    
    issues_data = []
    result = result.drop_duplicates(subset = ['Pretty Addresses', 'First Result'] if 'First Result' in result.columns else ['Pretty Addresses', 'Second Result'] )
    print("Final result")
    print(result)
    result = result.reset_index()
    for index, row in result.iterrows():
        address_info = houses_data[houses_data["NAME"] == row['Pretty Addresses']]
        #print(address_info)
        material_id = False if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else houses_data[houses_data["NAME"] == row['Pretty Addresses']].iloc[0]["COL_769"]
        roof_id = False if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else houses_data[houses_data["NAME"] == row['Pretty Addresses']].iloc[0]["COL_781"]
        #print(material_id)
        #print(materials_dict.head(5))
        #print(materials_dict[materials_dict["ID"] == material_id])
        #print(roof_id)
        #print("0" if roof_id == False else roofs_dict[roofs_dict["ID"] == float(roof_id)/1]['NAME'].iloc[0])
        workname = worksdict[row['First Result']][0] if 'First Result' in result.columns else row['Second Result']
        issues_data.append(
        {
        'adress': row['Адрес'] if 'Адрес' in row.index else row['Address'].replace('Российская Федерация,', '').replace('город Москва,', ''), 
        'workname': [workname.title()], 
        "stats" : 
        {
            "Год постройки МКД" : "0" if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else address_info.iloc[0]["COL_756"],
            "Материал стен": "0" if material_id == False else (materials_dict[materials_dict["ID"] == float(material_id)/1]['NAME'].iloc[0]).title(),
            "Количество этажей" : "0" if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else address_info.iloc[0]["COL_759"],
            "Количество подъездов" : "0" if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else address_info.iloc[0]["COL_760"],
            "Количество квартир" : "0" if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else address_info.iloc[0]["COL_761"],
            "Износ объекта (по БТИ)" : "0" if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else address_info.iloc[0]["COL_766"],
            "Материал кровли" : "0" if roof_id == False else (roofs_dict[roofs_dict["ID"] == float(roof_id)/1]['NAME'].iloc[0]).title(),
            "Количество грузовых лифтов" : "0" if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else address_info.iloc[0]["COL_3363"],
            "Количество пассажирских лифтов" : "0" if len(houses_data[houses_data["NAME"] == row['Pretty Addresses']]) == 0 else address_info.iloc[0]["COL_771"]
        },
        'priority': "Плановая работа" if 'First Result' not in row.index else 'Срочная работа' if worksdict[row['First Result']][1] == '1' or worksdict[row['First Result']][2] == '1' else "Плановая работа",
        'causes':[]
        })
        if 'First Result' in row.index:
            if worksdict[row['First Result']][1] == '1': issues_data[index]['causes'].append('МосГаз')
            if worksdict[row['First Result']][2] == '1': issues_data[index]['causes'].append('Авария')

    if 'First Result' not in row.index:
        new_issues = []
        unique_addresses = []
        for elem in issues_data:
            if elem['adress'] not in unique_addresses:
                unique_addresses.append(elem["adress"])
        for address in unique_addresses:
            address_works = []
            address_priority = str()
            address_stats = dict()
            for issue in issues_data:
                if issue["adress"] == address:
                    address_stats = issue["stats"]
                    address_priority = issue["priority"]
                    if issue["workname"][0] not in address_works: address_works.append(issue["workname"][0]) 
            new_issues.append({
                'adress': address,
                'workname': address_works,
                'stats': address_stats,
                'priority': address_priority
            })
        analysis_result = {'result': new_issues, 'type': 'Advanced', 'criterias': [objtype, worktype, dates], 'date': str(date.today()).replace('-', '.')}
    else:
        analysis_result = {'result': issues_data, 'type': 'Advanced', 'criterias': [objtype, worktype, dates], 'date': str(date.today()).replace('-', '.')}

    id = Save(analysis_result)

    analysis_result.pop('_id')
    analysis_result['id'] = str(id)
    #print(analysis_result)

    return analysis_result

"""

    


    
@app.get('/updatedata')
def update_houses_data():
    processor = Processor([GEO, ADDRESS])
    houses_data = pd.read_excel('Storage/houses.xlsx')
    houses_data.info()
    houses_data = houses_data[houses_data.NAME != None]
    houses_data.info()    
    testset = houses_data
    print(testset)
    banlist = []
    for index, text in testset.iterrows():
        result = processor(str(text))
        if result.matches:
            referent = result.matches[0].referent
            display_shortcuts(referent)
            if len(addr) < 2:
                banlist.append(index)
            elif 'улица' not in addr[0].keys():
                banlist.append(index)
            elif addr[0]['улица'] != '':
                testset.loc[index, 'NAME'] = addr[0]['улица'].title() + ' ' + addr[1]['дом']
                print(addr)
            else:
                banlist.append(index)
        addr.clear()
    testset.drop(banlist, inplace=True)
    bamlist = [5, 9, 10, 17, 19, 28, 29, 31, 32, 44, 46, 47, 48, 50, 51, 56, 61, 63, 64, 68, 76, 87, 89, 98, 100, 101, 106, 107, 120, 121, 125, 126, 129, 134, 139, 142, 154, 157, 159, 160, 165, 166, 167, 175, 177, 200, 211, 220, 223, 230, 233, 239, 244, 247, 261, 262, 264, 274, 281, 282, 285, 286, 289, 290, 293, 300, 304, 305, 307, 320, 334, 335, 341, 343, 351, 353, 354, 362, 367, 368, 381, 382, 385, 392, 406, 411, 420, 424, 426, 436, 453, 459, 493, 495, 499, 501, 504, 507, 512, 513, 516, 531, 535, 537, 543, 547, 565, 569, 570, 571, 574, 584, 586, 595, 596, 600, 607, 609, 617, 619, 624, 628, 632, 636, 642, 655, 656, 659, 664, 665, 670, 672, 673, 674, 676, 680, 692, 695, 697, 706, 711, 712, 713, 714, 716, 719, 722, 724, 737, 741, 742, 744, 746, 748, 751, 754, 763, 764, 765, 767, 776, 789, 794, 795, 799, 803, 817, 830, 835, 839, 845, 846, 847, 848, 849, 860, 863, 868, 870, 873, 878, 883, 889, 892, 896, 905, 906, 909, 914, 915, 916, 917, 920, 927, 928, 936, 942, 947, 951, 955, 968, 971, 975, 977, 978, 982, 985, 990, 996, 1008, 1011, 1018, 1019, 1021, 1022, 1028, 1031, 1032, 1041, 1044, 1047, 1050, 1054, 1057, 1058, 1059, 1061, 1063, 1068, 1069, 1071, 1075, 1078, 1080, 1083, 1086, 1091, 1094, 1102, 1107, 1109, 1110, 1113, 1116, 1120, 1133, 1135, 1136, 1148, 1149, 1152, 1159, 1164, 1166, 1169, 1176, 1182, 1184, 1186, 1204, 1213, 1229, 1234, 1235, 1248, 1256, 1268, 1270, 1272, 1276, 1292, 1297, 1304, 1312, 1318, 1324, 1325, 1326, 1334, 1335, 1341, 1351, 1363, 1365, 1369, 1381, 1384, 1393, 1406, 1408, 1415, 1416, 1425, 1427, 1428, 1429, 1433, 1438, 1439, 1445, 1451, 1453, 1469, 1470, 1483, 1486, 1491, 1495, 1501, 1513, 1514, 1520, 1522, 1526, 1534, 1537, 1542, 1548, 1549, 1558, 1580, 1582, 1584, 1590, 1592, 1593, 1597, 1604, 1606, 1607, 1609, 1610, 1617, 1620, 1632, 1660, 1670, 1673, 1675, 1678, 1679, 1680, 1682, 1684, 1690, 1697, 1702, 1704, 1714, 1716, 1718, 1723, 1726, 1727, 1731, 1732, 1746, 1750, 1756, 1761, 1775, 1776, 1779, 1780, 1787, 1790, 1796, 1797, 1802, 1810, 1813, 1821, 1822, 1832, 1835, 1847, 1848, 1850, 1855, 1857, 1862, 1871, 1872, 1883, 1884, 1885, 1887, 1896, 1900, 1902, 1906, 1907, 1908, 1909, 1914, 1915, 1918, 1938, 1948, 1949, 1951, 1952, 1954, 1964, 1970, 1982, 1984, 1986, 1988, 1989, 1993, 2004, 2009, 2018, 2019, 2028, 2032, 2036, 2039, 2051, 2052, 2059, 2061, 2067, 2069, 2070, 2079, 2084, 2085, 2089, 2090, 2093, 2096, 2097, 2105, 2106, 2108, 2109, 2110, 2111, 2120, 2126, 2133, 2150, 2161, 2162, 2164, 2167, 2169, 2172, 2178, 2179, 2189, 2196, 2199, 2209, 2218, 2219, 2224, 2225, 2233, 2235, 2237, 2256, 2257, 2265, 2268, 2287, 2288, 2297, 2305, 2307, 2308, 2313, 2319, 2323, 2325, 2326, 2328, 2330, 2351, 2360, 2372, 2374, 2376, 2377, 2382, 2383, 2386, 2391, 2394, 2416, 2422, 2427, 2429, 2432, 2435, 2439, 2444, 2446, 2453, 2455, 2456, 2457, 2461, 2462, 2463, 2467, 2471, 2477, 2481, 2483, 2488, 2489, 2505, 2513, 2514, 2520, 2524, 2534, 2536, 2545, 2547, 2552, 2553, 2554, 2556, 2559, 2565, 2572, 2579, 2583, 2592, 2601, 2604, 2605, 2610, 2614, 2617, 2624, 2637, 2641, 2643, 2646, 2670, 2674, 2677, 2683, 2689, 2694, 2698, 2699, 2700, 2702, 2709, 2711, 2719, 2722, 2723, 2731, 2737, 2738, 2739, 2743, 2745, 2746, 2750, 2752, 2754, 2756, 2776, 2778, 2780, 2782, 2785, 2791, 2798, 2804, 2807, 2808, 2809, 2829, 2830, 2833, 2835, 2838, 2840, 2844, 2847, 2849, 2854, 2882, 2884, 2895, 2899, 2903, 2910, 2912, 2914, 2919, 2922, 2930, 2931, 2935, 2936, 2940, 2945, 2948, 2949, 2951, 2956, 2958, 2961, 2964, 2971, 2972, 2973, 2982, 2985, 2987, 2990, 2992, 3001, 3004, 3005, 3007, 3011, 3013, 3018, 3023, 3029, 3032, 3034, 3047, 3048, 3049, 3057, 3064, 3065, 3068, 3071, 3073, 3074, 3080, 3088, 3089, 3090, 3093, 3095, 3096, 3100, 3102, 3105, 3109, 3111, 3114, 3120, 3124, 3125, 3133, 3134, 3139, 3140, 3145, 3146, 3176, 3181, 3185, 3193, 3196, 3197, 3202, 3204, 3208, 3212, 3213, 3221, 3244, 3249, 3250, 3254, 3255, 3262, 3263, 3269, 3274, 3280, 3281, 3289, 3292, 3296, 3297, 3299, 3301, 3328, 3329, 3331, 3344, 3347, 3360, 3362, 3366, 3373, 3376, 3377, 3380, 3382, 3383, 3387, 3389, 3390, 3392, 3402, 3405, 3408, 3416, 3423, 3435, 3443, 3447, 3448, 3450, 3456, 3465, 3470, 3472, 3490, 3491, 3512, 3520, 3524, 3527, 3529, 3530, 3555, 3556, 3558, 3563, 3567, 3569, 3577, 3578, 3579, 3580, 3582, 3584, 3591, 3592, 3597, 3608, 3609, 3611, 3623, 3628, 3637, 3638, 3639, 3653, 3657, 3658, 3671, 3673, 3685, 3686, 3687, 3689, 3697, 3704, 3706, 3707, 3708, 3713, 3724, 3727, 3729, 3730, 3737, 3738, 3742, 3748, 3751, 3754, 3755, 3757, 3758, 3763, 3764, 3770, 3772, 3776, 3779, 3786, 3791, 3792, 3798, 3803, 3806, 3807, 3811, 3812, 3814, 3817, 3823, 3830, 3834, 3860, 3864, 3881, 3883, 3886, 3894, 3895, 3897, 3899, 3903, 3908, 3910, 3911, 3912, 3923, 3924, 3927, 3928, 3931, 3933, 3950, 3952, 3954, 3955, 3968, 3970, 3971, 3976, 3978, 3984, 3992, 3998, 4002, 4007, 4008, 4009, 4012, 4015, 4020, 4023, 4029, 4038, 4041, 4043, 4046, 4047, 4048, 4049, 4059, 4062, 4066, 4067, 4072, 4073, 4079, 4088, 4099, 4100, 4102, 4109, 4111, 4119, 4121, 4128, 4139, 4145, 4148, 4151, 4162, 4168, 4180, 4184, 4189, 4194, 4202, 4203, 4204, 4207, 4213, 4214, 4218, 4229, 4230, 4233, 4237, 4238, 4241, 4245, 4247, 4248, 4253, 4262, 4271, 4272, 4289, 4292, 4299, 4303, 4304, 4311, 4312, 4314, 4322, 4326, 4328, 4338, 4348, 4352, 4353, 4358, 4363, 4364, 4366, 4368, 4374, 4376, 4377, 4384, 4394, 4397, 4401, 4402, 4403, 4404, 4406, 4420, 4428, 4437, 4439, 4441, 4452, 4464, 4465, 4470, 4473, 4475, 4486, 4496, 4499, 4505, 4507, 4512, 4515, 4528, 4531, 4533, 4547, 4548, 4564, 4567, 4568, 4580, 4581, 4582, 4590, 4599, 4602, 4604, 4622, 4623, 4625, 4642, 4648, 4655, 4658, 4674, 4678, 4682, 4685, 4702, 4703, 4707, 4711, 4715, 4717, 4719, 4722, 4724, 4731, 4736, 4739, 4742, 4743, 4744, 4754, 4756, 4757, 4769, 4772, 4779, 4785, 4797, 4805, 4809, 4813, 4814, 4827, 4831, 4832, 4835, 4838, 4840, 4843, 4852, 4853, 4859, 4869, 4875, 4878, 4880, 4886, 4894, 4895, 4898, 4901, 4911, 4912, 4916, 4920, 4928, 4932, 4940, 4943, 4953, 4967, 4975, 4978, 4982, 4991, 4992, 4996, 5008, 5014, 5016, 5023, 5025, 5027, 5032, 5033, 5035, 5043, 5044, 5049, 5050, 5073, 5078, 5080, 5083, 5096, 5108, 5123, 5128, 5132, 5137, 5139, 5140, 5142, 5157, 5158, 5163, 5164, 5171, 5178, 5180, 5181, 5182, 5185, 5189, 5190, 5195, 5198, 5201, 5208, 5210, 5211, 5212, 5216, 5217, 5218, 5226, 5235, 5241, 5253, 5258, 5271, 5280, 5283, 5288, 5292, 5299, 5300, 5304, 5306, 5307, 5309, 5318, 5320, 5321, 5327, 5331, 5334, 5337, 5341, 5342, 5343, 5344, 5346, 5351, 5352, 5357, 5366, 5368, 5377, 5380, 5384, 5391, 5393, 5398, 5399, 5400, 5401, 5404, 5406, 5411, 5414, 5418, 5422, 5428, 5430, 5440, 5441, 5444, 5445, 5449, 5451, 5453, 5457, 5462, 5464, 5465, 5467, 5471, 5478, 5480, 5484, 5496, 5499, 5515, 5518, 5521, 5522, 5523, 5527, 5528, 5533, 5535, 5539, 5542, 5562, 5577, 5581, 5587, 5591, 5592, 5593, 5597, 5598, 5628, 5629, 5630, 5631, 5635, 5636, 5641, 5643, 5646, 5647, 5654, 5655, 5698, 5699, 5701, 5702, 5728, 5729, 5730, 5731, 5732, 5734, 5735, 5736, 5737, 5738, 5739, 5740, 5741, 5742, 5743, 5744, 5745, 5755, 5761, 5763, 5766, 5770, 5771, 5772, 5784, 5792, 5793, 5796, 5811, 5812, 5824, 5833, 5835, 5837, 5840, 5842, 5843, 5845, 5852, 5854, 5856, 5860, 5864, 5868, 5876, 5890, 5896, 5905, 5906, 5910, 5914, 5923, 5927, 5975, 5982, 5988, 5989, 5993, 5994, 5997, 6008, 6009, 6010, 6014, 6022, 6024, 6032, 6033, 6034, 6064, 6065, 6067, 6069, 6076, 6081, 6094, 6101, 6122, 6139, 6147, 6149, 6153, 6154, 6156, 6158, 6160, 6162, 6163, 6164, 6168, 6169, 6187, 6188, 6192, 6195, 6198, 6208, 6209, 6210, 6211, 6212, 6213, 6214, 6215, 6216, 6217, 6218, 6219, 6220, 6221, 6222, 6223, 6224, 6225, 6226, 6227, 6228, 6231, 6232, 6235, 6238, 6240, 6241, 6252, 6253, 6254, 6255, 6256, 6257, 6258, 6265, 6269, 6270, 6276, 6278, 6279, 6285, 6291, 6297, 6304, 6317, 6320, 6322, 6326, 6329, 6333, 6338, 6339, 6340, 6341, 6344, 6345, 6350, 6351, 6352, 6353, 6354, 6356, 6358, 6359, 6360, 6361, 6364, 6365, 6366, 6368, 6369, 6372, 6374, 6375, 6376, 6377, 6379, 6380, 6381, 6382, 6383, 6385, 6388, 6389, 6391, 6393, 6395, 6399, 6404, 6405, 6420, 6423, 6426, 6427, 6429, 6434, 6441, 6447, 6451, 6452, 6453, 6454, 6455, 6456, 6478, 6479, 6487, 6492, 6496, 6498, 6500, 6504, 6506, 6510, 6511, 6516, 6520, 6522, 6523, 6526, 6545, 6548, 6554, 6555, 6561, 6563, 6567, 6585, 6586, 6591, 6592, 6593, 6595, 6608, 6610, 6611, 6616, 6618, 6619, 6621, 6622, 6623, 6624, 6625, 6626, 6636, 6644, 6645, 6656, 6657, 6664, 6665, 6666, 6667, 6668, 6669, 6671, 6672, 6673, 6674, 6675, 6677, 6678, 6679, 6686, 6687, 6691, 6703, 6707, 6709, 6714, 6715, 6737, 6740, 6742, 6744, 6746, 6751, 6752, 6760, 6765, 6766, 6769, 6770, 6777, 6778, 6779, 6788, 6789, 6790, 6798, 6800, 6814, 6815, 6818, 6819, 6825, 6831, 6832, 6835, 6836, 6837, 6838, 6839, 6840, 6841, 6842, 6843, 6844, 6845, 6848, 6850, 6851, 6854, 6856, 6857, 6858, 6859, 6860, 6862, 6863, 6865, 6866, 6868, 6869, 6870, 6871, 6873, 6875, 6876, 6877, 6888, 6893, 6894, 6895, 6898, 6899, 6904, 6906, 6907, 6910, 6920, 6932, 6938, 6939, 6944, 6945, 6946, 6947, 6948, 6949, 6950, 6951, 6953, 6955, 6958, 6959, 6960, 6961, 6967, 6972, 6975, 6981, 6983, 6988, 6998, 6999, 7001, 7009, 7012, 7021, 7031, 7032, 7033, 7034, 7037, 7041, 7047, 7055, 7057, 7060, 7061, 7062, 7063, 7064, 7075, 7076, 7078, 7085, 7094, 7099, 7100, 7101, 7111, 7126, 7132, 7133, 7140, 7141, 7146, 7147, 7148, 7151, 7161, 7166, 7169, 7172, 7176, 7177, 7178, 7183, 7184, 7203, 7204, 7206, 7207, 7208, 7209, 7210, 7211, 7212, 7213, 7214, 7215, 7216, 7217, 7218, 7219, 7220, 7221, 7226, 7227, 7231, 7232, 7233, 7234, 7235, 7236, 7237, 7238, 7281, 7282, 7283, 7284, 7285, 7286, 7287, 7288, 7291, 7293, 7296, 7297, 7298, 7300, 7302, 7303, 7304, 7317, 7319, 7320, 7322, 7323, 7324, 7336, 7337, 7340, 7341, 7354, 7355, 7356, 7367, 7368, 7369, 7370, 7371, 7372, 7373, 7374, 7375, 7381, 7382, 7383, 7384, 7385, 7386, 7387, 7388, 7389, 7396, 7407, 7408, 7409, 7410, 7411, 7412, 7413, 7414, 7415, 7416, 7417, 7418, 7420, 7422, 7423, 7424, 7425, 7426, 7429, 7430, 7431, 7432, 7433, 7434, 7464, 7467, 7469, 7480, 7481, 7482, 7483, 7484, 7485, 7486, 7495, 7496, 7497, 7498, 7499, 7507, 7508, 7509, 7511, 7517, 7521, 7523, 7575, 7576, 7577, 7582, 7597, 7598, 7600, 7607, 7616, 7619, 7620, 7637, 7640, 7643, 7644, 7645, 7648, 7649, 7650, 7657, 7660, 7664, 7669, 7681, 7691, 7706, 7715, 7718, 7719, 7723, 7732, 7733, 7734, 7735, 7736, 7741, 7748, 7752, 7753, 7759, 7761, 7767, 7776, 7785, 7786, 7790, 7792, 7817, 7822, 7824, 7825, 7828, 7836, 7847, 7859, 7860, 7861, 7869, 7875, 7876, 7886, 7894, 7895, 7896, 7897, 7902, 7903, 7920, 7921, 7923, 7929, 7933, 7934, 7935, 7937, 7940, 7942, 7943, 7945, 7963, 7971, 7984, 7989, 7991, 7993, 7994, 7998, 8000, 8001, 8002, 8003, 8004, 8010, 8011, 8013, 8014, 8015, 8017, 8019, 8027, 8029, 8036, 8037, 8038, 8047, 8050, 8063, 8068, 8070, 8072, 8074, 8080, 8088, 8090, 8091, 8092, 8100, 8113, 8114, 8115, 8117, 8121, 8122, 8123, 8125, 8129, 8130, 8135, 8145, 8146, 8151, 8161, 8173, 8174, 8175, 8177, 8178, 8182, 8185, 8186, 8187, 8238, 8239, 8240, 8241, 8242, 8243, 8244, 8245, 8246, 8247, 8248, 8249, 8250, 8252, 8255, 8256, 8257, 8258, 8259, 8260, 8261, 8262, 8263, 8285, 8287, 8299, 8300, 8301, 8302, 8303, 8304, 8305, 8306, 8319, 8320, 8321, 8323, 8324, 8326, 8327, 8328, 8329, 8330, 8345, 8363, 8383, 8384, 8385, 8388, 8408, 8419, 8421, 8422, 8423, 8424, 8425, 8426, 8427, 8428, 8440, 8441, 8442, 8443, 8444, 8449, 8452, 8453, 8454, 8471, 8472, 8488, 8491, 8492, 8493, 8494, 8495, 8496, 8497, 8498, 8505, 8506, 8507, 8508, 8509, 8510, 8511, 8512, 8513, 8531, 8532, 8533, 8534, 8546, 8549, 8550, 8551, 8552, 8553, 8554, 8555, 8558, 8559, 8590, 8591, 8592, 8598, 8602, 8607, 8627, 8628, 8629, 8630, 8631, 8632, 8641, 8642, 8643, 8644, 8645, 8646, 8647, 8648, 8649, 8650, 8651, 8652, 8660, 8661, 8662, 8663, 8664, 8665, 8666, 8669, 8670, 8671, 8674, 8677, 8691, 8692, 8693, 8694, 8695, 8696, 8697, 8698, 8702, 8703, 8769, 8770, 8771, 8772, 8773, 8774, 8775, 8776, 8777, 8778, 8794, 8795, 8796, 8797, 8798, 8799, 8800, 8801, 8827, 8828, 8829, 8830, 8831, 8832, 8833, 8834, 8835, 8836, 8837, 8838, 8839, 8842, 8843, 8844, 8845, 8846, 8847, 8848, 8849, 8924, 8925, 8926, 8927, 8928, 8939, 8941, 8942, 8951, 8956, 8957, 8958, 8959, 8960, 8961, 8962, 8965, 8966, 8969, 8976, 8981, 8985, 8989, 8990, 8991, 8992, 8993, 8994, 8995, 8996, 8997, 8998, 8999, 9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9067, 9068, 9069, 9070, 9071, 9072, 9073, 9099, 9100, 9101, 9102, 9103, 9106, 9107, 9108, 9109, 9110, 9112, 9113, 9114, 9115, 9118, 9125, 9126, 9127, 9128, 9129, 9130, 9131, 9132, 9133, 9134, 9135, 9136, 9137, 9138, 9176, 9191, 9197, 9199, 9205, 9206, 9207, 9208, 9209, 9210, 9215, 9216, 9237, 9238, 9239, 9240, 9241, 9242, 9243, 9245, 9246, 9247, 9248, 9249, 9250, 9251, 9252, 9253, 9254, 9255, 9256, 9257, 9258, 9263, 9264, 9265, 9266, 9267, 9268, 9269, 9270, 9271, 9272, 9273, 9274, 9275, 9276, 9277, 9278, 9279, 9280, 9281, 9296, 9298, 9299, 9300, 9301, 9302, 9303, 9304, 9305, 9306, 9322, 9323, 9324, 9328, 9329, 9330, 9331, 9332, 9333, 9334, 9335, 9336, 9346, 9348, 9349, 9350, 9351, 9359, 9360, 9361, 9362, 9363, 9364, 9365, 9366, 9369, 9382, 9383, 9385, 9398, 9399, 9412, 9446, 9453, 9454, 9457, 9479, 9480, 9481, 9482, 9483, 9484, 9485, 9486, 9487, 9488, 9489, 9490, 9491, 9492, 9493, 9494, 9495, 9496, 9497, 9498, 9508, 9509, 9510, 9511, 9512, 9513, 9514, 9515, 9516, 9517, 9518, 9519, 9520, 9521, 9522, 9523, 9524, 9525, 9526, 9527, 9528, 9529, 9530, 9531, 9532, 9533, 9534, 9535, 9536, 9537, 9538, 9539, 9540, 9541, 9542, 9543, 9544, 9545, 9546, 9547, 9548, 9549, 9566, 9567, 9568, 9569, 9570, 9571, 9607, 9608, 9616, 9617, 9618, 9619, 9620, 9621, 9634, 9635, 9636, 9649, 9650, 9651, 9705, 9706, 9734, 9737, 9739, 9740, 9741, 9742, 9743, 9744, 9745, 9746, 9747, 9748, 9749, 9750, 9751, 9752, 9753, 9766, 9767, 9768, 9769, 9770, 9771, 9772, 9773, 9774, 9789, 9795, 9801, 9839, 9841, 9850, 9891, 9892, 9893, 9894, 9895, 9896, 9897, 9916, 9917, 9918, 9919, 9920, 9921, 9922, 9923, 9924, 9925, 9926, 9927, 9928, 9962, 9963, 9964, 9998, 10001, 10002, 10003, 10004, 10005, 10006, 10007, 10008, 10009, 10010, 10014, 10017, 10018, 10019, 10020, 10024, 10031, 10033, 10035, 10058, 10059, 10060, 10075, 10123, 10124, 10125, 10126, 10135, 10145, 10147, 10148, 10149, 10151, 10152, 10166, 10177, 10178, 10183, 10184, 10190, 10191, 10192, 10193, 10194, 10195, 10196, 10197, 10198, 10199, 10200, 10201, 10202, 10203, 10204, 10206, 10217, 10218, 10219, 10220, 10221, 10222, 10223, 10235, 10236, 10237, 10238, 10239, 10240, 10241, 10242, 10243, 10289, 10290, 10293, 10294, 10296, 10297, 10310, 10311, 10312, 10313, 10314, 10315, 10316, 10319, 10320, 10321, 10322, 10323, 10324, 10325, 10327, 10330, 10331, 10332, 10333, 10340, 10341, 10342, 10343, 10344, 10345, 10346, 10347, 10349, 10350, 10351, 10356, 10375, 10389, 10412, 10449, 10453, 10479, 10495, 10496, 10497, 10498, 10511, 10512, 10513, 10518, 10519, 10521, 10522, 10523, 10544, 10545, 10546, 10547, 10548, 10549, 10550, 10551, 10552, 10553, 10554, 10562, 10572, 10573, 10574, 10595, 10597, 10598, 10599, 10603, 10604, 10607, 10610, 10611, 10645, 10646, 10647, 10648, 10679, 10680, 10681, 10684, 10692, 10693, 10695, 10698, 10703, 10705, 10732, 10733, 10734, 10735, 10747, 10748, 10749, 10750, 10751, 10752, 10753, 10754, 10759, 10765, 10767, 10768, 10769, 10770, 10771, 10772, 10773, 10774, 10775, 10776, 10777, 10778, 10779, 10780, 10781, 10782, 10783, 10784, 10785, 10786, 10787, 10788, 10792, 10795, 10796, 10797, 10798, 10819, 10820, 10822, 10823, 10824, 10825, 10826, 10827, 10829, 10830, 10839, 10840, 10841, 10842, 10843, 10844, 10845, 10846, 10847, 10848, 10849, 10850, 10855, 10858, 10859, 10860, 10861, 10862, 10863, 10864, 10865, 10866, 10867, 10868, 10869, 10870, 10873, 10880, 10886, 10898, 10899, 10900, 10901, 10902, 10903, 10916, 10919, 10920, 10921, 10922, 10924, 10925, 10926, 10931, 10942, 10943, 10944, 10945, 10946, 10947, 10948, 10949, 10950, 10951, 10952, 10954, 10958, 10959, 10960, 10966, 10967, 10968, 10969, 10970, 10971, 10973, 10974, 10978, 10981, 10982, 10983, 10984, 10985, 10986, 10987, 10988, 10989, 10995, 10996, 10997, 10998, 11002, 11003, 11004, 11005, 11007, 11021, 11035, 11049, 11050, 11051, 11052, 11053, 11054, 11059, 11060, 11061, 11062, 11080, 11088, 11089, 11090, 11091, 11092, 11093, 11094, 11110, 11115, 11124, 11128, 11132, 11155, 11158, 11171, 11172, 11173, 11174, 11175, 11181, 11193, 11194, 11195, 11198, 11207, 11208, 11210, 11218, 11220, 11246, 11247, 11248, 11252, 11261, 11262, 11263, 11264, 11265, 11292, 11340, 11350, 11351, 11352, 11380, 11383, 11386, 11387, 11388, 11389, 11390, 11391, 11392, 11395, 11396, 11397, 11398, 11425, 11426, 11427, 11428, 11440, 11441, 11442, 11453, 11454, 11455, 11456, 11457, 11458, 11459, 11460, 11461, 11462, 11463, 11474, 11475, 11480, 11482, 11483, 11484, 11486, 11487, 11492, 11494, 11495, 11500, 11519, 11534, 11566, 11567, 11570, 11572, 11575, 11577, 11584, 11585, 11587, 11601, 11602, 11603, 11604, 11605, 11606, 11607, 11609, 11613, 11618, 11619, 11627, 11630, 11641, 11642, 11647, 11648, 11649, 11650, 11655, 11656, 11657, 11658, 11659, 11660, 11661, 11662, 11677, 11683, 11684, 11685, 11686, 11687, 11688, 11690, 11693, 11699, 11704, 11711, 11716, 11717, 11718, 11726, 11749, 11773, 11777, 11794, 11798, 11799, 11810, 11811, 11813, 11817, 11818, 11819, 11825, 11826, 11834, 11835, 11842, 11844, 11845, 11852, 11855, 11856, 11857, 11860, 11870, 11871, 11877, 11878, 11879, 11880, 11881, 11882, 11883, 11884, 11889, 11893, 11894, 11895, 11896, 11907, 11909, 11910, 11911, 11912, 11913, 11914, 11916, 11917, 11918, 11919, 11920, 11938, 11950, 11951, 11952, 11953, 11954, 11959, 11961, 11962, 11963, 11964, 11970, 11971, 11972, 11973, 11977, 11979, 11980, 11981, 11982, 11983, 11984, 11985, 11986, 11987, 11988, 11989, 11990, 11991, 11993, 11994, 11995, 11996, 11997, 12004, 12005, 12011, 12015, 12016, 12017, 12018, 12019, 12020, 12021, 12022, 12023, 12024, 12025, 12026, 12031, 12032, 12057, 12058, 12059, 12061, 12063, 12073, 12074, 12075, 12076, 12077, 12078, 12079, 12080, 12081, 12093, 12094, 12106, 12107, 12109, 12110, 12113, 12114, 12115, 12116, 12126, 12127, 12156, 12157, 12158, 12161, 12163, 12164, 12170, 12176, 12187, 12188, 12189, 12190, 12191, 12192, 12193, 12194, 12195, 12199, 12210, 12221, 12222, 12232, 12233, 12234, 12236, 12237, 12238, 12243, 12253, 12258, 12259, 12260, 12261, 12262, 12263, 12264, 12265, 12266, 12273, 12274, 12275, 12276, 12277, 12278, 12287, 12288, 12289, 12290, 12291, 12292, 12321, 12322, 12323, 12324, 12325, 12331, 12333, 12334, 12340, 12341, 12343, 12344, 12346, 12347, 12364, 12365, 12366, 12372, 12374, 12375, 12376, 12378, 12385, 12388, 12400, 12403, 12409, 12410, 12415, 12419, 12421, 12422, 12423, 12426, 12429, 12436, 12440, 12443, 12448, 12450, 12465, 12495, 12508, 12509, 12531, 12533, 12538, 12542, 12543, 12545, 12549, 12559, 12567, 12568, 12569, 12585, 12601, 12602, 12603, 12604, 12605, 12606, 12607, 12608, 12609, 12610, 12611, 12613, 12625, 12627, 12628, 12632, 12634, 12635, 12638, 12639, 12642, 12643, 12644, 12658, 12663, 12664, 12665, 12666, 12667, 12669, 12671, 12673, 12674, 12675, 12676, 12706, 12717, 12725, 12730, 12731, 12732, 12733, 12734, 12735, 12736, 12740, 12741, 12742, 12744, 12762, 12763, 12778, 12779, 12780, 12791, 12792, 12793, 12794, 12795, 12796, 12797, 12803, 12810, 12815, 12820, 12821, 12822, 12823, 12824, 12825, 12826, 12827, 12834, 12842, 12843, 12844, 12845, 12846, 12847, 12855, 12861, 12862, 12864, 12868, 12877, 12882, 12883, 12884, 12885, 12897, 12898, 12899, 12900, 12901, 12902, 12903, 12935, 12938, 12939, 12945, 12950, 12955, 12957, 12959, 12987, 13004, 13005, 13006, 13035, 13057, 13058, 13059, 13060, 13061, 13095, 13096, 13109, 13115, 13149, 13160, 13166, 13172, 13174, 13179, 13180, 13187, 13188, 13189, 13190, 13192, 13193, 13197, 13207, 13212, 13231, 13238, 13239, 13240, 13241, 13242, 13243, 13244, 13245, 13246, 13247, 13248, 13249, 13250, 13251, 13252, 13255, 13257, 13258, 13259, 13260, 13262, 13263, 13264, 13267, 13268, 13372, 13373, 13374, 13375, 13376, 13377, 13378, 13379, 13380, 13381, 13382, 13383, 13384, 13385, 13386, 13387, 13388, 13389, 13390, 13391, 13392, 13393, 13394, 13395, 13396, 13397, 13398, 13399, 13400, 13401, 13402, 13403, 13404, 13405, 13406, 13407, 13408, 13409, 13410, 13411, 13412, 13413, 13414, 13415, 13416, 13417, 13418, 13419, 13420, 13421, 13423, 13424, 13425, 13435, 13436, 13437, 13438, 13440, 13441, 13445, 13463, 13464, 13465, 13468, 13469, 13470, 13471, 13475, 13476, 13477, 13478, 13479, 13480, 13481, 13482, 13483, 13484, 13485, 13486, 13492, 13493, 13494, 13495, 13496, 13497, 13506, 13507, 13508, 13509, 13522, 13523, 13525, 13526, 13527, 13528, 13529, 13530, 13531, 13532, 13533, 13534, 13542, 13585, 13586, 13592, 13593, 13601, 13602, 13603, 13604, 13605, 13606, 13607, 13608, 13609, 13610, 13611, 13612, 13613, 13614, 13615, 13616, 13617, 13618, 13624, 13625, 13626, 13627, 13628, 13629, 13630, 13631, 13632, 13633, 13634, 13635, 13636, 13637, 13638, 13639, 13640, 13641, 13659, 13660, 13661, 13662, 13663, 13664, 13665, 13666, 13667, 13674, 13675, 13676, 13710, 13712, 13713, 13727, 13728, 13729, 13730, 13731, 13732, 13733, 13734, 13769, 13770, 13780, 13781, 13782, 13783, 13784, 13785, 13786, 13787, 13788, 13789, 13825, 13829, 13830, 13831, 13832, 13833, 13834, 13835, 13836, 13839, 13840, 13858, 13863, 13865, 13873, 13874, 13875, 13876, 13877, 13878, 13879, 13880, 13881, 13882, 13896, 13897, 13900, 13901, 13902, 13903, 13905, 13931, 13935, 13939, 13944, 13945, 13946, 13947, 13951, 13952, 13953, 13960, 13967, 13977, 13978, 13982, 13983, 13986, 13991, 13992, 13993, 13994, 13996, 13997, 14013, 14015, 14016, 14017, 14020, 14022, 14023, 14024, 14025, 14026, 14029, 14030, 14031, 14032, 14033, 14034, 14035, 14036, 14037, 14038, 14039, 14040, 14041, 14042, 14044, 14045, 14046, 14048, 14057, 14058, 14059, 14060, 14061, 14062, 14063, 14064, 14065, 14066, 14067, 14068, 14069, 14070, 14073, 14083, 14086, 14087, 14090, 14091, 14092, 14094, 14096, 14098, 14107, 14110, 14111, 14112, 14113, 14114, 14115, 14116, 14117, 14118, 14119, 14120, 14123, 14124, 14125, 14126, 14127, 14128, 14133, 14143, 14144, 14145, 14157, 14159, 14160, 14168, 14174, 14176, 14178, 14182, 14187, 14188, 14189, 14190, 14193, 14194, 14195, 14196, 14197, 14198, 14199, 14200, 14206, 14211, 14212, 14213, 14214, 14215, 14216, 14217, 14218, 14222, 14223, 14224, 14226, 14227, 14228, 14235, 14236, 14237, 14238, 14239, 14240, 14241, 14242, 14243, 14244, 14245, 14246, 14247, 14248, 14249, 14255, 14256, 14257, 14258, 14259, 14260, 14261, 14262, 14263, 14267, 14269, 14270, 14271, 14272, 14274, 14275, 14276, 14277, 14278, 14279, 14280, 14281, 14282, 14283, 14284, 14285, 14286, 14287, 14288, 14289, 14290, 14294, 14295, 14296, 14297, 14302, 14303, 14305, 14306, 14307, 14308, 14309, 14310, 14311, 14312, 14313, 14314, 14315, 14316, 14317, 14318, 14319, 14320, 14321, 14322, 14333, 14335, 14336, 14337, 14338, 14339, 14340, 14341, 14342, 14347, 14348, 14349, 14353, 14359, 14360, 14361, 14362, 14363, 14364, 14365, 14366, 14369, 14373, 14374, 14375, 14376, 14377, 14378, 14379, 14380, 14381, 14387, 14389, 14390, 14391, 14392, 14393, 14394, 14396, 14397, 14398, 14402, 14403, 14405, 14407, 14413, 14414, 14416, 14432, 14433, 14450, 14451, 14452, 14453, 14454, 14455, 14458, 14459, 14460, 14472, 14473, 14477, 14483, 14484, 14485, 14486, 14487, 14488, 14490, 14491, 14494, 14495, 14496, 14497, 14498, 14499, 14500, 14501, 14502, 14503, 14505, 14506, 14513, 14519, 14523, 14531, 14548, 14549, 14550, 14554, 14555, 14556, 14559, 14560, 14563, 14571, 14576, 14583, 14593, 14594, 14595, 14596, 14601, 14606, 14610, 14617, 14619, 14620, 14626, 14638, 14644, 14645, 14646, 14647, 14649, 14650, 14662, 14670, 14671, 14674, 14675, 14688, 14689, 14690, 14691, 14710, 14715, 14716, 14732, 14733, 14734, 14735, 14736, 14737, 14742, 14747, 14750, 14752, 14753, 14754, 14756, 14757, 14767, 14768, 14771, 14777, 14779, 14780, 14787, 14788, 14789, 14791, 14793, 14794, 14795, 14797, 14799, 14801, 14803, 14804, 14805, 14807, 14808, 14809, 14811, 14812, 14813, 14814, 14815, 14816, 14817, 14818, 14819, 14820, 14821, 14832, 14837, 14838, 14839, 14840, 14841, 14842, 14843, 14844, 14845, 14846, 14847, 14848, 14849, 14850, 14851, 14852, 14853, 14860, 14874, 14875, 14877, 14878, 14879, 14884, 14885, 14890, 14892, 14894, 14899, 14905, 14906, 14910, 14911, 14912, 14913, 14914, 14915, 14916, 14917, 14920, 14921, 14922, 14923, 14924, 14925, 14931, 14937, 14942, 14943, 14948, 14951, 14952, 14953, 14954, 14972, 14973, 14974, 14975, 14976, 14996, 15000, 15014, 15015, 15016, 15017, 15022, 15023, 15027, 15028, 15031, 15032, 15033, 15034, 15035, 15038, 15040, 15041, 15046, 15048, 15055, 15063, 15065, 15066, 15067, 15068, 15069, 15070, 15071, 15072, 15073, 15075, 15076, 15077, 15078, 15079, 15080, 15085, 15086, 15087, 15088, 15089, 15090, 15105, 15107, 15108, 15114, 15116, 15118, 15121, 15131, 15135, 15136, 15143, 15151, 15155, 15162, 15163, 15166, 15167, 15168, 15169, 15170, 15171, 15172, 15173, 15174, 15185, 15203, 15213, 15214, 15215, 15220, 15221, 15233, 15234, 15235, 15236, 15238, 15239, 15241, 15242, 15243, 15244, 15245, 15246, 15247, 15249, 15252, 15255, 15257, 15262, 15267, 15273, 15274, 15275, 15279, 15280, 15281, 15282, 15284, 15289, 15291, 15292, 15295, 15296, 15300, 15301, 15302, 15303, 15304, 15322, 15323, 15325, 15327, 15329, 15333, 15335, 15344, 15345, 15351, 15353, 15359, 15365, 15369, 15377, 15378, 15379, 15382, 15383, 15385, 15386, 15388, 15389, 15391, 15392, 15394, 15398, 15401, 15403, 15404, 15405, 15407, 15411, 15414, 15416, 15420, 15421, 15422, 15423, 15424, 15425, 15426, 15427, 15428, 15429, 15430, 15431, 15432, 15433, 15434, 15435, 15436, 15437, 15438, 15439, 15440, 15441, 15442, 15443, 15446, 15447, 15448, 15449, 15450, 15451, 15452, 15453, 15454, 15455, 15456, 15457, 15475, 15476, 15478, 15481, 15484, 15485, 15486, 15488, 15489, 15490, 15491, 15492, 15493, 15494, 15495, 15496, 15505, 15506, 15520, 15521, 15522, 15523, 15524, 15525, 15527, 15531, 15532, 15538, 15543, 15544, 15546, 15547, 15548, 15555, 15556, 15557, 15558, 15559, 15560, 15562, 15587, 15588, 15595, 15610, 15611, 15612, 15613, 15614, 15622, 15623, 15624, 15625, 15626, 15628, 15629, 15630, 15631, 15632, 15633, 15634, 15635, 15636, 15637, 15646, 15655, 15681, 15695, 15697, 15706, 15711, 15712, 15724, 15729, 15736, 15737, 15739, 15740, 15741, 15742, 15743, 15744, 15745, 15746, 15749, 15750, 15751, 15752, 15769, 15771, 15780, 15781, 15786, 15787, 15788, 15789, 15790, 15791, 15793, 15794, 15798, 15802, 15805, 15806, 15807, 15811, 15812, 15813, 15816, 15817, 15818, 15819, 15820, 15822, 15823, 15826, 15835, 15841, 15842, 15843, 15844, 15845, 15846, 15847, 15848, 15849, 15850, 15851, 15852, 15853, 15854, 15855, 15856, 15857, 15858, 15859, 15860, 15861, 15862, 15863, 15864, 15865, 15866, 15867, 15868, 15869, 15870, 15871, 15873, 15874, 15875, 15917, 15918, 15919, 15920, 15922, 15923, 15925, 15926, 15927, 15928, 15929, 15930, 15931, 15932, 15935, 15936, 15937, 15938, 15939, 15940, 15945, 15946, 15947, 15948, 15953, 15954, 15958, 15963, 15964, 15965, 15966, 15970, 15971, 15972, 15973, 15974, 15977, 15979, 15980, 15981, 15982, 15983, 15984, 15985, 15986, 15987, 15988, 15989, 15990, 15991, 15992, 15993, 15994, 15995, 15996, 15998, 15999, 16000, 16001, 16002, 16003, 16004, 16005, 16006, 16007, 16008, 16010, 16011, 16012, 16013, 16014, 16015, 16016, 16017, 16026, 16027, 16028, 16029, 16039, 16048, 16049, 16054, 16055, 16056, 16057, 16058, 16059, 16060, 16061, 16062, 16068, 16069, 16070, 16071, 16087, 16088, 16089, 16090, 16091, 16092, 16094, 16095, 16096, 16098, 16099, 16100, 16101, 16102, 16103, 16107, 16110, 16113, 16115, 16120, 16121, 16143, 16144, 16149, 16150, 16181, 16183, 16189, 16193, 16194, 16195, 16196, 16200, 16201, 16202, 16203, 16204, 16205, 16206, 16214, 16215, 16216, 16217, 16223, 16227, 16228, 16238, 16241, 16246, 16250, 16259, 16260, 16268, 16276, 16279, 16282, 16283, 16284, 16285, 16286, 16292, 16294, 16295, 16296, 16301, 16313, 16315, 16316, 16317, 16318, 16319, 16320, 16321, 16331, 16332, 16335, 16338, 16347, 16348, 16356, 16359, 16363, 16366, 16367, 16368, 16369, 16370, 16373, 16379, 16385, 16386, 16387, 16389, 16400, 16412, 16416, 16429, 16437, 16443, 16456, 16457, 16460, 16492, 16493, 16494, 16495, 16496, 16500, 16501, 16504, 16510, 16511, 16513, 16514, 16515, 16518, 16519, 16521, 16523, 16526, 16529, 16530, 16532, 16539, 16540, 16542, 16548, 16549, 16552, 16554, 16559, 16560, 16562, 16565, 16574, 16575, 16576, 16577, 16578, 16579, 16580, 16581, 16582, 16583, 16585, 16586, 16587, 16588, 16589, 16590, 16591, 16592, 16593, 16598, 16599, 16600, 16601, 16602, 16603, 16604, 16605, 16606, 16607, 16608, 16609, 16611, 16612, 16613, 16614, 16615, 16623, 16624, 16628, 16632, 16636, 16637, 16641, 16643, 16655, 16656, 16660, 16663, 16664, 16667, 16671, 16674, 16675, 16677, 16678, 16679, 16680, 16683, 16685, 16686, 16701, 16706, 16709, 16710, 16713, 16714, 16722, 16723, 16732, 16733, 16737, 16738, 16739, 16755, 16756, 16759, 16771, 16775, 16784, 16785, 16811, 16812, 16813, 16814, 16815, 16818, 16830, 16832, 16855, 16857, 16861, 16862, 16864, 16865, 16866, 16867, 16868, 16869, 16870, 16871, 16872, 16891, 16902, 16903, 16905, 16906, 16907, 16911, 16922, 16923, 16924, 16941, 16942, 16943, 16944, 16945, 16946, 16947, 16948, 16949, 16950, 16951, 16952, 16953, 16959, 16960, 16961, 16964, 16965, 16966, 16967, 16968, 16973, 16975, 16977, 16984, 16985, 16986, 16987, 16988, 16989, 16990, 16991, 16992, 16993, 16994, 16995, 16996, 16997, 16998, 16999, 17000, 17001, 17002, 17003, 17004, 17008, 17009, 17010, 17011, 17012, 17013, 17014, 17015, 17016, 17017, 17018, 17019, 17020, 17021, 17022, 17023, 17024, 17025, 17026, 17027, 17028, 17029, 17031, 17037, 17038, 17040, 17041, 17042, 17043, 17044, 17045, 17046, 17047, 17048, 17049, 17050, 17064, 17065, 17066, 17067, 17068, 17069, 17071, 17072, 17073, 17074, 17075, 17078, 17080, 17084, 17085, 17086, 17087, 17088, 17089, 17090, 17091, 17092, 17093, 17094, 17095, 17096, 17103, 17104, 17105, 17106, 17107, 17108, 17109, 17111, 17112, 17113, 17115, 17116, 17117, 17118, 17119, 17120, 17121, 17122, 17123, 17124, 17125, 17126, 17127, 17128, 17129, 17136, 17137, 17140, 17145, 17150, 17151, 17157, 17172, 17179, 17180, 17181, 17182, 17189, 17193, 17198, 17212, 17213, 17214, 17215, 17224, 17229, 17230, 17231, 17254, 17255, 17258, 17259, 17260, 17261, 17262, 17263, 17264, 17265, 17266, 17267, 17268, 17270, 17275, 17277, 17278, 17279, 17280, 17281, 17282, 17283, 17284, 17294, 17316, 17323, 17324, 17326, 17327, 17339, 17344, 17345, 17346, 17347, 17355, 17356, 17359, 17363, 17370, 17371, 17384, 17385, 17387, 17389, 17428, 17429, 17431, 17432, 17433, 17434, 17435, 17436, 17437, 17439, 17451, 17452, 17461, 17462, 17463, 17466, 17471, 17478, 17479, 17482, 17488, 17501, 17502, 17508, 17512, 17513, 17515, 17516, 17528, 17529, 17530, 17531, 17532, 17533, 17541, 17548, 17552, 17553, 17554, 17555, 17556, 17557, 17560, 17561, 17562, 17563, 17570, 17574, 17593, 17594, 17595, 17615, 17616, 17617, 17622, 17623, 17624, 17626, 17627, 17628, 17633, 17634, 17639, 17642, 17643, 17646, 17647, 17648, 17650, 17652, 17655, 17658, 17660, 17669, 17671, 17672, 17673, 17675, 17676, 17677, 17678, 17680, 17684, 17687, 17688, 17689, 17691, 17695, 17696, 17700, 17705, 17706, 17708, 17709, 17710, 17714, 17717, 17718, 17723, 17735, 17738, 17739, 17740, 17742, 17743, 17761, 17762, 17763, 17766, 17767, 17769, 17770, 17771, 17772, 17773, 17774, 17776, 17788, 17789, 17797, 17798, 17805, 17806, 17807, 17820, 17821, 17822, 17823, 17824, 17825, 17826, 17827, 17828, 17829, 17830, 17831, 17832, 17833, 17834, 17835, 17836, 17839, 17840, 17841, 17842, 17843, 17849, 17850, 17851, 17852, 17853, 17854, 17866, 17872, 17873, 17874, 17876, 17880, 17883, 17884, 17885, 17889, 17895, 17897, 17899, 17907, 17910, 17912, 17913, 17914, 17919, 17924, 17925, 17930, 17931, 17937, 17938, 17939, 17940, 17947, 17948, 17961, 17962, 17963, 17964, 17966, 17973, 17979, 17980, 17981, 17982, 17983, 17984, 17985, 17986, 17987, 17988, 17989, 17994, 17995, 17996, 17997, 18002, 18008, 18009, 18010, 18011, 18013, 18016, 18022, 18039, 18041, 18044, 18045, 18046, 18047, 18051, 18053, 18054, 18055, 18056, 18057, 18058, 18059, 18060, 18061, 18062, 18063, 18064, 18065, 18066, 18067, 18068, 18069, 18070, 18071, 18072, 18073, 18074, 18075, 18076, 18077, 18078, 18079, 18080, 18081, 18082, 18083, 18084, 18085, 18086, 18087, 18088, 18089, 18090, 18091, 18092, 18093, 18094, 18095, 18096, 18097, 18098, 18099, 18100, 18101, 18102, 18103, 18104, 18105, 18106, 18107, 18109, 18110, 18111, 18112, 18113, 18114, 18115, 18116, 18117, 18118, 18119, 18120, 18121, 18122, 18123, 18135, 18140, 18150, 18151, 18152, 18157, 18158, 18159, 18173, 18174, 18175, 18176, 18177, 18178, 18179, 18180, 18181, 18182, 18183, 18184, 18185, 18186, 18187, 18188, 18189, 18190, 18191, 18192, 18193, 18194, 18195, 18196, 18197, 18198, 18199, 18200, 18201, 18202, 18204, 18235, 18240, 18241, 18299, 18300, 18301, 18302, 18303, 18304, 18305, 18306, 18307, 18308, 18309, 18310, 18323, 18326, 18327, 18328, 18329, 18331, 18333, 18334, 18335, 18336, 18337, 18338, 18339, 18340, 18341, 18342, 18343, 18344, 18345, 18346, 18347, 18357, 18358, 18359, 18361, 18362, 18363, 18364, 18365, 18366, 18367, 18375, 18377, 18385, 18389, 18392, 18394, 18395, 18396, 18398, 18402, 18405, 18406, 18407, 18408, 18409, 18410, 18412, 18416, 18417, 18425, 18426]
    testset.info()
    testset.describe()
    testset.to_csv('housesdata.csv')
    print(banlist)
    return 0
    
@app.get('/bandata')
def ban_data():
    df = pd.read_csv('housesdata.csv')
    bamlist = [5, 9, 10, 17, 19, 28, 29, 31, 32, 44, 46, 47, 48, 50, 51, 56, 61, 63, 64, 68, 76, 87, 89, 98, 100, 101, 106, 107, 120, 121, 125, 126, 129, 134, 139, 142, 154, 157, 159, 160, 165, 166, 167, 175, 177, 200, 211, 220, 223, 230, 233, 239, 244, 247, 261, 262, 264, 274, 281, 282, 285, 286, 289, 290, 293, 300, 304, 305, 307, 320, 334, 335, 341, 343, 351, 353, 354, 362, 367, 368, 381, 382, 385, 392, 406, 411, 420, 424, 426, 436, 453, 459, 493, 495, 499, 501, 504, 507, 512, 513, 516, 531, 535, 537, 543, 547, 565, 569, 570, 571, 574, 584, 586, 595, 596, 600, 607, 609, 617, 619, 624, 628, 632, 636, 642, 655, 656, 659, 664, 665, 670, 672, 673, 674, 676, 680, 692, 695, 697, 706, 711, 712, 713, 714, 716, 719, 722, 724, 737, 741, 742, 744, 746, 748, 751, 754, 763, 764, 765, 767, 776, 789, 794, 795, 799, 803, 817, 830, 835, 839, 845, 846, 847, 848, 849, 860, 863, 868, 870, 873, 878, 883, 889, 892, 896, 905, 906, 909, 914, 915, 916, 917, 920, 927, 928, 936, 942, 947, 951, 955, 968, 971, 975, 977, 978, 982, 985, 990, 996, 1008, 1011, 1018, 1019, 1021, 1022, 1028, 1031, 1032, 1041, 1044, 1047, 1050, 1054, 1057, 1058, 1059, 1061, 1063, 1068, 1069, 1071, 1075, 1078, 1080, 1083, 1086, 1091, 1094, 1102, 1107, 1109, 1110, 1113, 1116, 1120, 1133, 1135, 1136, 1148, 1149, 1152, 1159, 1164, 1166, 1169, 1176, 1182, 1184, 1186, 1204, 1213, 1229, 1234, 1235, 1248, 1256, 1268, 1270, 1272, 1276, 1292, 1297, 1304, 1312, 1318, 1324, 1325, 1326, 1334, 1335, 1341, 1351, 1363, 1365, 1369, 1381, 1384, 1393, 1406, 1408, 1415, 1416, 1425, 1427, 1428, 1429, 1433, 1438, 1439, 1445, 1451, 1453, 1469, 1470, 1483, 1486, 1491, 1495, 1501, 1513, 1514, 1520, 1522, 1526, 1534, 1537, 1542, 1548, 1549, 1558, 1580, 1582, 1584, 1590, 1592, 1593, 1597, 1604, 1606, 1607, 1609, 1610, 1617, 1620, 1632, 1660, 1670, 1673, 1675, 1678, 1679, 1680, 1682, 1684, 1690, 1697, 1702, 1704, 1714, 1716, 1718, 1723, 1726, 1727, 1731, 1732, 1746, 1750, 1756, 1761, 1775, 1776, 1779, 1780, 1787, 1790, 1796, 1797, 1802, 1810, 1813, 1821, 1822, 1832, 1835, 1847, 1848, 1850, 1855, 1857, 1862, 1871, 1872, 1883, 1884, 1885, 1887, 1896, 1900, 1902, 1906, 1907, 1908, 1909, 1914, 1915, 1918, 1938, 1948, 1949, 1951, 1952, 1954, 1964, 1970, 1982, 1984, 1986, 1988, 1989, 1993, 2004, 2009, 2018, 2019, 2028, 2032, 2036, 2039, 2051, 2052, 2059, 2061, 2067, 2069, 2070, 2079, 2084, 2085, 2089, 2090, 2093, 2096, 2097, 2105, 2106, 2108, 2109, 2110, 2111, 2120, 2126, 2133, 2150, 2161, 2162, 2164, 2167, 2169, 2172, 2178, 2179, 2189, 2196, 2199, 2209, 2218, 2219, 2224, 2225, 2233, 2235, 2237, 2256, 2257, 2265, 2268, 2287, 2288, 2297, 2305, 2307, 2308, 2313, 2319, 2323, 2325, 2326, 2328, 2330, 2351, 2360, 2372, 2374, 2376, 2377, 2382, 2383, 2386, 2391, 2394, 2416, 2422, 2427, 2429, 2432, 2435, 2439, 2444, 2446, 2453, 2455, 2456, 2457, 2461, 2462, 2463, 2467, 2471, 2477, 2481, 2483, 2488, 2489, 2505, 2513, 2514, 2520, 2524, 2534, 2536, 2545, 2547, 2552, 2553, 2554, 2556, 2559, 2565, 2572, 2579, 2583, 2592, 2601, 2604, 2605, 2610, 2614, 2617, 2624, 2637, 2641, 2643, 2646, 2670, 2674, 2677, 2683, 2689, 2694, 2698, 2699, 2700, 2702, 2709, 2711, 2719, 2722, 2723, 2731, 2737, 2738, 2739, 2743, 2745, 2746, 2750, 2752, 2754, 2756, 2776, 2778, 2780, 2782, 2785, 2791, 2798, 2804, 2807, 2808, 2809, 2829, 2830, 2833, 2835, 2838, 2840, 2844, 2847, 2849, 2854, 2882, 2884, 2895, 2899, 2903, 2910, 2912, 2914, 2919, 2922, 2930, 2931, 2935, 2936, 2940, 2945, 2948, 2949, 2951, 2956, 2958, 2961, 2964, 2971, 2972, 2973, 2982, 2985, 2987, 2990, 2992, 3001, 3004, 3005, 3007, 3011, 3013, 3018, 3023, 3029, 3032, 3034, 3047, 3048, 3049, 3057, 3064, 3065, 3068, 3071, 3073, 3074, 3080, 3088, 3089, 3090, 3093, 3095, 3096, 3100, 3102, 3105, 3109, 3111, 3114, 3120, 3124, 3125, 3133, 3134, 3139, 3140, 3145, 3146, 3176, 3181, 3185, 3193, 3196, 3197, 3202, 3204, 3208, 3212, 3213, 3221, 3244, 3249, 3250, 3254, 3255, 3262, 3263, 3269, 3274, 3280, 3281, 3289, 3292, 3296, 3297, 3299, 3301, 3328, 3329, 3331, 3344, 3347, 3360, 3362, 3366, 3373, 3376, 3377, 3380, 3382, 3383, 3387, 3389, 3390, 3392, 3402, 3405, 3408, 3416, 3423, 3435, 3443, 3447, 3448, 3450, 3456, 3465, 3470, 3472, 3490, 3491, 3512, 3520, 3524, 3527, 3529, 3530, 3555, 3556, 3558, 3563, 3567, 3569, 3577, 3578, 3579, 3580, 3582, 3584, 3591, 3592, 3597, 3608, 3609, 3611, 3623, 3628, 3637, 3638, 3639, 3653, 3657, 3658, 3671, 3673, 3685, 3686, 3687, 3689, 3697, 3704, 3706, 3707, 3708, 3713, 3724, 3727, 3729, 3730, 3737, 3738, 3742, 3748, 3751, 3754, 3755, 3757, 3758, 3763, 3764, 3770, 3772, 3776, 3779, 3786, 3791, 3792, 3798, 3803, 3806, 3807, 3811, 3812, 3814, 3817, 3823, 3830, 3834, 3860, 3864, 3881, 3883, 3886, 3894, 3895, 3897, 3899, 3903, 3908, 3910, 3911, 3912, 3923, 3924, 3927, 3928, 3931, 3933, 3950, 3952, 3954, 3955, 3968, 3970, 3971, 3976, 3978, 3984, 3992, 3998, 4002, 4007, 4008, 4009, 4012, 4015, 4020, 4023, 4029, 4038, 4041, 4043, 4046, 4047, 4048, 4049, 4059, 4062, 4066, 4067, 4072, 4073, 4079, 4088, 4099, 4100, 4102, 4109, 4111, 4119, 4121, 4128, 4139, 4145, 4148, 4151, 4162, 4168, 4180, 4184, 4189, 4194, 4202, 4203, 4204, 4207, 4213, 4214, 4218, 4229, 4230, 4233, 4237, 4238, 4241, 4245, 4247, 4248, 4253, 4262, 4271, 4272, 4289, 4292, 4299, 4303, 4304, 4311, 4312, 4314, 4322, 4326, 4328, 4338, 4348, 4352, 4353, 4358, 4363, 4364, 4366, 4368, 4374, 4376, 4377, 4384, 4394, 4397, 4401, 4402, 4403, 4404, 4406, 4420, 4428, 4437, 4439, 4441, 4452, 4464, 4465, 4470, 4473, 4475, 4486, 4496, 4499, 4505, 4507, 4512, 4515, 4528, 4531, 4533, 4547, 4548, 4564, 4567, 4568, 4580, 4581, 4582, 4590, 4599, 4602, 4604, 4622, 4623, 4625, 4642, 4648, 4655, 4658, 4674, 4678, 4682, 4685, 4702, 4703, 4707, 4711, 4715, 4717, 4719, 4722, 4724, 4731, 4736, 4739, 4742, 4743, 4744, 4754, 4756, 4757, 4769, 4772, 4779, 4785, 4797, 4805, 4809, 4813, 4814, 4827, 4831, 4832, 4835, 4838, 4840, 4843, 4852, 4853, 4859, 4869, 4875, 4878, 4880, 4886, 4894, 4895, 4898, 4901, 4911, 4912, 4916, 4920, 4928, 4932, 4940, 4943, 4953, 4967, 4975, 4978, 4982, 4991, 4992, 4996, 5008, 5014, 5016, 5023, 5025, 5027, 5032, 5033, 5035, 5043, 5044, 5049, 5050, 5073, 5078, 5080, 5083, 5096, 5108, 5123, 5128, 5132, 5137, 5139, 5140, 5142, 5157, 5158, 5163, 5164, 5171, 5178, 5180, 5181, 5182, 5185, 5189, 5190, 5195, 5198, 5201, 5208, 5210, 5211, 5212, 5216, 5217, 5218, 5226, 5235, 5241, 5253, 5258, 5271, 5280, 5283, 5288, 5292, 5299, 5300, 5304, 5306, 5307, 5309, 5318, 5320, 5321, 5327, 5331, 5334, 5337, 5341, 5342, 5343, 5344, 5346, 5351, 5352, 5357, 5366, 5368, 5377, 5380, 5384, 5391, 5393, 5398, 5399, 5400, 5401, 5404, 5406, 5411, 5414, 5418, 5422, 5428, 5430, 5440, 5441, 5444, 5445, 5449, 5451, 5453, 5457, 5462, 5464, 5465, 5467, 5471, 5478, 5480, 5484, 5496, 5499, 5515, 5518, 5521, 5522, 5523, 5527, 5528, 5533, 5535, 5539, 5542, 5562, 5577, 5581, 5587, 5591, 5592, 5593, 5597, 5598, 5628, 5629, 5630, 5631, 5635, 5636, 5641, 5643, 5646, 5647, 5654, 5655, 5698, 5699, 5701, 5702, 5728, 5729, 5730, 5731, 5732, 5734, 5735, 5736, 5737, 5738, 5739, 5740, 5741, 5742, 5743, 5744, 5745, 5755, 5761, 5763, 5766, 5770, 5771, 5772, 5784, 5792, 5793, 5796, 5811, 5812, 5824, 5833, 5835, 5837, 5840, 5842, 5843, 5845, 5852, 5854, 5856, 5860, 5864, 5868, 5876, 5890, 5896, 5905, 5906, 5910, 5914, 5923, 5927, 5975, 5982, 5988, 5989, 5993, 5994, 5997, 6008, 6009, 6010, 6014, 6022, 6024, 6032, 6033, 6034, 6064, 6065, 6067, 6069, 6076, 6081, 6094, 6101, 6122, 6139, 6147, 6149, 6153, 6154, 6156, 6158, 6160, 6162, 6163, 6164, 6168, 6169, 6187, 6188, 6192, 6195, 6198, 6208, 6209, 6210, 6211, 6212, 6213, 6214, 6215, 6216, 6217, 6218, 6219, 6220, 6221, 6222, 6223, 6224, 6225, 6226, 6227, 6228, 6231, 6232, 6235, 6238, 6240, 6241, 6252, 6253, 6254, 6255, 6256, 6257, 6258, 6265, 6269, 6270, 6276, 6278, 6279, 6285, 6291, 6297, 6304, 6317, 6320, 6322, 6326, 6329, 6333, 6338, 6339, 6340, 6341, 6344, 6345, 6350, 6351, 6352, 6353, 6354, 6356, 6358, 6359, 6360, 6361, 6364, 6365, 6366, 6368, 6369, 6372, 6374, 6375, 6376, 6377, 6379, 6380, 6381, 6382, 6383, 6385, 6388, 6389, 6391, 6393, 6395, 6399, 6404, 6405, 6420, 6423, 6426, 6427, 6429, 6434, 6441, 6447, 6451, 6452, 6453, 6454, 6455, 6456, 6478, 6479, 6487, 6492, 6496, 6498, 6500, 6504, 6506, 6510, 6511, 6516, 6520, 6522, 6523, 6526, 6545, 6548, 6554, 6555, 6561, 6563, 6567, 6585, 6586, 6591, 6592, 6593, 6595, 6608, 6610, 6611, 6616, 6618, 6619, 6621, 6622, 6623, 6624, 6625, 6626, 6636, 6644, 6645, 6656, 6657, 6664, 6665, 6666, 6667, 6668, 6669, 6671, 6672, 6673, 6674, 6675, 6677, 6678, 6679, 6686, 6687, 6691, 6703, 6707, 6709, 6714, 6715, 6737, 6740, 6742, 6744, 6746, 6751, 6752, 6760, 6765, 6766, 6769, 6770, 6777, 6778, 6779, 6788, 6789, 6790, 6798, 6800, 6814, 6815, 6818, 6819, 6825, 6831, 6832, 6835, 6836, 6837, 6838, 6839, 6840, 6841, 6842, 6843, 6844, 6845, 6848, 6850, 6851, 6854, 6856, 6857, 6858, 6859, 6860, 6862, 6863, 6865, 6866, 6868, 6869, 6870, 6871, 6873, 6875, 6876, 6877, 6888, 6893, 6894, 6895, 6898, 6899, 6904, 6906, 6907, 6910, 6920, 6932, 6938, 6939, 6944, 6945, 6946, 6947, 6948, 6949, 6950, 6951, 6953, 6955, 6958, 6959, 6960, 6961, 6967, 6972, 6975, 6981, 6983, 6988, 6998, 6999, 7001, 7009, 7012, 7021, 7031, 7032, 7033, 7034, 7037, 7041, 7047, 7055, 7057, 7060, 7061, 7062, 7063, 7064, 7075, 7076, 7078, 7085, 7094, 7099, 7100, 7101, 7111, 7126, 7132, 7133, 7140, 7141, 7146, 7147, 7148, 7151, 7161, 7166, 7169, 7172, 7176, 7177, 7178, 7183, 7184, 7203, 7204, 7206, 7207, 7208, 7209, 7210, 7211, 7212, 7213, 7214, 7215, 7216, 7217, 7218, 7219, 7220, 7221, 7226, 7227, 7231, 7232, 7233, 7234, 7235, 7236, 7237, 7238, 7281, 7282, 7283, 7284, 7285, 7286, 7287, 7288, 7291, 7293, 7296, 7297, 7298, 7300, 7302, 7303, 7304, 7317, 7319, 7320, 7322, 7323, 7324, 7336, 7337, 7340, 7341, 7354, 7355, 7356, 7367, 7368, 7369, 7370, 7371, 7372, 7373, 7374, 7375, 7381, 7382, 7383, 7384, 7385, 7386, 7387, 7388, 7389, 7396, 7407, 7408, 7409, 7410, 7411, 7412, 7413, 7414, 7415, 7416, 7417, 7418, 7420, 7422, 7423, 7424, 7425, 7426, 7429, 7430, 7431, 7432, 7433, 7434, 7464, 7467, 7469, 7480, 7481, 7482, 7483, 7484, 7485, 7486, 7495, 7496, 7497, 7498, 7499, 7507, 7508, 7509, 7511, 7517, 7521, 7523, 7575, 7576, 7577, 7582, 7597, 7598, 7600, 7607, 7616, 7619, 7620, 7637, 7640, 7643, 7644, 7645, 7648, 7649, 7650, 7657, 7660, 7664, 7669, 7681, 7691, 7706, 7715, 7718, 7719, 7723, 7732, 7733, 7734, 7735, 7736, 7741, 7748, 7752, 7753, 7759, 7761, 7767, 7776, 7785, 7786, 7790, 7792, 7817, 7822, 7824, 7825, 7828, 7836, 7847, 7859, 7860, 7861, 7869, 7875, 7876, 7886, 7894, 7895, 7896, 7897, 7902, 7903, 7920, 7921, 7923, 7929, 7933, 7934, 7935, 7937, 7940, 7942, 7943, 7945, 7963, 7971, 7984, 7989, 7991, 7993, 7994, 7998, 8000, 8001, 8002, 8003, 8004, 8010, 8011, 8013, 8014, 8015, 8017, 8019, 8027, 8029, 8036, 8037, 8038, 8047, 8050, 8063, 8068, 8070, 8072, 8074, 8080, 8088, 8090, 8091, 8092, 8100, 8113, 8114, 8115, 8117, 8121, 8122, 8123, 8125, 8129, 8130, 8135, 8145, 8146, 8151, 8161, 8173, 8174, 8175, 8177, 8178, 8182, 8185, 8186, 8187, 8238, 8239, 8240, 8241, 8242, 8243, 8244, 8245, 8246, 8247, 8248, 8249, 8250, 8252, 8255, 8256, 8257, 8258, 8259, 8260, 8261, 8262, 8263, 8285, 8287, 8299, 8300, 8301, 8302, 8303, 8304, 8305, 8306, 8319, 8320, 8321, 8323, 8324, 8326, 8327, 8328, 8329, 8330, 8345, 8363, 8383, 8384, 8385, 8388, 8408, 8419, 8421, 8422, 8423, 8424, 8425, 8426, 8427, 8428, 8440, 8441, 8442, 8443, 8444, 8449, 8452, 8453, 8454, 8471, 8472, 8488, 8491, 8492, 8493, 8494, 8495, 8496, 8497, 8498, 8505, 8506, 8507, 8508, 8509, 8510, 8511, 8512, 8513, 8531, 8532, 8533, 8534, 8546, 8549, 8550, 8551, 8552, 8553, 8554, 8555, 8558, 8559, 8590, 8591, 8592, 8598, 8602, 8607, 8627, 8628, 8629, 8630, 8631, 8632, 8641, 8642, 8643, 8644, 8645, 8646, 8647, 8648, 8649, 8650, 8651, 8652, 8660, 8661, 8662, 8663, 8664, 8665, 8666, 8669, 8670, 8671, 8674, 8677, 8691, 8692, 8693, 8694, 8695, 8696, 8697, 8698, 8702, 8703, 8769, 8770, 8771, 8772, 8773, 8774, 8775, 8776, 8777, 8778, 8794, 8795, 8796, 8797, 8798, 8799, 8800, 8801, 8827, 8828, 8829, 8830, 8831, 8832, 8833, 8834, 8835, 8836, 8837, 8838, 8839, 8842, 8843, 8844, 8845, 8846, 8847, 8848, 8849, 8924, 8925, 8926, 8927, 8928, 8939, 8941, 8942, 8951, 8956, 8957, 8958, 8959, 8960, 8961, 8962, 8965, 8966, 8969, 8976, 8981, 8985, 8989, 8990, 8991, 8992, 8993, 8994, 8995, 8996, 8997, 8998, 8999, 9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9067, 9068, 9069, 9070, 9071, 9072, 9073, 9099, 9100, 9101, 9102, 9103, 9106, 9107, 9108, 9109, 9110, 9112, 9113, 9114, 9115, 9118, 9125, 9126, 9127, 9128, 9129, 9130, 9131, 9132, 9133, 9134, 9135, 9136, 9137, 9138, 9176, 9191, 9197, 9199, 9205, 9206, 9207, 9208, 9209, 9210, 9215, 9216, 9237, 9238, 9239, 9240, 9241, 9242, 9243, 9245, 9246, 9247, 9248, 9249, 9250, 9251, 9252, 9253, 9254, 9255, 9256, 9257, 9258, 9263, 9264, 9265, 9266, 9267, 9268, 9269, 9270, 9271, 9272, 9273, 9274, 9275, 9276, 9277, 9278, 9279, 9280, 9281, 9296, 9298, 9299, 9300, 9301, 9302, 9303, 9304, 9305, 9306, 9322, 9323, 9324, 9328, 9329, 9330, 9331, 9332, 9333, 9334, 9335, 9336, 9346, 9348, 9349, 9350, 9351, 9359, 9360, 9361, 9362, 9363, 9364, 9365, 9366, 9369, 9382, 9383, 9385, 9398, 9399, 9412, 9446, 9453, 9454, 9457, 9479, 9480, 9481, 9482, 9483, 9484, 9485, 9486, 9487, 9488, 9489, 9490, 9491, 9492, 9493, 9494, 9495, 9496, 9497, 9498, 9508, 9509, 9510, 9511, 9512, 9513, 9514, 9515, 9516, 9517, 9518, 9519, 9520, 9521, 9522, 9523, 9524, 9525, 9526, 9527, 9528, 9529, 9530, 9531, 9532, 9533, 9534, 9535, 9536, 9537, 9538, 9539, 9540, 9541, 9542, 9543, 9544, 9545, 9546, 9547, 9548, 9549, 9566, 9567, 9568, 9569, 9570, 9571, 9607, 9608, 9616, 9617, 9618, 9619, 9620, 9621, 9634, 9635, 9636, 9649, 9650, 9651, 9705, 9706, 9734, 9737, 9739, 9740, 9741, 9742, 9743, 9744, 9745, 9746, 9747, 9748, 9749, 9750, 9751, 9752, 9753, 9766, 9767, 9768, 9769, 9770, 9771, 9772, 9773, 9774, 9789, 9795, 9801, 9839, 9841, 9850, 9891, 9892, 9893, 9894, 9895, 9896, 9897, 9916, 9917, 9918, 9919, 9920, 9921, 9922, 9923, 9924, 9925, 9926, 9927, 9928, 9962, 9963, 9964, 9998, 10001, 10002, 10003, 10004, 10005, 10006, 10007, 10008, 10009, 10010, 10014, 10017, 10018, 10019, 10020, 10024, 10031, 10033, 10035, 10058, 10059, 10060, 10075, 10123, 10124, 10125, 10126, 10135, 10145, 10147, 10148, 10149, 10151, 10152, 10166, 10177, 10178, 10183, 10184, 10190, 10191, 10192, 10193, 10194, 10195, 10196, 10197, 10198, 10199, 10200, 10201, 10202, 10203, 10204, 10206, 10217, 10218, 10219, 10220, 10221, 10222, 10223, 10235, 10236, 10237, 10238, 10239, 10240, 10241, 10242, 10243, 10289, 10290, 10293, 10294, 10296, 10297, 10310, 10311, 10312, 10313, 10314, 10315, 10316, 10319, 10320, 10321, 10322, 10323, 10324, 10325, 10327, 10330, 10331, 10332, 10333, 10340, 10341, 10342, 10343, 10344, 10345, 10346, 10347, 10349, 10350, 10351, 10356, 10375, 10389, 10412, 10449, 10453, 10479, 10495, 10496, 10497, 10498, 10511, 10512, 10513, 10518, 10519, 10521, 10522, 10523, 10544, 10545, 10546, 10547, 10548, 10549, 10550, 10551, 10552, 10553, 10554, 10562, 10572, 10573, 10574, 10595, 10597, 10598, 10599, 10603, 10604, 10607, 10610, 10611, 10645, 10646, 10647, 10648, 10679, 10680, 10681, 10684, 10692, 10693, 10695, 10698, 10703, 10705, 10732, 10733, 10734, 10735, 10747, 10748, 10749, 10750, 10751, 10752, 10753, 10754, 10759, 10765, 10767, 10768, 10769, 10770, 10771, 10772, 10773, 10774, 10775, 10776, 10777, 10778, 10779, 10780, 10781, 10782, 10783, 10784, 10785, 10786, 10787, 10788, 10792, 10795, 10796, 10797, 10798, 10819, 10820, 10822, 10823, 10824, 10825, 10826, 10827, 10829, 10830, 10839, 10840, 10841, 10842, 10843, 10844, 10845, 10846, 10847, 10848, 10849, 10850, 10855, 10858, 10859, 10860, 10861, 10862, 10863, 10864, 10865, 10866, 10867, 10868, 10869, 10870, 10873, 10880, 10886, 10898, 10899, 10900, 10901, 10902, 10903, 10916, 10919, 10920, 10921, 10922, 10924, 10925, 10926, 10931, 10942, 10943, 10944, 10945, 10946, 10947, 10948, 10949, 10950, 10951, 10952, 10954, 10958, 10959, 10960, 10966, 10967, 10968, 10969, 10970, 10971, 10973, 10974, 10978, 10981, 10982, 10983, 10984, 10985, 10986, 10987, 10988, 10989, 10995, 10996, 10997, 10998, 11002, 11003, 11004, 11005, 11007, 11021, 11035, 11049, 11050, 11051, 11052, 11053, 11054, 11059, 11060, 11061, 11062, 11080, 11088, 11089, 11090, 11091, 11092, 11093, 11094, 11110, 11115, 11124, 11128, 11132, 11155, 11158, 11171, 11172, 11173, 11174, 11175, 11181, 11193, 11194, 11195, 11198, 11207, 11208, 11210, 11218, 11220, 11246, 11247, 11248, 11252, 11261, 11262, 11263, 11264, 11265, 11292, 11340, 11350, 11351, 11352, 11380, 11383, 11386, 11387, 11388, 11389, 11390, 11391, 11392, 11395, 11396, 11397, 11398, 11425, 11426, 11427, 11428, 11440, 11441, 11442, 11453, 11454, 11455, 11456, 11457, 11458, 11459, 11460, 11461, 11462, 11463, 11474, 11475, 11480, 11482, 11483, 11484, 11486, 11487, 11492, 11494, 11495, 11500, 11519, 11534, 11566, 11567, 11570, 11572, 11575, 11577, 11584, 11585, 11587, 11601, 11602, 11603, 11604, 11605, 11606, 11607, 11609, 11613, 11618, 11619, 11627, 11630, 11641, 11642, 11647, 11648, 11649, 11650, 11655, 11656, 11657, 11658, 11659, 11660, 11661, 11662, 11677, 11683, 11684, 11685, 11686, 11687, 11688, 11690, 11693, 11699, 11704, 11711, 11716, 11717, 11718, 11726, 11749, 11773, 11777, 11794, 11798, 11799, 11810, 11811, 11813, 11817, 11818, 11819, 11825, 11826, 11834, 11835, 11842, 11844, 11845, 11852, 11855, 11856, 11857, 11860, 11870, 11871, 11877, 11878, 11879, 11880, 11881, 11882, 11883, 11884, 11889, 11893, 11894, 11895, 11896, 11907, 11909, 11910, 11911, 11912, 11913, 11914, 11916, 11917, 11918, 11919, 11920, 11938, 11950, 11951, 11952, 11953, 11954, 11959, 11961, 11962, 11963, 11964, 11970, 11971, 11972, 11973, 11977, 11979, 11980, 11981, 11982, 11983, 11984, 11985, 11986, 11987, 11988, 11989, 11990, 11991, 11993, 11994, 11995, 11996, 11997, 12004, 12005, 12011, 12015, 12016, 12017, 12018, 12019, 12020, 12021, 12022, 12023, 12024, 12025, 12026, 12031, 12032, 12057, 12058, 12059, 12061, 12063, 12073, 12074, 12075, 12076, 12077, 12078, 12079, 12080, 12081, 12093, 12094, 12106, 12107, 12109, 12110, 12113, 12114, 12115, 12116, 12126, 12127, 12156, 12157, 12158, 12161, 12163, 12164, 12170, 12176, 12187, 12188, 12189, 12190, 12191, 12192, 12193, 12194, 12195, 12199, 12210, 12221, 12222, 12232, 12233, 12234, 12236, 12237, 12238, 12243, 12253, 12258, 12259, 12260, 12261, 12262, 12263, 12264, 12265, 12266, 12273, 12274, 12275, 12276, 12277, 12278, 12287, 12288, 12289, 12290, 12291, 12292, 12321, 12322, 12323, 12324, 12325, 12331, 12333, 12334, 12340, 12341, 12343, 12344, 12346, 12347, 12364, 12365, 12366, 12372, 12374, 12375, 12376, 12378, 12385, 12388, 12400, 12403, 12409, 12410, 12415, 12419, 12421, 12422, 12423, 12426, 12429, 12436, 12440, 12443, 12448, 12450, 12465, 12495, 12508, 12509, 12531, 12533, 12538, 12542, 12543, 12545, 12549, 12559, 12567, 12568, 12569, 12585, 12601, 12602, 12603, 12604, 12605, 12606, 12607, 12608, 12609, 12610, 12611, 12613, 12625, 12627, 12628, 12632, 12634, 12635, 12638, 12639, 12642, 12643, 12644, 12658, 12663, 12664, 12665, 12666, 12667, 12669, 12671, 12673, 12674, 12675, 12676, 12706, 12717, 12725, 12730, 12731, 12732, 12733, 12734, 12735, 12736, 12740, 12741, 12742, 12744, 12762, 12763, 12778, 12779, 12780, 12791, 12792, 12793, 12794, 12795, 12796, 12797, 12803, 12810, 12815, 12820, 12821, 12822, 12823, 12824, 12825, 12826, 12827, 12834, 12842, 12843, 12844, 12845, 12846, 12847, 12855, 12861, 12862, 12864, 12868, 12877, 12882, 12883, 12884, 12885, 12897, 12898, 12899, 12900, 12901, 12902, 12903, 12935, 12938, 12939, 12945, 12950, 12955, 12957, 12959, 12987, 13004, 13005, 13006, 13035, 13057, 13058, 13059, 13060, 13061, 13095, 13096, 13109, 13115, 13149, 13160, 13166, 13172, 13174, 13179, 13180, 13187, 13188, 13189, 13190, 13192, 13193, 13197, 13207, 13212, 13231, 13238, 13239, 13240, 13241, 13242, 13243, 13244, 13245, 13246, 13247, 13248, 13249, 13250, 13251, 13252, 13255, 13257, 13258, 13259, 13260, 13262, 13263, 13264, 13267, 13268, 13372, 13373, 13374, 13375, 13376, 13377, 13378, 13379, 13380, 13381, 13382, 13383, 13384, 13385, 13386, 13387, 13388, 13389, 13390, 13391, 13392, 13393, 13394, 13395, 13396, 13397, 13398, 13399, 13400, 13401, 13402, 13403, 13404, 13405, 13406, 13407, 13408, 13409, 13410, 13411, 13412, 13413, 13414, 13415, 13416, 13417, 13418, 13419, 13420, 13421, 13423, 13424, 13425, 13435, 13436, 13437, 13438, 13440, 13441, 13445, 13463, 13464, 13465, 13468, 13469, 13470, 13471, 13475, 13476, 13477, 13478, 13479, 13480, 13481, 13482, 13483, 13484, 13485, 13486, 13492, 13493, 13494, 13495, 13496, 13497, 13506, 13507, 13508, 13509, 13522, 13523, 13525, 13526, 13527, 13528, 13529, 13530, 13531, 13532, 13533, 13534, 13542, 13585, 13586, 13592, 13593, 13601, 13602, 13603, 13604, 13605, 13606, 13607, 13608, 13609, 13610, 13611, 13612, 13613, 13614, 13615, 13616, 13617, 13618, 13624, 13625, 13626, 13627, 13628, 13629, 13630, 13631, 13632, 13633, 13634, 13635, 13636, 13637, 13638, 13639, 13640, 13641, 13659, 13660, 13661, 13662, 13663, 13664, 13665, 13666, 13667, 13674, 13675, 13676, 13710, 13712, 13713, 13727, 13728, 13729, 13730, 13731, 13732, 13733, 13734, 13769, 13770, 13780, 13781, 13782, 13783, 13784, 13785, 13786, 13787, 13788, 13789, 13825, 13829, 13830, 13831, 13832, 13833, 13834, 13835, 13836, 13839, 13840, 13858, 13863, 13865, 13873, 13874, 13875, 13876, 13877, 13878, 13879, 13880, 13881, 13882, 13896, 13897, 13900, 13901, 13902, 13903, 13905, 13931, 13935, 13939, 13944, 13945, 13946, 13947, 13951, 13952, 13953, 13960, 13967, 13977, 13978, 13982, 13983, 13986, 13991, 13992, 13993, 13994, 13996, 13997, 14013, 14015, 14016, 14017, 14020, 14022, 14023, 14024, 14025, 14026, 14029, 14030, 14031, 14032, 14033, 14034, 14035, 14036, 14037, 14038, 14039, 14040, 14041, 14042, 14044, 14045, 14046, 14048, 14057, 14058, 14059, 14060, 14061, 14062, 14063, 14064, 14065, 14066, 14067, 14068, 14069, 14070, 14073, 14083, 14086, 14087, 14090, 14091, 14092, 14094, 14096, 14098, 14107, 14110, 14111, 14112, 14113, 14114, 14115, 14116, 14117, 14118, 14119, 14120, 14123, 14124, 14125, 14126, 14127, 14128, 14133, 14143, 14144, 14145, 14157, 14159, 14160, 14168, 14174, 14176, 14178, 14182, 14187, 14188, 14189, 14190, 14193, 14194, 14195, 14196, 14197, 14198, 14199, 14200, 14206, 14211, 14212, 14213, 14214, 14215, 14216, 14217, 14218, 14222, 14223, 14224, 14226, 14227, 14228, 14235, 14236, 14237, 14238, 14239, 14240, 14241, 14242, 14243, 14244, 14245, 14246, 14247, 14248, 14249, 14255, 14256, 14257, 14258, 14259, 14260, 14261, 14262, 14263, 14267, 14269, 14270, 14271, 14272, 14274, 14275, 14276, 14277, 14278, 14279, 14280, 14281, 14282, 14283, 14284, 14285, 14286, 14287, 14288, 14289, 14290, 14294, 14295, 14296, 14297, 14302, 14303, 14305, 14306, 14307, 14308, 14309, 14310, 14311, 14312, 14313, 14314, 14315, 14316, 14317, 14318, 14319, 14320, 14321, 14322, 14333, 14335, 14336, 14337, 14338, 14339, 14340, 14341, 14342, 14347, 14348, 14349, 14353, 14359, 14360, 14361, 14362, 14363, 14364, 14365, 14366, 14369, 14373, 14374, 14375, 14376, 14377, 14378, 14379, 14380, 14381, 14387, 14389, 14390, 14391, 14392, 14393, 14394, 14396, 14397, 14398, 14402, 14403, 14405, 14407, 14413, 14414, 14416, 14432, 14433, 14450, 14451, 14452, 14453, 14454, 14455, 14458, 14459, 14460, 14472, 14473, 14477, 14483, 14484, 14485, 14486, 14487, 14488, 14490, 14491, 14494, 14495, 14496, 14497, 14498, 14499, 14500, 14501, 14502, 14503, 14505, 14506, 14513, 14519, 14523, 14531, 14548, 14549, 14550, 14554, 14555, 14556, 14559, 14560, 14563, 14571, 14576, 14583, 14593, 14594, 14595, 14596, 14601, 14606, 14610, 14617, 14619, 14620, 14626, 14638, 14644, 14645, 14646, 14647, 14649, 14650, 14662, 14670, 14671, 14674, 14675, 14688, 14689, 14690, 14691, 14710, 14715, 14716, 14732, 14733, 14734, 14735, 14736, 14737, 14742, 14747, 14750, 14752, 14753, 14754, 14756, 14757, 14767, 14768, 14771, 14777, 14779, 14780, 14787, 14788, 14789, 14791, 14793, 14794, 14795, 14797, 14799, 14801, 14803, 14804, 14805, 14807, 14808, 14809, 14811, 14812, 14813, 14814, 14815, 14816, 14817, 14818, 14819, 14820, 14821, 14832, 14837, 14838, 14839, 14840, 14841, 14842, 14843, 14844, 14845, 14846, 14847, 14848, 14849, 14850, 14851, 14852, 14853, 14860, 14874, 14875, 14877, 14878, 14879, 14884, 14885, 14890, 14892, 14894, 14899, 14905, 14906, 14910, 14911, 14912, 14913, 14914, 14915, 14916, 14917, 14920, 14921, 14922, 14923, 14924, 14925, 14931, 14937, 14942, 14943, 14948, 14951, 14952, 14953, 14954, 14972, 14973, 14974, 14975, 14976, 14996, 15000, 15014, 15015, 15016, 15017, 15022, 15023, 15027, 15028, 15031, 15032, 15033, 15034, 15035, 15038, 15040, 15041, 15046, 15048, 15055, 15063, 15065, 15066, 15067, 15068, 15069, 15070, 15071, 15072, 15073, 15075, 15076, 15077, 15078, 15079, 15080, 15085, 15086, 15087, 15088, 15089, 15090, 15105, 15107, 15108, 15114, 15116, 15118, 15121, 15131, 15135, 15136, 15143, 15151, 15155, 15162, 15163, 15166, 15167, 15168, 15169, 15170, 15171, 15172, 15173, 15174, 15185, 15203, 15213, 15214, 15215, 15220, 15221, 15233, 15234, 15235, 15236, 15238, 15239, 15241, 15242, 15243, 15244, 15245, 15246, 15247, 15249, 15252, 15255, 15257, 15262, 15267, 15273, 15274, 15275, 15279, 15280, 15281, 15282, 15284, 15289, 15291, 15292, 15295, 15296, 15300, 15301, 15302, 15303, 15304, 15322, 15323, 15325, 15327, 15329, 15333, 15335, 15344, 15345, 15351, 15353, 15359, 15365, 15369, 15377, 15378, 15379, 15382, 15383, 15385, 15386, 15388, 15389, 15391, 15392, 15394, 15398, 15401, 15403, 15404, 15405, 15407, 15411, 15414, 15416, 15420, 15421, 15422, 15423, 15424, 15425, 15426, 15427, 15428, 15429, 15430, 15431, 15432, 15433, 15434, 15435, 15436, 15437, 15438, 15439, 15440, 15441, 15442, 15443, 15446, 15447, 15448, 15449, 15450, 15451, 15452, 15453, 15454, 15455, 15456, 15457, 15475, 15476, 15478, 15481, 15484, 15485, 15486, 15488, 15489, 15490, 15491, 15492, 15493, 15494, 15495, 15496, 15505, 15506, 15520, 15521, 15522, 15523, 15524, 15525, 15527, 15531, 15532, 15538, 15543, 15544, 15546, 15547, 15548, 15555, 15556, 15557, 15558, 15559, 15560, 15562, 15587, 15588, 15595, 15610, 15611, 15612, 15613, 15614, 15622, 15623, 15624, 15625, 15626, 15628, 15629, 15630, 15631, 15632, 15633, 15634, 15635, 15636, 15637, 15646, 15655, 15681, 15695, 15697, 15706, 15711, 15712, 15724, 15729, 15736, 15737, 15739, 15740, 15741, 15742, 15743, 15744, 15745, 15746, 15749, 15750, 15751, 15752, 15769, 15771, 15780, 15781, 15786, 15787, 15788, 15789, 15790, 15791, 15793, 15794, 15798, 15802, 15805, 15806, 15807, 15811, 15812, 15813, 15816, 15817, 15818, 15819, 15820, 15822, 15823, 15826, 15835, 15841, 15842, 15843, 15844, 15845, 15846, 15847, 15848, 15849, 15850, 15851, 15852, 15853, 15854, 15855, 15856, 15857, 15858, 15859, 15860, 15861, 15862, 15863, 15864, 15865, 15866, 15867, 15868, 15869, 15870, 15871, 15873, 15874, 15875, 15917, 15918, 15919, 15920, 15922, 15923, 15925, 15926, 15927, 15928, 15929, 15930, 15931, 15932, 15935, 15936, 15937, 15938, 15939, 15940, 15945, 15946, 15947, 15948, 15953, 15954, 15958, 15963, 15964, 15965, 15966, 15970, 15971, 15972, 15973, 15974, 15977, 15979, 15980, 15981, 15982, 15983, 15984, 15985, 15986, 15987, 15988, 15989, 15990, 15991, 15992, 15993, 15994, 15995, 15996, 15998, 15999, 16000, 16001, 16002, 16003, 16004, 16005, 16006, 16007, 16008, 16010, 16011, 16012, 16013, 16014, 16015, 16016, 16017, 16026, 16027, 16028, 16029, 16039, 16048, 16049, 16054, 16055, 16056, 16057, 16058, 16059, 16060, 16061, 16062, 16068, 16069, 16070, 16071, 16087, 16088, 16089, 16090, 16091, 16092, 16094, 16095, 16096, 16098, 16099, 16100, 16101, 16102, 16103, 16107, 16110, 16113, 16115, 16120, 16121, 16143, 16144, 16149, 16150, 16181, 16183, 16189, 16193, 16194, 16195, 16196, 16200, 16201, 16202, 16203, 16204, 16205, 16206, 16214, 16215, 16216, 16217, 16223, 16227, 16228, 16238, 16241, 16246, 16250, 16259, 16260, 16268, 16276, 16279, 16282, 16283, 16284, 16285, 16286, 16292, 16294, 16295, 16296, 16301, 16313, 16315, 16316, 16317, 16318, 16319, 16320, 16321, 16331, 16332, 16335, 16338, 16347, 16348, 16356, 16359, 16363, 16366, 16367, 16368, 16369, 16370, 16373, 16379, 16385, 16386, 16387, 16389, 16400, 16412, 16416, 16429, 16437, 16443, 16456, 16457, 16460, 16492, 16493, 16494, 16495, 16496, 16500, 16501, 16504, 16510, 16511, 16513, 16514, 16515, 16518, 16519, 16521, 16523, 16526, 16529, 16530, 16532, 16539, 16540, 16542, 16548, 16549, 16552, 16554, 16559, 16560, 16562, 16565, 16574, 16575, 16576, 16577, 16578, 16579, 16580, 16581, 16582, 16583, 16585, 16586, 16587, 16588, 16589, 16590, 16591, 16592, 16593, 16598, 16599, 16600, 16601, 16602, 16603, 16604, 16605, 16606, 16607, 16608, 16609, 16611, 16612, 16613, 16614, 16615, 16623, 16624, 16628, 16632, 16636, 16637, 16641, 16643, 16655, 16656, 16660, 16663, 16664, 16667, 16671, 16674, 16675, 16677, 16678, 16679, 16680, 16683, 16685, 16686, 16701, 16706, 16709, 16710, 16713, 16714, 16722, 16723, 16732, 16733, 16737, 16738, 16739, 16755, 16756, 16759, 16771, 16775, 16784, 16785, 16811, 16812, 16813, 16814, 16815, 16818, 16830, 16832, 16855, 16857, 16861, 16862, 16864, 16865, 16866, 16867, 16868, 16869, 16870, 16871, 16872, 16891, 16902, 16903, 16905, 16906, 16907, 16911, 16922, 16923, 16924, 16941, 16942, 16943, 16944, 16945, 16946, 16947, 16948, 16949, 16950, 16951, 16952, 16953, 16959, 16960, 16961, 16964, 16965, 16966, 16967, 16968, 16973, 16975, 16977, 16984, 16985, 16986, 16987, 16988, 16989, 16990, 16991, 16992, 16993, 16994, 16995, 16996, 16997, 16998, 16999, 17000, 17001, 17002, 17003, 17004, 17008, 17009, 17010, 17011, 17012, 17013, 17014, 17015, 17016, 17017, 17018, 17019, 17020, 17021, 17022, 17023, 17024, 17025, 17026, 17027, 17028, 17029, 17031, 17037, 17038, 17040, 17041, 17042, 17043, 17044, 17045, 17046, 17047, 17048, 17049, 17050, 17064, 17065, 17066, 17067, 17068, 17069, 17071, 17072, 17073, 17074, 17075, 17078, 17080, 17084, 17085, 17086, 17087, 17088, 17089, 17090, 17091, 17092, 17093, 17094, 17095, 17096, 17103, 17104, 17105, 17106, 17107, 17108, 17109, 17111, 17112, 17113, 17115, 17116, 17117, 17118, 17119, 17120, 17121, 17122, 17123, 17124, 17125, 17126, 17127, 17128, 17129, 17136, 17137, 17140, 17145, 17150, 17151, 17157, 17172, 17179, 17180, 17181, 17182, 17189, 17193, 17198, 17212, 17213, 17214, 17215, 17224, 17229, 17230, 17231, 17254, 17255, 17258, 17259, 17260, 17261, 17262, 17263, 17264, 17265, 17266, 17267, 17268, 17270, 17275, 17277, 17278, 17279, 17280, 17281, 17282, 17283, 17284, 17294, 17316, 17323, 17324, 17326, 17327, 17339, 17344, 17345, 17346, 17347, 17355, 17356, 17359, 17363, 17370, 17371, 17384, 17385, 17387, 17389, 17428, 17429, 17431, 17432, 17433, 17434, 17435, 17436, 17437, 17439, 17451, 17452, 17461, 17462, 17463, 17466, 17471, 17478, 17479, 17482, 17488, 17501, 17502, 17508, 17512, 17513, 17515, 17516, 17528, 17529, 17530, 17531, 17532, 17533, 17541, 17548, 17552, 17553, 17554, 17555, 17556, 17557, 17560, 17561, 17562, 17563, 17570, 17574, 17593, 17594, 17595, 17615, 17616, 17617, 17622, 17623, 17624, 17626, 17627, 17628, 17633, 17634, 17639, 17642, 17643, 17646, 17647, 17648, 17650, 17652, 17655, 17658, 17660, 17669, 17671, 17672, 17673, 17675, 17676, 17677, 17678, 17680, 17684, 17687, 17688, 17689, 17691, 17695, 17696, 17700, 17705, 17706, 17708, 17709, 17710, 17714, 17717, 17718, 17723, 17735, 17738, 17739, 17740, 17742, 17743, 17761, 17762, 17763, 17766, 17767, 17769, 17770, 17771, 17772, 17773, 17774, 17776, 17788, 17789, 17797, 17798, 17805, 17806, 17807, 17820, 17821, 17822, 17823, 17824, 17825, 17826, 17827, 17828, 17829, 17830, 17831, 17832, 17833, 17834, 17835, 17836, 17839, 17840, 17841, 17842, 17843, 17849, 17850, 17851, 17852, 17853, 17854, 17866, 17872, 17873, 17874, 17876, 17880, 17883, 17884, 17885, 17889, 17895, 17897, 17899, 17907, 17910, 17912, 17913, 17914, 17919, 17924, 17925, 17930, 17931, 17937, 17938, 17939, 17940, 17947, 17948, 17961, 17962, 17963, 17964, 17966, 17973, 17979, 17980, 17981, 17982, 17983, 17984, 17985, 17986, 17987, 17988, 17989, 17994, 17995, 17996, 17997, 18002, 18008, 18009, 18010, 18011, 18013, 18016, 18022, 18039, 18041, 18044, 18045, 18046, 18047, 18051, 18053, 18054, 18055, 18056, 18057, 18058, 18059, 18060, 18061, 18062, 18063, 18064, 18065, 18066, 18067, 18068, 18069, 18070, 18071, 18072, 18073, 18074, 18075, 18076, 18077, 18078, 18079, 18080, 18081, 18082, 18083, 18084, 18085, 18086, 18087, 18088, 18089, 18090, 18091, 18092, 18093, 18094, 18095, 18096, 18097, 18098, 18099, 18100, 18101, 18102, 18103, 18104, 18105, 18106, 18107, 18109, 18110, 18111, 18112, 18113, 18114, 18115, 18116, 18117, 18118, 18119, 18120, 18121, 18122, 18123, 18135, 18140, 18150, 18151, 18152, 18157, 18158, 18159, 18173, 18174, 18175, 18176, 18177, 18178, 18179, 18180, 18181, 18182, 18183, 18184, 18185, 18186, 18187, 18188, 18189, 18190, 18191, 18192, 18193, 18194, 18195, 18196, 18197, 18198, 18199, 18200, 18201, 18202, 18204, 18235, 18240, 18241, 18299, 18300, 18301, 18302, 18303, 18304, 18305, 18306, 18307, 18308, 18309, 18310, 18323, 18326, 18327, 18328, 18329, 18331, 18333, 18334, 18335, 18336, 18337, 18338, 18339, 18340, 18341, 18342, 18343, 18344, 18345, 18346, 18347, 18357, 18358, 18359, 18361, 18362, 18363, 18364, 18365, 18366, 18367, 18375, 18377, 18385, 18389, 18392, 18394, 18395, 18396, 18398, 18402, 18405, 18406, 18407, 18408, 18409, 18410, 18412, 18416, 18417, 18425, 18426]
    df = df.drop(bamlist)
    df.to_csv('banned.csv')
 
@app.get('/createdicts')
def create_dicts():
    pass



@app.get('/houses/process')
def process_houses():
    valid_houses = pd.read_csv('housesdata.csv')
    houses
 