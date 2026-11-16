# Возможности: исследовательские, не измеренные ускорения

| Направление | Evidence | Следующий шаг | Риск |
|---|---|---|---|
| Duplicate distance в UpdateDestination | Два native distance sites в конечной ветви | Callback/float/retry proof; затем отдельное разрешение на narrow change | Высокий |
| ScheduleRu canvas scan cadence | Установленный IL + interval=0 | Измерить один canvas scan, задержки текста, baseline | Средний |
| ScheduleRu diagnostic append | DumpUntranslated и AppendAllText | Измерить редкость/стоимость, согласовать потерю диагностик | Низкий/средний |
| Texture budget | Конфигурация 8000 MB, historical 4 GB GPU | CPU/GPU/texture counters, один контролируемый эксперимент | Качество/подгрузки |
| Path-cache access/ownership | Retained reference, linear matching | Все owners/writers и cache frequency | Высокий |
| Plant light recomputation | Grid/LightExposureNode loop | Invalidation/event map; не менять рост | Высокий |
| Coroutine temporary objects | Allocation helper в отдельных branches | Runtime frequency и lifetime; generic type resolve | Средний/высокий |
| Dynamic mod interaction | ShouldSave declared overlap | Проверить semantics обеих реализаций | Сохранения |

## Не считать новой оптимизацией
Avoidance 2 Hz/random staggering уже есть. Ring buffer/path cache/Burst Average уже есть. Animator hash cache уже есть. Shadow setter dedup и distance LOD уже есть. ActionList staggered callbacks уже есть.

Не делать blanket FixedUpdate throttling, GC.Collect/GC disable, global shader warmup, новые allocator budgets, PhysX toggles, root-motion culling или resource repack без доказательств и согласования.
