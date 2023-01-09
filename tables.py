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
                    number = (int(old_marks[i]) - int(marks[i]))/int(old_marks[i]) * 100
                    percent = f'(- {round(number, 1)} %)'
                else:
                    number = (int(marks[i]) - int(old_marks[i]))/int(marks[i]) * 100
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
            result = f'{result}\n\nСредний бал в этой четверти: {round(average_mark, 2)}, ' \
                     f'что на {round(((average_mark - average_mark_old)/average_mark * 100), 1)}% лучше, ' \
                     f'чем в прошлой. ' \
                     f'Средний бал в прошлой четверти: {round(average_mark_old, 2)}'
        if average_mark_old > average_mark:
            result = f'{result}\n\nСредний бал в этой четверти: {round(average_mark, 2)}, ' \
                     f'что на {round(((average_mark_old - average_mark) / average_mark_old * 100), 1)}% хуже, ' \
                     f'чем в прошлой. ' \
                     f'Средний бал в прошлой четверти: {round(average_mark_old, 2)}'
        if average_mark_old == average_mark:
            result = f'{result}\n\nСредний бал в этой четверти: {round(average_mark, 2)}, ' \
                     'что совпадает с прошлой.'
    else:
        if average_mark != 0:
            result = f'{result}\n\nСредний бал в этой четверти: {round(average_mark, 2)}'

    return result
