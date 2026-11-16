# Дополнение к AUDIT_AB: оставшиеся вопросы

2026-11-16. Источник продолжения: ../phase2-ab-audit-20261116-0047/AUDIT_AB.md. Завершённая карта UpdateDestination повторно не исследовалась.

## Обозначения и пределы
P = ../EXPORT/AI_RESEARCH_PACKAGE/.
N = evidence/ в этой новой папке.
A = ../phase2-ab-audit-20261116-0047/evidence/.
Все адреса ниже RVA. CONFIRMED_STATIC означает проверенный листинг/metadata, не runtime. UNKNOWN означает, что не доказано ни наличие, ни отсутствие поведения по оставшимся косвенным цепочкам.

Метод: локальные MCP file/command tools; Python 3.12 pathlib/json/hashlib/struct; существующий .NET 8 Analyzer с Iced/Mono.Cecil в supplementary mode. Дополнительный metadata-reader/Program.cs собран локальным SDK с пустым списком NuGet sources, без установки пакетов. Игровая Cpp2IL DLL читается Mono.Cecil как metadata, не исполняется. Новый код и результаты только в этой папке. Пакет, старый аудит, игра и сохранения не изменялись. Новых извлечённых диапазонов 28, INVALID нет. Не выполнялся глобальный native scan.

## 1. Реальные overrides WalkCallback
callback-metadata.json получен из Assembly-CSharp Cpp2IL stub. Для 12 объявлений IsVirtual=true, IsNewSlot=false и проверена цепочка Base. Три отдельные базовые виртуальные семьи: Behaviour 919EF0, NPCAction 9641D0, Employee 6D7B40. Employee не override Behaviour. LocationBasedAction и LocationDialogue делят один адрес 968180: 12 override-объявлений, 11 уникальных override-тел. Всего с базами 15 объявлений / 14 уникальных тел. Это покрытие именного WalkCallback в данной assembly, не всех произвольно названных Action<WalkResult>.

Файл для каждой строки N/helper_<RVA>.asm.txt, кроме базы Behaviour: A/helper_919EF0.asm.txt.

| Метод | RVA | Проверенный эффект и точка продолжения | Назначение пути |
|---|---|---|---|
| Behaviour.WalkCallback | 919EF0 | счётчик Failed++ 919F50, иначе reset 919F44 | прямого SetDestination нет |
| Employee.WalkCallback | 6D7B40 | счётчик с временным ограничением 6D7B7C | прямого SetDestination нет; отдельная семья |
| NPCAction.WalkCallback | 9641D0 | IsActive 964218; счётчик 964229/35 и logging | прямого SetDestination нет |
| CustomerAttendDealBehaviour | 925460 | Active && Success: FaceDirection 925601, затем virtual call 92563E [r9+4F8] | прямого нет; эффект virtual target UNKNOWN |
| SmokeBreakBehaviour | 95AB50 | база 95AB62; Success -> BeginSmokeBreak 95AB71 | direct нет; продолжение 959E10 ниже |
| MoveToAndActBehaviour | 962AD0 | Success -> FaceDirection 962B86 и StartAct tail 962BA4; Failed >=3 -> virtual call 962C54 [rax+288] | direct нет; virtual/RPC продолжения UNKNOWN |
| NPCEvent_Conversate | 9668E0 | Active && Success -> FaceDirection 966965 | прямого назначения нет |
| NPCEvent_LocationBasedAction / LocationDialogue | 968180 | Active && Success && server -> virtual call 9681C4 [rax+408] | UNKNOWN после virtual call |
| NPCEvent_Sit | 96B7D0 | Active && Success && server -> virtual call 96B868 [r10+408], аргумент из списка мест | UNKNOWN после virtual call |
| NPCEvent_StayInBuilding | 96CBF0 | Active && server && (Success/Partial) -> PlayEnterAnimation 96CC2F | direct нет; coroutine ниже |
| NPCSignal_DriveToCarPark | 96DD10 | Active && server && (Success/Partial) -> virtual call на NPC 96DD69 [rax+798] | UNKNOWN после virtual call |
| NPCSignal_UseATM | 96EE50 | Active && Success -> Purchase 96EE7F | direct нет; coroutine ниже |
| NPCSignal_UseVendingMachine | 970370 | Active && Success -> Purchase 97039F | direct нет; coroutine ниже |
| NPCSignal_WalkToLocation | 970BE0 | Success: сетевой путь, затем virtual tail 970D44 [rax+2C8] | UNKNOWN после virtual tail |

