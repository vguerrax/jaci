# Evidência de ativação — BL-0009 / 1.5.0

Estado: **pendente, sem ativação ou ensaios executados**. Registro inicial em
2026-10-30. Não preencher campos por suposição ou com resultados históricos.
Documentação de referência: [runbook](backup-encryption.md).

| Evidência | Situação / valor sanitizado |
| --- | --- |
| Topologia | Confirmada pelo usuário: Jaci/HD locais; PostgreSQL e Caddy em Oracle separadas |
| Data, operador, versão/commit implantado | Pendente |
| data_directory e correlação com volume real | Pendente; sem consulta ao servidor |
| Boot/block volume OCI (alias sanitizado) | Pendente |
| Criptografia do volume e gestão efetiva da chave | Pendente de conferência OCI pelo operador |
| Espaço local/remoto e tamanho do conjunto | Pendente; contemplar retenção e readback |
| Diretório 0700 / arquivos 0600 / montagem pública readonly | Pendente |
| Fingerprint da lista de destinatários públicos | Pendente; não registrar identidades privadas |
| Duas cópias recuperáveis da identidade, guardadas pelo usuário | Pendente; registrar somente confirmação de guarda |
| Primeiro conjunto criptografado: ID/data/hash | Pendente |
| Teste de recuperação com cada cópia de chave | Não executado |
| Chave incorreta e corrupção em cópias descartáveis | Não executado |
| Restauração PostgreSQL vazia/isolada e revisão Alembic | Não executado |
| Grupos/autorizações, snapshots, totais e recorrência conferidos | Não executado |
| RPO <=24h / RTO <=4h, incluindo obtenção da chave/conjunto | Não medido |
| Legados abertos inventariados e exceções/decisões de conversão | Pendente; nenhum original alterado |
| Rotação: chaves antigas necessárias aos conjuntos retidos | Pendente |
| Integração BL-0007, readback remoto e recuperação da cópia rsync | Pendente de integração/validação autorizadas |
| Testes automatizados e build | Não executados por restrição explícita do usuário |
| Publicação e aceite operacional | Pendentes |

Não anexar dados pessoais, URLs com credenciais, chaves privadas, catálogos com
dados identificáveis ou informações de outros grupos. Descrever o resultado e
referenciar evidência restrita por identificador seguro quando necessário.
A referência pública da OCI não preenche a verificação do volume específico.
