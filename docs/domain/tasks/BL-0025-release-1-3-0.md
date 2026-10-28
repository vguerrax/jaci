# Refinamento — BL-0025 — Preparar e publicar versão 1.3.0

## Rastreabilidade

- Item de backlog: [BL-0025](../backlog/items/BL-0025-release-1-3-0.md).
- Branch: `feature/BL-0025-release-1-3-0`, criada da develop em `9ca2ad9`.
- Responsável pelo refinamento: Engenharia Jaci.
- Estado do refinamento: `pronto_para_implementacao`.
- A branch é documental nesta etapa; será preservada após integração documental.
  Antes das alterações executáveis, atualizá-la com a develop vigente.
- Aprovação: usuário aprovou explicitamente em 2026-10-28 após o commit
  documental `3f4f9cd` e merge `113b397`. Branch atualizada até `4d6143e`,
  incluindo versão no menu e simplificação da resposta `/health`, preservados.

## Objetivo e critérios de sucesso

### Objetivo

Publicar a develop atual como v1.3.0 e concluir a BL-0020 antes de iniciar
mudanças de estrutura ou fluxos de trabalho.

### Critérios de sucesso

1. Versões internas, OpenAPI, tag e ambiente publicado identificam 1.3.0.
2. O candidato inclui a develop em `9ca2ad9`, BL-0020, correção Alembic e
   documentação; acréscimos limitam-se à preparação e correções impeditivas aprovadas.
3. Regressão atual sem falhas ou XPASS, xfail justificados fora do escopo,
   imagem construída e migrações verificadas em PostgreSQL descartável.
4. Aceite manual da BL-0020 concluído e evidenciado, incluindo fallback HTML.
5. Publicação da tag exata, verificações em produção e encerramento rastreados.

## Escopo

### Incluído

- Metadados 1.3.0, consolidação da develop, validação e publicação existentes.
- Conferência da correção Alembic para caracteres `%` na URL.
- Correção dos estados documentais desatualizados na matriz de testes.
- Notas externas da release, com descrição fiel das funcionalidades entregues.

### Excluído

- Reestruturação, novos fluxos, novas APIs, novas revisões de esquema e Playwright.
- Implementação de outras demandas apenas registradas ou refinadas na develop.
- Backfill de vínculos históricos e alteração automática de dados financeiros.

## Riscos e regras preservadas

- Segurança e LGPD: não registrar segredos, URLs reais, dados pessoais ou financeiros;
  testes e evidências usam dados sintéticos.
- Isolamento por grupo: manter autorização e testes de pertencimento de sugestões.
- Offline: distribuir shell v32, preservar IndexedDB/fila e conflitos explícitos;
  não limpar armazenamento local como procedimento de atualização.
- Histórico financeiro: incorporação mantém valores do snapshot; retorno de versão
  não executa exclusões nem reversão automática de banco.
- Recorrência: nenhuma regra nova; regressão cobre datas e execuções avulsas.
- Template/execução: confirmação explícita para incorporação e independência dos snapshots.

## Plano de implementação

### Etapa 1 — Preparar o candidato

#### Ticket 1.1 — Alinhar metadados e documentação

##### Fatia 1.1.1 — Preparação mínima

- Ordem: 1; dependência: aprovação explícita deste refinamento versionado.
- Usar `vgx-development` para alterações executáveis e `vgx-doc-management`
  para estado e evidências; promover item/índice a em_implementacao.
- Atualizar `app/__init__.py` e o padrão `Settings.app_version` em
  `app/config.py` para 1.3.0, sem mudar a precedência de `APP_VERSION`.
- Corrigir em `tests/README.md` os estados que divergem do backlog canônico.
- Arquivos esperados: os três acima e item/refinamento/índice da BL-0025.
- Validação focada: imports dos metadados, versão padrão e override de ambiente,
  `git diff --check` e revisão dos estados; não criar testes que apenas repitam literais.
- Atualizar o grafo com `venv/bin/graphify update .` após modificar código.
- Preparar texto externo das notas: BL-0020, correção Alembic e metadados;
  documentação de demandas futuras não deve ser anunciada como produto entregue.

### Etapa 2 — Validar e obter aceite

#### Ticket 2.1 — Fechar o candidato

##### Fatia 2.1.1 — Regressão e validação manual

