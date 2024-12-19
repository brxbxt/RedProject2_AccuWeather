# Проверка работоспособности веб-сервиса прогноза погоды

## Проведенные проверки:
1. Корректные названия городов: Проверены различные города с известными координатами (Москва, Санкт-Петербург, Лондон).  Сервис успешно возвращал прогноз погоды.
2. Некорректные названия городов: Введены несуществующие или неправильно написанные названия городов.  Сервис возвращал сообщение об ошибке.
3. Отсутствие данных от API: Имитировалось отсутствие данных от AccuWeather API (например, отключив интернет).  Сервис корректно выводил сообщение об ошибке "Ошибка получения данных о погоде для '{название_города}'. Возможно, проблема с API или сетью.".
4. Крайние значения погоды: Проверены случаи с экстремально высокими и низкими температурами, сильным ветром и высокой вероятностью осадков.  Модель `check_bad_weather` корректно классифицировала эти условия как "плохие".
5. Различные комбинации погоды: Проверены все комбинации хорошей/плохой погоды в начальной и конечной точках маршрута.  Вывод итогового сообщения ("Можно отправляться!" или "Сейчас не время для путешествий!") работает корректно.

## Обработка ошибок:
Система обрабатывает следующие типы ошибок:
1. Ошибка геокодирования: Возникает, если не удается определить координаты по названию города.
2. Ошибка получения данных от API: Возникает при проблемах с подключением к API или отсутствии данных от API.  Пользователь получает сообщение о проблеме с API или сетью, указывается город, где возникла проблема.
3. Другие ошибки: Любые другие исключения обрабатываются общим сообщением об ошибке.

## Влияние ошибок на общую работоспособность:
Все ошибки обрабатываются в блоках `try-except`, что предотвращает падение всего приложения. Пользователь получает понятное сообщение об ошибке и может предпринять необходимые действия для исправления проблемы (например, проверить название города или подключение к интернету).
