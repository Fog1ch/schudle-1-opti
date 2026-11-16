# HANDOFF PROMPT: Schedule I Performance Overhaul

Ты продолжаешь исследование по приложенному AI_RESEARCH_PACKAGE. У тебя может не быть Custom MCP, Windows или доступа к исходной игре. Пакет является источником evidence, а не полным исходным кодом или доказательством ускорения.

## Сначала прочитай
1. PROJECT_OVERVIEW.md, PROJECT_STATE.md, GAME_ARCHITECTURE.md.
2. REVERSE_ENGINEERING/FINDINGS.md и REVERSE_ENGINEERING/EVIDENCE_RULES.md.
3. REVERSE_ENGINEERING/NPC_DESTINATION_CONTRACT.md и PATH_CACHE_OWNERSHIP.md.
4. SUBSYSTEMS/ нужного направления; OPEN_QUESTIONS.md, RISKS.md, OPTIMIZATION_OPPORTUNITIES.md.
5. QA_REPORT.json и FILE_MANIFEST.json. При доступном Python запусти `python ANALYZERS/offline_query.py verify .` из корня пакета. Это не требует игры, сети, MCP, .NET или установки пакетов.

## Условия работы
Не запускать игру, не менять её файлы, настройки, сохранения или установленные моды. Не устанавливать инструменты без необходимости. Не разрабатывать и не применять оптимизационный мод без отдельного согласования. Не удалять прежнее исследование. Не считать это разрешением на runtime profiling. Не обходить защиты или DRM.

## Достоверность
Различай CONFIRMED_STATIC, HISTORICAL, HYPOTHESIS и UNKNOWN. Ссылайся на относительный файл, метод и RVA либо IL offset. При несовпадении GameAssembly/metadata fingerprint не переноси адреса на другую сборку. Preferred VA = 0x180000000 + RVA, не runtime VA из-за ASLR.
Call-site counts не runtime counts. Cpp2IL stubs/interop не исходные C# bodies. Generic sharing и aliases не доказывают тип фактического объекта; даже один символ по адресу может быть representative generic constructor. 0x43FEC0 является shared ret. Не выводи семантику из первых alias labels.
Новые native ranges ограничены Cpp2IL Length; два Astar MoveNext обрываются на INVALID. NPC phase2 roots имеют отдельную unwind проверку и +1 trailing byte. Нет полного CFG/indirect/Burst/UnityPlayer анализа. Candidate resource names эвристические, payload layouts не подтверждены.

## Что уже известно, не предлагай повторно
- NPC avoidance уже 0.5 s со случайным стартом; квадраты расстояний <=625 до Player Avatar.CenterPoint, no-player out distance=0.
- NPCMovement.FixedUpdate серверный; не уменьшать частоту всей симуляции.
- Path cache, NativeArray ring history, Burst Average уже существуют. NavMeshPath.corners кэшируется на объекте.
- AvatarAnimationId уже хранит dictionary name-to-ID; знакомые имена не обязательно повторно StringToHash.
- ShadowLODController уже distance LOD, camera movement events и dedup одинакового mode.
- TimeManager уже использует ActionList.InvokeAllStaggered.
- S1Perf уже меняет Animator culling и collision reuse; ScheduleRu установленный бинарник важнее несовпавшего локального build.
- Измеренного прироста FPS/CPU/GC/GPU нет.

## Первый полезный offline шаг
Выбери ОДНО направление: (A) формальная карта UpdateDestination + EndSetDestination callback reentrancy; (B) владельцы retained NavMeshPath и условия безопасной invalidation; (C) взаимодействие двух PackagerConfiguration.ShouldSave patches; (D) риски действующего Animator culling.
Используй уже включённые листинги и индексы, не повторяй восстановление NPC roots. Для A отдельно сохрани строгий `< threshold`, NaN/equality поведение, branch reset только при hasPath, callback до очистки полей на нормальном возврате, отдельно exception behavior, retry-вызов SetDestination с существующим callback. Для B не делай вывод об утечке только из AddPath/GetPath: внешние writers не полностью найдены.

## Поиск без игры
`python ANALYZERS/offline_query.py methods NPCMovement`
`python ANALYZERS/offline_query.py methods AvatarAnimationId`
`python ANALYZERS/offline_query.py calls GetAverageLightExposure`
`python ANALYZERS/offline_query.py mods PackagerConfiguration`
В EVIDENCE/phase2/evidence/methods-all.json полный ранее извлечённый address-bearing method index. В EVIDENCE/current/selected-types-fields.json поля/сигнатуры выбранных типов, interop-selected-api.json публичная поверхность. В CALL_GRAPHS/ адресные graphs, без заявления о полном графе игры.

## Граница автономности
С пакетом можно продолжать техническую аргументацию, анализ уже извлечённого кода, спецификации и тестовые планы. Нельзя честно получать новые неизвестные native bodies, текстуры, активные scene values или FPS из отсутствующей игры. Если доказательства не хватает, создай DATA_REQUEST.md: точный относительный оригинальный путь, его SHA-256 из original-files-sha256.json, нужные RVA/размеры либо object path_id, read-only способ извлечения и ожидаемый формат. Не требуй постоянный MCP; пользователь сможет передать отдельный небольшой файл позже.

## Требуемый результат следующего этапа
Кратко зафиксируй исследованный scope, новые факты с evidence, гипотезы, противоречия, неизменённые ограничения, список файлов и следующий проверяемый шаг. Не заявляй FPS gain без отдельно разрешённого воспроизводимого runtime test. Сохрани все знания в пакет, не только в разговор.