Enum проверен metadata: Failed=0, Interrupted=1, Stopped=2, Partial=3, Success=4 (callback-metadata.json).

Дополнительные продолжения, каждый файл N/helper_<RVA>.asm.txt:
- BeginSmokeBreak 959E10: SmokeCigarette.Begin 959E7F -> 989CE0; FaceDirection 959F85. 989CE0 вызывает Equip_Networked 989D04 и OverrideIKWeight 989D47. Явного назначения пути в этих телах нет; полная цепочка Equip_Networked не исследована.
- StartAct 9628D0: проверенный wrapper выполняет сетевую отправку. RpcLogic___StartAct 961E10 завершает virtual jump 961E1A [rax+398]; runtime override не разрешён.
- PlayEnterAnimation 96C660 tail -> RpcLogic 96C800 на 96C767; StartCoroutine на 96C8D8.
- Purchase ATM 96E840 tail -> RpcLogic 96E970 на 96E947; FaceDirection 96EA74, StartCoroutine 96EB15.
- Purchase vending 96FCE0 tail -> RpcLogic 96FE00 на 96FDE7; FaceDirection 96FF8A, StartCoroutine 97002B.
StartCoroutine нельзя считать заведомо отложенным до возврата callback: первый MoveNext может выполняться синхронно. Тела этих iterator MoveNext и virtual destinations не разрешены в этом дополнении.

ИТОГ A: прямых вызовов SetDestination в 14 уникальных WalkCallback-телах не найдено. Это НЕ доказательство невозможности назначения пути: остаются перечисленные virtual/coroutine/equipment продолжения. Реентерабельное назначение не подтверждено и не исключено. Нельзя объявлять весь вопрос закрытым.

## 2. Paths: реальные readers/writers против адресных алиасов
Проверенные уникальные RVA (по полному methods-all.json каждый имеет одну запись):

| Роль | Файл | Метод и site RVA |
|---|---|---|
| владелец кэша / создание списка | P/EVIDENCE/phase2/evidence/_ctor_8FAE60.asm.txt | NPCMovement ctor 8FAE60: list store 8FB085; _pathCache store 8FB0A2 |
| создание списка | P/EVIDENCE/current/native/8FB770.asm.txt | NPCPathCache ctor: store Paths 8FB7C7 |
| reader/append writer | P/EVIDENCE/current/native/8FB4A0.asm.txt | AddPath: read list 8FB4E6, retained Path store 8FB524, append 8FB57D / grow tail 8FB56D |
| reader/append writer inline | P/EVIDENCE/phase2/evidence/UpdateCache_8F99B0.asm.txt | cache read 8F9A20, list read 8F9A96, Path store 8F9AC4, append 8F9B3B / grow 8F9B1C |
| reader/append writer inline | P/EVIDENCE/phase2/evidence/FixedUpdate_8F49E0.asm.txt | cache read 8F4CB5, list read 8F4D2C, Path store 8F4D5C, append fast/grow block 8F4EA0 / 8F4DBF |
| reader/enumerator | P/EVIDENCE/current/native/8FB5B0.asm.txt | GetPath list read 8FB610, enumerator 8FB629, return Path 8FB6F7/70A |
| caller/consumer | P/EVIDENCE/phase2/evidence/SetDestination_8F8110.asm.txt | _pathCache read 8F8708, GetPath call 8F8771 |
| entry-field writer, not list writer | A/helper_8FF4B0.asm.txt | PathCache ctor: Path store 8FF4F1 |

Full metadata scan of Assembly-CSharp finds typed cache owner NPCMovement._pathCache only, plus cache's own List<PathCache> backing field (callback-metadata.json CacheFields). This does not exclude generic object fields, reflection, mods or another assembly.

ALIASES, not unique implementations:
- get_Paths 423EA0: 542 address-bearing rows in full methods-all.json.
- set_Paths 469210: 247 rows; P/EVIDENCE/current/native/469210.asm.txt writes [rcx+10] at 469210. It can replace Paths only if rcx is proved to be NPCPathCache. The same instructions serve other fields/types.
- No direct calls to these two addresses or NavMeshPath ClearCorners/Finalize/Destroy wrappers were found in the saved P/EVIDENCE .asm listings by this bounded search (path-api-sites.json). Not a whole-game absence proof; inline access is already established.
- False offset hit explicitly excluded: CheckHit_8F3620.asm.txt 8F3B6D reads +1B8 from NPC loaded at 8F3B5D, followed by NPCHealth.TakeDamage 8F3B87. This is not NPCMovement._pathCache.

