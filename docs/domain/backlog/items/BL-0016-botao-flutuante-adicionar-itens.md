# BL-0016 — Disponibilizar botão flutuante para adicionar itens

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0016` |
| Título | Disponibilizar botão flutuante para adicionar itens |
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

Nas telas de detalhe da Lista e da Compra, o formulário de adição fica em uma
posição específica do layout. Após percorrer muitos itens, o usuário precisa
voltar até essa área para incluir um novo produto.

### Comportamento esperado

As telas mutáveis de Lista e Compra devem oferecer um botão flutuante acessível
durante a rolagem. O botão deve abrir o fluxo existente de adição a partir de
qualquer ponto da tela, preservar suas validações e comportamento offline e não
encobrir conteúdo ou outras ações importantes.

### Impacto e abrangência

- Impacto: reduz deslocamentos e mantém a inclusão de itens disponível no
  contexto em que a necessidade surge.
- Abrangência: detalhe de templates e execuções mutáveis, formulários de
  adição, navegação por teclado e layouts móvel e desktop.
- Frequência: sempre que um item precisar ser incluído depois que o usuário
  tiver rolado a tela.

### Passos de reprodução

1. Abrir uma Lista ou Compra com itens suficientes para exigir rolagem.
2. Rolar para uma posição distante do formulário de adição.
3. Tentar adicionar um produto e observar que é necessário retornar à área do
   formulário.

### Evidências sanitizadas

- [Tela de detalhe da Lista](../../../../app/templates/pages/templates/detail.html).
- [Tela da Compra](../../../../app/templates/pages/executions/in_progress.html).
- [Padrão visual existente de botão flutuante](../../../../app/static/css/jaci-theme.css).

### Workaround

Rolar manualmente até o formulário de adição antes de incluir cada novo item.

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
| Dependências | Formulários existentes, acessibilidade, layout responsivo e suporte offline; detalhamento `a_triar` |
| Duplicidades | Nenhuma identificada no diagnóstico inicial; confirmar na triagem |
| Responsável pela próxima etapa | `a_definir` |
| Próximo passo | Triar interação, acessibilidade, posicionamento e reutilização dos formulários existentes |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: somente diagnóstico documental; nenhuma validação executável
  iniciada.
- Publicação: ainda não publicada.
- Itens relacionados: `BL-0013`, `BL-0014` e `BL-0015`, registrados como
  melhorias correlatas da experiência de Lista e Compra.

### Impedimentos

- Nenhum registrado; critérios detalhados dependem da triagem.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-08-03 18:03 -03` | Codex | Item criado em `recebido` | Solicitação do usuário |
