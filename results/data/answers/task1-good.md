Я нашёл отчёт: **«SDU Campus Assistant — Sprint 5 Report.docx»** в папке Downloads. Он датирован 11 ноября 2026, дедлайн спринта 15 ноября 2026. Всё ниже взято только из этого отчёта. Если чего-то в отчёте нет, я так и пишу, чтобы ты не сказал на защите лишнего.

---

## 1. Цель проекта

Отдельного раздела «Project goal» в отчёте нет, но цель понятна из содержания.

**SDU Campus Assistant** — это веб-сайт и помощник для студентов SDU. Он работает на живом сайте **sdu-campus-assistant.vercel.app** и помогает в повседневной жизни на кампусе:
- вести личное расписание пар;
- узнать, где следующая пара и как туда дойти;
- смотреть предстоящие события кампуса, искать и фильтровать их;
- видеть всё это на **плане кампуса**: аудитория подсвечивается, и строится маршрут.

**Цель Sprint 5** — четыре user story:
- **Timetable (расписание):** US17, US18.
- **Events (события):** US19, US20.

Итог: все 4 истории выполнены (Done) и проходят свои тест-сценарии, за 4 дня до дедлайна.

---

## 2. Разбор отчёта по разделам

### 2.1 Summary (краткое резюме)
- Все 4 истории готовы и работают на живом сайте.
- Расписание: страница `/schedule` и вопрос «where is my next class». Ответ даёт аудиторию, время начала и маршрут.
- События: страница `/events`. Список идёт по дате, есть поиск по словам и фильтры Today / This week / This month / диапазон дат. Событие можно открыть на плане.
- Проверки 11 ноября:
  - **802** автотеста прошли;
  - **22 из 22** браузерных приёмочных проверок прошли на локальной копии релиза;
  - **13 из 13** прошли на живом сайте под гостем (visitor).

### 2.2 Stories at a glance (таблица историй)

| Story | Название | Владелец | Estimate | Priority |
|---|---|---|---|---|
| US17 | Manual Class Schedule Entry | Bexultan Nyshan | 4/10 | LC&HV |
| US18 | Where Is My Next Class | Zhomart Mankeyev | 4/10 | HC&HV |
| US19 | Campus Event List | Alan Kassymbek | 3/10 | LC&HV |
| US20 | Event Search and Date Filter | Olzhas Khussain | 3/10 | LC&HV |

У каждой истории «Pass 1/1, Fail 2/2», статус Done.

Важное правило из отчёта: **Fail-сценарий считается выполненным, когда описанный в нём сбой невозможен** (в таблицах это «Cannot happen»).

Каждая история также имеет **Deferred** пункт (отложено). Он либо не сделан, либо сделан как «extra» вне истории (раздел Beyond the stories).

> В отчёте **не расшифрованы** сокращения LC&HV / HC&HV и шкала «4/10». Скорее всего это *Low Cost & High Value* / *High Cost & High Value* (оценка «стоимость/ценность»), а 4/10 — оценка трудоёмкости по 10-балльной шкале. Сверь это с вашей командной методикой до защиты. Если не уверен, так и скажи: «this is our cost/value priority label».

### 2.3 US17 · Manual Class Schedule Entry (ручной ввод расписания)
- **Что делает:** авторизованный студент собирает свою неделю на `/schedule`: предмет, день недели, начало, конец, аудитория. Аудиторию выбирают из **справочника на 268 аудиторий**.
- **Какую проблему решает:** без личного расписания помощник не может сказать, куда идти. Это фундамент для US18.
- **Как работает:** данные хранятся **по аккаунту в Postgres** на живом сайте. Читать и менять расписание может только владелец.
- **Проверки:**
  - Pass: добавить, изменить и удалить пару, изменения сохраняются. Пример: INF 304 добавлен в D103, MAT 201 перенесён F202 → E101, затем удалён. API показывает то же самое.
  - Fail 1: «пользователь читает чужое расписание». Это невозможно: студент B, запрашивая пару студента A по id, получает **404** на GET и DELETE, а свой список у B пуст.
  - Fail 2: «пара с аудиторией не из справочника». Это невозможно: «VR 93» отклоняется с сообщением *«Choose a room from the list, like D103 or Hall A1»*, ничего не сохраняется. Правило действует и для редактирования, и для импорта.
  - Deferred: импорт из студенческого портала **не сделан**, с портала ничего не загружается.
  - QA 1: после повторного входа пара на месте. QA 2: расписание приватно.
