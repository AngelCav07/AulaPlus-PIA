# Business Requirements Document (BRD) — AulaPlus

## 1. Información General y Contexto del Negocio
* **Nombre del Sistema:** AulaPlus  
* **Giro del Negocio:** Plataforma de intermediación y gestión de tutorías académicas personalizadas 1 a 1.  
* **Actores Principales:** Estudiante, Tutor, Sistema Automatizado AulaPlus y Administrador/Soporte.  
* **Recurso Clave:** Sesión de tutoría académica (90 minutos de duración pactada).  
* **Objetivo del Negocio:** Automatizar la reserva, control de disponibilidad, validación de evidencia mediante grabaciones y la liquidación financiera justa e inmutable entre estudiantes y tutores.

---

## 2. Glosario del Dominio (Ubiquitous Language)
* **Estudiante:** Usuario que solicita y recibe la asesoría académica para una materia y tema específico.
* **Tutor:** Asesor académico encargado de impartir la sesión personalizada.
* **Sesión:** Agregado raíz que representa el compromiso académico pactado entre un estudiante y un tutor en una fecha y modalidad determinada[cite: 2].
* **Modalidad:** Formato de impartición de la sesión, pudiendo ser `Presencial` o `EnLinea`.
* **Estado de la Sesión:** Ciclo de vida por el que transita una tutoría: `Programada`, `Confirmada`, `Completada`, `Cancelada` o `Reembolsada`.
* **Liquidación:** Objeto de valor financiero que desglosa el costo pactado (\$200.00 MXN), la comisión retenida por la plataforma (\$40.00 MXN) y el monto a transferir al tutor (\$160.00 MXN).
* **Grabación:** Evidencia audiovisual de la clase en línea cuya duración efectiva se audita frente al umbral del 70% ($\ge 63$ minutos) para autorizar la liquidación.

---

## 3. Reglas de Negocio Formales (RN)
* **RN-01 (Anticipación Mínima de Reserva):** Toda reserva de sesión debe realizarse con un mínimo estricto de 48 horas de anticipación respecto a la hora actual de solicitud (CP-01 a CP-03).
* **RN-02 (Tarifa y Desglose Financiero Estándar):** La tarifa por sesión es fija de \$200.00 MXN; al completarse con éxito, \$160.00 MXN se transfieren al tutor y \$40.00 MXN corresponden a la comisión de servicio de AulaPlus.
* **RN-03 (Límite Diario de Tutores):** Un tutor puede tener asignadas un máximo de 5 sesiones confirmadas en un mismo día calendario (CP-10, CP-11).
* **RN-04 (Umbral Mínimo de Grabación Efectiva):** Para que una sesión en línea pase a estado `Completada` y se libere la dispersión de fondos, la grabación debe cubrir al menos el 70% de la duración total pactada (mínimo 63 minutos de 90 minutos) (CP-04, CP-06).
* **RN-05 (Reembolso por Incumplimiento de Duración):** Si la duración reportada en la grabación es menor al 70% (< 63 minutos), la sesión cambia automáticamente a estado `Reembolsada`, se bloquea el pago al tutor y se notifica a soporte (CP-05, CP-07).
* **RN-06 (Inmutabilidad de Sesiones Finalizadas):** No se permite la cancelación ni la modificación de sesiones que se encuentren en estado `Completada` o previamente `Cancelada`.

---

## 4. Flujo del Proceso de Negocio (Ciclo de Estados)
```text
           [Solicitud de Reserva]
                     │
         ¿Anticipación >= 48 h?
        ├── No ──> [Rechazo / 400 Bad Request]
        └── Sí ──> (CONFIRMADA)
                     │
              [Subir Grabación]
                     │
         ¿Duración >= 70% (63 min)?
        ├── No ──> (REEMBOLSADA) ──> [Dispersión = $0.00]
        └── Sí ──> (COMPLETADA)  ──> [Dispersión Tutor = $160.00]
```

---

## 5. Historias de Usuario con Criterios Gherkin

### US-01: Reserva de tutoría por estudiante
**Como** estudiante  
**Quiero** reservar una sesión indicando materia, tema, modalidad, fecha y horario  
**Para** asegurar mi tutoría con al menos 48 horas de anticipación  

* **Escenario: Reserva válida con anticipación suficiente (CP-01)**
  * **Given** que el estudiante seleccionó materia, tema, modalidad, fecha y horario, y la fecha/hora seleccionada es al menos 48 horas posterior al momento actual
  * **When** el estudiante confirma la reserva
  * **Then** el sistema crea la reserva y la envía a asignación automática de tutor en estado `Confirmada`.

