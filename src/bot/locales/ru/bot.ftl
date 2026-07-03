
cmd-start = Привет, { $name }!

btn-to-menu = Меню

menu =
    Главное меню

btn-menu-create = Создать опрос
btn-menu-start-survey = Начать опрос
btn-menu-statistics = Статистика


survey-creation-waiting-json = Введите json строку в нужном формате
survey-creation-success = 
    Отлично! Опрос создан, вот его UUID:
    { $survey_id }
survey-creation-error = Ошибка! Не получилось создать опрос. Проверьте формат


survey-representation = 
    Название: { $title }
    Описание: { $description }


survey-start-waiting-uuid = Введите uuid опроса
survey-start-error = Ошибка! Введите корректный uuid опроса
survey-answer-error = Ошибка! Выберите корректный вопрос
survey-end = Опрос пройден!


survey-statistics-waiting-uuid = Введите uuid опроса для просмотра статистики
survey-statistics-error = Ошибка! Введите корректный uuid опроса
survey-statistics = 
    Статистика:
    { $stats }