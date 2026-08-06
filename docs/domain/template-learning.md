# Aprendizado contínuo dos templates

## BL-029 — Detecção de itens adicionados na execução

Itens copiados de um template para uma execução mantêm o vínculo `template_item_id`.
Itens adicionados durante a compra ficam sem vínculo com item de template.

Durante a análise de uma execução, o serviço de aprendizado considera sugestões de
novo item apenas quando:

- a execução está vinculada a um template;
- a execução não é avulsa;
- o item de execução não possui `template_item_id`;
- não existe item no template com o mesmo nome normalizado.

O serviço apenas detecta as sugestões. Nenhuma alteração é aplicada ao template sem
confirmação explícita do usuário.

## BL-030 — Incorporação de itens

No fechamento da execução, itens criados durante a compra são exibidos como
sugestões de inclusão no template. O usuário escolhe cada item individualmente e
pode ajustar categoria e quantidade planejada antes de aplicar.

Quando a inclusão é confirmada, a criação do `TemplateItem` e o preenchimento de
`ExecutionItem.template_item_id` no item que originou a sugestão são persistidos na
mesma transação. O snapshot financeiro da execução não é alterado. O serviço
valida que item, execução, template e grupo pertencem ao mesmo fluxo antes de
estabelecer o vínculo.

## Identidade do item após a primeira compra

O nome de um `TemplateItem` torna-se imutável quando existe ao menos um
`ExecutionItem` vinculado com `is_completed = true`. Quantidade planejada,
categoria e observações do planejamento continuam editáveis, e itens que ainda
não foram comprados permanecem renomeáveis.

Na interface da lista, o nome protegido continua visível em modo somente leitura.
Essa regra fica centralizada no serviço para que um POST adulterado não consiga
renomear o produto nem persistir parcialmente os outros campos.

## BL-031 e BL-032 — Quantidades recorrentes

O histórico de execuções finalizadas do template é analisado por item vinculado ao
template. Uma sugestão de quantidade só é criada quando a mesma quantidade comprada
aparece em pelo menos três execuções recentes. Ao aceitar, apenas o item do template
é atualizado; execuções existentes permanecem como histórico.

## BL-033 e BL-034 — Observações recorrentes

Observações repetidas em itens vinculados ao template também exigem pelo menos três
ocorrências. Ao aceitar a sugestão, a observação passa a ser copiada para execuções
futuras geradas a partir do template.

## BL-075 e BL-076 — Orçamentos recorrentes

O aprendizado de orçamento considera apenas execuções finalizadas, vinculadas ao
template e não avulsas. O orçamento padrão do template é comparado com a mediana
dos orçamentos efetivamente usados nas execuções finalizadas.

Uma sugestão de atualização é gerada quando:

- existem pelo menos três execuções finalizadas com orçamento definido;
- a mediana calculada difere em pelo menos 10% do orçamento atual do template;
- o grupo mantém o aprendizado de templates habilitado.

O template nunca é alterado automaticamente. No fechamento da execução, o usuário
visualiza o orçamento atual, o orçamento sugerido e a explicação da mediana. Ao
marcar a sugestão, apenas o orçamento padrão do template é atualizado, afetando
execuções futuras. Execuções existentes preservam o orçamento usado originalmente.

## Sugestões ignoradas

Sugestões exibidas e não selecionadas no fechamento são registradas em
`template_learning_dismissals`, evitando reapresentação na mesma execução.

## Configuração por grupo

Grupos possuem a flag `template_learning_enabled`. Quando desativada, o serviço não
gera sugestões imediatas nem sugestões históricas para os templates do grupo.
O criador do grupo pode alterar essa configuração nos detalhes do grupo, no mesmo
modal usado para editar o nome.