* **Escenario: Reserva rechazada por falta de anticipación (CP-02)**
  * **Given** que el estudiante seleccionó una fecha/hora con menos de 48 horas de anticipación
  * **When** intenta confirmar la reserva
  * **Then** el sistema rechaza la operación y muestra el mensaje "La reserva debe realizarse con al menos 48 horas de anticipación".

---

### US-02: Asignación automática de tutor
**Como** estudiante  
**Quiero** que el sistema me asigne automáticamente un tutor disponible que cumpla mis criterios  
**Para** no tener que buscar tutor manualmente  

* **Escenario: Asignación automática exitosa**
  * **Given** que existe al menos un tutor con disponibilidad que coincide en materia, tema, modalidad, fecha y horario
  * **When** el estudiante confirma la reserva
  * **Then** el sistema asigna automáticamente uno de los tutores disponibles y la reserva queda en estado `Confirmada`.

* **Escenario: No hay tutor disponible**
  * **Given** que no existe ningún tutor con disponibilidad que coincida con los criterios seleccionados
  * **When** el estudiante confirma la reserva
  * **Then** el sistema no crea la sesión y muestra "No hay tutores disponibles para los criterios seleccionados".

---

### US-03: Pago de reserva de sesión
**Como** estudiante  
**Quiero** pagar $200 MXN al confirmar mi reserva  
**Para** asegurar mi lugar con el tutor asignado  

* **Escenario: Pago exitoso al confirmar reserva**
  * **Given** que el estudiante confirmó una reserva válida
  * **When** se procesa el pago de $200 MXN
  * **Then** la reserva queda registrada como pagada y se genera el comprobante de la transacción.

* **Escenario: Pago fallido**
  * **Given** que el estudiante confirmó una reserva válida
  * **When** el pago de $200 MXN es rechazado por el procesador
  * **Then** la reserva no se confirma y el sistema muestra "El pago no pudo ser procesado. Intente nuevamente".

---

### US-04: Calificación de la sesión
**Como** estudiante  
**Quiero** calificar la sesión dentro de las 24 horas posteriores a su finalización  
**Para** dar retroalimentación sobre el servicio del tutor  

* **Escenario: Calificación dentro del plazo**
  * **Given** que la sesión fue marcada como `Completada` y han transcurrido menos de 24 horas desde su finalización
  * **When** el estudiante envía su calificación
  * **Then** el sistema registra la calificación asociada al tutor.

* **Escenario: Calificación fuera de plazo**
  * **Given** que han transcurrido más de 24 horas desde que la sesión se marcó como `Completada`
  * **When** el estudiante intenta calificar
  * **Then** el sistema rechaza la acción y muestra "El periodo de calificación ha finalizado".

---

### US-05: Cancelación de sesión por estudiante
**Como** estudiante  
**Quiero** solicitar la cancelación de una sesión con al menos 48 horas de anticipación  
**Para** no recibir penalización  

* **Escenario: Solicitud de cancelación sin penalización**
  * **Given** que la sesión está programada para dentro de más de 48 horas
  * **When** el estudiante solicita la cancelación
  * **Then** la solicitud se envía a Soporte para su ejecución y no se aplica penalización al estudiante.

* **Escenario: Solicitud de cancelación con menos de 48 horas**
  * **Given** que la sesión está programada para dentro de menos de 48 horas
  * **When** el estudiante solicita la cancelación
  * **Then** la solicitud se envía a Soporte y se aplica la política de penalización correspondiente según reglas de negocio.

---

### US-06: Cambio de horario por estudiante
**Como** estudiante  
**Quiero** solicitar un cambio de horario de mi sesión  
**Para** adaptarla a mi disponibilidad, siempre que lo pida con 48 horas de anticipación  

* **Escenario: Solicitud de cambio de horario válida**
  * **Given** que la sesión está programada para dentro de más de 48 horas
  * **When** el estudiante solicita un nuevo horario
  * **Then** la solicitud queda pendiente de aprobación por Soporte.

* **Escenario: Solicitud de cambio de horario rechazada por falta de anticipación**
  * **Given** que la sesión está programada para dentro de menos de 48 horas
  * **When** el estudiante solicita un cambio de horario
  * **Then** el sistema rechaza la solicitud y muestra "Los cambios de horario requieren mínimo 48 horas de anticipación".

---

### US-07: Cambio de modalidad por estudiante
**Como** estudiante  
**Quiero** solicitar un cambio de modalidad  
**Para** adaptar la sesión a mis circunstancias, respetando el mínimo de 48 horas  

* **Escenario: Solicitud de cambio de modalidad válida**
  * **Given** que la sesión está programada para dentro de más de 48 horas
  * **When** el estudiante solicita cambiar la modalidad
  * **Then** la solicitud queda pendiente de aprobación por Soporte.

