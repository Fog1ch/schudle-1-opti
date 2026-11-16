# Текущее состояние

Дата: 2026-11-16. Статическая исследовательская поставка. Итог машинной проверки находится в [QA_REPORT.json](QA_REPORT.json); сама проверка не доказывает полноту reverse engineering.

## Выполнено
- Прочитаны исходные PROJECT_STATE, REPORT, README и phase2 REPORT. Проверены все 252 entries прежнего phase2 manifest, несовпадений нет.
- Исходные шесть identity hashes совпали. Инвентаризированы и хэшированы 889 файлов, исключены save paths. Хэши не являются копией их содержимого.
- Повторно использованы 146047 address-bearing method entries и исходное NPC evidence. Полный глобальный native scan не повторялся.
- Расширенный выбранный индекс: 1507 method entries; 89 native ranges; 2124 call/jump/indirect records; два Astar диапазона с INVALID, остальные выбранные диапазоны без INVALID.
- 15 managed mod/library assemblies, 26013 IL call/newobj sites, 103 Harmony attribute records. Один подтверждённый overlap объявленных targets.
- 9 SerializedFile v22 containers, 39 external file reference entries, 11016 выбранных serialized object index rows.
- Новые evidence и контрольная точка сохранены в phase3-handoff до упаковки.

## Новая информация относительно phase2
Animator ID cache, event-driven shadow LOD со setter dedup, ActionList staggering, retained path reference в AddPath/GetPath, callback-before-clear в EndSetDestination, Plant-light dependency, конкретный ShouldSave overlap. См. [находки](REVERSE_ENGINEERING/FINDINGS.md).

## Следующая граница
Формализовать callback reentrancy и все исходы UpdateDestination; закончить ownership/invalidation NPCPathCache; исследовать фактические patch semantics. Полная runtime приоритизация не выполнена и не разрешена. Не повторять готовую декомпозицию NPC roots без смены бинарников.

## Не выполнено
Нет полного indirect/callback/Burst/UnityPlayer graph, декодирования всех textures/scenes, активного render pipeline asset, всех dynamic Harmony targets, актуальных CPU/GPU/GC timings, FPS или поведения host/client в игре.

Предыдущая точка продолжения сохранена без изменений: [исходный PROJECT_STATE](EVIDENCE/prior/PROJECT_STATE.md).
