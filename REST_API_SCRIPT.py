from CulinaryApp import CulinaryApp
from CulinaryApp import possible_beginnings
import sys
import re
sys.setdefaultencoding('utf-8')


def InteractWithRestAPI():
    if len(sys.argv) > 1:
        i = sys.argv[1]
    else:
        i = None
    if len(sys.argv) > 2:
        ingr_list = sys.argv[2]
    else:
        ingr_list = None
    if i is not None:
        try:
            i = int(i)
        except ValueError:
            print('Вы не отправили число в теле запроса')
        if i not in range(12):
            print('Вы отправили неверное число в теле запроса')
        A = CulinaryApp([possible_beginnings[i]], load=False, print_=True)
        # temporary code - will be deleted BEGIN
        tmp = A.BackEnd.total_ingredients
        answer = sorted(tmp)
#        for j in answer:
#            j1=re.sub('«','',j)
#            j2=re.sub('»','',j1)
#            print(j2)
        answer = str(answer)
        answer = re.sub('«', '', answer)
        answer = re.sub('»', '', answer)
        print('Вы отправили индекс ' + str(i))
        if ingr_list is None:
            print('Выберите ингредиенты из следующих:')
            print(answer)
        # temporary code END
    if ingr_list is not None:

        try:
            ingr_list = re.sub('_', ' ', ingr_list)
            ingredient_list = ingr_list.split(',')
            # REPLACE _ TO ' '
        except KeyError:
            print('Неверный формат запроса')
        try:
            for ingredient in ingredient_list:
                assert ingredient.lower() in A.BackEnd.total_ingredients
        except AssertionError:
            print('ОШИБКА-Ингредиент ' + str(ingredient) + ' не найден')
        A.BackEnd.user_ingredients = ingredient_list
        answer = A.BackEnd.ingredient_search(
            print_answer=False, save_answer=True)
        return answer


InteractWithRestAPI()
#