- **Отступление от формулировки истории:** расписание вынесено на отдельную страницу `/schedule` со ссылкой из профиля. Профиль показывает следующую пару и пары на сегодня.
- **Как рассказать:** «US17 lets a student enter their own weekly timetable. It's stored per account in Postgres, it's private, and rooms must come from our 268-room directory, so we never save a room that doesn't exist.»

### 2.4 US18 · Where Is My Next Class (где следующая пара)
- **Что делает:** на запрос «Where is my next class» или «следующая пара» выбирает следующую пару из **своей** недели спрашивающего.
- **Какую проблему решает:** студенту не нужно вспоминать расписание и искать аудиторию, он сразу получает аудиторию, время и маршрут.
- **Как работает:**
  - время считается в **кампусном часовом поясе Asia/Almaty**;
  - карточка показывает пару, день и время, аудиторию, подсвеченную на плане, и кнопку **«How do I get there?»**;
  - если следующая пара сегодня, маршрут строится **от аудитории предыдущей пары**, а не от главного входа.
- **Проверки:**
  - Pass: в браузере карточка «Your next class · INF 304 [04-P] · Tomorrow, 10:00–10:50», D103 подсвечена.
  - Fail 1: «прошедшая пара названа следующей». Это невозможно. Тестировали до, во время и после пары и **на каждой минуте недели**: начавшаяся пара называется «on now», никогда не «next».
  - Fail 2: «гость видит ошибку сервера». Это невозможно: гость получает «This needs an account» и ссылку Sign in на `/login`, ошибок скриптов нет.
  - Deferred: уведомления перед парой не входят в историю. Они сделаны как extra.
  - QA 2 («нет расписания») проверен на живом сайте под гостем.
- **Как рассказать:** «US18 answers 'where is my next class' from the student's own schedule, in Almaty time. A class that has already started is shown as 'on now', not 'next', and a visitor gets a sign-in prompt instead of an error.»

### 2.5 US19 · Campus Event List (список событий)
- **Что делает:** `/events` показывает события, которые ещё не закончились, ближайшие первыми. У каждого есть дата, время, место, организатор и местоположение на кампусе. 11 ноября там было **16 событий** с 12 по 27 ноября.
- **Какую проблему решает:** студенту нужен один удобный список реальных событий кампуса.
- **Как работает:**
  - события **реальные**: каждые **30 минут** они копируются со страницы университета **SDU Life** в **собственную таблицу events** проекта;
  - все запросы читают эту таблицу. Так соблюдается ограничение «события хранятся в своей БД, без интеграции с календарём»;
  - сортировка по времени начала, затем по названию;
  - событие пропадает из списка в ту минуту, когда оно заканчивается.
- **Проверки:**
  - Pass: 16 событий в правильном порядке.
  - Fail «прошедшие события» и Fail «порядок вставки вместо порядка даты» невозможны.
  - Deferred: напоминания о событиях не сделаны.
  - QA 2: событие ZHAUAP BER! открывается на плане с подсвеченной G116 (Mini Red Hall).
- **Задача «связать место события с аудиторией»:** 13 из 16 событий размещены на плане. Это может быть аудитория (Бочка С1 = hall C1, D113), блок (G block аллея), Wi-Fi Zone или SDU Life Centre. У остальных 3 места нет: у двух «not announced», одно онлайн.

### 2.6 US20 · Event Search and Date Filter (поиск и фильтр по дате)
- **Что делает:** над списком есть поиск, чипы Today / This week / This month и две даты. Показывается, сколько событий подходит.
- **Какую проблему решает:** быстро найти нужное событие среди многих.
- **Как работает:**
  - каждое изменение фильтра отправляет **один SQL-запрос** к таблице events;
  - **каждое** слово должно быть в названии или описании, регистр не важен, в том числе для кириллицы;
  - событие должно **пересекаться** с выбранными днями;
  - между поисками в памяти **не хранится** список, всё делается запросами к БД (это требование истории).
- **Проверки:**
  - Pass: «Relay» → 2 из 16 (оба SDU Team Relay); This week (9–15 Nov) → 10.
  - Fail «события вне диапазона» невозможен: 6 событий после 15 ноября скрыты, отфильтрованные строки совпадают с таблицей строка в строку.
  - Fail «пустой результат = пустая страница» невозможен: показывается «No upcoming events match. Try another word, or a longer period.» и есть способ сбросить фильтры.
  - Deferred: сохранённые поиски и подписки не сделаны.
  - QA: счётчик «2 of 16 upcoming events»; This week = понедельник–воскресенье по кампусному времени.

