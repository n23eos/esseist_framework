# Публикация эссе на raincoat.cc

Только по явной команде «публикуй». Процесс проверен 2026-08-29 на эссе «Инструмент всех инструментов».

## Устройство сайта

Репо `n23eos/raincoat_website`, GitHub Pages, ветка `master`, домен raincoat.cc. Локальный клон: `~/code_projects/raincoat_website` (нет — склонировать). Блог клиентский: `blog.html` рендерит `posts/<slug>.md`, список постов — `posts/index.json`.

## Шаги

1. `git -C ~/code_projects/raincoat_website pull` — сайт мог меняться с других машин.
2. Спроси одной строкой: «С английским переводом?» (по умолчанию — да, так было в первый раз).
3. Скопируй `draft.md` → `posts/<slug>.md`. Под заголовком добавь строку:
   `*Написано при помощи фреймворка [esseist_framework](https://github.com/n23eos/esseist_framework).*`
4. Если перевод: создай `posts/<slug>-en.md` — перевод, сохраняющий голос (не гладкий канцелярит). Под заголовком две строки:
   `*Auto-translated from Russian by AI. Original: [«<русское название>»](blog.html?post=<slug>).*`
   `*Written with the [esseist_framework](https://github.com/n23eos/esseist_framework).*`
5. Добавь записи в `posts/index.json` (slug, date, title, desc; для EN в desc пометка «Auto-translated from Russian by AI»). Проверь JSON валидность.
6. Учти мини-рендерер сайта: заголовки `#`–`###`, списки, цитаты, `**`/`*`/`` ` ``, картинки, `---`. Таблиц и сносок нет — не использовать.
7. Коммит в формате `feat: add essay '<название>' (ru/en)` (без attribution), push в `master`.
8. Проверь живой деплой: `curl -sf https://raincoat.cc/posts/<slug>.md` в цикле until (Pages собирается ~1 минуту), затем открой `https://raincoat.cc/blog.html?post=<slug>` и убедись, что рендер живой.
9. Отдай пользователю обе ссылки.

## После

В session.md к статусу done допиши строку `published: <дата> <ссылки>`.
