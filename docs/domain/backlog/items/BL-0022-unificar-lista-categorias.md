# BL-0022 — Unificar a gestão de categorias em uma única lista

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0022` |
| Título | Unificar a gestão de categorias em uma única lista |
| Versão-alvo | `1.8.0` |
| Tipo | `melhoria` |
| Estado | `pronto_para_refinamento` |
| Severidade | `N/A` |
| Prioridade | `P2` |
| Data de entrada | `2026-09-17` |
| Origem | Solicitação do usuário para simplificar a gestão de categorias |
| Ambiente/versão | Estado de `develop` (`2ca3e7e`) em `2026-09-17` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-10-28` |

### Comportamento observado

A tela de categorias apresenta cada categoria duas vezes: primeiro em uma lista
dedicada aos botões de mover para cima e para baixo e depois em cartões separados
com contagem de itens e opções de editar e excluir. O usuário precisa relacionar
visualmente duas representações para ordenar e administrar o mesmo registro.

### Comportamento esperado

A tela deve exibir uma única lista mobile-first. Cada linha de categoria deve
reunir cor, nome, quantidade de itens vinculados, botões para mover para cima e
para baixo e um menu de opções para editar ou excluir.

“Sem categoria” deve continuar visível na posição configurada, sem ações de
edição ou exclusão. Os limites da ordenação devem permanecer explícitos, com o
botão impossível desabilitado na primeira e na última categoria.

### Impacto e abrangência

- Impacto: reduz duplicidade visual e torna ordenação e manutenção executáveis
  no mesmo contexto, especialmente em telas estreitas.
- Abrangência: página de categorias do grupo ativo, controles de ordenação,
  edição, exclusão e posição de “Sem categoria”.
- Frequência: sempre que uma pessoa consulta, reorganiza ou administra as
  categorias do grupo.

### Passos de reprodução

1. Abrir a página de categorias de um grupo com categorias cadastradas.
2. Observar a lista “Ordem de exibição”, com os controles de movimento.
3. Observar abaixo os cartões das mesmas categorias, com editar e excluir.
4. Confirmar que nenhuma representação reúne todas as ações.

### Evidências sanitizadas

- [Template da lista de categorias](../../../../app/templates/pages/categories/list.html)
  renderiza a lista de ordenação e, em seguida, uma grade com as mesmas
  categorias.
- [`move_category`](../../../../app/services/category_service.py) já move uma
  categoria uma posição por vez e não exige alteração de modelo.
- [Rotas de categorias](../../../../app/routers/categories.py) já expõem as
  ações de mover, editar e excluir sob autorização do grupo.

### Workaround

Usar a lista superior para ordenar e localizar a mesma categoria nos cartões
inferiores para editar ou excluir.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `confirmado` por inspeção do template e das rotas atuais |
| Classificação | Melhoria de experiência e consolidação visual sem mudança de domínio ou persistência |
| Domínio afetado | Categorias e configuração de ordem do grupo ativo |
| Regras de negócio afetadas | Preservar ordem por `sort_order`, posição configurada de “Sem categoria”, contagem de vínculos e autorização existente |
| Risco de segurança | Baixo — as ações existentes continuam POSTs autorizados; a consolidação visual não deve transformar links ou JavaScript em autorização |
| Risco de LGPD | Não — nenhum dado pessoal ou novo atributo é coletado, persistido ou exposto |
| Risco de isolamento por grupo | Médio — os controles unificados devem continuar operando somente sobre categorias do grupo ativo e rejeitar IDs externos |
| Risco offline/sincronização | Baixo — a tela continua server-rendered; indisponibilidade de rede deve falhar sem reordenação visual falsa ou persistência parcial |
| Risco ao histórico financeiro | Baixo — editar ou excluir categoria conserva as regras existentes de desvinculação e não altera itens ou valores históricos |
| Risco à recorrência | Não — nenhuma data, template recorrente ou geração de execução é modificada |
| Risco à separação template/execução | Baixo — a categoria continua compartilhada pelo grupo, sem copiar ou propagar outros campos entre template e execução |
| Dependências | Template, rotas e serviço de categorias existentes; futura cobertura de navegador acompanhada pela BL-0011 |
| Duplicidades | Nenhuma; a [BL-0013](BL-0013-filtrar-itens-lista-compra.md) padronizou listas de itens, não a tela administrativa de categorias |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Refinar composição da linha única, comportamento mobile e sem JavaScript, confirmação de exclusão, acessibilidade dos controles e cenários TDD |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: triagem por inspeção estática da tela, rotas e serviço; validações
  executáveis ainda não iniciadas.
- Publicação: ainda não publicada.
- Itens relacionados: [BL-0011](BL-0011-ampliar-cobertura-testes-ui.md) e
  [BL-0013](BL-0013-filtrar-itens-lista-compra.md).

### Impedimentos

- Nenhum registrado.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-09-17 16:36 -03` | Codex | Item criado em `recebido` | Solicitação do usuário para uma única lista de categorias |
| `2026-09-17 16:36 -03` | Codex | `recebido` → `em_triagem` | Duplicidade visual e capacidades atuais confirmadas no template, rotas e serviço |
| `2026-09-17 16:36 -03` | Usuário/Codex | `em_triagem` → `pronto_para_refinamento` | Escopo de linha única, prioridade P2, riscos e relação com BL-0013 definidos |
| `2026-10-28 20:40 -03` | Codex | Versão-alvo 1.8.0 associada | Roadmap aprovado para formalização; estado e prioridade preservados, sem autorizar implementação |
