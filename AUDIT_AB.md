# Phase 2 A/B: прямой локальный аудит

2026-11-16. Этот отчёт заменяет неподтверждённые выводы прежних отчётов в чате. Исходный пакет не менялся.

## Метод и целостность
Прочитаны phase2 листинги, npc-fields.json, полный methods-all.json, npc-incoming/outgoing.json, current/native-edges.json и CALL_GRAPHS/01-NPC-AI.json, 02-PATHFINDING.json. Собственная проверка SHA-256 по FILE_MANIFEST: 447 записей, 0 несовпадений (package-integrity-check.json). Это проверка файлов, не полноты CFG.
Python pathlib/json/hashlib/struct: локальное чтение, PE mapping, constants, unwind. Рекурсивный поиск имён четырёх отсутствующих листингов выполнен по всей лаборатории; отсутствие имени не доказывает отсутствия эквивалентного текста под другим именем.
После чтения Program.cs скопирован существующий phase2-npcmovement/analyzer/bin/Release/net8.0 в НОВУЮ папку аудита и выполнен Analyzer.exe 919EF0:E7 919A60:30A 8FF4B0:52 2B20AF0:86. Использованы существующие .NET 8, Iced.Intel, Mono.Cecil. Без установки пакетов. GameAssembly читался как данные, не исполнялся. Supplementary mode также создал новые methods-all/npc-methods/npc-fields; глобальный native scan не запускался. Старые файлы не перезаписаны.
GameAssembly SHA до и после: 61829050e56ca180d67be592e4bfe61ec97d2e9573f720d90a54e318a7e4381d.
Metadata SHA перед извлечением: e775c97da277da8eb1a90265478f3b65c9c3d6464aff4f7255d45280a1d1181f.

## A. Проверенные исходы UpdateDestination
Источник: EVIDENCE/phase2/evidence/UpdateDestination_8F9B70.asm.txt. RVA ниже, не runtime VA.
- 8F9B80: !_hasDestination -> возврат.
- 8F9BAF: IsInVehicle -> 8F9E05, result=1, EndSetDestination через 8F9DE3.
- 8F9BBE / 8F9BDD: IsMoving / pathPending -> возврат.
- 8F9BEF / 8F9C01: !CanMove / IsOnLadder -> возврат.
- 8F9C32: IsAsCloseAsPossible с 0.5 (float по RVA 2E5CB40). False -> 8F9C88 вызывает именно SetDestination 8F8110: текущая цель, существующий callback, bool=false, текущий success threshold, cache threshold=1.0 (2E5CB44), затем возврат.
- 8F9CB9: !hasPath пропускает ResetPath и обе очистки. Иначе ResetPath 8F9CCD, _currentPath=null 8F9CDD, _currentPathCorners=null 8F9CF0.
- 8F9D64/67: первое строгое distance<threshold -> result=4.
- При неуспехе заново читаются destination, position и threshold. 8F9DD3/D6: второе строгое сравнение -> result=4; иначе result=3 (8F9DDB). Вызов завершения 8F9DE3.
- Null-ветви ведут к helper 317B80 через 8F9E0F, а не к Success/Partial.
Равенство и unordered не проходят ja; result=3 следует только если достигнут финальный блок и обе проверки не прошли. Поведение аппаратных FP exceptions отдельно не доказано.

IsAsCloseAsPossible_8F59C0: первый strict test 8F5A90/94; иначе GetClosestReachablePoint 8F5AF6, failure -> false; success -> повторный strict test 8F5BAD/B1. NaN в первой distance сам по себе не доказывает итог false: остаётся fallback.
SetDestination_8F8110: NaN/inf компонентов цели отклоняются на 8F8247/60/71 и 8F8284/97/A8. Бесконечный retry не доказан. Прерывание старого callback на 8F8625 требует bool=true; retry=false пропускает именно это прерывание. Callback/threshold записываются на 8F862A/8649; дальнейшие failure-пути всё ещё могут завершить callback с result=0.

