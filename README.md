# Это наш проект CulinaryApp

Функционал проекта - приложение, куда вводишь то, что есть в холодильнике, и оно предлагает, что можно приготовить из имеющейся еды

[![Build Status][travis-badge]][travis-url]
[![Coverage][coverage-image]][coverage-url]

Как установить:

скачать репозиторий

Как запустить:

перейти в главную директорию проекта, набрать python CulinaryApp.py

Как запустить юнит-тесты:

перейти в главную директорию проекта, набрать python test_all.py

Как запустить REST API:

1)Поставить проект в корень диска С(чтобы адрес был С://CulinaryApp). Либо же поставить проект в другую папку и прописать глобальную переменную CULINARY_APP_DIR в качестве этой директории. 

2)Прописать глобальную переменную python_path - путь к exe-шнику python(для корректной работы REST API)

3)Запустить ( от имени администратора) файл CulinaryServer/CulinaryServer/bin/Debug/CulinaryServer.exe , после чего совершать POST запросы для взаимодействия с приложением. В качестве первого запроса должно быть число от 0 до 12, в качестве второго запроса - это же число и(через пробел) список наименований ингредиентов(без кавычек, разделенный только запятыми), каждое наименование должно дословно соответствовать выведенным на экране выше. Если в наименовании больше 1 слова, разделяйте слова знаком _ , но не пробелом.

ПРИМЕР ПЕРВОГО ЗАПРОСА: 0

ПРИМЕР ВТОРОГО ЗАПРОСА: 0 вода,водка,гашеная_сода,грибы

4)После запуска откройте файл Receipts.txt в C://CulinaryApp

[travis-url]: https://travis-ci.org/dimakarp1996/CulinaryApp
[travis-badge]: https://travis-ci.org/dimakarp1996/CulinaryApp.svg?branch=master
[coverage-image]: https://codecov.io/gh/dimakarp1996/CulinaryApp/branch/master/graph/badge.svg
[coverage-url]: https://codecov.io/gh/dimakarp1996/CulinaryApp

