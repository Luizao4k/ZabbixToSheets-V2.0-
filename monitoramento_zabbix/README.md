🚀 Automação de Incidentes Zabbix → Google Sheets
⬆️ Versão Atual: 2.0 — Arquitetura Modular

Sistema desenvolvido para coletar incidentes automaticamente do Zabbix, processar os dados com regras inteligentes de filtragem e organizar as informações em abas estruturadas no Google Sheets.

O projeto nasceu como um script único e evoluiu para uma arquitetura modular, mais preparada para manutenção, escalabilidade e uso em ambientes corporativos.

🎯 Objetivo

Automatizar o fluxo de monitoramento transformando eventos do Zabbix em registros organizados para análise operacional e tomada de decisão.

Este projeto elimina tarefas manuais como:

Consultar incidentes no Zabbix

Filtrar severidade

Separar por grupos ou hosts

Identificar município / DRE

Criar e organizar abas

Evitar duplicidade de eventos

Tudo acontece de forma automática.

🧠 Como o Sistema Funciona

Conecta à API do Zabbix

Busca incidentes ativos

Aplica filtros inteligentes:

Severidade mínima

Grupos permitidos

Prefixos de host

Detecta o município e mapeia para sua DRE

Evita eventos duplicados

Organiza os dados por aba no Google Sheets

Escreve os registros em lote (melhor performance)

🔥 Versão 2.0 — Refatoração Arquitetural

Esta versão representa uma evolução significativa do projeto.

Principais melhorias:

✅ Refatoração de script monolítico para arquitetura modular
✅ Separação clara de responsabilidades
✅ Código mais legível e manutenível
✅ Redução de leituras desnecessárias no Google Sheets
✅ Uso de cache local para maior performance
✅ Estrutura preparada para crescimento
✅ Melhor confiabilidade para execução em produção

Essa mudança transforma o projeto de uma automação funcional para um serviço de integração mais robusto.

🛠️ Tecnologias Utilizadas

Python

Zabbix API (pyzabbix)

Google Sheets API (gspread)

Service Account

dotenv

JSON para configuração

Unicode normalization

Processamento em lote

📁 Estrutura do Projeto (exemplo)
monitoramento_zabbix/
│
├── app/
│   ├── __init__.py
│   ├── __main__.py              # Ponto de entrada da aplicação
│   │
│   ├── application/            # Camada de orquestração
│   │   └── incidente_orchestrator.py
│   │
│   ├── domain/                 # Regras de negócio
│   │   ├── models.py
│   │   └── incident_processor.py
│   │
│   ├── infrastructure/         # Integrações externas
│   │   ├── zabbix_service.py
│   │   └── google_sheets_service.py
│   │
│   ├── config/                 # Configurações do sistema
│   │   └── settings.py
│   │
│   └── utils/                  # Utilidades compartilhadas
│       └── logger.py
│
├── tests/                      # Testes automatizados
│
├── logs/                       # Arquivos de log da aplicação
│
├── secrets/                    # Credenciais 
│
├── .env                        # Variáveis de ambiente
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
└── README.md

A estrutura modular facilita testes, manutenção e futuras expansões.

⚙️ Variáveis de Ambiente

Crie um arquivo .env:

ZABBIX_URL=https://seu_zabbix
ZABBIX_TOKEN=seu_token
SPREADSHEET_NAME=nome_da_planilha
MIN_SEVERITY=2
🔐 Autenticação Google

Utilize uma Service Account e compartilhe a planilha com o e-mail gerado pelo Google Cloud.

Arquivo esperado:

service_account.json

⚠️ Nunca versionar esse arquivo no Git.

Adicione ao .gitignore.

▶️ Como Executar

Instale as dependências:

pip install -r requirements.txt

Execute:

python main.py
🐳 Docker (Opcional, mas recomendado)

O projeto está preparado para containerização, permitindo execução padronizada em qualquer ambiente.

📊 Benefícios da Automação

✔ Redução de trabalho manual
✔ Padronização dos registros
✔ Melhor rastreabilidade de incidentes
✔ Organização automática por região
✔ Maior velocidade na análise operacional

🔭 Melhorias Futuras

Estrutura de logs mais robusta

Políticas de retry para falhas de API

Monitoramento da execução

Dashboard para visualização

👨‍💻 Autor

Luiz Paulo

Projeto desenvolvido com foco em automação operacional, integração de APIs e boas práticas de engenharia de software.

⭐ Observação

Sistema funcional ativo na SEDUC, desenvolvido para automação de incidentes, proporcionando uma resolução real de problemas e otimização do fluxo operacional.