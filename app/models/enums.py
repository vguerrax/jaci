import enum


class ExecutionStatus(str, enum.Enum):
    scheduled = "scheduled"         # agendada
    in_progress = "in_progress"      # em_andamento
    completed = "completed"          # finalizada
    cancelled = "cancelled"          # cancelada


class RecurrenceType(str, enum.Enum):
    daily = "daily"                  # diária
    weekly = "weekly"                # semanal
    biweekly = "biweekly"            # quinzenal
    monthly = "monthly"              # mensal
    yearly = "yearly"                # anual