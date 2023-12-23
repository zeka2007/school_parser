import os
import shutil


class UserData:
    def __init__(self, student_id: int, data_dir: str = 'data'):
        self.student_id = student_id
        self.data_dir = data_dir

        if not os.path.exists(f'{data_dir}/{self.student_id}/'):
            os.mkdir(f'{data_dir}/{self.student_id}')

    def get_lessons(self):
        if os.path.exists(f'{self.data_dir}/{self.student_id}/lessons.txt'):
            with open(f'{self.data_dir}/{self.student_id}/lessons.txt', 'r') as file:
                return file.read().split('\n')[0:-1]
        return None

    def set_lessons(self, lessons: list):
        with open(f'{self.data_dir}/{self.student_id}/lessons.txt', 'w') as file:
            write = ''
            for lesson in lessons:
                write = write + lesson + '\n'
            file.write(write)

    def remove_all_data(self):
        path = f'{self.data_dir}/{self.student_id}'
        if os.path.exists(path):
            shutil.rmtree(path)
