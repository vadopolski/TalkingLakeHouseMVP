---

description: "Task list for Sales & Website Analytics Chat Assistant implementation"
---

# Tasks: Sales & Website Analytics Chat Assistant

**Input**: Design documents from `/specs/001-sales-chat-assistant/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Tests are NOT requested in the feature specification, so test tasks are excluded per template guidelines.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md summary indicating a web application with LLM pipeline:
- **Backend**: `src/` (Python-based backend with LLM integration)
- **Frontend**: `frontend/src/` (chat interface)
- **Templates**: `templates/sql/` (version-controlled SQL templates)
- **Tests**: `tests/` (contract, integration, unit - not included as tests not requested)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure per implementation plan (src/, frontend/src/, templates/sql/, tests/, config/)
- [X] T002 Initialize Python backend project with requirements.txt for LLM, database, and web framework dependencies
- [X] T003 [P] Initialize frontend project with package.json for chat UI framework
- [X] T004 [P] Create configuration files for database connection, LLM API keys, rate limits, and query timeouts in config/settings.py
- [X] T005 [P] Setup logging infrastructure for audit trail in src/logging/audit_logger.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Create SQL template schema definition in templates/sql/template_schema.json (template_id, description, sql_structure, parameters, whitelisted_tables, chart_type)
- [X] T007 Create database connection manager with read-only credentials in src/database/connection_manager.py
- [X] T008 [P] Implement table/column whitelist enforcement in src/security/whitelist_validator.py
- [X] T009 [P] Implement SQL keyword blocker for risky operations (DROP, DELETE, UPDATE, INSERT, etc.) in src/security/sql_validator.py
- [X] T010 [P] Create parameter validation framework with type and range checking in src/validation/parameter_validator.py
- [X] T011 [P] Implement query timeout enforcement wrapper in src/database/query_executor.py
- [X] T012 [P] Implement rate limiting middleware (10 queries/min per user) in src/middleware/rate_limiter.py
- [X] T013 Create few-shot example library for LLM template selection in templates/few_shot_examples.json
- [X] T014 Implement LLM pipeline orchestrator (classify → pick template → extract params → validate → execute → format response) in src/pipeline/query_pipeline.py
- [X] T015 Create template loader that loads SQL templates from Git into memory in src/templates/template_loader.py
- [X] T016 [P] Create chart type selector based on data characteristics in src/visualization/chart_selector.py
- [X] T017 [P] Create text response formatter for natural language summaries in src/formatting/text_formatter.py
- [X] T018 [P] Implement data source citation generator (table names, date ranges) in src/formatting/citation_generator.py
- [X] T019 Create conversational context manager for follow-up questions in src/context/context_manager.py
- [X] T020 [P] Setup frontend chat interface component in frontend/src/components/ChatInterface.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Quick Sales Metrics Query (Priority: P1) 🎯 MVP

**Goal**: Enable business users to query sales data through natural language and receive text + chart responses

**Independent Test**: Ask "What were total sales this month?" and receive both text answer and bar chart showing daily breakdown

### Implementation for User Story 1

- [X] T021 [P] [US1] Create SQL template for sales by date range in templates/sql/sales_by_date_range.json
- [X] T022 [P] [US1] Create SQL template for top selling products in templates/sql/top_products.json
- [X] T023 [P] [US1] Create SQL template for sales aggregation by period in templates/sql/sales_aggregation.json
- [X] T024 [P] [US1] Add few-shot examples for sales queries ("sales last week", "top products", "revenue this month") in templates/few_shot_examples.json
- [X] T025 [US1] Implement LLM intent classifier for sales-related questions in src/pipeline/intent_classifier.py
- [X] T026 [US1] Implement template selector for sales query patterns in src/pipeline/template_selector.py
- [X] T027 [US1] Implement parameter extractor for sales queries (dates, product names) in src/pipeline/parameter_extractor.py
- [X] T028 [US1] Add LIMIT clause injection to all sales templates (default 100, max 1000) in src/templates/limit_injector.py
- [X] T029 [US1] Create bar chart renderer for daily sales data in frontend/src/components/charts/BarChart.tsx
- [X] T030 [US1] Create line chart renderer for sales trends in frontend/src/components/charts/LineChart.tsx
- [X] T031 [US1] Implement sales response handler that combines text + chart in frontend/src/handlers/SalesResponseHandler.tsx
- [X] T032 [US1] Add sales-specific error messages for edge cases (no data, ambiguous dates) in src/errors/sales_errors.py
- [X] T033 [US1] Create API endpoint for sales queries POST /api/query/sales in src/api/sales_endpoint.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Website Traffic Analysis (Priority: P2)

**Goal**: Enable marketing analysts to explore website visit patterns through natural language

**Independent Test**: Ask "How many visitors did we have yesterday?" and receive text count plus hourly visit distribution chart

### Implementation for User Story 2

- [ ] T034 [P] [US2] Create SQL template for visitor count by date range in templates/sql/visitors_by_date_range.sql
- [ ] T035 [P] [US2] Create SQL template for peak traffic time analysis in templates/sql/peak_traffic_times.sql
- [ ] T036 [P] [US2] Create SQL template for visitor source breakdown in templates/sql/visitor_sources.sql
- [ ] T037 [P] [US2] Create SQL template for period-over-period traffic comparison in templates/sql/traffic_comparison.sql
- [ ] T038 [P] [US2] Add few-shot examples for traffic queries ("visitors yesterday", "peak hours", "traffic trends") in templates/few_shot_examples.json
- [ ] T039 [US2] Extend LLM intent classifier to handle traffic-related questions in src/pipeline/intent_classifier.py
- [ ] T040 [US2] Extend template selector for traffic query patterns in src/pipeline/template_selector.py
- [ ] T041 [US2] Extend parameter extractor for traffic queries (time ranges, sources, regions) in src/pipeline/parameter_extractor.py
- [ ] T042 [US2] Add LIMIT clause injection to all traffic templates in src/templates/limit_injector.py
- [ ] T043 [US2] Create pie chart renderer for visitor source distribution in frontend/src/components/charts/PieChart.tsx
- [ ] T044 [US2] Create dual-line chart renderer for period comparisons in frontend/src/components/charts/DualLineChart.tsx
- [ ] T045 [US2] Implement traffic response handler that combines text + chart in frontend/src/handlers/TrafficResponseHandler.tsx
- [ ] T046 [US2] Add traffic-specific error messages in src/errors/traffic_errors.py
- [ ] T047 [US2] Create API endpoint for traffic queries POST /api/query/traffic in src/api/traffic_endpoint.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Combined Sales & Traffic Insights (Priority: P3)

**Goal**: Enable business owners to understand conversion relationships between traffic and sales

**Independent Test**: Ask "What's our conversion rate this week?" and receive calculated percentage with chart showing visitors vs. purchases

### Implementation for User Story 3

- [ ] T048 [P] [US3] Create SQL template for conversion rate calculation (requires JOIN between sales and visits tables) in templates/sql/conversion_rate.sql
- [ ] T049 [P] [US3] Create SQL template for revenue per visitor calculation in templates/sql/revenue_per_visitor.sql
- [ ] T050 [P] [US3] Create SQL template for best conversion days ranking in templates/sql/best_conversion_days.sql
- [ ] T051 [P] [US3] Create SQL template for multi-metric business summary in templates/sql/business_summary.sql
- [ ] T052 [P] [US3] Add few-shot examples for conversion queries ("conversion rate", "revenue per visitor", "business health") in templates/few_shot_examples.json
- [ ] T053 [US3] Extend LLM intent classifier to handle multi-metric questions in src/pipeline/intent_classifier.py
- [ ] T054 [US3] Extend template selector for conversion query patterns in src/pipeline/template_selector.py
- [ ] T055 [US3] Extend parameter extractor for conversion queries in src/pipeline/parameter_extractor.py
- [ ] T056 [US3] Add LIMIT clause injection to all conversion templates in src/templates/limit_injector.py
- [ ] T057 [US3] Create scatter plot renderer for visitors vs. revenue correlation in frontend/src/components/charts/ScatterChart.tsx
- [ ] T058 [US3] Create mixed chart renderer for multi-metric dashboards in frontend/src/components/charts/MixedChart.tsx
- [ ] T059 [US3] Implement conversion response handler with multi-metric support in frontend/src/handlers/ConversionResponseHandler.tsx
- [ ] T060 [US3] Add conversion-specific error messages in src/errors/conversion_errors.py
- [ ] T061 [US3] Create API endpoint for conversion queries POST /api/query/conversion in src/api/conversion_endpoint.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T062 [P] Implement template mismatch handler that lists available query types in src/errors/template_mismatch_handler.py
- [ ] T063 [P] Add comprehensive audit logging for all queries (template selection, parameters, execution time, results) in src/logging/query_auditor.py
- [ ] T064 [P] Create health check endpoint for monitoring in src/api/health_endpoint.py
- [ ] T065 [P] Add response time tracking and performance metrics in src/monitoring/performance_tracker.py
- [ ] T066 [P] Implement graceful error handling that never exposes SQL or system internals in src/errors/error_sanitizer.py
- [ ] T067 [P] Create template validation tool for Git pre-commit hook in tools/validate_templates.py
- [ ] T068 [P] Add data export functionality (CSV, JSON) for query results in src/export/data_exporter.py
- [ ] T069 [P] Create documentation for adding new SQL templates in docs/template_creation_guide.md
- [ ] T070 [P] Setup frontend loading states and error displays in frontend/src/components/LoadingState.tsx
- [ ] T071 [P] Add accessibility features to charts (alt text, ARIA labels) in frontend/src/components/charts/

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories (fully independent)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Technically uses data from both sales and visits tables, but templates are self-contained with hardcoded JOINs

### Within Each User Story

- SQL templates (marked [P]) before implementation
- Few-shot examples can be added in parallel with SQL templates
- LLM pipeline extensions (classifier, selector, extractor) must be sequential within each story
- Frontend charts can be built in parallel
- API endpoints come last after backend logic is complete

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- SQL templates within each story marked [P] can run in parallel
- Frontend charts within each story can run in parallel
- Polish tasks are all parallel

---

## Parallel Example: User Story 1

```bash
# Launch all SQL templates for User Story 1 together:
Task T021: "Create SQL template for sales by date range in templates/sql/sales_by_date_range.sql"
Task T022: "Create SQL template for top selling products in templates/sql/top_products.sql"
Task T023: "Create SQL template for sales aggregation by period in templates/sql/sales_aggregation.sql"
Task T024: "Add few-shot examples for sales queries in templates/few_shot_examples.json"

# After templates complete, launch frontend charts together:
Task T029: "Create bar chart renderer for daily sales data in frontend/src/components/charts/BarChart.tsx"
Task T030: "Create line chart renderer for sales trends in frontend/src/components/charts/LineChart.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently - "What were total sales this month?"
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Sales queries)
   - Developer B: User Story 2 (Traffic analysis)
   - Developer C: User Story 3 (Conversion insights)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are NOT included as they were not requested in the feature specification
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All SQL templates MUST include hardcoded JOINs (no automatic JOIN generation)
- All SQL templates MUST have LIMIT clauses injected before execution
- Template library is version-controlled in Git at templates/sql/
- Few-shot examples guide LLM for high accuracy (90% correct interpretation target)
- LLM pipeline enforces constitutional safety principles at every step
