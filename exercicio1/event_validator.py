import json
import boto3

_SQS_CLIENT = None
# Observação: Para simular o fluxo em ambiente local, comentar todas as linhas que usam qualquer recurso externo,
# Somente testado em ambiente local para verificar se o event passa no teste de data quality.

def validateRequirementsFields(jsonData,schemaJson):
    '''
        # Função responsavel por verificar o json tem todos os campos do schema.   
        :parm jsonData: Evento (dict)  

        :parm schemaJson: schema com as propriedades esperadas no jsonData (dict)

        :return: (boolean) 
            True se estiver com o schema certo;  
            False se estiver com algum erro no schema
    '''
    # Se tiver algum campo a mais no json, retorna false 
    for field in jsonData.keys():
        if field not in schemaJson['required']:
            return False

    # Se todos os campos do schema estiverem no json, retorna True
    for requirement in schemaJson['required']:
        if requirement in jsonData.keys():
            flag = True
        else:
            flag = False
            return flag
    return flag

def validateTypeFields(jsonData,schemaJson):
    '''
        # Função responsavel por verificar os tipos dos campos do são iguais aos do schema.   
        :parm jsonData: Evento (dict)  

        :parm schemaJson: schema com as propriedades esperadas no jsonData (dict)

        :return: (boolean) 
            True se estiver com todos os tipos iguais aos do schema;  
            False é retornado sem verificar todos se acusar que ao menos que 1 campo tem o tipo diferente do esperado
    '''
    # Primeiro, pega todos os requerimentos 
    for requirement in schemaJson['required']:
        # Somente o endereco, era um object, então primeiro, verifica os outros tipos
        if schemaJson['properties'][requirement]['type'] != 'object':
            if (type(schemaJson['properties'][requirement]['examples'][0]) 
                == type(jsonData[requirement])):
                flag = True
            else:
                flag = False
                return flag
        # Quando é um object, então verifica os subcampos dele tambem.
        if schemaJson['properties'][requirement]['type'] == 'object':
            for item in schemaJson['properties'][requirement]['properties']: 
                if item in schemaJson['properties'][requirement]['required']:
                    if (type(schemaJson['properties'][requirement]['properties'][item]['examples'][0])
                        == type(jsonData[requirement][item])):
                        flag = True
                    else:
                        flag = False
                        return flag
    return flag

def send_event_to_queue(event, queue_name):
    '''
     Responsável pelo envio do evento para uma fila
    :param event: Evento  (dict)
    :param queue_name: Nome da fila (str)
    :return: None
    '''
    
    sqs_client = boto3.client("sqs", region_name="us-east-1")
    response = sqs_client.get_queue_url(
        QueueName=queue_name
    )
    queue_url = response['QueueUrl']
    response = sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(event)
    )
    print(f"Response status code: [{response['ResponseMetadata']['HTTPStatusCode']}]")

def handler(event):
    '''
    #  Função principal que é sensibilizada para cada evento
    Aqui você deve começar a implementar o seu código
    Você pode criar funções/classes à vontade
    Utilize a função send_event_to_queue para envio do evento para a fila,
        não é necessário alterá-la
    '''

    # Começa carregando o arquivo com o schema padrao.
    with open('schema.json') as f:
        data = f.read()        
    schemaJson = json.loads(data)
    
    # Depois segue para a validação.
    # Primeiro, validando se o evento tem os mesmos campos do schema.
    if validateRequirementsFields(event,schemaJson):
        # Em seguida, validando se o tipo dos campos são iguais aos tipos do schema.
        if validateTypeFields(event,schemaJson):
            # Se estiver tudo certo, envia o evento para a fila, sem alterar ele.
            send_event_to_queue(event,'valid-events-queue')
        else:
            return False 
    else:
        return False