### 2.7 How it was verified (как проверяли)
- **pytest**, автотесты по всему проекту, названы по сценариям и задачам историй: **802 passed, 0 failed**.
- **Браузерная приёмка** всех QA-сценариев с **двумя студенческими аккаунтами** на локальной копии релиза: **22/22**.
- **Браузерная приёмка как гость** (US18 QA 2, US19, US20) на живом сайте: **13/13**.
- **Почему аккаунтные сценарии проверяли локально:** регистрация тестовых аккаунтов на живом сайте заняла бы студенческие номера, которые могут принадлежать реальным студентам. Локальная копия запускает тот же код, что и продакшн: **commit 619e73b**.

### 2.8 Beyond the stories (сделано сверх историй)
Ни один из этих пунктов не ломает сценарии и не нарушает Deferred-пункты.
1. **Импорт расписания со скриншота.** Скриншот Course Schedule из портала читается **в браузере** и показывается на проверку до сохранения. С портала ничего не загружается, поэтому Deferred-пункт US17 соблюдён. Аудитории не из справочника отсеиваются. Как именно читается скриншот, в отчёте не сказано, не придумывай технологию.
2. **Напоминания о парах и .ics-файл.** Уведомление за несколько минут до пары с маршрутом, плюс .ics для календаря телефона. Это extra, потому что в US18 уведомления значатся как Deferred.
3. **Места из SDU Life.** Если поле места размыто, площадка берётся из описания («Venue: Blue Hall»). Размещены блоки, Wi-Fi Zone (она же Shanyraq Zone), Mini Red Hall (G116), Sport Hall и Blue Hall в SDU Life Centre.
4. **Единая карта кампуса.** Student House, SDU Life Centre, спортплощадки и подъезды нарисованы вокруг главного здания на каждом этаже. Для SDU Life Centre и Student House есть маршруты, другие входы предлагаются как альтернативы.
5. **Новости SDU.** Рядом с событиями показываются 10 последних новостей с sdu.edu.kz.

---

## 3. Технические термины простым языком

| Термин | Простыми словами |
|---|---|
| **Sprint** | Короткий период работы (в Scrum), за который команда делает набор задач. |
| **User Story (US)** | Требование с точки зрения пользователя: «как студент, я хочу…, чтобы…». |
| **Pass / Fail test script** | Pass описывает, что должно работать. Fail описывает сбой, который **не должен** случаться. |
| **Deferred** | Отложено, сознательно не входит в историю. |
| **QA scenario** | Сценарий проверки качества глазами пользователя. |
| **Acceptance check** | Приёмочная проверка: работает ли функция так, как требует история. |
| **Postgres (PostgreSQL)** | Реляционная база данных, где хранятся расписания и события. |
| **API** | «Дверь» к серверу, через которую страница получает и отправляет данные. |
| **GET / DELETE** | HTTP-методы: GET читает данные, DELETE удаляет. |
| **404** | Код ответа «не найдено». Чужая пара для другого пользователя просто «не существует», так ничего не раскрывается. |
| **SQL query** | Запрос к БД, например «дай события, где есть слово X и дата в диапазоне». |
| **Asia/Almaty (time zone)** | Часовой пояс кампуса. Нужен, чтобы «следующая пара» и «эта неделя» считались по местному времени. |
| **pytest** | Фреймворк автотестов на Python. |
| **Vercel** | Хостинг, где развёрнут живой сайт. |
| **Production / live site** | Рабочая версия, доступная всем. |
| **Local copy** | Та же версия, запущенная на своём компьютере. |
| **Commit 619e73b** | Конкретная версия кода в git. Доказывает, что локально и в продакшне один и тот же код. |
| **Visitor** | Незалогиненный пользователь (гость). |
| **.ics** | Стандартный файл календаря, который импортируется в календарь телефона. |
| **Room directory** | Справочник допустимых аудиторий (268 штук). |
| **Overlap (пересечение) дат** | Событие подходит, если хотя бы часть его времени попадает в выбранный период. |
| **Case-insensitive** | Поиск без учёта регистра («relay» = «Relay»), и для кириллицы тоже. |

---

## 4. Порядок устной защиты (примерно 5–7 минут)

1. **Вступление** (30 с): проект, команда, цель Sprint 5.
2. **Результат одной фразой** (20 с): 4 из 4 историй Done, за 4 дня до дедлайна, работает на живом сайте.
3. **Timetable** (1,5 мин): US17, потом US18. Подчеркни приватность, справочник аудиторий, часовой пояс и «on now».
4. **Events** (1,5 мин): US19, потом US20. Подчеркни реальные данные из SDU Life каждые 30 минут, собственную таблицу, SQL-фильтрацию и пустое состояние.
5. **Как проверяли** (1 мин): 802 / 22 / 13, и почему аккаунтные проверки шли локально.
6. **Beyond the stories** (40 с): экстра-функции, которые не нарушают Deferred.
7. **Заключение** (20 с) и переход к вопросам.