EndSetDestination_8F4490: callback 8F44B2, затем callback=null 8F44BC, _hasDestination=false 8F44CE, destination 8F4506/0E. При null callback пропускается блок вызова и null-store. PE runtime-function [8F4490,8F451A), unwind 36A41E0, flags=0: локального handler/chained unwind нет. При исключении callback обычная последующая очистка не исполняется; внешние обработчики и последующие тики UNKNOWN. Сам callback может менять поля, поэтому нельзя утверждать сохранность всех старых значений.

## Новые диапазоны callback
- evidence/helper_919EF0.asm.txt: базовый Behaviour.WalkCallback НЕ вызывает SetDestination. При Active result=0 увеличивает счётчик (919F50), ненулевой сбрасывает (919F44). Прежняя гипотеза retry в базовом теле не подтверждилась.
- evidence/helper_919A60.asm.txt: callback создаётся через виртуальный слот (919CF6), затем 919D36 вызывает overload 8F8C90. Полный индекс содержит другие WalkCallback implementations. Базовое тело не закрывает все overrides. Затирание новой цели после реентерабельного callback остаётся условным риском, не доказанным runtime-событием.

## B. Владение и writers
- npc-fields.json: _pathCache +1B8, _cacheNextPath +1C0, _currentPath +168, _currentPathCorners +170.
- _ctor_8FAE60: создаёт кэш и список; list store 8FB085, _pathCache store 8FB0A2. Инициализация на экземпляр NPCMovement. Общий кэш нескольких NPC НЕ доказан; последующая передача ссылок другими writers не исключена.
- UpdateCache_8F99B0: flag, nonnull path, corners.Length>1; flag=false 8F99F3; entry содержит первый/последний corner и текущую ссылку path (8F9AC4). Append 8F9B3B либо grow 8F9B1C. Прямого вызова AddPath не требуется.
- FixedUpdate: встроенный writer с guards 8F4C54/61/7E, flag clear 8F4C88, path store 8F4D5C, grow 8F4DBF. Пустой поиск входящих AddPath edges не доказывает отсутствия записи!
- SetDestination: GetPath 8F8771; cached SetPath 8F87F4 либо agent.SetDestination 8F8824. Затем agent.get_path 8F898E, _currentPath store 8F8993, corners store 8F89C0. helper_2B1F000 создаёт отдельный объект/handle и копирует путь агента. Cache-hit reference НЕ следует автоматически отождествлять с последующим _currentPath snapshot.
- AddPath сохраняет входной reference на 8FB524. GetPath возвращает entry.Path на 8FB6F7/70A; squared-distance comparisons 8FB6B8/BB и 8FB6EE/F1 строго исключают equality/unordered.
- Полный индекс: get_Paths 423EA0 имеет 542 записи-алиаса, set_Paths 469210 имеет 247. Ранее выбранный индекс скрывал это; тип receiver не определяется одним адресом.
- NPCMovement.OnDestroy_8F5F10 останавливает coroutine, явного очищения кэша в этом теле нет. Stop содержит локальные path/corners clears 8F9635/48. LoadManager.CleanUp -> NavMeshUtility.ClearCache на 5865BD не доказывает очистку NPCPathCache.
- Новый helper_8FF4B0: ctor entry сохраняет reference на 8FF4F1.
- Новый helper_2B20AF0: icall DestroyNavMeshPath на 2B20B38, затем m_Ptr=0 на 2B20B3F при нормальном возврате. Строка resolver по RVA 2F65030 подтверждает имя UnityEngine.AI.NavMeshPath::DestroyNavMeshPath(System.IntPtr). Native implementation и момент освобождения UNKNOWN.

## Инвалидация и исправления
Очистка локального path != удаление cache entry != инвалидация corners != уничтожение handle.
Удаление только managed-ссылки из списка не обязано ждать исчезновения остальных consumers: их ссылки могут продолжать держать объект. Destructive dispose/pooling/mutation требует отдельного доказательства lifetime. Прежнее требование отсутствия consumers для любого удаления entry было чрезмерным.
Утечка, безопасный pooling, общий меж-NPC кэш, все внешние writers и все virtual callbacks НЕ доказаны. Полный indirect/UnityPlayer/mod graph не восстановлен. Измерений FPS/GC нет.

Игра не запускалась. Игровые файлы, настройки и сохранения не менялись. Исходное исследование сохранено.
