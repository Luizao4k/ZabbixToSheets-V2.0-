graph LR
    subgraph Fontes de Configuração
        CONF1[(.env)] 
        CONF2[(config_groups.json)]
        CONF3[(dre_map.json)]
        CONF4[(config_severity.json)]
    end

    subgraph Script Principal
        CORE[zabbix_sheets.py]
        NORM[Normalizador de Texto]
        FILT[Motor de Filtragem]
    end

    subgraph Provedores Externos
        ZBX[(Zabbix Server)]
        GAPI[Google Sheets API]
    end

    subgraph Destino Final
        SHEET[[Planilha Google]]
        ABA1[Aba DRE - Norte]
        ABA2[Aba DRE - Sul]
        ABA3[Aba DRE - ...]
    end

    %% Conexões
    CONF1 & CONF2 & CONF3 & CONF4 --> CORE
    CORE <--> ZBX
    CORE --> NORM
    CORE --> FILT
    CORE <--> GAPI
    GAPI --> SHEET
    SHEET --> ABA1 & ABA2 & ABA3