<!--
Sync Impact Report:
Version change: [NONE] → 1.0.0
Modified principles: Initial creation
Added sections: Core Principles (7 principles), Safety & Security, Output Standards, Governance
Removed sections: None
Templates requiring updates:
  ✅ .specify/templates/plan-template.md - Constitution Check section will reference these principles
  ✅ .specify/templates/spec-template.md - Requirements align with principles
  ✅ .specify/templates/tasks-template.md - Task organization reflects principles
Follow-up TODOs: None - all placeholders filled
-->

# TalkingLakeHouseHC Constitution

## Core Principles

### I. Single Database Source of Truth

**The system MUST maintain exactly one authoritative database as the source of truth for all data queries and analytics.**

- All data queries MUST be executed against the designated primary database
- No data duplication or caching layers that could serve as alternative sources of truth
- All user questions about data MUST be answered from this single database
- No derived data stores unless explicitly synchronized and marked as read replicas

**Rationale**: Prevents data inconsistency, simplifies architecture, ensures users always receive accurate information from the canonical source.

### II. English Chat User Experience

**Users MUST interact with the system exclusively through natural English language chat interface.**

- All user inputs are natural language questions or requests
- No SQL knowledge required from end users
- No technical query language exposure to users
- System responses MUST be conversational and context-aware
- Support for follow-up questions and clarifications

**Rationale**: Democratizes data access, removes technical barriers, enables business users to query data without SQL expertise.

### III. Template-Only SQL Generation

**All SQL queries MUST be generated exclusively from pre-defined, vetted templates.**

- SQL is NEVER dynamically composed from scratch by the LLM
- Every query type MUST have a corresponding approved template
- Templates contain placeholders for user-specific values only
- No arbitrary SQL generation outside the template library
- New query patterns require new template creation and review

**Rationale**: Ensures predictable, safe, auditable SQL execution; prevents injection attacks and malformed queries.

### IV. No Automatic JOIN Operations

**The system MUST NOT automatically infer or generate JOIN operations between tables.**

- JOINs are only allowed if explicitly defined in pre-approved templates
- LLM MUST NOT determine JOIN conditions based on schema introspection
- Multi-table queries require explicit template support with hardcoded JOIN logic
- No automatic foreign key relationship traversal

**Rationale**: Prevents incorrect data associations, performance issues from cartesian products, and semantic errors from misunderstood relationships.

### V. LLM Template Parameter Filling

**The LLM's role is strictly limited to selecting appropriate templates and filling their parameters based on user intent.**

- LLM analyzes user natural language input
- LLM selects the matching template from the approved library
- LLM extracts values from user input to populate template placeholders
- LLM MUST NOT modify template structure or SQL logic
- Template selection and parameter mapping MUST be logged

**Rationale**: Leverages LLM's natural language understanding while constraining SQL generation to safe, pre-approved patterns.

### VI. Strict Safety Controls

**The system MUST enforce multiple layers of safety mechanisms to prevent data exposure, modification, or performance degradation.**

Safety requirements:

- **Whitelist-only operations**: Only explicitly permitted tables, columns, and operations are allowed
- **Mandatory LIMIT clauses**: All SELECT queries MUST include a LIMIT clause (default and maximum configurable)
- **Read-only access**: Database connections MUST use read-only credentials
- **Blocked SQL keywords**: DROP, DELETE, UPDATE, INSERT, TRUNCATE, ALTER, CREATE, GRANT, REVOKE are forbidden
- **Parameter validation**: All template parameters MUST be validated against type and range constraints
- **Query timeout limits**: All queries MUST have maximum execution time limits
- **Rate limiting**: User queries MUST be rate-limited to prevent abuse

**Rationale**: Defense-in-depth approach prevents accidental or malicious data damage, ensures system stability and performance.

### VII. Consistent Output Formats

**The system MUST provide consistent, predictable output formats for both textual responses and visualizations.**

Requirements:

- **Text outputs**: Structured as natural language summaries with clear data presentation
- **Chart outputs**: Standardized chart types (bar, line, pie, scatter) with consistent styling
- **Data tables**: Formatted with clear headers, aligned columns, and appropriate precision
- **Error messages**: User-friendly explanations without exposing system internals
- **Response structure**: Consistent format including answer, data source citation, and confidence indicators
- **Visualization selection**: Chart type selection based on data characteristics and query intent

**Rationale**: Ensures professional, user-friendly experience; enables users to quickly understand results; maintains brand consistency.

## Safety & Security

All implementations MUST enforce the safety controls defined in Principle VI:

1. **Database Access**: Read-only credentials with minimal schema permissions
2. **Template Library**: Version-controlled, code-reviewed, tested before deployment
3. **Input Validation**: Strict parameter type checking, range validation, and sanitization
4. **SQL Injection Prevention**: Parameterized queries only; no string concatenation
5. **Monitoring**: Log all queries, template selections, and parameter values for audit
6. **Failure Modes**: Graceful degradation; never expose raw SQL or system errors to users

## Output Standards

All feature implementations MUST comply with Principle VII output requirements:

- **Natural Language**: Responses in clear, concise English prose
- **Data Transparency**: Always indicate the source tables and time range of data
- **Visual Clarity**: Charts with labeled axes, legends, and appropriate scaling
- **Accessibility**: Text descriptions accompanying all visualizations
- **Pagination**: Large result sets presented in manageable chunks
- **Export Options**: Support for downloading results in standard formats (CSV, JSON)

## Governance

**Constitution Authority**: This constitution supersedes all other development practices, coding standards, and implementation decisions.

**Amendment Process**:
- Amendments require documented rationale and impact analysis
- Breaking changes to principles require major version increment
- All template files MUST be updated to reflect constitutional changes
- Version history maintained in this document's sync impact report

**Compliance Review**:
- All feature specifications MUST pass Constitution Check (plan-template.md)
- Pull requests MUST verify compliance with all applicable principles
- Complexity violations MUST be explicitly justified in planning documentation
- Regular audits to ensure template library adheres to safety principles

**Version Management**:
- MAJOR: Principle removal, redefinition, or backward-incompatible changes
- MINOR: New principles added or substantial guidance additions
- PATCH: Clarifications, wording improvements, non-semantic updates

**Enforcement**:
- Constitution violations block feature approval
- Template modifications require security review
- Any deviation requires explicit documentation in Complexity Tracking section

**Version**: 1.0.0 | **Ratified**: 2025-10-31 | **Last Amended**: 2025-10-31
