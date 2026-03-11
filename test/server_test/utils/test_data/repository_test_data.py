"""Данные для тестов репозитория."""
import datetime

from server.database.repository import DataRepository
from common.base import DBFields, CommonStruct


'creating_method', 'updating_method', 'obj_data', 'updating_data', 'get_by_id_method', 'expected'
test_updating_objects_data = [
    [
        DataRepository.add_personal_tasks, DataRepository.update_personal_tasks,
         {
             DBFields.name: f'PersonalTask{j}', DBFields.description: ''.join(['desc' for i in range(100)]),
             DBFields.owner_id: 1, DBFields.status_id: 1, DBFields.plan_deadline: datetime.datetime.now().strftime(CommonStruct.datetime_format)
         },
        {DBFields.name: f'PersonalTask-1'},
        DataRepository.get_personal_tasks_by_id,
        {
            DBFields.name: f'PersonalTask-1', DBFields.description: ''.join(['desc' for i in range(100)]),
            DBFields.owner: 1, DBFields.status: 1, DBFields.plan_deadline: datetime.datetime.now().strftime(CommonStruct.datetime_format), DBFields.work_direction: None,
            DBFields.fact_deadline: None, DBFields.plan_start_work_date: None, DBFields.fact_start_work_date: None,
            DBFields.plan_time: None, DBFields.fact_time: None, DBFields.parent_task: None, DBFields.tags: None,
            DBFields.child_tasks: None, DBFields.task_events: None
        },
    ] for j in range(10)
          ]