* **Escenario: Cambio de modalidad rechazado por falta de anticipación**
  * **Given** que la sesión está programada para dentro de menos de 48 horas
  * **When** el estudiante solicita cambiar la modalidad
  * **Then** el sistema rechaza la solicitud automáticamente.

---

### US-08: Gestión ante cancelación justificada del tutor
**Como** estudiante  
**Quiero** elegir entre reembolso total, reasignación a otro tutor o reprogramación cuando el tutor avisó con anticipación o justificó una emergencia  
**Para** decidir la opción que más me convenga  

* **Escenario: Tutor avisó con anticipación**
  * **Given** que el tutor notificó su ausencia con al menos 48 horas de anticipación o justificó una emergencia
  * **When** el sistema notifica al estudiante
  * **Then** el estudiante puede elegir entre reembolso total, reasignación de tutor o reprogramación.

* **Escenario: Tutor cancela sin aviso ni justificación**
  * **Given** que el tutor cancela con menos de 48 horas y sin justificación
  * **When** Soporte ejecuta la cancelación
  * **Then** se reembolsa automáticamente el 100% al estudiante y se aplica penalización al tutor.

---

### US-09: Gestión de disponibilidad por tutor
**Como** tutor  
**Quiero** registrar y actualizar mis días, horas, materias/temas, modalidad y zona  
**Para** que el sistema me asigne reservas correctamente  

* **Escenario: Actualización exitosa de disponibilidad**
  * **Given** que el tutor modifica sus horarios o materias disponibles
  * **When** guarda los cambios
  * **Then** el sistema actualiza la disponibilidad en tiempo real y las nuevas reservas usan la disponibilidad actualizada.

* **Escenario: Intento de modificar bloque con sesión confirmada**
  * **Given** que el tutor tiene una sesión confirmada en un bloque de disponibilidad
  * **When** intenta eliminar o modificar ese bloque
  * **Then** el sistema impide la modificación y muestra "No se puede modificar disponibilidad que contiene sesiones confirmadas".

---

### US-10: Asignación automática y límite diario de tutor
**Como** tutor  
**Quiero** que el sistema me asigne sesiones que coinciden con mi disponibilidad  
**Para** no tener que gestionar solicitudes manualmente, entendiendo que no puedo rechazarlas  

* **Escenario: Asignación dentro de disponibilidad registrada**
  * **Given** que una reserva de estudiante coincide con la disponibilidad registrada del tutor
  * **When** el sistema ejecuta la asignación automática
  * **Then** la sesión se agrega al calendario del tutor sin opción de rechazo.

* **Escenario: Rechazo de asignación por límite diario de 5 sesiones (CP-10 / CP-11)**
  * **Given** que el tutor ya tiene 5 sesiones asignadas en un día
  * **When** el sistema intenta asignarle una sexta sesión ese mismo día
  * **Then** la asignación falla mediante la regla `LimiteDiarioTutorSpec` y se busca otro tutor disponible.

---

### US-11: Liquidación de honorarios al tutor
**Como** tutor  
**Quiero** recibir el 80% ($160 MXN) del valor de cada sesión completada  
**Para** obtener mi ingreso por el servicio prestado  

* **Escenario: Liquidación de pago tras sesión completada (CP-08)**
  * **Given** que la sesión fue marcada como `Completada`
  * **When** el sistema procesa la liquidación
  * **Then** se transfieren $160 MXN al tutor y se registran $40 MXN como comisión de la plataforma.

* **Escenario: No se liquida sesión con reembolso (CP-09)**
  * **Given** que la sesión generó un reembolso total al estudiante
  * **When** el sistema intenta liquidar al tutor
  * **Then** no se realiza ninguna transferencia y el pago se marca como "No aplicable - reembolso".

---

### US-12: Notificación de ausencia por tutor
**Como** tutor  
**Quiero** notificar con 48 horas de anticipación que no podré impartir una sesión  
**Para** evitar la penalización automática  

* **Escenario: Notificación con anticipación suficiente**
  * **Given** que el tutor notifica su ausencia con 48 horas o más de anticipación
  * **When** el sistema recibe la notificación
  * **Then** no se aplica penalización al tutor y se ofrece al estudiante reembolso, reasignación o reprogramación.

* **Escenario: Notificación tardía sin justificación**
  * **Given** que el tutor notifica su ausencia con menos de 48 horas y sin justificar emergencia
  * **When** el sistema recibe la notificación
  * **Then** se aplica penalización al tutor y se reembolsa el 100% al estudiante.

---

### US-13: Ejecución controlada de cancelaciones por Soporte
**Como** personal de Soporte  
**Quiero** ejecutar las cancelaciones solicitadas por estudiantes o tutores  
**Para** mantener un único flujo controlado de cancelaciones  

