import sys
from CulinaryApp import CulinaryApp
from CulinaryApp import possible_beginnings
import re


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
            print('You did not send a number')
        if i not in range(12):
            print('You have sent a wrong number')
        print('The number is read: ' + str(i))
        answer = None
        A = CulinaryApp(urls=[possible_beginnings[i]], load=False,
                        max_num=50, print_=True)
        tmp = A.BackEnd.total_ingredients
        answer = sorted(tmp)
#        for j in answer:
#            j1=re.sub('«','',j)
#            j2=re.sub('»','',j1)
#            print(j2)
        answer = str(answer)
        answer = re.sub('«', '', answer)
        answer = re.sub('»', '', answer)
        print('You have sent index ' + str(i))
        if ingr_list is None:
            print('Choose ingredients from the following:')
            print(answer)
            file = open(
                "C://CulinaryApp//possible_ingredients_"
                + str(i) + ".txt", "w", encoding="utf-8")
            file.write(answer)
            file.close()
            print('Due to the possible issues with encoding,' +
                  'ingredient list is also recorded into ' +
                  "C://CulinaryApp//")
    if ingr_list is not None:
        print("Processing ingr_list")
        try:
            ingr_list = re.sub('_', ' ', ingr_list)
            ingredient_list = ingr_list.split(',')
            # REPLACE _ TO ' '
        except KeyError:
            print('wrong query format')
        try:
            for ingredient in ingredient_list:
                assert ingredient.lower() in A.BackEnd.total_ingredients
        except AssertionError:
            print('Error - at least 1 ingredient  not found')
        A.BackEnd.user_ingredients = ingredient_list
        answer = A.BackEnd.ingredient_search(
            print_answer=False, save_answer=True)
        # Печатать ответ при использовании текущего Rest API нельзя!!!!
        # Ошибка из-за кодировки
        # А вот при вызове с консоли ответ можно печатать
        print('Due to the possible encoding issues,')
        print("3 most similar receipts are found" +
              "and are located in C://CulinaryApp//receipts.txt")
    return answer


InteractWithRestAPI()
#
