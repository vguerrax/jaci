# BL-0016 — Disponibilizar botão flutuante para adicionar itens

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0016` |
| Título | Disponibilizar botão flutuante para adicionar itens |
| Tipo | `melhoria` |
| Estado | `pronto_para_implementacao` |
| Severidade | `N/A` |
| Prioridade | `P2` |
| Data de entrada | `2026-08-03` |
| Origem | Solicitação do usuário |
| Ambiente/versão | Estado de `develop` (`e07bcfe`) em `2026-08-03` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-08-04` |

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
| Confirmação | `confirmado` |
| Classificação | Melhoria de experiência mobile-first por atalho progressivo para o formulário de adição existente |
| Domínio afetado | Detalhes de Lista e Compra, acessibilidade, layout responsivo e distribuição PWA |
| Regras de negócio afetadas | Nenhuma regra de persistência nova; preservar validações, estados mutáveis, autorização e semântica dos formulários existentes |
| Risco de segurança | Baixo — o atalho não cria endpoint nem mutação e as submissões continuam autenticadas e autorizadas pelas rotas atuais |
| Risco de LGPD | Baixo — nenhum dado pessoal, financeiro ou identificador adicional será coletado ou exposto |
| Risco de isolamento por grupo | Baixo — o alvo pertence à página já autorizada e IDs de template, execução e categoria continuam validados no servidor |
| Risco offline/sincronização | Médio — o atalho deve funcionar sem JavaScript e a Compra deve continuar submetendo o mesmo formulário marcado para fila offline, com o CSS vigente distribuído pelo cache PWA |
| Risco ao histórico financeiro | Baixo — não altera quantidade, valor, total ou histórico; em compra em andamento o valor unitário continua obrigatório |
| Risco à recorrência | Baixo — não altera finalização, data-base nem geração de execuções |
| Risco à separação template/execução | Baixo — cada atalho aponta somente para o formulário da tela corrente, sem copiar ou promover dados entre os domínios |
| Dependências | Formulários atuais, `.btn-fab`, indicador global de sincronização, áreas seguras mobile, cache PWA e entregas integradas BL-0013 a BL-0015 |
| Duplicidades | Nenhuma; BL-0013, BL-0014 e BL-0015 são melhorias correlatas, e a BL-0011 acompanha infraestrutura de testes UI |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Aguardar aprovação explícita do refinamento versionado antes de criar contratos executáveis ou alterar a interface |

## Acompanhamento até produção

- Documento refinado: [Refinamento BL-0016](../../tasks/BL-0016-botao-flutuante-adicionar-itens.md).
- Implementação (commits/PRs): ainda não iniciada.
- Validações: somente diagnóstico documental; nenhuma validação executável
  iniciada.
- Publicação: ainda não publicada.
- Itens relacionados: `BL-0011`, `BL-0013`, `BL-0014` e `BL-0015`; a BL-0011
  acompanha a infraestrutura Playwright e as demais são melhorias correlatas
  da experiência de Lista e Compra.

### Impedimentos

- Nenhum.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-08-03 18:03 -03` | Codex | Item criado em `recebido` | Solicitação do usuário |
| `2026-08-04 16:55 -03` | Codex | `recebido` -> `em_triagem` | Formulários, FAB existente, indicador de sincronização, estados mutáveis e comportamento PWA diagnosticados |
| `2026-08-04 16:55 -03` | Codex | `em_triagem` -> `pronto_para_refinamento` | Solução progressiva sem formulário duplicado nem nova persistência definida |
| `2026-08-04 16:55 -03` | Codex | `pronto_para_refinamento` -> `em_refinamento` | Documento técnico criado e ligado ao item |
| `2026-08-04 16:55 -03` | Codex | `em_refinamento` -> `pronto_para_implementacao` | Objetivo, fatia única, contratos TDD, cenários UI e validações refinados; aguarda nova aprovação explícita |
