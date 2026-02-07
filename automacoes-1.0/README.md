#Zabbix to Google Sheets Integrator
>[!NOTE] Relato de Evolução Pessoal

>Este projeto representa um marco importante na minha jornada como desenvolvedor: é a minha primeira aplicação com uso real.

>Sendo honesto, a estrutura atual está um pouco "bagunçada" porque, inicialmente, eu estava apenas testando se a ideia era viável. Para minha felicidade, o projeto não só funcionou, como cumpriu seu papel com maestria apesar da simplicidade.

>Já estou planejando a versão 2.0, que contará com uma arquitetura mais organizada e limpa. Deixo este registro aqui no GitHub não apenas como uma ferramenta útil, mas como um ponto de controle para minha própria evolução no desenvolvimento de software. :p

Este projeto automatiza a exportação de incidentes ativos do Zabbix para planilhas do Google Sheets, organizando-os automaticamente em abas baseadas na DRE (Diretoria Regional de Educação) ou unidade correspondente.

🚀 Funcionalidades
Filtragem Inteligente: Filtra incidentes por severidade mínima, prefixos de host e grupos específicos.

Organização por Abas: Detecta o município no nome do host e mapeia para a aba da DRE correta.

Deduplicação: Verifica os EVENT_ID já existentes na planilha para evitar registros duplicados.

Escrita em Lote: Utiliza atualização em lote para otimizar a performance e respeitar as quotas da API do Google.

Normalização: Tratamento de strings para evitar erros com acentos ou letras minúsculas/maiúsculas.

📋 Pré-requisitos
Python 3.8+

Conta de serviço no Google Cloud Console com a API do Google Sheets e Drive ativadas.

Acesso à API do Zabbix (URL e Token).

🛠️ Instalação e Configuração
Clonar o repositório:

Bash
git clone https://github.com/seu-usuario/zabbix-sheets.git
cd zabbix-sheets
Instalar dependências:

Bash
pip install -r requirements.txt
Configurar credenciais do Google:

Renomeie o arquivo service_account.example.json para service_account.json.

Cole suas credenciais reais dentro do arquivo.

Importante: Compartilhe sua Planilha Google com o e-mail da client_email gerado no JSON.

Configurar variáveis de ambiente: Crie um arquivo .env na raiz do projeto:

Snippet de código
ZABBIX_URL="https://seu-zabbix.com/api_jsonrpc.php"
ZABBIX_TOKEN="seu_token_aqui"
SPREADSHEET_NAME="Nome da Sua Planilha"
MIN_SEVERITY=2
Ajustar arquivos de configuração (JSON):

config_groups.json: Defina os grupos e prefixos de hosts permitidos.

dre_map.json: Mapeie municípios para suas respectivas DREs.

config_severity.json: Defina o nível de severidade mínima.

📂 Estrutura de Arquivos
Plaintext
.
├── zabbix_sheets.py           # Script principal
├── service_account.json       # Credenciais Google (Não subir ao Git)
├── .env                       # Variáveis de ambiente (Não subir ao Git)
├── config_groups.json         # Filtros de grupos e prefixos
├── dre_map.json               # Dicionário Município -> DRE
├── config_severity.json       # Configuração de criticidade
└── requirements.txt           # Bibliotecas necessárias
🚀 Como executar
Basta rodar o script principal:

Bash
python zabbix_sheets.py
O script exibirá um resumo da execução no terminal, informando quantos incidentes novos foram adicionados e quantos foram ignorados pelos filtros.

## 📊 Documentação Visual
Para uma compreensão profunda da arquitetura e dos componentes, acesse:
- [Diagramas de Fluxo](DiagramaFluxo.md)
- [Diagrama de Arquitetura](DiagramaArquitetura.md)

> [!CAUTION]⚠️ Segurança
>Este repositório contém arquivos de exemplo (.example.json). Nunca exponha seus arquivos "service_account.json" ou ".env" .