Если покажешь демо: открой `/events` → поиск «Relay» → This week → открыть событие на плане. Аккаунтную часть показывай на локальной копии, как в отчёте.

---

## 5. Текст выступления (английский)

> Good morning. I'm presenting Sprint 5 of our project, SDU Campus Assistant, a web assistant that helps SDU students with their timetable, campus events and finding their way on campus. It runs live at sdu-campus-assistant.vercel.app.
>
> This sprint had four user stories, US17 to US20, and all four are done and meet their test scripts. We finished on the 11th of November, four days before the deadline.
>
> The first two stories are about the timetable. In US17, a signed-in student builds their own week on the /schedule page: subject, weekday, start and end time, and a room chosen from our directory of 268 rooms. The schedule is stored per account in Postgres, and only the owner can read or change it. We checked that: when one student asks for another student's class by its id, the server answers 404. A room that isn't in the directory, like "VR 93", is refused, so we never save a room that doesn't exist.
>
> US18 builds on that. When a student asks "Where is my next class", or "следующая пара" in Russian, the assistant takes the next class from their own week, using campus time, Asia/Almaty. The card shows the class, the day and time, and the room lit on the campus plan, with a "How do I get there?" button. We tested every minute of a week: a class that has already started is called "on now", never "next". A visitor who isn't signed in gets a sign-in prompt, not an error.
>
> The other two stories are about events. In US19, the /events page lists upcoming events, soonest first, with date, time, place and organiser. The events are real: every 30 minutes we copy them from the university's SDU Life page into our own events table, and every query reads that table. On the 11th of November there were 16 upcoming events, and 13 of them can be opened on the plan.
>
> US20 adds a search box and date filters: Today, This week, This month, or a custom range. Each change sends one SQL query to the events table. Every word must appear in the title or description, and the event must overlap the chosen days. The page shows how many events match, and if nothing matches, it says so and lets you clear the filters instead of showing a blank page.
>
> For verification, 802 automated pytest tests pass. 22 of 22 browser acceptance checks pass on a local copy of the release with two student accounts, and 13 of 13 pass on the live site as a visitor. We ran the account checks locally on purpose: registering test accounts on the live site could take student numbers that belong to real students. The local copy runs the same commit as production.
>
> On top of the stories, we added a few extras that don't break any script: importing a timetable from a screenshot, class reminders with an .ics calendar file, better event locations taken from SDU Life descriptions, one map of the whole campus, and the latest SDU news next to the events.
>
> That's Sprint 5. Thank you, I'm happy to answer your questions.

---

## 6. Возможные вопросы и ответы

**Q1. What was the goal of Sprint 5?**
A: To let students keep a personal timetable and find their next class, and to give them a searchable list of real campus events. That's US17 to US20.
*Цель: личное расписание + следующая пара, и список событий с поиском.*

**Q2. How do you make sure one student can't see another's schedule?**
A: The schedule is stored per account, and the server only returns classes that belong to the signed-in user. We tested it: student B asking for A's class by id gets 404 on GET and DELETE.
*Данные привязаны к аккаунту. 404 вместо 403 означает, что чужая запись для B просто «не существует», и даже факт её существования не раскрывается. Последнее — общее объяснение, в отчёте написано только про 404.*

**Q3. Why choose rooms from a list instead of free text?**
A: So every saved room really exists and can be lit on the plan and routed to. "VR 93" is refused with a hint like "D103 or Hall A1". The same rule applies to edits and imports.
*Справочник из 268 аудиторий нужен для корректности данных и маршрутов.*

**Q4. How does "next class" handle a class that's in progress?**
A: A class that has started is shown as "on now", never as "next". We tested before, during and after a class, and at every minute of a week.
*Это защита от Fail-сценария «прошедшая пара названа следующей».*

**Q5. Why does the time zone matter?**
A: The server may run in a different time zone. We calculate in Asia/Almaty, campus time, so "next class" and "this week" (Monday to Sunday) are correct for students.
*Без этого «следующая пара» могла бы сдвинуться на несколько часов.*

**Q6. What happens if a visitor asks "where is my next class"?**
A: They get "This needs an account" and a Sign in link to /login, with no server or script errors.

