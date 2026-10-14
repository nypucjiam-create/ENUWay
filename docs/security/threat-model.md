# ENUWay аутентификация модулінің STRIDE моделі

Модельдің шекарасы: ENU пайдаланушысын растау, сессия ашу, user DB және аудит журналы. Төлем мен толық сапар логикасы модель шекарасына кірмейді.

| STRIDE | Санат | Қауіп | Компонент | Мера | Статус | Backlog |
|---|---|---|---|---|---|---|
| S | Spoofing | ENU пайдаланушысын немесе сессияны қолдан жасау | Пайдаланушы → Auth API | Бір реттік 15 минуттық токен, rate limit, сессияны қайтарып алу, ENU domain allowlist. | Open | #31 |
| T | Tampering | Рөл немесе бронь дерегін өзгерту | Web қолданба → Auth API / Booking API | Серверлік schema validation, deny-by-default RBAC, CSRF қорғанысы, атомарлық транзакция. | Open | #32 |
| R | Repudiation | Пайдаланушы әрекетін жоққа шығару | Auth API → Audit log | Append-only аудит, correlation ID, actor ID, уақыт және нәтиже; журналды 1 жыл сақтау. | Open | #33 |
| I | Information disclosure | Профиль және сапар деректерінің ашылуы | Auth API ↔ User DB | Field-level masking, least privilege, TLS, rest encryption, логта PII жазбау, сақтау мерзімі. | Open | #33 |
| D | Denial of service | Кіру мен растауды сұраулармен басу | Интернет → Auth API | IP және account rate limit, 429 жауабы, кезек лимиті, circuit breaker және метрика. | Open | #31 |
| E | Elevation of privilege | Moderator құқығын заңсыз алу | Auth API → Moderator функциясы | Рөлді тек серверден алу, әр endpoint-те authorization, privilege-change audit және теріс тесттер. | Open | #33 |

Редакцияланатын OWASP Threat Dragon файлы: `enuway-auth-threat-model.json`. Сурет: `enuway-auth-threat-model.png`.
