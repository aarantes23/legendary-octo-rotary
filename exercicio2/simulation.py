import json
from queue import Empty

def getFieldsAndTypes(schemaJson):
    result = []
    for requirement in schemaJson['required']:
        if schemaJson['properties'][requirement]['type'] != 'object':            
            result.append([requirement,schemaJson['properties'][requirement]['type']])
        if schemaJson['properties'][requirement]['type'] == 'object':
            for item in schemaJson['properties'][requirement]['properties']: 
                if item in schemaJson['properties'][requirement]['required']:
                    result.append([str(requirement+"_"+item),schemaJson['properties'][requirement]['properties'][item]['type']])
    return dict(result)

def createQuery(schemaJson): 
    part_0 = """
    CREATE EXTERNAL TABLE IF NOT EXISTS
    data.cliente (\n        """

    schema = getFieldsAndTypes(schemaJson)
    part_1 = ""
    for key,value in schema.items():
        if part_1 != "":
            part_1 = part_1+"        "+key+" "+value+",\n"
        else: 
            part_1 = part_1+key+" "+value+",\n"
    part_1 = part_1[:-2]
    part_2 = """
    ) ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
    WITH SERDEPROPERTIES (
    'separatorChar' = ',',
    'quoteChar' = '\"',
    'escapeChar' = '\\'
    )
    STORED AS PARQUET
    LOCATION 's3://iti-query-results/';
    """

    return (part_0+part_1+part_2)

def main():    
    with open('schema.json') as f:
        data = f.read()        
    schemaJson = json.loads(data)
    print(createQuery(schemaJson))

if __name__ == "__main__":
    main()