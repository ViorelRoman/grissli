# grissli
Тестовое задание для собеседования

# Install
Чтобы установить данное приложение, достаточно скачать его из репозитория

    git clone https://github.com/ViorelRoman/grissli.git
    cd grissli
    pip install -r requirements.txt

# Setup
Перед тем как начать работу, надо создать базу данных:

    python manage.py makemirations

затем создать супер-пользователя:

    python manage.py createsuperuser

# Run
Чтобы запустить приложение, вы должны выполнить в директории проекта команду

    ./run.sh

После этого зайдите в админку по адрессу http://ip_тестовой_машины:8000/admin/ и добавьте задания в модель URLs.
Далее, для того чтобы выполнить задания, зайдите на страничку http://ip_тестовой_машины:8000/. Автоматически начнется выполнение заданий. Полученные данные так же сохраняются и в базе данных в модели URLInfo. 