* **Escenario: Cancelación ejecutada por Soporte**
  * **Given** que existe una solicitud de cancelación
  * **When** Soporte la ejecuta
  * **Then** el sistema actualiza el estado de la sesión a `Cancelada` y aplica la política de reembolso/penalización correspondiente.

* **Escenario: Intento de ejecución por otro rol**
  * **Given** que un usuario con rol Estudiante, Tutor o Administración intenta ejecutar una cancelación
  * **When** intenta cambiar el estado de la sesión
  * **Then** el sistema deniega la acción y muestra "Solo Soporte puede ejecutar operaciones sobre sesiones".

---

### US-14: Auditoría y cálculo de reembolso por duración de grabación
**Como** sistema AulaPlus  
**Quiero** calcular automáticamente si corresponde reembolso cuando la duración grabada es menor al 70% del tiempo contratado  
**Para** resolver estos casos sin intervención manual  

* **Escenario: Duración grabada menor al 70% (CP-05 / CP-07)**
  * **Given** que la sesión finalizó con una duración grabada menor al 70% (< 63 minutos de 90 min)
  * **When** el sistema evalúa la grabación
  * **Then** se actualiza el estado a `Reembolsada` y se genera un reembolso automático al estudiante.

* **Escenario: Duración grabada igual o mayor al 70% (CP-04 / CP-06)**
  * **Given** que la sesión finalizó con una duración grabada $\ge 70\%$ ($\ge 63$ minutos)
  * **When** el sistema evalúa la grabación
  * **Then** no se genera reembolso y la sesión permanece en estado `Completada`.

---

### US-15: Reportes operativos y de negocio
**Como** Administrador  
**Quiero** consultar reportes de sesiones agendadas, completadas vs canceladas, pagos pendientes/liquidados y disputas  
**Para** dar seguimiento a la operación de negocio  

* **Escenario: Generación de reporte por periodo**
  * **Given** que el administrador selecciona un rango de fechas
  * **When** solicita el reporte de sesiones
  * **Then** el sistema muestra sesiones agendadas, completadas y canceladas en ese periodo.

* **Escenario: Identificación de tutores con más cancelaciones**
  * **Given** que existen tutores con múltiples cancelaciones
  * **When** el administrador solicita el reporte de cancelaciones
  * **Then** se listan los tutores ordenados por número de cancelaciones y su estado de penalización.

---

### US-16: Administración de políticas de plataforma
**Como** Administrador  
**Quiero** definir y actualizar políticas generales  
**Para** mantener el modelo de negocio actualizado  

* **Escenario: Actualización de política de comisión**
  * **Given** que el administrador modifica el porcentaje de comisión
  * **When** guarda el cambio
  * **Then** el sistema aplica el nuevo porcentaje a las liquidaciones futuras.

* **Escenario: Intento de ejecutar operación operativa**
  * **Given** que el administrador intenta cancelar o modificar una sesión individual
  * **When** realiza la acción
  * **Then** el sistema deniega la operación y muestra "Solo Soporte puede ejecutar operaciones sobre sesiones".

---

## 6. Matriz de Trazabilidad Completa

| ID Requisito | User Story | Criterio Gherkin / Regla | Componente en Código (DDD / Patrón) | Caso de Prueba / Verificación |
| :--- | :--- | :--- | :--- | :--- |
| **RN-01** | US-01 | Anticipación $\ge 48$ h | `Sesion.crear` / `AnticipacionMinimaSpec` | `CP-01`, `CP-02`, `CP-03` |
| **RN-02** | US-03, US-11 | Tarifa fija \$200, \$160 tutor, \$40 comisión | `Liquidacion` (Value Object) | `CP-01`, `CP-08` |
| **RN-03** | US-10 | Límite de 5 sesiones diarias por tutor | `LimiteDiarioTutorSpec` (Specification) | `test_specification_combinada_*` |
| **RN-04** | US-14 | Umbral de grabación $\ge 70\%$ ($\ge 63$ min) | `Grabacion.es_duracion_valida` / `GrabacionAprobadaSpec` | `CP-04`, `CP-06` |
| **RN-05** | US-14 | Reembolso por grabación $< 70\%$ | `Sesion.completar_con_grabacion` | `CP-05`, `CP-07`, `CP-09` |
| **RN-06** | US-08, US-13 | Transiciones inválidas y control de soporte | `Sesion.cancelar_por_soporte` / `TransicionInvalidaException` | `test_api_liquidar_sesion_inexistente_retorna_404` |
| **RN-07** | US-03, US-11 | Integración con pasarela externa simulada | `MockPagoGateway` / `LiquidacionService` | `CP-08`, `CP-09` |
| **RN-08** | Todas | Persistencia transaccional de estados | `SqlAlchemySesionRepository` | `CP-12` (Commit/Rollback) |