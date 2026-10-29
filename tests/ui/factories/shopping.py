from datetime import datetime,timezone
from sqlalchemy import select
from app.models import User,Group
from app.models.enums import RecurrenceType
from app.services.template_service import create_template,add_item_to_template
from app.services.execution_service import create_execution_from_template,start_execution
from tests.ui.helpers.data import unique_ui_name,ui_db_session


def create_purchase(*,started=True,extra_item=False):
    with ui_db_session() as db:
        user=db.scalar(select(User).where(User.email=='owner@example.com'))
        group=db.scalar(select(Group).where(Group.owner_id==user.id))
        template=create_template(db,group,unique_ui_name('Lista UI'),RecurrenceType.weekly,100)
        item=add_item_to_template(db,template,unique_ui_name('Arroz'),2)
        execution=create_execution_from_template(db,template,datetime.now(timezone.utc),user)
        if extra_item:
            from app.services.execution_service import add_item_to_execution
            additional=add_item_to_execution(db,execution,unique_ui_name('Avulso'),1)
            additional_id=additional.id
        if started:
            start_execution(db,execution)
        return {'execution':execution.id,'item':execution.items[0].id,
                'template':template.id,'template_item':item.id,'name':item.name,
                'extra':additional_id if extra_item else None}
