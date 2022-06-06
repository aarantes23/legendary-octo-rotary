import json

_ATHENA_CLIENT = None
# Observação: Para simular o fluxo em ambiente local, comentar todas as linhas que usam qualquer recurso externo,
# Somente testado em ambiente local para verificar o resultado da string criada em createQuery.

def getFieldsAndTypes(schemaJson):
    '''
        # Função responsavel para coletar os campos e tipos do schema.           

        :parm schemaJson: schema com as propriedades necessarias para o create table no athena (dict)

        :return: dict(result) Dicionario para montar a query com os campos necessarios 
    '''
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
    """
        # Função responsavel para montar a string de create table do Athena.

        :parm schemaJson: schema com as propriedades necessarias para o create table no athena (dict)

        :return: string para enviar a função create_hive_table_with_athena(query)
    """
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

def create_hive_table_with_athena(query):
    '''
    Função necessária para criação da tabela HIVE na AWS
    :param query: Script SQL de Create Table (str)
    :return: None
    '''
    
    print(f"Query: {query}")
    _ATHENA_CLIENT.start_query_execution(
        QueryString=query,
        ResultConfiguration={
            'OutputLocation': f's3://iti-query-results/'
        }
    )

def handler():
    '''
    #  Função principal
    Aqui você deve começar a implementar o seu código
    Você pode criar funções/classes à vontade
    Utilize a função create_hive_table_with_athena para te auxiliar
        na criação da tabela HIVE, não é necessário alterá-la
    '''
    # Carrega o schema para pegar os campos e tipos 
    with open('schema.json') as f:
        data = f.read()
    schemaJson = json.loads(data)
    # Monta a query
    query = createQuery(schemaJson)
    # Envia a query
    create_hive_table_with_athena(query) 
