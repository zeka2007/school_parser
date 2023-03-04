import math


def quarter_marks_analytics(lessons: list,
                            marks: list,
                            old_marks: list = None
                            ):
    result = 'Предмет / отметка за текущую\n\n'
    if old_marks is not None:
        result = 'Предмет / отметка за прошлую четверть / отметка за текущую\n\n'
    for i in range(len(lessons)):
        if old_marks is not None:
            percent = ''
            if marks[i] != 'з.' and old_marks[i] != 'з.' and marks[i] != 'Нет' and old_marks[i] != 'Нет':
                if old_marks[i] > marks[i]:
                    number = (int(old_marks[i]) - int(marks[i])) / int(old_marks[i]) * 100
                    percent = f'(- {round(number, 1)} %)'
                else:
                    number = (int(marks[i]) - int(old_marks[i])) / int(marks[i]) * 100
                    percent = f'(+ {round(number, 1)} %)'

            row = f'{lessons[i]} / {old_marks[i]} / {marks[i]} {percent}\n'
        else:
            row = f'{lessons[i]} / {marks[i]}\n'

        result = result + row

    average_mark = 0
    count = 0
    for mark in marks:
        if mark != 'з.' and mark != 'Нет':
            average_mark = average_mark + int(mark)
            count = count + 1
    if count != 0:
        average_mark = average_mark / count

    average_mark_old = 0
    if old_marks is not None:
        count = 0
        for mark in old_marks:
            if mark != 'з.' and mark != 'Нет':
                average_mark_old = average_mark_old + int(mark)
                count = count + 1
        if count != 0:
            average_mark_old = average_mark_old / count

    if average_mark_old != 0 and average_mark != 0:
        if average_mark > average_mark_old:
            result = f'{result}\n\nСредний балл в этой четверти: {round(average_mark, 2)}, ' \
                     f'что на {round(((average_mark - average_mark_old) / average_mark * 100), 1)}% лучше, ' \
                     f'чем в прошлой. ' \
                     f'Средний балл в прошлой четверти: {round(average_mark_old, 2)}'
        if average_mark_old > average_mark:
            result = f'{result}\n\nСредний балл в этой четверти: {round(average_mark, 2)}, ' \
                     f'что на {round(((average_mark_old - average_mark) / average_mark_old * 100), 1)}% хуже, ' \
                     f'чем в прошлой. ' \
                     f'Средний балл в прошлой четверти: {round(average_mark_old, 2)}'
        if average_mark_old == average_mark:
            result = f'{result}\n\nСредний балл в этой четверти: {round(average_mark, 2)}, ' \
                     'что совпадает с прошлой.'
    else:
        if average_mark != 0:
            result = f'{result}\n\nСредний балл в этой четверти: {round(average_mark, 2)}'

    return result


def lessons_marks_table(marks: list, lesson: str = None):
    all_marks = ''
    for mark in marks:
        all_marks = all_marks + str(mark) + ' '
    if all_marks == '':
        text = f'Отметок нет'
        return text

    middle_mark = 0
    for mark in marks:
        middle_mark = middle_mark + mark

    middle_mark = middle_mark / len(marks)

    text = f'Предмет: {lesson}\n' \
           f'Отметки: {all_marks}\n' \
           f'Средний балл: {round(middle_mark, 2)}\n'

    if lesson is None:
        text = f'Отметки: {all_marks}\n' \
               f'Средний балл: {round(middle_mark, 2)}\n'

    test_mark = 1
    new_middle_mark = 0
    while True:
        if test_mark > 10:
            break
        for mark in marks:
            new_middle_mark = new_middle_mark + mark
        new_middle_mark = (new_middle_mark + test_mark) / (len(marks) + 1)
        if math.ceil(new_middle_mark) > math.ceil(middle_mark):
            break
        test_mark = test_mark + 1
        new_middle_mark = 0

    if math.ceil(new_middle_mark) > math.ceil(middle_mark):
        if test_mark == 10:
            text = text + f'Подсказка: получив {test_mark} вы можете получить {math.ceil(new_middle_mark)} за четверть'
        else:
            text = text + f'Подсказка: получив {test_mark} или выше вы можете получить {math.ceil(new_middle_mark)} за четверть'

    return text


def lessons_marks_fix_table(marks: list, lesson: str):
    all_marks = ''
    for mark in marks:
        all_marks = all_marks + str(mark) + ' '
    if all_marks == '':
        text = f'Отметок нет'
        return text

    middle_mark = 0
    for mark in marks:
        middle_mark = middle_mark + mark

    middle_mark = middle_mark / len(marks)

    text = f'Предмет: {lesson}\n' \
           f'Отметки: {all_marks}\n' \
           f'Средний балл: {round(middle_mark, 2)}\n\n'

    new_middle_mark = 0
    mark_counter = {}
    for key in range(1, 11):
        mark_counter[key] = 0

    counter = 0

    for test_mark in range(1, 11):
        for i in range(1, 8):
            for mark in marks:
                new_middle_mark = new_middle_mark + mark
            new_middle_mark = new_middle_mark + i * test_mark
            new_middle_mark = new_middle_mark / (len(marks) + i)
            mark_counter[test_mark] = mark_counter[test_mark] + 1
            if math.ceil(new_middle_mark) > math.ceil(middle_mark):
                counter = counter + 1
            # print(f'(i : {i})({counter}){middle_mark} > {new_middle_mark} ({math.ceil(new_middle_mark)})')

            new_middle_mark = 0

        if counter == 1:
            mark_counter[test_mark] = 1

        elif counter == 0:
            mark_counter[test_mark] = 0

        else:
            mark_counter[test_mark] = (mark_counter[test_mark] + 1) - counter
        counter = 0

    can_change_count = 0
    for mark in mark_counter:
        if mark_counter[mark] != 0:
            can_change_count = can_change_count + 1

    if can_change_count == 0:
        text = text + 'Вы не можете повысить свою отметку'
        return text

    text = text + f'Для получения отметки {math.ceil(middle_mark) + 1}:\n'

    for mark in mark_counter:
        if mark_counter[mark] != 0:
            text = text + f'Вы должны получить {mark} в количестве {mark_counter[mark]}\n'
            if mark != 10:
                if mark_counter[mark + 1] != 0:
                    text = text + 'ИЛИ\n'

    return text


def lessons_if_get_mark_table(marks: list, lesson: str):
    all_marks = ''
    for mark in marks:
        all_marks = all_marks + str(mark) + ' '
    if all_marks == '':
        text = f'Отметок нет'
        return text

    middle_mark = 0
    for mark in marks:
        middle_mark = middle_mark + mark

    middle_mark = middle_mark / len(marks)

    text = f'Предмет: {lesson}\n' \
           f'Отметки: {all_marks}\n' \
           f'Средний балл: {round(middle_mark, 2)}\n\n' \
           f'Чтобы узнать, какие отметки могут повлиять на ваш' \
           f'бал, введите отметки, разделяя их пробелом.\n' \
           f'Пример: 8 10 7\n' \
           f'При отправке нового сообщения все введенные отметки сбрасываются!'

    return text

