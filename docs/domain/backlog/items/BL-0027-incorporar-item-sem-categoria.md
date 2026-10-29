# BL-0027 — Incorporar item sem categoria ao finalizar compra

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0027` |
| Título | Incorporar item sem categoria ao finalizar compra |
| Tipo | `bug` |
| Versão-alvo | `1.4.0` |
| Estado | `em_validacao` |
| Severidade | `S2` |
| Prioridade | `P1` |
| Data de entrada | `2026-10-29` |
| Origem | Playwright da BL-0011 autorizado pelo usuário |
| Ambiente/versão | Backend de develop b289771, ambiente sintético isolado |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-10-29` |

### Comportamento observado

Ao finalizar uma execução com novo item comprado sem categoria, selecionar sua
incorporação ao template envia category_id=0. O backend interpreta zero como ID
real e rejeita a finalização com 422 e “Categoria não pertence ao grupo do template.”

### Comportamento esperado

A opção Sem categoria deve ser interpretada como ausência de categoria. A
incorporação confirmada cria o item e vínculo histórico, permitindo finalizar a
compra. IDs positivos continuam validados contra o grupo, sem autorizar IDs forjados.

### Impacto e abrangência

- Impacto: bloqueia a finalização com incorporação de item sem categoria.
- Abrangência: formulário de fechamento de execução vinculada a template.
- Frequência: sempre que essa combinação é enviada.

### Passos de reprodução

1. Criar execução de template e adicionar item avulso sem categoria.
2. Comprar os itens, abrir fechamento e selecionar incorporação do item novo.
3. Manter Sem categoria e finalizar; observar rejeição 422.

### Evidências sanitizadas

- Cenário BL-0011 test_finishing_purchase_incorporates_only_selected_item, Chromium.
- Execução UI 156644451c404805a57b813048e59247; screenshot test-failed-1.png,
  somente dados sintéticos. Artifacts locais ignorados; sem tokens ou dados reais.
- _read_template_learning_choices converte string 0 para inteiro 0 e
  stage_item_for_template valida esse valor como categoria real.

### Workaround

Escolher uma categoria válida do grupo ou não incorporar o item nessa finalização.
O caminho sem categoria precisa ser corrigido; não ocultar a falha alterando a fixture.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | confirmado por navegador e inspeção do parser/serviço |
| Classificação | Normalização incorreta do sentinela Sem categoria no formulário |
| Domínio afetado | Fechamento, aprendizagem do template e vínculo histórico |
| Regras de negócio afetadas | Confirmação manual da incorporação e preservação do snapshot |
| Risco de segurança | Baixo — manter validação de categoria positiva no serviço |
| Risco de LGPD | Baixo — sem dado novo e evidência exclusivamente sintética |
| Risco de isolamento por grupo | Médio — testar categoria de grupo alheio rejeitada |
| Risco offline/sincronização | Baixo — não ampliar fila ou alterar protocolos offline |
| Risco ao histórico financeiro | Médio — finalizar sem alterar valores já comprados |
| Risco à recorrência | Baixo — preservar geração do próximo ciclo existente |
| Risco à separação template/execução | Médio — vínculo só com seleção explícita |
| Dependências | Parser HTML e serviço de incorporação existentes; cenário BL-0011 |
| Duplicidades | Lacuna da BL-0020, descoberta após sua publicação; novo defeito corretivo |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Aprovar refinamento versionado, correção e integração para liberar UI |

## Acompanhamento até produção

- Documento refinado: [BL-0027](../../tasks/BL-0027-incorporar-item-sem-categoria.md).
- Implementação: normalização mínima no parser HTML, preservando validação de grupo;
  branch feature/BL-0027-incorporar-item-sem-categoria.
- Validações: duas falhas corretivas reproduzidas antes do código; 48 testes
  focais aprovados, incluindo rejeição de categoria alheia sem finalizar ou vincular.
  Regressão: 282 passes/5 xfail legados, sem falhas/XPASS; grafo atualizado.
  Cenário UI será repetido pela BL-0011 após a integração autorizada.
- Publicação: ainda não publicada.
- Itens relacionados: BL-0011 e BL-0020.

### Impedimentos

- Aceite UI final e publicação pendentes; integração autorizada pelo usuário.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-10-29` | Codex | recebido → em_triagem → pronto_para_refinamento; S2/P1 | Defeito reproduzido pelo Playwright autorizado, distinto da implementação de testes |
| `2026-10-29` | Codex | em_refinamento → pronto_para_implementacao | Correção mínima e validações refinadas, aguardando aprovação após versionamento |
| `2026-10-29` | Usuário/Codex | Refinamento e integração aprovados; em_implementacao | Aprovação explícita posterior a e25a531; contratos com duas falhas esperadas e autorização estrangeira preservada |
| `2026-10-29` | Codex | em_implementacao → em_validacao | 48 testes focais e regressão com 282 passes/5 xfail aprovados; sem migração e sem publicação |
