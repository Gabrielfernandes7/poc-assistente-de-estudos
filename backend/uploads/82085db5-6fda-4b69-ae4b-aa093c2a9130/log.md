# Change Log
- [2026-05-29] Initialization of the LLM Wiki.
- [2026-05-29] Ingested: Atendimento a chamado 18602 (Versioning).
- [2026-05-29] Ingested: db_keys.md (Data Dictionary).
- [2026-05-29] Ingested: User Story 1 (Data Hygiene).
- [2026-05-29] Refined: Added Module entities (Comum, Estagio) and Sources Index.
- [2026-05-29] Refined: Detailed steps for Data Hygiene workflow added to recipe.
- [2026-06-01] Refactored wiki schema to nested folders (Projects, Databases, Tickets, User-Stories, Modules, Tables) and updated all cross-references.
- [2026-06-02] Ingested SQL findings for `estagio.local_estagio` sanitization and updated User Story 1 roadmap.
- [2026-06-08] Updated Script Final with verified FK dependencies for `termo_estagio` and `termo_estagio_discente_externo`.
- [2026-06-08] Finalized constraint strategy: Composite Unique (cnpj, nome) following Taiga recommendation.
- [2026-06-08] User Story 1 Completed: 1678 records unified in `estagio.local_estagio`, FKs rebinded, and unique constraint applied.
- [2026-06-08] PIVOT: Iniciado Plano de Migração Robusta após análise de riscos operacionais. Foco em backups, validadores DB e fontes institucionais.
- [2026-06-08] Ingested: Engenheiro de Dados - Por Onde Começar em 7 Passos (Career concepts added).
- [2026-06-08] Finalized User Story 1: Reestruturado script final para implementar a versão robusta do Plano de Migração Robusta (incluindo backups operacionais, cruzamento com fonte de verdade institucional, score qualitativo para survivorship e auditoria física persistente).
- [2026-06-08] Ingested: Estratégia de solução para chamado #18602 (Versionamento de Modelos de Contratos de Estágio).
- [2026-06-09] Ingested: Comprehensive compilation of `@raw/*.sql` scripts. Added 'Bolsas' module, Versioning entities (Modelo_Documento_Versao, Documento_Instancia), and Troubleshooting recipes (Permission Assignment, Regex Snippets, Template Migration). Integrated concepts of Survivorship Scoring and Snapshot Pattern.

