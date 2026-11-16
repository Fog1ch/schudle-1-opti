# Инвентаризация

889 файлов вне save paths, 7064229127 bytes. Это размер инвентаризированной установки на диске, не RAM/VRAM. 68 save-path файлов исключены из чтения и хэширования.

Полный путь относительно `B:\Schedule I`, размер, время снимка и SHA-256: [original-files-sha256.json](EVIDENCE/current/original-files-sha256.json). Важные 30 fingerprint entries: [critical-fingerprints.json](EVIDENCE/baseline/critical-fingerprints.json).

Категории: Player/native DLL; metadata; Cpp2IL stubs; interop/Managed libraries; Mods и UserLibs; serialized scene/asset containers; .resS/.resource payloads; конфигурации. Backup-like DLL не объявляются загруженными.

15 индексированных managed mod/library assemblies не означают 15 активных модов: это 10 DLL верхнего уровня Mods и 5 UserLibs. Другие subdirectories и сторонние network helpers отражены в файловом inventory, но не исследовались на обход защиты.

## Как получить отсутствующий оригинал локально
Найти точный относительный путь и SHA-256 в inventory. Проверить `Get-FileHash -Algorithm SHA256 -LiteralPath <полный путь>` в PowerShell. Не скачивать неизвестный бинарник вместо оригинала. Для нового native метода использовать включённый analyser с его RVA и соответствующим index; для asset object использовать container/path_id/file_offset/serialized_bytes из CSV. Выгружать только нужный небольшой диапазон с hash исходника и способом извлечения.

## Ресурсные индексы
[Containers и external refs](EVIDENCE/current/asset-containers-current.json), [object index](EVIDENCE/current/asset-object-index.csv), [предыдущие counts](EVIDENCE/prior/assets.json). 3064 Texture2D, 1310 AudioClip, 206 Shader records из прежнего аудита сверяются с текущими tables в QA. Это не уникальные или активные ресурсы. Candidate names не подтверждены class database.

## Конфигурации
[Безопасная выборка](EVIDENCE/current/performance-config-evidence.json) содержит performance preferences и boot diff относительно локального `.orig` неизвестного происхождения. Не включены save payloads, полные логи, translator service credentials или исходные игровые бинарники. Прежние значения подтверждаются отдельно hash comparison текущих конфигураций с исторической baseline.
