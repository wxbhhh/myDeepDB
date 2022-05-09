
import csv
import os.path


# 获取每个模型的相关信息
def get_model_info():
    modelConfigInfo = {}

    current_path = os.path.dirname(__file__)
    modelConfigPath = '{}/../config/model_config.csv'.format(current_path)
    with open(modelConfigPath, 'r') as modelConfigFile:
        for row in modelConfigFile:
            lineArr = row.split(',')
            modelName = lineArr[1]
            modelIndex = lineArr[0]
            modelTables = lineArr[2].split('#')
            modelProperties = lineArr[3].strip().split('#')

            model = {'index': modelIndex, 'table': modelTables, 'properties': modelProperties}
            modelConfigInfo[modelName] = model
    return modelConfigInfo


# 获取数据库每张表的属性的相关信息
def get_db_column_min_max_dnv_vals():
    current_path = os.path.dirname(__file__)
    file_name_column_min_max_vals = "{}/../config/column_min_max_vals.csv".format(current_path)
    column_min_max_dnv_vals = {}
    with open(file_name_column_min_max_vals, 'r') as f:
        data_raw = list(list(rec) for rec in csv.reader(f, delimiter=','))
        for i, row in enumerate(data_raw):
            if i == 0:
                continue
            # column_min_max_vals[row[0]] = [float(row[1]), float(row[2])]
            column_min_max_dnv_vals[row[0]] = {'min': float(row[1]), 'max': float(row[2]), 'dnv': int(row[4])}
    return column_min_max_dnv_vals


# 获取每个模型每个属性的dnv
def get_models_dnv_vals():
    column_min_max_dnv_vals = get_db_column_min_max_dnv_vals()
    current_path = os.path.dirname(__file__)
    model_dnv_vals_file_path = "{}/../config/model_config.csv".format(current_path)
    with open(model_dnv_vals_file_path, 'rU') as model_dnv_vals_file:
        data_raw = list(list(rec) for rec in csv.reader(model_dnv_vals_file, delimiter=','))

        model_dnv_vals = {}
        for row in data_raw:
            model_name = row[1]
            model_properties = row[3].split('#')
            properties_dnv = []
            for properties in model_properties:
                properties_dnv.append(column_min_max_dnv_vals[properties]['dnv'])
            model_dnv_vals[model_name] = properties_dnv
    return model_dnv_vals

