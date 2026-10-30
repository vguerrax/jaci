# Refinamento — BL-0027 — Incorporação sem categoria

## Rastreabilidade

- Item: [BL-0027](../backlog/items/BL-0027-incorporar-item-sem-categoria.md).
- Versão-alvo: 1.4.0; responsável: Engenharia Jaci.
- Branch: feature/BL-0027-incorporar-item-sem-categoria, de develop b289771,
  em worktree separado para preservar a BL-0011 em andamento.
- Estado: concluido; refinamento e integração aprovados explicitamente após e25a531.
- Depois do merge documental, atualizar a branch antes do código. Não alterar nem
  integrar o código funcional pela branch de testes BL-0011.

## Objetivo e critérios de sucesso

Normalizar a opção Sem categoria do formulário de aprendizagem e permitir a
finalização com incorporação confirmada, sem reduzir a autorização das categorias.
O cenário UI reprovado deve passar com os mesmos dados sem categoria.

## Escopo e riscos

- Corrigir somente a normalização de category_id=0 para None na fronteira HTML.
- Valores positivos continuam passando pela validação de grupo; não remover a
  validação do serviço nem converter categorias alheias para ausência silenciosamente.
- Preservar segurança/isolamento, confirmação explícita, nomes, quantidades,
  preços e histórico. Não alterar recorrência, protocolos offline ou modelo de dados.
- LGPD: testes sintéticos; não coletar dado novo. Sem migração ou backfill.

## Plano de implementação

### Etapa 1 / Ticket 1 / Fatia 1.1 — Normalizar o sentinela

- Escrever contratos antes do código: parser reconhece zero/vazio como None;
  categoria válida é mantida; rota finaliza e incorpora item sem categoria com
  snapshot financeiro intacto; categoria de outro grupo continua rejeitada.
- Arquivos esperados: app/routers/executions.py, tests/test_template_execution_flow.py
  e/ou tests/test_template_learning_tdd.py; acompanhamento BL-0027.
- Implementação mínima: normalizar zero no parser das escolhas antes do serviço.
  Não adicionar lógica de negócio no template, nem mocks para ocultar o problema.
- Focal: testes do parser/fechamento e aprendizagem; regressão completa Python.
- Atualizar grafo após código. Sem novas revisões de esquema.
- Após autorização de integração, mergear correção validada na develop, preservar
  branch e levar a develop atualizada à BL-0011. Não agrupar demandas na mesma branch.

## Cenários TDD

1. Dado category_id_...=0, a escolha selecionada contém category_id=None.
2. Vazio permanece None; ID positivo mantém seu valor para validação posterior.
3. Fechamento com item avulso comprado sem categoria e incorporação selecionada
   finaliza, cria vínculo e mantém quantidade, valor unitário e total.
4. Categoria de outro grupo é rejeitada sem incorporar ou finalizar parcialmente.

## Estratégia de validação

- Contratos corretivos vermelhos antes da alteração e verdes depois dela.
- Regressão: bash scripts/run_tests.sh; pytest direto isolado se necessário no worktree.
- UI: repetir o cenário da BL-0011 com os mesmos dados após integrar a correção,
  pelo scripts/run_ui_tests.sh; a execução UI já foi solicitada pelo usuário.
- Aceite: incorporação sem categoria, com categoria válida e rejeição de categoria alheia.
- Publicação: registrar versão e commit antes de concluir a demanda; sem deploy nesta fatia.

## Progresso

| Etapa/ticket | Fatias concluídas | Restantes | Estado |
| --- | --- | --- | --- |
| 1 — Correção | 1/1 | 0 | Correção e testes aprovados; aceite UI pendente |

## Fechamento

- Reprodução: UI da BL-0011 reprovada; evidência sintética no item.
- Código: normalização 0 para None no parser HTML. Contratos corretivos vermelhos
  antes da alteração, 48 testes focais verdes depois dela; categoria alheia rejeitada.
- Validação: regressão 282 passes/5 xfail; migrações não necessárias; grafo atualizado.
  UI corretiva executada na BL-0011: nove cenários aprovados em 20,65s;
  mesmas entradas sem categoria e snapshot financeiro preservado.
- Publicação: pendente.

- Correção 12ee496 integrada com autorização na develop em d303c38;
  aceite UI automatizado aprovado, publicação da 1.4.0 ainda pendente.

## Publicação 1.4.0 — 2026-10-29

Publicação em produção informada pelo usuário. Tag v1.4.0 em
a1e188eecaff68cf1a24d65e7286c595338c7516 (PR #46), conferida localmente,
contendo a correção AUTH_MOCK 98c788d e o commit do usuário 00a7bc9 em run.py.
Validação final da release já registrada: 307 testes Python aprovados, dois xfail
FL-08 externos ao escopo, dez Chromium, PostgreSQL 17 e CI aprovados; cobertura
60,02%. Nenhum novo teste, migração, deploy ou ajuste de ambiente foi executado
para este registro. Os registros anteriores de publicação pendente são históricos.

Estado em_validacao mantido até confirmação do aceite final da release, sem
inferir aceite manual do anúncio de publicação. Acompanhamento consolidado na
branch coordenadora feature/BL-0026-ferramentas-ambiente-testes, preservada até
a liberação de integração pelo usuário.

## Encerramento da 1.4.0

O usuário confirmou a validação offline após anunciar a publicação. Estado
concluido em 2026-10-29; tag v1.4.0, commit publicado a1e188eecaff68cf1a24d65e7286c595338c7516.

CI do commit publicado conferido diretamente: [workflow manual 40978823250](https://github.com/vguerrax/jaci/actions/runs/40978823250),
com Python coverage e Chromium mobile and desktop concluídos com success e dois
artifacts. O usuário informou duração de 2m42s. A execução inicial por push
40978445816 falhou no job Chromium; a execução manual posterior passou no mesmo
commit. A causa daquela falha não foi investigada neste registro.

A confirmação manual registrada é a operação offline; os demais cenários têm a
cobertura automatizada documentada. Publicação/aceite deixam de ser pendências;
os registros anteriores de espera ficam preservados como histórico. A linha do
item foi movida à visão arquivada do índice, mantendo seu arquivo e identificador.
Nenhum código, ambiente, banco, migração ou implantação foi alterado aqui.
