"""Утилита для отправки запросов к серверу от нескольких пользователей"""
import datetime
import typing as tp
import logging
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from client.src.requester.requester import Requester, Request
from client.src.client_model.model import Model
from client.src.requester.errors import APIError
from common.base import DBFields

logging.basicConfig(level=logging.INFO)


def prepare_request(request: Request, request_name: str, session_id: str) -> dict | None:
    logging.debug(f'SESSION {session_id} STARTED PREPARING REQUEST: {request_name}')
    try:
        result = request.result()
        if isinstance(result.content, list):
            return result.content[0]
        return result.content
    except APIError as e:
        logging.error(f'SESSION {session_id}: Unexpected error during preparing request: {request_name}: {e}')


def sent_requests(address: str, thread: int, process: int):

    session_id = f'T{thread}P{process}'

    logging.debug(f'STARTED USER SESSION (ID {session_id}): Thread: {thread} | Process: {process}.')
    requests_with_data = 0
    requests = 7

    requester = Requester(address)
    logging.debug('1')
    model = Model('../../../client/data/config_data/storage', '')
    access_token = model.get_access_token()
    logging.debug('2')
    user_request = requester.get_user_info(access_token)
    user_request.wait_until_complete()
    logging.debug('3')
    user = prepare_request(user_request, 'user', session_id)
    if user:
        requests_with_data += 1

    logging.debug('4')

    wf_tasks_request = requester.get_wf_tasks_by_user(user[DBFields.id], access_token, datetime.date.today())
    wf_tasks_request.wait_until_complete()
    wf_tasks = prepare_request(wf_tasks_request, 'wf_tasks', session_id)
    if wf_tasks:
        requests_with_data += 1

    personal_tasks_request = requester.get_personal_tasks(user[DBFields.id], access_token, datetime.date.today())
    personal_tasks_request.wait_until_complete()
    personal_tasks = prepare_request(personal_tasks_request, 'personal_tasks', session_id)
    if personal_tasks:
        requests_with_data += 1

    wf_daily_events_request = requester.get_wf_daily_events_by_user(user[DBFields.id], [], access_token, datetime.date.today())
    wf_many_days_events_request = requester.get_wf_many_days_events_by_user(user[DBFields.id], [], access_token, datetime.date.today())
    personal_daily_events_request = requester.get_personal_daily_events(user[DBFields.id], access_token, datetime.date.today())
    personal_many_days_events_request = requester.get_personal_many_days_events(user[DBFields.id], access_token, datetime.date.today())

    wf_daily_events_request.wait_until_complete()
    wf_many_days_events_request.wait_until_complete()
    personal_daily_events_request.wait_until_complete()
    personal_many_days_events_request.wait_until_complete()

    wf_daily = prepare_request(wf_daily_events_request, 'wf_daily_events', session_id)
    wf_many_days = prepare_request(wf_many_days_events_request, 'wf_many_days_events', session_id)
    personal_daily = prepare_request(personal_daily_events_request, 'personal_daily_events', session_id)
    personal_many_days = prepare_request(personal_many_days_events_request, 'personal_many_days_events', session_id)

    if wf_daily:
        requests_with_data += 1
    if wf_many_days:
        requests_with_data += 1
    if personal_daily:
        requests_with_data += 1
    if personal_many_days:
        requests_with_data += 1

    logging.debug(f'SESSION {session_id}: REQUESTS PREPARED. REQUESTS: {requests}. WITH DATA: {requests_with_data}')


def sent_requests_in_threads(args_list: tuple[int, str, str]):
    with ThreadPoolExecutor(args_list[0]) as executor:
        for i in range(args_list[0]):
            executor.submit(lambda: sent_requests(args_list[1], i + 1, args_list[2]))


if __name__ == '__main__':
    print('Утилита для отправки запросов к серверу от нескольких пользователей.')
    print('Перед запуском на клиент должны быть переданы валидные JWT-токены.')

    address_ = input('Адрес сервера: ')
    if not address_:
        address_ = 'http://127.0.0.1:80'
    processes = int(input('Использовать процессов: '))
    if processes > 4:
        processes = 4
    threads = int(input('Использовать потоков (на процесс): '))
    if threads > 15:
        threads = 15
    cycles = int(input('Циклов:'))

    logging.info(f'STARTED WITH: Address: {address_} | Processes: {processes} | Threads: {threads}')

    time_start = datetime.datetime.now()
    params = [[[threads, address_, i] for i in range(1, processes + 1)] for i in range(cycles)]

    results = []
    with ProcessPoolExecutor() as executor:
        for i in range(cycles):
            results.extend(executor.map(sent_requests_in_threads, params[i]))

    time_end = datetime.datetime.now()
    logging.info(f'FINISHED. TIME: {time_end - time_start}')
