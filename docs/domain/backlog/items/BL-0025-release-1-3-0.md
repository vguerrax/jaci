# BL-0025 — Preparar e publicar versão 1.3.0

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0025` |
| Título | Preparar e publicar versão 1.3.0 |
| Tipo | `ajuste` |
| Estado | `pronto_para_implementacao` |
| Severidade | `N/A` |
| Prioridade | `P1` |
| Data de entrada | `2026-10-28` |
| Origem | Solicitação do usuário para executar o plano da versão 1.3.0 |
| Ambiente/versão | `develop` em `9ca2ad9`; última release `v1.2.1` em `f9cb4dd` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-10-28` |

### Comportamento observado

A develop contém a BL-0020, a correção da URL do Alembic e atualizações
documentais posteriores à v1.2.1. A BL-0020 permanece em validação e sem
publicação; os dois metadados internos de versão ainda declaram 1.0.0.

### Comportamento esperado

Consolidar esse conteúdo na v1.3.0, com metadados coerentes, regressão atual,
aceite manual e publicação rastreável. A reestruturação do projeto e dos fluxos
de trabalho começará depois, em demanda independente.

### Impacto e abrangência

- Impacto: estabelecer uma base publicada e identificável antes da reestruturação.
- Abrangência: preparação de release, BL-0020, PWA e publicação existente.
- Frequência: isolado — fechamento da versão 1.3.0.

### Passos de reprodução

1. Comparar `v1.2.1..develop` e consultar o estado da BL-0020.
2. Conferir `app/__init__.py` e `Settings.app_version`.
3. Observar mudanças ainda não publicadas e metadados em 1.0.0.

### Evidências sanitizadas

- Comparação inicial: 35 commits, 28 sem merges; develop e origin/develop
  coincidentes em `9ca2ad9` na consulta anterior.
- BL-0020 integrada pelo PR #40; correção Alembic no commit `d1ed784`.
- Tag v1.3.0 ausente na inspeção local de 2026-10-28.

### Workaround

Manter a versão publicada atual até a conclusão das validações e do aceite.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | confirmado por inspeção do Git, configuração e registros da BL-0020 |
| Classificação | Consolidação de release e alinhamento de metadados |
| Domínio afetado | Publicação, configuração, identidade dos itens e sincronização |
| Regras de negócio afetadas | Preservar os contratos da BL-0020 e as regras existentes |
| Risco de segurança | Baixo — não alterar autenticação; sanitizar evidências e configuração |
| Risco de LGPD | Baixo — usar dados sintéticos nas validações e não registrar dados pessoais |
| Risco de isolamento por grupo | Médio — validar rejeição de sugestões de outra execução/grupo |
| Risco offline/sincronização | Médio — conferir distribuição v32, conflitos e preservação da fila |
| Risco ao histórico financeiro | Médio — validar vínculo sem reescrever valores; retorno não deve apagar dados |
| Risco à recorrência | Baixo — regressão confirma preservação do ciclo existente |
| Risco à separação template/execução | Médio — incorporação somente mediante confirmação e snapshots preservados |
| Dependências | Aprovação do refinamento versionado, aceite BL-0020 e acesso ao ambiente de publicação |
| Duplicidades | BL-0020 entrega o comportamento; BL-0025 coordena a release, sem duplicar implementação |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Apresentar refinamento versionado e obter aprovação explícita antes das alterações executáveis |

## Acompanhamento até produção

- Documento refinado: [Refinamento BL-0025](../../tasks/BL-0025-release-1-3-0.md).
- Implementação (commits/PRs): não iniciada; branch `feature/BL-0025-release-1-3-0`.
- Validações: links locais, estado, ausência de placeholders, continuidade da tabela
  e `git diff --check` aprovados; resultados executáveis pendentes de aprovação.
- Publicação: ainda não publicada.
- Itens relacionados: [BL-0020](BL-0020-bloquear-renomeacao-item-vinculado.md),
  [BL-0001](BL-0001-operacao-offline-cobertura-rastreabilidade.md) e
  [BL-0011](BL-0011-ampliar-cobertura-testes-ui.md).

### Impedimentos

- Nenhum técnico identificado; aprovação documental e aceite de release pendentes.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-10-28 18:01 -03` | Usuário/Codex | Registro em recebido, severidade a_triar e prioridade a_definir | Solicitação de executar o plano da versão 1.3.0 |
| `2026-10-28 18:01 -03` | Codex | recebido → em_triagem → pronto_para_refinamento; N/A e P1 | Conteúdo Git, dependências e riscos conferidos |
| `2026-10-28 18:01 -03` | Codex | pronto_para_refinamento → em_refinamento → pronto_para_implementacao | Plano convertido em refinamento local; aguarda aprovação posterior ao versionamento |
