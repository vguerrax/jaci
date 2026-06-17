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

## BL-031 e BL-032 — Quantidades recorrentes

O histórico de execuções finalizadas do template é analisado por item vinculado ao
template. Uma sugestão de quantidade só é criada quando a mesma quantidade comprada
aparece em pelo menos três execuções recentes. Ao aceitar, apenas o item do template
é atualizado; execuções existentes permanecem como histórico.

## BL-033 e BL-034 — Observações recorrentes

Observações repetidas em itens vinculados ao template também exigem pelo menos três
ocorrências. Ao aceitar a sugestão, a observação passa a ser copiada para execuções
futuras geradas a partir do template.

## Sugestões ignoradas

Sugestões exibidas e não selecionadas no fechamento são registradas em
`template_learning_dismissals`, evitando reapresentação na mesma execução.

## Configuração por grupo

Grupos possuem a flag `template_learning_enabled`. Quando desativada, o serviço não
gera sugestões imediatas nem sugestões históricas para os templates do grupo.
O criador do grupo pode alterar essa configuração nos detalhes do grupo, no mesmo
modal usado para editar o nome.
