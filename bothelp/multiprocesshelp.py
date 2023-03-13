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
    def __init__(self):
        self.parse = parser.Parser()

    def get_marks_process(self, user_id: int, quarter: int, page: int, q, lesson_name: str = None):

        marks = self.parse.get_all_marks_from_page(user_id, quarter, page, lesson_name)
        # print(marks)
        for mark in marks:
            q.put(mark)

    def get_all_marks(self, user_id: int, quarter: int, lesson_name: str = None):
        weeks = self.parse.get_pages_count(user_id, quarter)

        q = Queue()

        proc = []

        for i in range(1, weeks + 1):
            process = Process(target=self.get_marks_process, args=(user_id, quarter, i, q, lesson_name,))
            proc.append(process)

        for process in proc:
            process.start()

        for process in proc:
            process.join()

        all_marks = []

        while not q.empty():
            data = q.get()
            if data is not None:
                all_marks.append(data)

        return all_marks

# if __name__ == '__main__':
#     p = Multiprocess()
#     p.get_marks(1134428403, 3, 'Физика')