- Ordem: 2; dependência: fatia 1.1.1.
- Registrar o hash exato do candidato e mover item/índice para em_validacao.
- Arquivos esperados: evidências em item/refinamento BL-0025 e atualização do
  aceite em item/refinamento BL-0020; sem novos testes salvo defeito que os justifique.
- Executar os comandos e cenários abaixo; resultados históricos não substituem execução atual.
- Usar PostgreSQL descartável e configuração isolada para migrações; nunca apontar
  validação de upgrade para produção ou banco local com dados do usuário.
- Registrar impedimento concreto se Docker/PostgreSQL/ambiente de aceite não estiverem
  disponíveis; não marcar cenário como aprovado por inferência.
- Qualquer correção impeditiva exige documentação e aprovação do escopo antes do código.

### Etapa 3 — Publicar e encerrar

#### Ticket 3.1 — Entregar a versão validada

##### Fatia 3.1.1 — Integração, publicação e rastreabilidade

- Ordem: 3; dependência: regressão aprovada e aceite manual registrado.
- Arquivos esperados: índice, itens e refinamentos BL-0020/BL-0025; notas externas.
- Integrar a preparação na develop com autorização; congelar o candidato sem
  funcionalidades posteriores. Se houver novos commits, revisar o delta e revalidar.
- Integrar o candidato na main e criar tag anotada `v1.3.0` no resultado mediante
  autorização de publicação; conferir que a tag não existe antes de criá-la.
- Publicar a tag exata com `./publish.sh /caminho/ambiente.env`, conforme README;
  conferir APP_VERSION sem expor o arquivo de ambiente e preservar volume de backups.
- Verificar os cenários de produção abaixo e publicar as notas externas da release.
- Só então registrar ambiente, versão, tag, commit, data e evidências; concluir
  BL-0020 e BL-0025, mover linhas para arquivados e sincronizar registro na develop.
- Preservar branches; não fazer push, merge de código ou deploy antes das respectivas
  condições de aceite/autorização descritas neste refinamento.

## Cenários TDD

Os contratos comportamentais da release já estão na suíte da BL-0020. Reutilizá-los;
novos testes executáveis só serão criados para lacuna ou defeito concreto após aprovação.

1. Nome de item vinculado não muda por edição online nem por sincronização offline;
   rejeição não altera os demais campos, versão ou broadcast indevidamente.
2. Sugestão de outro grupo/execução é rejeitada; incorporação válida cria vínculo
   atomicamente e preserva o snapshot financeiro.
3. Template com compra registrada mantém nome protegido; template nunca comprado
   e item avulso mantêm possibilidade de renomeação.
4. POST adulterado recebe 422 com página HTML, alerta e formulário protegido.
5. Migrações aceitam URL PostgreSQL com caracteres codificados por `%` e chegam ao head.
6. Metadados e OpenAPI identificam 1.3.0; APP_VERSION explícito mantém precedência.

### Contratos de etapas futuras

Não criar novos xfail nesta demanda. Playwright permanece na BL-0011; contratos
legados offline fora do escopo permanecem rastreados pela BL-0001.

## Estratégia de validação

### Por fatia

- `git diff --check`; sintaxe com `node --check` em offline-cache.js e service-worker.js.
- Conferência dos metadados e resposta OpenAPI no ambiente candidato.
- `docker compose --env-file /caminho/ambiente-isolado.env build` sem subir produção.
- Em PostgreSQL descartável com credencial sintética codificada na URL:
  `venv/bin/alembic upgrade head` e `venv/bin/alembic current`; conferir ausência
  de novas revisões de esquema e mesmo head usado pela v1.2.1.

### Validação manual

Usar viewport móvel e dados sintéticos; conferir os dez cenários manuais do
[refinamento BL-0020](BL-0020-bloquear-renomeacao-item-vinculado.md), incluindo:

1. Edição de item vinculado agendado/em andamento e demais campos editáveis.
2. Item avulso e item de template nunca comprado renomeáveis.
3. Nome protegido nos modais de editar/comprar/editar compra, online e offline.
4. Fila preservada ao desconectar e sincronização correta ao reconectar.
5. Alternância dos modais sem vazamento de readonly/ajuda entre itens.
6. POST adulterado retorna HTML 422 sem alteração parcial.
7. Incorporação confirmada preserva finanças, cria vínculo e alimenta execução futura.
8. Cliente PWA com cache anterior recebe v32 sem perder operações locais pendentes.

