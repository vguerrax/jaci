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
