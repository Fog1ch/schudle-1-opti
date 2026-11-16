# Открытые вопросы и узкие запросы данных

- Callback reentrancy: все consumers EndSetDestination callback и exceptions; закрыть formal contract перед implementation.
- Path ownership: все readers/writers Paths, destruction и invalidation; нет доказанного memory leak.
- Два Astar MoveNext с INVALID: определить корректные PE boundaries/control flow, не выполнять их. Это не блокирует существующее NPCMovement evidence.
- Generic delegate constructors: representative labels не являются доказательством runtime типа. Нужна metadata usage/type resolution.
- Render pipeline asset: расшифровать GraphicsSettings/QualitySettings и references; URP assembly alone недостаточна.
- Texture formats/mips/compression/streaming и native Unity setter cost: не извлечены.
- Полный AI/physics/Animator/IK/Burst graph: текущий выбранный scope не исчерпывающий.
- Dynamic Harmony targets/patch order и семантика ShouldSave prefix/postfix: статическое пересечение есть, конфликт не доказан.
- Активные NPC/lights/plants, CPU/GPU/GC/frametime и branch frequency: требуют отдельно разрешённого runtime, нельзя вывести offline.

## Формат DATA_REQUEST
Указать вопрос, оригинальный относительный путь, SHA-256 из inventory, method signature/RVA/range либо container/path_id/offset, read-only способ извлечения, ожидаемый небольшой формат и критерий проверки. Не просить всю игру или постоянный Custom MCP.

## Первая offline задача
Сформулировать тестовые обязательства для UpdateDestination на основе уже включённых листингов. Не писать мод, пока user отдельно не согласует разработку.
