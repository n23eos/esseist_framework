# Routing eval: 20 промптов по конфликтам C1–C4

Проверяет, какой скилл из библиотеки письма триггерится на пользовательский запрос.
Конфликты из ресерча 2026-09-01 (§1): C1 «пост/сценарий/тред» ловят 3 скилла,
C2 де-слоп ловят 2, C3 «essay/article» без разграничения, C4 первенство голоса.

Метод: судья (свежий сабагент) получает description всех 8 скиллов дословно и один
промпт; отвечает, какой скилл вызвал бы первым (или none). Прогон до правки
description и после; успех — колонка «факт» совпадает с «ожидание» ≥18/20.

| # | Промпт | Ожидание | Конфликт |
|---|--------|----------|----------|
| 1 | давай сценарий про прокрастинацию | essayist | C1 |
| 2 | пост про то, что заметки не работают | essayist | C1 |
| 3 | напишем тред про агентов | essayist | C1 |
| 4 | новое эссе про свободу воли | essayist | C1 |
| 5 | help me write an essay about why attention matters | essayist | C1 |
| 6 | перепиши этот черновик моим голосом (черновик приложен) | nikolai-voice | C1-граница |
| 7 | звучит ли этот текст как я? (текст приложен) | nikolai-voice | C1-граница |
| 8 | убери AI-слоп из этого текста (текст приложен) | no-ai-slop | C2 |
| 9 | does this read as AI-written? (text attached) | no-ai-slop | C2 |
| 10 | сделай текст менее роботным, но сохрани мой голос | no-ai-slop | C2 |
| 11 | write a tutorial blog post about Docker from these notes of mine | article-writing | C3 |
| 12 | напиши статью-рассуждение про минимализм | essayist | C3 |
| 13 | here are 20 of my posts, build a reusable style profile from them | brand-voice | C4 |
| 14 | напиши ответ на этот комментарий от моего лица | nikolai-voice | C4 |
| 15 | adapt this essay for LinkedIn and X | content-engine | — |
| 16 | make a content calendar for my YouTube channel | content-engine | — |
| 17 | разбери мою ситуацию как я бы сам разобрал | nikolai-mind | — |
| 18 | напиши README для этого репозитория | none | контроль |
| 19 | fix this failing test in auth.py | none | контроль |
| 20 | продолжим эссе | essayist | resume |

## Прогоны

Результаты дописываются ниже: дата, конфигурация description, счёт, промахи.

### 2026-09-01 — baseline (description как есть)

**Счёт: 20/20.** 4 судьи × 5 промптов, все совпали с ожиданием.

Оговорки судей:
- №8–10 (C2): humanizer против no-ai-slop — «реальная борьба каждый раз», no-ai-slop выигрывает
  на формулировках «preserving the writer's personal voice» и «asks whether writing reads as AI»,
  которых у humanizer нет. Запас маленький.
- №11 (C3): essayist против article-writing — решило наличие готовых заметок в промпте.
- Метод — форс-выбор из 8 description бок о бок. Это ЛЕГЧЕ реального триггеринга, где Claude
  видит description в списке и может зацепиться за первый подходящий (у nikolai-voice в описании
  есть глаголы черновика: «draft a Telegram/X post, video script, essay»). 20/20 здесь не
  гарантирует 20/20 в бою — негативные клаузы всё равно ставим.

Вывод: точечные правки, не перестройка. (1) nikolai-voice — убрать глаголы черновика,
негативная клауза на essayist. (2) humanizer — клауза «DO NOT TRIGGER when no-ai-slop applies».
(3) article-writing — клауза на essayist (нет материала → интервью). (4) brand-voice — исключение
для nikolai-voice как канона голоса владельца.

### 2026-09-01 — после развода триггеров

Внесены все 4 правки (nikolai-voice, humanizer, article-writing — description;
brand-voice — строка о canonical source в теле). **Счёт: 20/20**, 2 судьи × 10 промптов.

Качественный сдвиг против baseline: решения по спорным парам теперь опираются на явные
негативные клаузы, а не на тонкую разницу формулировок — №5/№11/№12 судьи разрешили через
«DO NOT TRIGGER» article-writing, №8–10 через клаузу humanizer («сам себя запрещает для
русского и когда голос должен выжить»), №6 — черновик против «from scratch» у nikolai-voice.
Детерминизм вместо удачи.

Попутно закрыт CRITICAL из ресерча (§1 «Мёртвое и протухшее»): установленный
`~/.claude/skills/essayist` был устаревшей копией без publish-raincoat.md — заменён
симлинком на репо, README теперь предписывает симлинк вместо cp.
