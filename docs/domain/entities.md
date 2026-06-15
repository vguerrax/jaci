## Pricipais Entidades

### Usuário

Reprensenta uma pessoa utilizando o sistema, a autênticação é responsabilidade do Auth Service do Tupã.

### Grupo

Unidade de compartilhamento (ex: "Minha Casa"), agrupa templates, execuções e categorias

### Categoria

Classificação de itens (Mantimentos, Limpeza, Açougue, etc.), global por grupo

### Template 

Modelo de lista com recorrência (diária/semanal/quinzenal/mensal/anual), contém itens planejados com quantidades

### Item de Template

Item dentro do template: nome, categoria, quantidade planejada

### Execução 

Instância concreta de uma compra, gerada a partir de um template ou avulsa. Possui data, status (agendada/em andamento/finalizada/cancelada), orçamento

### Item de Execução

Item sendo comprado: nome, categoria, quantidade planejada, quantidade comprada, valor unitário, local, status de conclusão, versão (para bloqueio otimista)

