# Учебный пример вебсервера



Данный проект является примером использования изучаемых 
технологий в рамках проекта "Webserver" курса "Python" в Яндекс.Лицее

Версия python: 3.7

## Установка зависимостей

Потребуются установить следующие пакеты
```
pip install flask
pip install flask_restful
pip install flask_wtf
pip install flask-socketio
```

## Запуск
```
python3 index.py
```
При первом запуске нужно инициализировать базу данных, для этого 
нужно выполнить запрос в браузере
http://localhost:8000/install

Сервис будет доступен по http://localhost:8000