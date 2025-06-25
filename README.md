# Jenkins Logs Processor
 
Este projeto tem como objetivo processar logs de builds do Jenkins, extrair os logs e armazená-los no **Azure Blob Storage**, controlando o processamento via banco de dados **PostgreSQL**. Toda a orquestração é feita com **Docker Compose** e o processamento assíncrono utiliza **Celery** e **Redis**.
 
## Funcionalidade Principal
 
-Conecta-se à API do Jenkins e obtém todos os jobs e builds disponíveis.

-Filtra builds de acordo com regras (por exemplo: logs antigos, falhas, etc).

-Separa o jobs que tiveram falhas na build e as salva em um banco de dados (usando PostgreSQL).

-Verifica se os logs dos builds já foram processados (usando PostgreSQL).

-Baixa os logs dos builds e os salva no **Azure Blob Storage**.

-Registra os logs processados no banco para evita reprocessamento.


 
## Tecnologias Utilizadas
 
- **Python 3.x**
- **Docker & Docker Compose**
- **Celery** : processamento assíncrono
- **Redis** : broker/resultado do Celery
- **PostgreSQL** : controle dos builds/logs
- **Azure Blob Storage** : armazenamento dos logs
- **aiohttp e aiofiles** : requisições/manipulação assíncrona
- **pytest** : testes
- **Pydantic** : validação e modelagem

 
## Requisitos
 
Antes de executar o projeto, você precisará:

- **Docker** e **Docker Compose** instalados.

- Conta no **Azure** e uma **string de conexão** válida para o Blob Storage.

- Instância do **Jenkins** rodando (pode ser local ou container).

- Definir variáveis de ambiente em um arquivo **.env** (veja abaixo).
 
## Instalação
 
1. Clone este repositório para sua máquina local:
   
   ```bash
   git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
    cd SEU_REPOSITORIO
   ```
 
2. Configure o arquivo .env na raiz do projeto (exemplo):
 
    AZURE_STORAGE_CONNECTION_STRING=SuaStringDeConexao
    AZURE_BLOB_CONTAINER=logs-jenkins
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    POSTGRES_DB=jenkinslogs
    JENKINS_URL=http://jenkins:8080/

3. Suba os serviços com Docker Compose:
    ```bash
    docker compose up --build
    ```

## Configuração
 
1. **Azure Blob Storage**:
   - Defina a **string de conexão** e o **nome do container** no arquivo .env.
 
2. **API do Jenkins**:
   - O código atualmente está configurado para acessar a URL de um Jenkins específico (`http://s6006as2917:8080/job/tp_mm_sap_bidt_dsv/api/json`). Modifique essa URL de acordo com o seu Jenkins.

3. **Banco de dados**:
    - As configurações do PostgreSQL já vêm prontas no docker-compose, mas podem ser ajustadas no .env.
 
## Executando o Projeto
 
- O projeto utiliza **Celery** para processar os jobs de maneira assíncrona.

- Para iniciar o processamento dos logs, basta garantir que os containers app (API/serviço principal) e worker (Celery) estejam rodando.

- Logs do Jenkins serão processados automaticamente conforme agendamento, chamada manual, ou por endpoints expostos pela API (em desenvolvimento).

- O Jenkins ficará disponível localmente em http://localhost:8080.
 
 
## Testes Unitários
 
- Este projeto utiliza pytest para garantir a qualidade do código. Os testes estão localizados na pasta jenkins_log/tests.

- Para rodar os testes, execute:

    '''bash
    pytest
    '''

- Os testes cobrem:

- Conexão e obtenção de jobs/builds do Jenkins

- Processamento e upload dos logs para o Azure Blob Storage

- Registro e verificação de builds já processados no PostgreSQL

- Fluxo completo de processamento de logs
 
## Contribuindo
 
1. Faça um fork deste repositório.
2. Crie uma branch para sua feature (`git checkout -b feature-nome`).
3. Faça commit das suas alterações (`git commit -am 'Adicionando nova funcionalidade'`).
4. Envie para a branch do seu fork (`git push origin feature-nome`).
5. Abra um Pull Request.

6. Para backup do banco: docker run --rm -v jenkins_logs_postgres_data:/var/lib/postgresql/data -v $(pwd):/backup ubuntu bash -c "cd /var/lib/postgresql/data && tar xzf /backup/backup.tar.gz --strip 1"

 
## Licença
 
Este projeto está licenciado sob a Licença MIT - consulte o arquivo [LICENSE](LICENSE) para mais detalhes.