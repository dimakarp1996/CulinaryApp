Это наш проект по курсу "Архитектура ПО"

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

1)Поставить проект в корень диска С(чтобы адрес был С://CulinaryApp). Распаковать CulinaryServer.rar в текущую папку

2)Перейти в директорию CulinaryServer/CulinaryServer/Program.cs и там заменить PYTHON_DIR на вашу директорию? в которой у вас лежит python.exe(если его нет, установите python - без него программа не будет работать)

3)Запустить файл CulinaryServer/CulinaryServer/bin/Debug/CulinaryServer.exe , после чего совершать POST запросы для взаимодействия с приложением. В качестве первого запроса должно быть число от 0 до 12, в качестве второго запроса - это же число и(через пробел) список наименований ингредиентов(без кавычек, разделенный только запятыми), каждое наименование должно дословно соответствовать выведенным на экране выше. Если в наименовании больше 1 слова, разделяйте слова знаком _ , но не пробелом.

4)После запуска откройте файл Receipts.txt в C://CulinaryApp

[travis-url]: https://travis-ci.org/dimakarp1996/CulinaryApp
[travis-badge]: https://travis-ci.org/dimakarp1996/CulinaryApp.svg?branch=master
[coverage-image]: https://codecov.io/gh/dimakarp1996/CulinaryApp/branch/master/graph/badge.svg
[coverage-url]: https://codecov.io/gh/dimakarp1996/CulinaryApp

