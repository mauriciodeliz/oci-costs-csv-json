import oci
import os
import csv
import json
import glob
import gzip
from datetime import datetime, timedelta
import locale

reporting_namespace = 'bling'
base_prefix = "FOCUS Reports"
destination_path = '/tmp/oci'

# Definir a localidade para formatação de números
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Criar o diretório se não existir
if not os.path.exists(destination_path):
    os.makedirs(destination_path)  # Use os.makedirs para criar todos os diretórios necessários

# Configuração do OCI
config = oci.config.from_file(oci.config.DEFAULT_LOCATION, oci.config.DEFAULT_PROFILE)
reporting_bucket = config['tenancy']
object_storage = oci.object_storage.ObjectStorageClient(config)

# Definir a data de ontem
yesterday = datetime.now() - timedelta(days=1)
yesterday_prefix = f"{base_prefix}/{yesterday.year}/{yesterday.month:02d}/{yesterday.day:02d}"

# Lista todos os objetos no bucket com o prefixo da data de ontem
report_bucket_objects = oci.pagination.list_call_get_all_results(
    object_storage.list_objects,
    reporting_namespace,
    reporting_bucket,
    prefix=yesterday_prefix
)

# Filtrar e baixar os objetos no diretório da data de ontem
for o in report_bucket_objects.data.objects:
    try:
        print('Found file ' + o.name)
        object_details = object_storage.get_object(reporting_namespace, reporting_bucket, o.name)
        filename = o.name.rsplit('/', 1)[-1]  # Extrai o nome do arquivo do caminho

        # Salva o arquivo no diretório de destino
        file_path = os.path.join(destination_path, filename)
        with open(file_path, 'wb') as f:
            for chunk in object_details.data.raw.stream(1024 * 1024, decode_content=False):
                f.write(chunk)
        print('----> File ' + o.name + ' Downloaded')
    except oci.exceptions.ServiceError as e:
        print(f"Service error retrieving object metadata for {o.name}: {str(e)}")

# Lista para armazenar os dados filtrados do CSV
filtered_data_list = []

# String padrão para buscar arquivos CSV
csv_pattern = '*.csv.gz'

# Caminho completo para buscar os arquivos CSV
gz_files = glob.glob(os.path.join(destination_path, csv_pattern))

# Variável para armazenar o valor total dos custos
total_cost = 0.0

# Função para descomprimir arquivos .gz
def decompress_gz(file_path):
    decompressed_file_path = file_path[:-3]  # Remove a extensão .gz
    print(f"Descompressing {file_path} to {decompressed_file_path}")
    with gzip.open(file_path, 'rb') as f_in:
        with open(decompressed_file_path, 'wb') as f_out:
            f_out.write(f_in.read())
    print(f"Decompressed file: {decompressed_file_path}")
    return decompressed_file_path

# Percorre cada arquivo .gz que corresponde ao padrão
for gz_file in gz_files:
    # Descomprime o arquivo .gz
    csv_file = decompress_gz(gz_file)

    # Abre o arquivo CSV e lê os dados
    with open(csv_file, mode='r') as file:
        # Cria um leitor CSV especificando o delimitador como vírgula
        csv_reader = csv.DictReader(file, delimiter=',')

        # Percorre as linhas do CSV e filtra os campos desejados
        for row in csv_reader:
            cost = float(row.get("BilledCost", 0))  # Converte o custo para float e soma ao total
            total_cost += cost
            filtered_row = {
                "ServiceName": row.get("ServiceName"),
                "ResourceType": row.get("ResourceType"),
                "ResourceId": row.get("ResourceId"),
                "ServiceCategory": row.get("ServiceCategory"),
                "Region": row.get("Region"),
                "BilledCost": row.get("BilledCost"),
                "AvailabilityZone": row.get("AvailabilityZone"),
                "BilledCost": row.get("BilledCost")
#                "Tags": row.get("Tags")       # Se deseja pegar as TAGs, colocar a "," na linha BilledCost e descomentar essa linha              
            }
            filtered_data_list.append(filtered_row)

    # Remove o arquivo CSV e o arquivo .gz após a leitura
    os.remove(csv_file)
    os.remove(gz_file)
    print(f'Files {csv_file} and {gz_file} have been deleted.')

# Converte a lista de dicionários filtrados para JSON
json_data = json.dumps(filtered_data_list, indent=4)

# Imprime o JSON gerado
print(json_data)

# Imprime o valor total dos custos no formato desejado
formatted_total_cost = locale.currency(total_cost, grouping=True)
print(f"Valor total dos custos em BRL (R$): {formatted_total_cost}")
