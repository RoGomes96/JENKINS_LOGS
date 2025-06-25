from datetime import datetime, timedelta
import json
import aiohttp
from azure.storage.blob.aio import BlobServiceClient
from settings import Settings

settings = Settings()


async def extract_builds_to_blob(
    url: str,
    blob_name: str
) -> aiohttp.ClientResponse | None:
    url = url
    print(">> URL final:", url)
    sas_token = settings.SAS_TOKEN
    account_url = settings.URL_BLOB
    blob_service_client = BlobServiceClient(
        account_url=account_url,
        credential=sas_token
    )
    container_name = settings.CONTAINER_NAME
    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob="jenkins/" + blob_name + ".json"
    )

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.read()
                    print(f"data carregada: {data}")
                    data_json = json.loads(data)
                    data_criacao_jenkins = datetime.fromtimestamp((data_json['timestamp']/1000))
                    print(f"data_criacao_jenkins: {data_criacao_jenkins}")

                    # Verifica se o timestamp da build é mais antigo que 7 dias
                    if data_criacao_jenkins <= (datetime.now() - timedelta(days=7)):
                        await blob_client.upload_blob(
                            data,
                            overwrite=True
                        )
                        print("Build mais ANTIGA que 7 dias, será salva no blob.")
                    else:
                        print("Build mais RECENTE que 7 dias, não será salva no blob.")

                    # Retorna o response e a data de criação do Jenkins
                    return response, data_criacao_jenkins
                else:
                    print(f"Resposta não OK, status: {response.status}")
                    return None
        except Exception as e:
            print(f"Erro ao obter informações da build {url} no jenkins: {e}")
            return None