**Q7. Where do events come from? Did you integrate with a calendar?**
A: No calendar integration. Every 30 minutes we copy events from the SDU Life page into our own events table, and all queries read that table. That was a constraint of the story.
*Важно: данные реальные, а не тестовые, и лежат в своей БД.*

**Q8. How do you make sure past events don't show?**
A: The list only includes events that haven't ended, and an event leaves the list the minute it ends. It's sorted by start time, then title.

**Q9. How does search and filtering work technically?**
A: Each change sends one SQL query to the events table. Every word must be in the title or description, case-insensitive, including Cyrillic, and the event must overlap the chosen date range. We don't keep a list in memory between searches.
*Фильтрация в БД, а не в браузере. Это прямое требование истории.*

**Q10. What does the user see when nothing matches?**
A: "No upcoming events match. Try another word, or a longer period.", with a way to clear the filters, not a blank page.

**Q11. Why were the account scenarios tested locally and not on the live site?**
A: Registering test accounts on the live site would use student numbers that may belong to real students. The local copy runs the same code as production, commit 619e73b.
*Это этичное решение, и оно не ослабляет проверку: код тот же самый.*

**Q12. What did you not do / what was deferred?**
A: Import from the student portal (US17), notifications (US18), event reminders (US19), and saved searches and subscriptions (US20) are deferred. Class notifications were built as an extra outside the story. Nothing is fetched from the portal.
*Будь честен: Deferred-пункты не входят в истории.*

**Q13. Isn't the screenshot import the same as the deferred portal import?**
A: No. The student uploads a screenshot themselves, it's read in the browser and shown for checking before saving. Nothing is fetched from the portal, so the deferred item stands. Rooms outside the directory are held back.
*Ключевое отличие: данные приносит сам студент, а не система забирает их с портала.*

**Q14. Why are 3 events not placed on the map?**
A: Two say "not announced" and one is online, so there's no physical place to show. 13 of 16 are placed.

**Q15. Did you change anything from the original story?**
A: Yes, one departure: the timetable lives on its own page, /schedule, linked from the profile. The profile shows the next class and today's classes.

**Q16. What do LC&HV / HC&HV and 4/10 mean?**
A: These are our priority (cost/value) and estimate labels. *В отчёте они не расшифрованы. Заранее уточни у команды точное значение, чтобы не ошибиться.*

**Q17. How do directions work for a class later today?**
A: The walk starts from the room of the class before it, not from the main entrance.

**Q18. What technologies did you use?**
A: From the report: Postgres for data, SQL queries for search, pytest for tests, hosted on Vercel. *Фреймворк фронтенда и бэкенда в отчёте не указан. Если спросят, отвечай по реальному коду проекта, а не наугад.*

---

## 7. Технические детали, которые нужно знать наизусть

- **Цифры:** 4/4 истории; 802 теста; 22/22 локально; 13/13 на живом сайте; 268 аудиторий; 16 событий (12–27 Nov); 13/16 на плане; синхронизация каждые 30 мин; «Relay» → 2 of 16; This week (9–15 Nov) → 10; 6 событий после 15 Nov скрыты; commit 619e73b.
- **Страницы:** `/schedule`, `/events`, `/login`, профиль (следующая пара + пары на сегодня).
- **Безопасность:** расписание хранится по аккаунту, только владелец, чужой id → 404 на GET и DELETE.
- **Валидация:** аудитория только из справочника, это работает для add, edit и import.
- **Время:** Asia/Almaty; «on now» против «next»; неделя Пн–Вс.
- **События:** своя таблица events, источник SDU Life, без календарной интеграции; сортировка start time → title.
- **Поиск:** один SQL-запрос на каждое изменение; все слова (AND) в title/description; без учёта регистра, включая кириллицу; пересечение по датам; без кэша в памяти; счётчик «X of Y»; дружелюбное пустое состояние.
- **Fail-логика:** «Fail met» = сбой невозможен.
- **Deferred против extras:** что отложено и что сделано сверх истории, без нарушения правил.
- **Почему локальная проверка аккаунтов:** реальные студенческие номера.

**Чего НЕ говорить, потому что этого нет в отчёте:** какой фреймворк или язык бэкенда, как именно распознаётся скриншот (OCR или другое), как реализован скрапинг SDU Life, как строится маршрут алгоритмически, есть ли AI/LLM-компонент. Если спросят, отвечай по коду проекта или честно скажи: *«That's not covered in the sprint report. I can check it in the code.»*

Если US18 — твоя история, подготовь её глубже всего: Asia/Almaty, «on now» против «next», проверку каждой минуты недели, ответ гостю и маршрут от предыдущей аудитории.
