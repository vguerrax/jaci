# BL-0013 — Filtrar itens nas telas de Lista e Compra

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0013` |
| Título | Filtrar itens nas telas de Lista e Compra |
| Tipo | `melhoria` |
| Estado | `recebido` |
| Severidade | `a_triar` |
| Prioridade | `a_definir` |
| Data de entrada | `2026-08-03` |
| Origem | Solicitação do usuário |
| Ambiente/versão | Estado de `develop` (`e07bcfe`) em `2026-08-03` |
| Responsável | `a_definir` |
| Atualizado em | `2026-08-03` |

### Comportamento observado

As telas de detalhe da Lista e da Compra exibem os itens agrupados por
categoria, mas não oferecem um campo para localizar um produto pelo nome. Em
listas extensas, o usuário precisa percorrer manualmente os grupos e itens.

### Comportamento esperado

As telas mutáveis de Lista e Compra devem permitir filtrar localmente, pelo
nome, os itens já carregados. A busca não deve depender de catálogo externo nem
de conexão ativa e deve permitir restaurar a visualização completa ao ser
limpa.

### Impacto e abrangência

- Impacto: reduz o tempo e o esforço para localizar produtos durante o
  planejamento e a execução da compra.
- Abrangência: itens existentes nas telas de detalhe de templates e de
  execuções mutáveis, inclusive em dispositivos móveis e offline.
- Frequência: sempre que o usuário precisar localizar um item em uma lista ou
  compra extensa.

### Passos de reprodução

1. Abrir uma Lista ou Compra que contenha vários itens e categorias.
2. Tentar localizar um produto específico pelo nome.
3. Observar que é necessário percorrer manualmente os grupos exibidos.

### Evidências sanitizadas

- [Tela de detalhe da Lista](../../../../app/templates/pages/templates/detail.html).
- [Tela da Compra](../../../../app/templates/pages/executions/in_progress.html).

### Workaround

Expandir as categorias e percorrer manualmente os itens até localizar o
produto desejado.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `a_triar` |
| Classificação | `a_triar` |
| Domínio afetado | `a_triar` |
| Regras de negócio afetadas | `a_triar` |
| Risco de segurança | `a_avaliar` |
| Risco de LGPD | `a_avaliar` |
| Risco de isolamento por grupo | `a_avaliar` |
| Risco offline/sincronização | `a_avaliar` |
| Risco ao histórico financeiro | `a_avaliar` |
| Risco à recorrência | `a_avaliar` |
| Risco à separação template/execução | `a_avaliar` |
| Dependências | Comportamento de agrupamento e atualização dos itens; detalhamento `a_triar` |
| Duplicidades | Nenhuma identificada no diagnóstico inicial; confirmar na triagem |
| Responsável pela próxima etapa | `a_definir` |
| Próximo passo | Triar critérios de correspondência, acessibilidade e atualização do filtro |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: somente diagnóstico documental; nenhuma validação executável
  iniciada.
- Publicação: ainda não publicada.
- Itens relacionados: `BL-0014`, `BL-0015` e `BL-0016`, registrados como
  melhorias correlatas da experiência de Lista e Compra.

### Impedimentos

- Nenhum registrado; critérios detalhados dependem da triagem.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-08-03 18:03 -03` | Codex | Item criado em `recebido` | Solicitação do usuário |