Após publicação: verificar autenticação, acesso ao grupo, lista, execução,
proteção dos nomes, versão efetiva, atualização PWA e logs de erros/sincronização.
Não criar ou editar compras reais para produzir evidência de smoke test.

### Regressão total

- `timeout 240 venv/bin/pytest` no candidato, registrando contagens e justificativas
  dos xfail existentes; falhas ou XPASS impedem publicação.
- Sem Playwright nesta entrega; aceite manual substitui a automação ainda ausente.

### Retorno de versão

Se houver regressão impeditiva, conferir compatibilidade dos vínculos históricos
acrescentados e retornar a aplicação à v1.2.1 pelo procedimento existente.
Não apagar dados, restaurar banco ou executar downgrade automaticamente.
Suspender operacionalmente o fluxo afetado durante a correção e registrar o incidente.

## Progresso

| Etapa/ticket | Fatias concluídas | Fatias restantes | Estado |
| --- | ---: | ---: | --- |
| 1 / 1.1 — Preparação | 1/1 | 0 | Concluída |
| 2 / 2.1 — Validação | 0/1 | 1 | Automatizada aprovada; aceite manual pendente |
| 3 / 3.1 — Publicação | 0/1 | 1 | Pendente |

## Evidências da preparação — 2026-10-28

- Base atualizada: `4d6143e`, preservando menu com versão e resposta `/health`
  simplificada. O usuário autorizou ajustar os requests sintéticos dos testes
  após reproduzir seis falhas com `KeyError: app` introduzidas por esse delta.
- Metadados `app.__version__`, Settings, OpenAPI e health: 1.3.0; override por
  APP_VERSION conferido com valor sintético, sem carregar ambiente de produção.
- Renderização: 55 testes focados aprovados após fornecer app nos requests de
  quatro módulos; comportamento de produção não alterado para acomodar testes.
- Regressão completa após ajuste: **247 passed, 5 xfailed em 12,01s**. Os dois
  contratos FL-08 pertencem a BL-0003/BL-0004; os três FL-09 legados pertencem
  a BL-0001. Nenhum xfail novo, falha ou XPASS. O usuário também forneceu uma
  execução anterior com 247 passes/5 xfail em 12,58s; não foi usada como
  substituta da nova execução do candidato.
- `node --check` dos dois JavaScripts e `git diff --check`: aprovados.
- `pylint`: indisponível no ambiente; não instalado para esta preparação mínima.
- Grafo atualizado com `venv/bin/graphify update .` (AST, sem chamadas LLM).
- Build isolada: imagem `jaci-bl0025-validation-jaci`, ID
  `sha256:e6a49f9df6356454a2ec05e455f9c180c18d3260d3a005008fe071cbac02aeca`.
  Metadados e OpenAPI verificados dentro da imagem com dados sintéticos.
  Os ajustes posteriores atingem testes/documentação/grafo, sem alteração
  adicional do código de produção. A publicação deverá reconstruir a tag exata.
- PostgreSQL 17 em container exclusivo, sem volumes: senha sintética com `%`
  codificada na URL; upgrade, current e check aprovados, head `20260617_0005`,
  nenhuma operação nova. Revisões de esquema idênticas às de v1.2.1.
  Container de teste removido ao terminar, sem tocar nos serviços existentes.
- Notas externas preparadas em `/tmp/jaci-v1.3.0-release-notes.md`; rascunho
  pendente de aceite/publicação, sem criar changelog no repositório.

## Fechamento

- Commits/PRs: preparação concluída; commit técnico a registrar na branch da demanda.
- Validações focadas: aprovadas conforme evidências acima; lint indisponível.
- Validação manual: pendente, incluindo aceite final da BL-0020 e atualização
  PWA v32 com preservação de fila. Testes de renderização não equivalem a aceite
  em navegador; nenhuma evidência manual ou de produção foi presumida.
- Regressão total: 247 passes, 5 xfail existentes fora do escopo.
- xfail pendentes no escopo: nenhum.
- Documentação atualizada: item/refinamento BL-0025, índice e matriz de testes;
  nova regressão também registrada na BL-0020 sem alterar seu aceite pendente.
- Publicação: pendente; sem integração de código em develop/main, push, tag ou deploy.
