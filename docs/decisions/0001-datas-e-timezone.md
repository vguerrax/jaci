# 0001 - Tratamento de datas e timezone

## Status

Aceita

## Contexto

O Jaci usa campos diferentes para dois conceitos:

- datas civis de planejamento, como `scheduled_date`;
- instantes de auditoria ou evento, como `created_at`, `updated_at`, `finished_at` e datas de sincronização.

Um bug recorrente apareceu quando datas vindas de `<input type="date">` foram
interpretadas como meia-noite UTC. Para o fuso `America/Sao_Paulo`, `2026-06-30
00:00 UTC` é `2026-06-29 21:00 -03`, causando exibição de um dia anterior.

## Decisão

Datas civis informadas pelo usuário devem ser interpretadas como datas locais de
`America/Sao_Paulo`.

Regras obrigatórias:

- Entradas `YYYY-MM-DD` de formulários, APIs offline e filtros devem usar
  `parse_local_date`.
- A persistência continua em UTC, usando o instante equivalente à meia-noite local.
- Exibição em templates deve usar `localdate` ou `localdatetime`.
- Valores de `<input type="date">` devem usar `localdate('%Y-%m-%d')`.
- Comparações por dia, mês ou período operacional devem calcular limites no fuso
  local e converter esses limites para UTC antes de consultar o banco.
- Instantes técnicos ou auditáveis devem continuar usando UTC, por exemplo
  `datetime.now(timezone.utc)`.

## Exemplos

Entrada do usuário:

```text
2026-06-30
```

Interpretação correta:

```text
2026-06-30 00:00:00 America/Sao_Paulo
```

Persistência em UTC:

```text
2026-06-30 03:00:00 UTC
```

Exibição:

```text
30/06/2026
```

## Antipadrões

Evite:

```python
datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
```

Use:

```python
parse_local_date(value)
```

Evite:

```jinja2
{{ execution.scheduled_date.strftime('%Y-%m-%d') }}
```

Use:

```jinja2
{{ execution.scheduled_date|localdate('%Y-%m-%d') }}
```

## Consequências

- Compras agendadas para hoje continuam válidas durante todo o dia local.
- Agenda mensal e filtros por dia usam o calendário visto pelo usuário.
- Próximos ciclos e recorrências preservam a separação entre execução e template,
  mas devem receber datas já normalizadas conforme esta decisão.
