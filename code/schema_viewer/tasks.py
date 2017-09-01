from datetime import datetime

from mgi.celery import app
from schema_viewer.models import FormDataSandbox
from utils.XSDParser.parser import delete_branch_from_db


@app.task(name='clean_db_sandbox')
def clean_db_sandbox():
    forms_data_sandbox = FormDataSandbox.objects.all()
    date_now = datetime.now()
    for form_data_sandbox in forms_data_sandbox:
        if (date_now - form_data_sandbox.timestamp).total_seconds() > 60 * 60:
            if form_data_sandbox.form_data.schema_element_root is not None:
                delete_branch_from_db(form_data_sandbox.form_data.schema_element_root.pk)

            form_data_sandbox.form_data.delete()
            form_data_sandbox.delete()