INVALIDATORS:
- Confirmed local refs clear: P/.../UpdateDestination_8F9B70.asm.txt 8F9CDD/8F9CF0 (hasPath branch); P/.../Stop_8F9560.asm.txt 8F9635/8F9648. These do NOT remove Paths entries.
- _cacheNextPath=false at UpdateCache 8F99F3 / FixedUpdate 8F4C88 consumes pending insertion, not cache invalidation.
- Confirmed corners-only invalidator: N/helper_2B20A60.asm.txt ClearCorners calls engine 2B20A8B, then m_Corners=null 2B20A91. No evidence it is invoked for cached objects in examined callers.
- NPCMovement.OnDestroy P/.../OnDestroy_8F5F10.asm.txt contains StopCoroutine tail 8F5F24; no Paths clear in that body.
- LoadManager.CleanUp P/EVIDENCE/current/native/586250.asm.txt calls NavMeshUtility.ClearCache at 5865BD. This does not establish invalidation of NPCPathCache.
- No confirmed runtime removal/clear/eviction/replacement caller for this Paths list in the examined scope. Global invalidator set remains UNKNOWN, not 'none'.

## 3. Ownership after cache hit and destruction
Distinguish P (cached path object) and Q (fresh agent.path snapshot).
1. cache owner -> Paths -> entry.Path holds P: AddPath 8FB524 / inline stores above.
2. GetPath returns P (8FB6F7/70A); SetDestination compares P to _currentPath at 8F877F. Equal-reference branch skips SetPath; otherwise SetPath call 8F87F4.
3. N/helper_2B1EC30.asm.txt SetPath forwards agent and P to icall via tail 2B1EC6F. Resolver string at GameAssembly RVA 2F64050 is UnityEngine.AI.NavMeshAgent::SetPath(UnityEngine.AI.NavMeshPath). The wrapper alone does NOT reveal whether engine copies, retains or mutates native path data. Engine-side ownership UNKNOWN.
4. At 8F898E SetDestination calls agent.get_path. P/EVIDENCE/phase2/evidence/helper_2B1F000.asm.txt allocates Q at 2B1F030, initializes native handle 2B1F061/63, calls CopyPathTo icall 2B1F08C. SetDestination stores Q at 8F8993 and corners at 8F89C0. Thus current snapshot is not automatically P.
5. N/helper_2B1E9B0.asm.txt CopyPathTo forwards arguments at 2B1E9EF; resolver string RVA 2F640A0 verifies name. Native copy semantics/depth UNKNOWN.
6. Under _cacheNextPath and corners-length guards, Q may be retained by another entry via UpdateCache/FixedUpdate. A cache-hit branch does not itself set _cacheNextPath=false, so do not infer 'cache hits never append' without prior-state proof.
7. Local clearing drops movement's Q reference; it neither clears the cache nor directly destroys a handle.
8. A/helper_2B20AF0.asm.txt Finalize reads object's m_Ptr at 2B20B12, calls resolved DestroyNavMeshPath at 2B20B38 and zeros m_Ptr at 2B20B3F on normal return.
9. N/helper_2B20AB0.asm.txt DestroyNavMeshPath is a separate wrapper forwarding at 2B20AE0 to the SAME resolver slot 3C0CBF8; Finalize uses the icall directly, not a call to wrapper RVA 2B20AB0. A graph searching only incoming edges to the wrapper misses this destruction path.
10. GC/runtime invocation of Finalize, all other potential native callers, engine implementation, timing and native sharing UNKNOWN. No runtime profiling performed.

## Remaining narrowly defined work
- Resolve concrete targets at 92563E, 962C54, 9681C4, 96B868, 96DD69, 970D44, 961E1A using actual IL2CPP slots/type usage, not guessed names.
- Resolve coroutine types allocated in RPC logic and inspect initial MoveNext before ruling out synchronous reentrancy.
- Full receiver-aware external/inlined Paths writer search is not covered by the saved selected graphs; no global rescan was repeated here.
- Engine SetPath/CopyPathTo/Destroy implementation lives beyond the resolved wrappers; ownership transfer and reclaim timing not established.

No leak or pooling-safety conclusion. Original package, previous audit and game files must remain unchanged.
