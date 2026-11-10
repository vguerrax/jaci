# Evidência de ativação — BL-0009 / 1.5.0

> **ARQUIVADO — BL-0009 abortada pelo usuário em 2026-11-10.** Este conteúdo
> descreve o trabalho descartado e não deve ser usado para ativação. Mantidos
> dumps diários sem criptografia, retenção padrão de 30 dias e cópias manuais.
> Ensaios/ativação abaixo não são mais trabalho pendente. Código e exemplo de
> implantação foram retirados da worktree; consulte os commits históricos.

Estado: **ativação e ensaios de restauração PostgreSQL pendentes**. Registro inicial em
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
| Chave incorreta e corrupção em cópias descartáveis | Contrato age real aprovado pelo usuário: 1 passed em 1,08s, com dados/chaves efêmeros e PostgreSQL simulado; ensaio do backup operacional pendente |
| Restauração PostgreSQL vazia/isolada e revisão Alembic | Não executado |
| Grupos/autorizações, snapshots, totais e recorrência conferidos | Não executado |
| RPO <=24h / RTO <=4h, incluindo obtenção da chave/conjunto | Não medido |
| Legados abertos inventariados e exceções/decisões de conversão | Pendente; nenhum original alterado |
| Rotação: chaves antigas necessárias aos conjuntos retidos | Cenário automatizado age real aprovado com duas chaves efêmeras; inventário e guarda operacional pendentes |
| Integração BL-0007, readback remoto e recuperação da cópia rsync | Pendente de integração/validação autorizadas |
| Testes automatizados | Usuário informou suíte 329 passes/1 skip/2 xfail e 60,04% de app em 63,35s; depois, o contrato age real antes ignorado passou isoladamente em 1,08s. Piso atual 60%; sem repetição pelo Codex |
| Build | Não executado |
| Publicação e aceite operacional | Pendentes |

Não anexar dados pessoais, URLs com credenciais, chaves privadas, catálogos com
dados identificáveis ou informações de outros grupos. Descrever o resultado e
referenciar evidência restrita por identificador seguro quando necessário.
A referência pública da OCI não preenche a verificação do volume específico.
