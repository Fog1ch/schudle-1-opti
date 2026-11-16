# Modding API и IL2CPP ограничения

[Проверенная interop поверхность](EVIDENCE/current/interop-selected-api.json) содержит public methods/properties/fields выбранных типов и путь proxy assembly. [Managed assembly index](EVIDENCE/current/managed-interop-assembly-index.json) содержит refs/MVID/versions/hash.

MelonLoader является сторонним загрузчиком. Прокси передают вызов в native IL2CPP; изменение IL proxy не переписывает машинное тело GameAssembly. Обычный Harmony IL transpiler не является универсальным решением. IL2CPP-aware managed hooks могут использовать native detour внутри реализации. Совместимость конкретных hooks и loader runtime здесь не испытана.

Гейты будущего мода: game/metadata hashes, signatures, loader/interop compatibility, existing patches, thread/lifecycle constraints. Предпочтительные VA не использовать как runtime addresses. Unity object/API обычно требуют main thread; не переносить Unity calls в Task ради ускорения.

Prefix/Postfix не удаляет середину native UpdateDestination. Inline работа FixedUpdate не исчезает от hook отдельного helper. Полная замена FixedUpdate опасна и не нужна для узкого duplicate.

[Declared patches](EVIDENCE/current/mod-declared-targets.json), [raw attributes](EVIDENCE/current/mod-patch-attributes.json), [overlap](EVIDENCE/current/mod-target-overlaps.json). Dynamic reflection targets и реальный order не разрешены. PackagerConfiguration.ShouldSave overlap нужно рассматривать с обеими реализациями, а не объявлять конфликтом.

В пакет не включён готовый оптимизационный мод. Старые apply/rollback профили не включены и не запускались.
