# BL-0025 — Preparar e publicar versão 1.3.0

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0025` |
| Título | Preparar e publicar versão 1.3.0 |
| Tipo | `ajuste` |
| Estado | `em_validacao` |
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
de trabalho começará depois, em demanda independente. A publicação deve exigir
versão explícita e atualizar APP_VERSION no .env.production (ou env selecionado)
antes dos comandos Docker.

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
| Próximo passo | Obter aceite manual da BL-0020 e autorizar integração/publicação da nova candidata |

## Acompanhamento até produção

- Documento refinado: [Refinamento BL-0025](../../tasks/BL-0025-release-1-3-0.md).
- Implementação (commits/PRs): preparação concluída na branch
  `feature/BL-0025-release-1-3-0`, base `4d6143e`; candidato inicial `e5451d4`; candidato atual `a0b57bd` após fatia 1.1.2.
- Validações: 55 testes focados aprovados; regressão atual com 247 passes e 5
  xfail em 12,01s, sem falhas/XPASS; metadados, OpenAPI, health, override de
  APP_VERSION, sintaxe JavaScript e diff aprovados. Build Docker isolada e
  verificação da versão na imagem aprovadas. PostgreSQL 17 descartável com
  credencial sintética contendo `%`: upgrade até 20260617_0005, current e check
  aprovados, sem operações novas. Container descartável removido; pylint ausente.
- Notas externas: rascunho local em `/tmp/jaci-v1.3.0-release-notes.md`.
- Fatia 1.1.2: script exige versão, atualiza APP_VERSION atomicamente no env
  selecionado e preserva permissões/configurações; README atualizado. Requer Python 3
  no host. Contratos falharam antes da implementação; 15 testes focados aprovados
  depois dela. Nova regressão: **262 passes e 5 xfail em 12,87s**, sem falhas/XPASS.
  `bash -n publish.sh`, diff e atualização AST do grafo aprovados. Todos os testes
  do script usam env temporário e Docker simulado; ambiente real não alterado.
- Publicação: ainda não publicada.
- Itens relacionados: [BL-0020](BL-0020-bloquear-renomeacao-item-vinculado.md),
  [BL-0001](BL-0001-operacao-offline-cobertura-rastreabilidade.md) e
  [BL-0011](BL-0011-ampliar-cobertura-testes-ui.md).

### Impedimentos

- Aceite manual móvel/online/offline da BL-0020 e atualização PWA pendentes.
- Publicação depende desse aceite e da autorização de integração/publicação.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-10-28 18:01 -03` | Usuário/Codex | Registro em recebido, severidade a_triar e prioridade a_definir | Solicitação de executar o plano da versão 1.3.0 |
| `2026-10-28 18:01 -03` | Codex | recebido → em_triagem → pronto_para_refinamento; N/A e P1 | Conteúdo Git, dependências e riscos conferidos |
| `2026-10-28 18:01 -03` | Codex | pronto_para_refinamento → em_refinamento → pronto_para_implementacao | Plano convertido em refinamento local; aguarda aprovação posterior ao versionamento |
| `2026-10-28 18:17 -03` | Usuário/Codex | Refinamento aprovado; pronto_para_implementacao → em_implementacao | Aprovação explícita após commit 3f4f9cd e merge 113b397; branch atualizada até 4d6143e |
| `2026-10-28 18:19 -03` | Usuário/Codex | Ajuste dos testes autorizado e concluído | Commit adicional 4d6143e usa request.app no menu; 6 falhas reproduzidas e corrigidas fornecendo app nos requests sintéticos |
| `2026-10-28 18:19 -03` | Codex | em_implementacao → em_validacao; etapa 1 concluída | 55 testes focados e 247 passes/5 xfail na regressão; imagem e PostgreSQL descartável aprovados; aceite manual e publicação pendentes |
| `2026-10-28 18:19 -03` | Codex | Candidato técnico registrado em e5451d4 | Preparação e regressão aprovadas; branch preservada sem merge, tag ou publicação |
| `2026-10-28 18:26 -03` | Usuário/Codex | em_validacao → em_refinamento → pronto_para_implementacao | Versão obrigatória e persistência no env refinadas na fatia 1.1.2; aguarda aprovação da revisão versionada, sem mudar o script ou ambiente real |
| `2026-10-28 18:28 -03` | Usuário/Codex | Revisão 28cfd90 aprovada; pronto_para_implementacao → em_implementacao | Versão obrigatória e atualização do env autorizadas; validações isoladas sem deploy real |
| `2026-10-28 18:29 -03` | Codex | Fatia 1.1.2 concluída; em_implementacao → em_validacao | 15 contratos de publicação aprovados; regressão com 262 passes/5 xfail; sem deploy real |
| `2026-10-28 18:29 -03` | Codex | Candidato atualizado para a0b57bd | Fatia 1.1.2, README, 15 testes e regressão atual aprovados; sem integração ou publicação |
