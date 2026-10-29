# Planejamento de releases após a 1.3.0

Base publicada: v1.3.0, commit ff16202, em 2026-10-28.
Plano solicitado pelo usuário em 2026-10-28. Versões são alvos sem datas fixas;
associação não altera prioridade, estado nem substitui aprovação do refinamento.
O [índice](README.md) e os itens são a fonte dos estados; esta visão não os duplica.

| Versão-alvo | Resultado | Demandas |
| --- | --- | --- |
| 1.4.0 | Ferramentas, ambiente isolado, testes e rastreabilidade offline | [BL-0026](items/BL-0026-ferramentas-ambiente-testes.md), [BL-0011](items/BL-0011-ampliar-cobertura-testes-ui.md), [BL-0001](items/BL-0001-operacao-offline-cobertura-rastreabilidade.md) |
| 1.5.0 | Recuperação e proteção em repouso | [BL-0007](items/BL-0007-replicacao-externa-backups.md), [BL-0009](items/BL-0009-criptografia-repouso.md) |
| 1.6.0 | Redefinição de senha e continuidade da sessão | [BL-0010](items/BL-0010-reset-senha-login-area-logada.md), [BL-0019](items/BL-0019-sessao-autenticada-oito-horas-inatividade.md) |
| 1.7.0 | Exclusão e anonimização de conta | [BL-0008](items/BL-0008-autoexclusao-anonimizacao-conta.md) |
| 1.8.0 | Ordenação de compras, categorias e autocomplete | [BL-0023](items/BL-0023-priorizar-compras-status-data.md), [BL-0022](items/BL-0022-unificar-lista-categorias.md), [BL-0024](items/BL-0024-autocomplete-itens-historico.md) |
| 1.9.0 | Unidades de medida | [BL-0002](items/BL-0002-unidades-medida.md) |
| 1.10.0 | Histórico de preços | [BL-0003](items/BL-0003-historico-precos.md) |
| 1.11.0 | Recomendações para próximas compras | [BL-0005](items/BL-0005-inteligencia-compras.md) |
| 1.12.0 | Dashboard financeiro | [BL-0004](items/BL-0004-analise-gastos-dashboard-financeiro.md) |
| 1.13.0 | API de integrações máquina a máquina | [BL-0021](items/BL-0021-api-integracoes-execucoes.md) |
| 1.14.0 | Calendário e compartilhamento iniciado pelo usuário | [BL-0006](items/BL-0006-integracoes-externas.md) |

## Organização da 1.4.0

- [BL-0026](items/BL-0026-ferramentas-ambiente-testes.md) é coordenadora do ambiente, AUTH_MOCK, scripts e metadados documentais;
  não coordena um merge único dos três IDs: cada demanda tem branch e aceite próprios.
- [BL-0011](items/BL-0011-ampliar-cobertura-testes-ui.md) usa esse ambiente para cobertura Python, Playwright e GitHub Actions.
- [BL-0001](items/BL-0001-operacao-offline-cobertura-rastreabilidade.md) reconcilia os três contratos Python legados de FL-09 e sua documentação.
  Não depende da conclusão da [BL-0011](items/BL-0011-ampliar-cobertura-testes-ui.md); se entregue antes dela, usa contratos JavaScript
  executados via Node e mantém os cenários em navegador vinculados à [BL-0011](items/BL-0011-ampliar-cobertura-testes-ui.md).
- Sequência de execução preferida: [BL-0026](items/BL-0026-ferramentas-ambiente-testes.md) → [BL-0011](items/BL-0011-ampliar-cobertura-testes-ui.md) → [BL-0001](items/BL-0001-operacao-offline-cobertura-rastreabilidade.md). Gate separado por item.
- Nenhuma migração arquitetural de módulos integra a reorganização: trata-se de
  estrutura de trabalho, ferramentas e ambiente de testes.

## Dependências das próximas versões

- 1.5.0 exige restauração comprovada, destino externo, retenção, RPO/RTO e gestão
  de chaves refinados; não pressupõe fornecedor ou infraestrutura já contratada.
- 1.6.0 e 1.7.0 confirmam contratos do Tupã; mudanças nele precisam de ID e branch
  próprios. [BL-0019](items/BL-0019-sessao-autenticada-oito-horas-inatividade.md) ainda requer triagem; não assumir aprovação pela versão-alvo.
- Unidades precedem comparações de preços e quantidades: [BL-0002](items/BL-0002-unidades-medida.md) → [BL-0003](items/BL-0003-historico-precos.md) e [BL-0005](items/BL-0005-inteligencia-compras.md).
- [BL-0004](items/BL-0004-analise-gastos-dashboard-financeiro.md) não depende tecnicamente do histórico de preços; sua posição é estratégica.
- Revisar [BL-0021](items/BL-0021-api-integracoes-execucoes.md) depois de unidades e da fundação de testes, incluindo o contrato
  de unidades e o Redis ainda não configurado. Seu refinamento atual não autoriza código.
- [BL-0006](items/BL-0006-integracoes-externas.md) mantém confirmação do usuário, sem WhatsApp Business API ou envio automático.

## Contrato de acompanhamento

1. Versão-alvo fica no item; mudar alvo exige atualizar esta visão e registrar motivo
   no histórico. A visão é uma proposta de escopo, não evidência de publicação.
2. Dependências técnicas ficam na triagem; ordem estratégica não cria bloqueios artificiais.
3. Tarefas, fatias, progresso, comandos e resultados ficam no refinamento; evidências
   ligadas ao item incluem commit, ambiente e data, sem dados sensíveis.
4. Manter IDs, diretórios, estados e históricos; adicionar campos sem migrar os arquivos.
5. Cada implementação segue gate documental, TDD e validação; releases exigem aceite
   dos fluxos afetados, regressão e publicação registrada antes do encerramento.
6. Correções de releases publicadas usam 1.x.y; não preencher uma versão-alvo como entregue.
7. Depois da 1.4.0, refinar apenas a próxima release; este plano não antecipa decisões
   de produto ou infraestrutura das demais versões.

## Correções descobertas na validação da 1.4.0

[BL-0027](items/BL-0027-incorporar-item-sem-categoria.md): incorporação sem
categoria rejeitada no fechamento; correção independente necessária para o aceite UI.
