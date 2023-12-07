from multiprocessing import Process, Queue
from bothelp import parser


# def checker(q):
#     data = []
#     while True:
#         found = q.get()
#         data.append(found)
#         print('data found to be processed: {}'.format(found))
#
#         if data == -1:
#             break


class Multiprocess:
    def __init__(self, user_id: int):
        self.user_id = user_id

    def get_marks_process(self, quarter: int, page: int, q, lesson_name: str = None):

        marks = parser.WebUser(self.user_id).get_all_marks_from_page(quarter, page, lesson_name)
        if marks:
            data = {
                'page': page,
                'marks': marks
            }
            q.put(data)

    def get_all_marks(self, quarter: int, lesson_name: str = None):
        weeks = parser.WebUser(self.user_id).get_pages_count(quarter)

        q = Queue()

        proc = []

        for i in range(1, weeks + 1):
            process = Process(target=self.get_marks_process, args=(quarter, i, q, lesson_name,))
            proc.append(process)

        for process in proc:
            process.start()

        for process in proc:
            process.join()

        all_marks = []
        data_list = []

        while not q.empty():
            data = q.get()
            if data is not None:
                # all_marks.append(data)
                data_list.append(data)

        sort_list = []
        for queue in data_list:
            sort_list.append(queue['page'])

        sort_list.sort()
        for sort in sort_list:
            for data_l in data_list:
                if data_l['page'] == sort:
                    for mark in data_l['marks']:
                        all_marks.append(mark)

        return all_marks

# if __name__ == '__main__':
#     p = Multiprocess()
#     p.get_marks(1134428403, 3, 'Физика')
