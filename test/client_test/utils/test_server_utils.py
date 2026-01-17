

class TestRepo:
    """Имитация репозитория"""

    CONTENT = 'content'
    LAST_REC_NUM = 'last_record_num'
    RECORDS_LEFT = 'records_left'

    def __init__(self):
        self._data_struct = {self.CONTENT: [f'{i}' for i in range(1000)]}

    def get_content(self, limit: int, offset: int) -> dict:
        result = self._data_struct.get(self.CONTENT)[offset: offset + limit]

        last_record_num = offset + limit
        records_left = len(self._data_struct.get(self.CONTENT)) - offset - limit
        return {self.CONTENT: result, self.LAST_REC_NUM: last_record_num, self.RECORDS_LEFT: records_left}

