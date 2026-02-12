graph TD
    Start([Início]) --> LoadEnv[Carregar .env e JSONs de Configuração]
    LoadEnv --> Auth{Autenticação}
    
    subgraph Autenticação
        Auth --> Zabbix[Conectar Zabbix API]
        Auth --> GSheets[Conectar Google Sheets API]
    end

    Zabbix --> FetchProblems[Buscar Incidentes Ativos]
    FetchProblems --> GetDetails[Obter Detalhes: HostID, Nome e Grupos]
    
    GetDetails --> LoopProblems{Para cada Problema}
    
    LoopProblems -- Próximo --> CheckSeverity{Severidade >= MIN?}
    CheckSeverity -- Não --> LoopProblems
    CheckSeverity -- Sim --> CheckGroup{Grupo Permitido?}
    
    CheckGroup -- Não --> LoopProblems
    CheckGroup -- Sim --> CheckPrefix{Prefixo Permitido?}
    
    CheckPrefix -- Não --> LoopProblems
    CheckPrefix -- Sim --> GetDRE[Identificar DRE via Município]
    
    GetDRE --> CheckExists{ID já existe na Planilha?}
    CheckExists -- Sim --> LoopProblems
    CheckExists -- Não --> Buffer[Adicionar ao lote de escrita da DRE]
    
    Buffer --> LoopProblems
    
    LoopProblems -- Fim da Lista --> BatchWrite[Escrita em Lote por Aba/DRE]
    BatchWrite --> End([Fim e Resumo])