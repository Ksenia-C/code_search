# Что за этим стоит:
 - желание писать логику, тесты и возможность экспериментировать.

# Идея, как должно работать - 

Запускать elastic search надо вручную

Есть обертка для консоли - запускается run.py (в одной из корневых папок)
После считывает ввод, где можно создавать индексы, загружать в них доки из папок или например предобрабатывать код,
а также делать запросы

Скрипт считывает и парсит аргументы и передает их в методы в views/method_name/view.py где сам запрос обрабатывается
Для этих view.py нужно только request/response, то есть по сути вещь вроде как универсальная

Тестов пока нет. Крутых настроек репозитория - тоже. Да и сам код не факт что такой и останется.
Логгирования пока нет. Всех методов - нет. Пройденного ревью - тоже(
    
Здесь хочется прикрутить UI, и пока я не уверена как буду это делать


# Пример запроса

Создать новый индекс c именем с загруженной схемой в файле src/views/init/index_schemas/index_name.json

init index_name

# Максиму

Часть, которую мы хотели, чтобы ты сделал - в папку src/views/load_data или как тебе будет удобно. Там тоже сейчас лежит какое-то описание.

В целом у меня команды init sample_index сработала
