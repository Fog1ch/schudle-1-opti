# Терминология

- IL2CPP: AOT преобразование управляемого кода в native implementation.
- Cpp2IL stubs: восстановленный metadata/API outline, не гарантированные тела исходника.
- Interop proxy: managed wrapper для native IL2CPP объекта/метода.
- RVA: адрес относительно загруженного PE image base.
- File offset: позиция bytes в исходном PE, определяется section mapping.
- Preferred VA: preferred image base + RVA; ASLR меняет реальную базу процесса.
- Alias/generic sharing: разные методы/инстанциации могут иметь общие machine bytes.
- Call site: статическое место инструкции, не измеренное число вызовов.
- CFG: граф базовых блоков и переходов управления; текущие graphs не полный CFG.
- Unwind span: range из PE exception metadata; не всегда весь исходный метод.
- PPtr: сериализованная ссылка по file ID/path ID.
- Type tree: описание сериализованного layout; в девяти исследованных файлах отсутствует.
- .resS/.resource: внешние payloads ресурсов; размер не равен resident memory.
- GC allocation: managed heap allocation; Vector3 на стеке сам по себе не GC allocation.
- Native handle: ресурс движка, lifetime которого не равен lifetime одной managed ссылки.
- Staggering: распределение callbacks во времени; не обязательно уменьшение их общего количества.
- p99 frametime: 99-й процентиль времени кадра; 1000/p99 не средний FPS худшего 1%.
- CONFIRMED_STATIC / HISTORICAL / HYPOTHESIS / UNKNOWN: уровни evidence данного пакета.
