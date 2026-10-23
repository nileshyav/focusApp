**# AGENTS.md**

**## Purpose**

This repository is a long-lived production-oriented application.

The primary goals are:

1\. Security
2\. Correctness
3\. Maintainability
4\. Readability
5\. Testability
6\. Scalability
7\. Operational simplicity
8\. Developer productivity

Code must be optimized for humans who will maintain the project months or years
after the original implementation.

AI-generated code must follow the existing architecture rather than introducing
new architectural patterns for individual features.

\---

**# 1. Engineering Principles**

Follow these principles in priority order:

1\. Security
2\. Correctness
3\. Simplicity
4\. Maintainability
5\. Readability
6\. Testability
7\. Performance
8\. Scalability

Do not sacrifice security or correctness for convenience.

Do not optimize prematurely.

Prefer boring, explicit, well-understood solutions over clever solutions.

Prefer the simplest architecture that satisfies the current requirements.

Do not introduce infrastructure, abstractions, libraries, services, queues,
caches, or distributed systems unless there is a demonstrated need.

\---

**# 2. Technology Stack**

Current stack:

\- Python
\- FastAPI
\- Jinja2
\- HTMX
\- Supabase
\- Alembic
\- pytest
\- Pydantic
\- SQLAlchemy


Frontend architecture:

\- Server-rendered HTML
\- Jinja2 templates
\- HTMX for dynamic interactions
\- CSS component framework DaisyUI + tailwind

Do not introduce:

\- React
\- Vue
\- Angular
\- Next.js
\- frontend state-management frameworks

unless explicitly requested.

Prefer HTMX over JS unless things can not be done using HTMX.


Do not replace an existing technology without an explicit architectural reason and discussion with me.

\---

**# 3. Architectural Style**

Use a modular monolith.

Organize the application primarily by business feature rather than by technical
type.

Preferred structure:

app/
    main.py

    core/
        config.py
        database.py
        security.py
        logging.py
        dependencies.py

    users/
        router.py
        service.py
        repository.py
        models.py
        schemas.py
        templates/
        tests/

    orders/
        router.py
        service.py
        repository.py
        models.py
        schemas.py
        templates/
        tests/

    payments/
        ...

Do not create all possible files in advance.

A feature should contain only the modules it actually needs.

\---

**# 4. Feature Boundaries**

Each feature should have a clear responsibility.

For example:

users/
orders/
payments/
notifications/

Do not allow unrelated features to directly manipulate another feature's
internal implementation.

Prefer:

orders.service
    ↓
users.service

over:

orders
    ↓
users.repository
    ↓
users database tables

Business rules should be accessed through the owning feature's public interface.

Avoid tight coupling between features.

\---

**# 5. Dependency Direction**

Use the following general dependency direction:

HTTP/HTMX
    ↓
Router
    ↓
Service / Business Logic
    ↓
Repository / Data Access
    ↓
Database

The dependency direction should not be reversed.

Rules:

\- Routers handle HTTP concerns.
\- Services contain business rules.
\- Repositories handle persistence concerns.
\- Models describe persistence structures.
\- Schemas describe validated data contracts.
\- Templates handle presentation.
\- Core contains genuinely cross-cutting infrastructure.

Do not place business logic inside routers.

Do not place database queries inside templates.

Do not make templates responsible for authorization decisions.

\---

**# 6. Avoid Architecture for Architecture's Sake**

Do not automatically create:

\- repositories
\- services
\- factories
\- interfaces
\- adapters
\- managers
\- base classes
\- dependency injection layers

unless they solve an actual problem.

For a simple operation:

router → database

may be acceptable.

For complex business logic:

router → service → repository → database

may be appropriate.

Architecture should evolve with complexity.

Do not create abstractions merely because they are considered "clean
architecture."

\---

**# 7. Code Readability**

Write code for a competent human developer first.

Prefer:

\- descriptive names
\- small functions
\- explicit control flow
\- type hints
\- straightforward error handling
\- cohesive modules
\- limited nesting

Avoid:

\- clever one-liners
\- unnecessary metaprogramming
\- deeply nested conditionals
\- magic values
\- implicit global state
\- unexplained abstractions
\- extremely generic utility functions

A developer should be able to understand a feature by reading the feature's
directory.

\---

**# 8. File and Module Size**

Avoid giant files.

As a guideline:

\- Prefer modules below \~300 lines.
\- Investigate modules above \~500 lines.
\- Do not mechanically split files simply to satisfy line counts.

When a module becomes difficult to understand, split it according to
responsibility or business capability.

Do not split a cohesive concept into many tiny files merely to reduce line
count.

\---

**# 9. Functions**

Functions should generally do one coherent thing.

Prefer:

validate\_order()
calculate\_total()
reserve\_inventory()
create\_order()

over:

process\_order()

containing hundreds of lines of unrelated logic.

Avoid functions with excessive numbers of parameters.

Use domain objects or typed structures when parameter lists become difficult
to understand.

\---

**# 10. Shared Code**

Do not create generic modules such as:

utils.py
helpers.py
common.py
misc.py

unless their contents are genuinely shared.

Prefer feature-local code.

For example:

orders/pricing.py

is preferable to:

utils/pricing.py

if pricing only belongs to orders.

Shared code should have multiple legitimate consumers.

Do not prematurely generalize code.

\---

**# 11. Security-First Development**

Security is a first-class architectural requirement.

Every new feature must consider:

\- authentication
\- authorization
\- input validation
\- output encoding
\- data exposure
\- secrets
\- logging
\- error handling
\- CSRF
\- SSRF
\- SQL injection
\- XSS
\- command injection
\- path traversal
\- insecure direct object references
\- rate limiting where appropriate
\- abuse cases

Do not assume that because a request is authenticated it is authorized.

Always verify that the authenticated user has permission to access the requested
resource.

Use least privilege.

Default to deny rather than default to allow.

\---

**# 12. Authentication and Authorization**

Authentication answers:

"Who is this user?"

Authorization answers:

"Is this user allowed to perform this action?"

Do not mix the two concepts.

Authorization must be enforced on the server.

Never rely on:

\- hidden HTML elements
\- disabled buttons
\- JavaScript checks
\- frontend route restrictions

for security.

Every protected operation must be authorized server-side.

\---

**# 13. Secrets**

Never hard-code:

\- passwords
\- API keys
\- tokens
\- JWT secrets
\- database credentials
\- encryption keys
\- Supabase service-role keys

Use environment variables or the deployment platform's secret-management
system.

Never commit:

.env
.env.\*
private keys
credentials
tokens

unless they are explicitly documented non-secret examples.

Public/browser-side configuration must never contain server-side secrets.

The Supabase service-role key must never be exposed to the browser.

\---

**# 14. Input Validation**

Treat all external input as untrusted.

Validate:

\- request parameters
\- form data
\- JSON payloads
\- query parameters
\- uploaded files
\- headers where relevant
\- webhook payloads

Use typed Pydantic schemas for request and response validation.

Do not trust client-side validation.

Client-side validation improves UX.

Server-side validation provides security.

\---

**# 15. Database Security**

Use parameterized queries.

Never construct SQL by concatenating user-controlled strings.

Prefer SQLAlchemy query mechanisms.

Database credentials must have the minimum permissions required.

Do not use highly privileged database credentials for normal application
operations when a restricted role is appropriate.

Do not expose database credentials to frontend code.

\---

**# 16. Database Migrations**

Alembic is the schema migration mechanism.

Never rely on:

Base.metadata.create\_all()

for production schema management.

Never manually modify a migration that has already been applied to a shared
or production database.

Instead:

1\. Create a new migration.
2\. Review it.
3\. Test it.
4\. Apply it.

Migration history is part of the application's source code.

Migration files must be committed to Git.

Avoid destructive migrations unless explicitly required.

Before destructive changes consider:

\- existing data
\- backward compatibility
\- deployment order
\- rollback strategy

\---

**# 17. Database Changes**

Distinguish between:

SCHEMA
and
DATA

Schema changes use Alembic.

Normal application data is created/modified by application behavior.

Do not create an Alembic migration for every user/order/product created.

Reference data may use controlled seed scripts or data migrations.

\---

**# 18. Backward-Compatible Changes**

When possible, database and application changes should be deployable safely
without requiring downtime.

Prefer:

1\. Add new column
2\. Deploy code that can handle old and new states
3\. Backfill data
4\. Switch reads/writes
5\. Remove old column later

Avoid changing a database structure and application behavior simultaneously
when doing so creates an unsafe deployment dependency.

\---

**# 19. HTMX Architecture**

The application is primarily server-rendered.

Prefer:

Browser
    ↓
HTMX request
    ↓
FastAPI
    ↓
business logic
    ↓
HTML fragment
    ↓
HTMX DOM update

Do not introduce a JSON API solely because an HTMX interaction exists.

Use JSON when there is a genuine API consumer or machine-to-machine requirement.

Keep HTMX attributes understandable.

Prefer explicit:

hx-get
hx-post
hx-delete
hx-target
hx-swap
hx-push-url

over complicated client-side JavaScript.

\---

**# 20. Templates**

Templates are presentation-layer code.

Templates may contain:

\- rendering logic
\- loops
\- conditional presentation
\- HTMX attributes
\- accessibility attributes

Templates should not contain:

\- database queries
\- authentication logic
\- authorization decisions
\- complex business rules

Prepare appropriate data in Python before rendering.

Avoid large blocks of embedded JavaScript.

\---

**# 21. HTML Security**

Escape untrusted content by default.

Do not introduce unsafe HTML rendering without understanding the security
implications.

Treat:

\| safe HTML
\| user-generated HTML
\| Markdown
\| uploaded content

as different trust levels.

Do not use unsafe HTML rendering to solve a formatting problem without
considering XSS.

\---

**# 22. CSRF**

State-changing browser requests must have appropriate CSRF protection when
cookie-based authentication is used.

Do not assume HTMX automatically solves CSRF.

Ensure CSRF tokens are correctly included in state-changing requests.

Any authentication mechanism should be evaluated according to its actual
browser security model.

\---

**# 23. File Uploads**

Treat uploaded files as untrusted.

Validate:

\- file size
\- file type
\- extension
\- content where appropriate
\- filename

Do not trust the filename supplied by the client.

Do not execute uploaded files.

Store uploads outside executable application directories.

Prefer object storage for persistent uploads.

\---

**# 24. Error Handling**

Never expose internal implementation details to users.

Do not return:

\- stack traces
\- database credentials
\- SQL statements containing secrets
\- internal filesystem paths
\- environment variables

Use structured logging internally.

Return appropriate user-facing error responses.

Do not silently swallow exceptions.

Never use:

except Exception:
    pass

unless there is a very specific documented reason.

\---

**# 25. Logging**

Logs must help operators diagnose problems without exposing sensitive data.

Never log:

\- passwords
\- authentication tokens
\- session cookies
\- API keys
\- database credentials
\- sensitive personal information

Use appropriate log levels:

DEBUG
INFO
WARNING
ERROR
CRITICAL

Avoid excessive logging in high-frequency paths.

\---

**# 26. Observability**

As the application grows, prefer structured observability.

Important production signals include:

\- request latency
\- error rate
\- request volume
\- database latency
\- background task failures
\- authentication failures
\- resource usage

Add instrumentation when operational complexity justifies it.

Do not add a large observability stack to a small application without a reason.

\---

**# 27. Testing Strategy**

Tests should provide confidence, not merely increase coverage numbers.

Use:

\- unit tests for isolated business logic
\- integration tests for database behavior
\- API/HTMX tests for request behavior
\- end-to-end tests for critical user journeys

Prioritize tests around:

\- authentication
\- authorization
\- payments
\- data integrity
\- destructive operations
\- important business rules

Do not mock everything.

Prefer testing real behavior at appropriate boundaries.

\---

**# 28. Test Requirements**

Every meaningful feature should include tests.

Before completing a feature:

1\. Run relevant tests.
2\. Run the full test suite when practical.
3\. Verify security-sensitive behavior.
4\. Check error paths.
5\. Check authorization boundaries.
6\. Review the final diff.

Do not claim a feature works without verification.

\---

**# 29. Dependency Management**

Do not add dependencies casually.

Before adding a dependency:

1\. Check the standard library.
2\. Check existing project dependencies.
3\. Determine whether the dependency is actively maintained.
4\. Check its security/reputation.
5\. Consider its license.
6\. Consider its long-term maintenance burden.

Prefer a small dependency surface.

Every dependency is part of the application's supply-chain attack surface.

\---

**# 30. Dependency Updates**

Do not blindly upgrade all dependencies.

Review major version upgrades individually.

For security updates:

\- understand the vulnerability
\- update the affected dependency
\- run tests
\- inspect compatibility

Pin or constrain dependencies appropriately for reproducible deployments.

\---

**# 31. Performance**

Do not optimize based on assumptions.

Measure first.

Pay particular attention to:

\- N+1 database queries
\- unnecessary database round trips
\- unbounded queries
\- missing indexes
\- expensive serialization
\- excessive external API calls
\- unnecessary template rendering

Use pagination for potentially large datasets.

Never load an unbounded table into memory simply because it works with development
data.

\---

**# 32. Scalability**

Design for horizontal scalability where practical.

Application instances should preferably be stateless.

Do not depend on:

\- local filesystem persistence
\- process-local state
\- in-memory session state

for functionality that must survive multiple instances.

Persistent state belongs in appropriate external systems:

\- PostgreSQL
\- object storage
\- cache
\- message broker

Introduce these systems only when required.

\---

**# 33. Caching**

Do not introduce caching before identifying the bottleneck.

When adding caching:

\- define cache invalidation behavior
\- define TTL
\- define failure behavior
\- consider stale data
\- ensure correctness does not depend blindly on the cache

The database remains the source of truth unless explicitly designed otherwise.

\---

**# 34. Background Work**

Do not perform long-running work inside a normal HTTP request if it can exceed
the application's request/timeout model.

When background processing becomes necessary, introduce an appropriate worker
or task system.

Do not introduce Celery/Redis/etc. merely because they are common.

Choose infrastructure based on actual requirements.

\---

**# 35. API Design**

Use consistent:

\- HTTP methods
\- status codes
\- resource naming
\- validation
\- error responses

Do not expose internal database structures directly as public API contracts.

Separate internal persistence models from externally exposed contracts when the
application requires a stable public API.

\---

**# 36. Configuration**

Configuration belongs outside application code.

Use environment-specific configuration for:

\- database URLs
\- credentials
\- external services
\- debug settings
\- allowed hosts
\- CORS
\- logging levels

Never use development configuration in production.

Fail fast when required production configuration is missing.

\---

**# 37. Environment Separation**

Maintain clear separation between:

development
testing
staging
production

Never accidentally run destructive operations against production.

Use separate credentials and databases where appropriate.

Do not use production credentials for local development.

\---

**# 38. Git Safety**

Do not execute destructive Git operations unless explicitly requested.

Never automatically:

\- force push
\- reset --hard
\- delete branches
\- rewrite history
\- discard unrelated user changes

Before making large changes:

inspect the repository state.

Before finishing:

inspect:

git status
git diff

Do not overwrite existing user work.

\---

**# 39. Change Scope**

Make the smallest change that correctly solves the problem.

Do not:

\- refactor unrelated code
\- rename unrelated files
\- reformat the entire repository
\- upgrade unrelated dependencies
\- change architecture unnecessarily

A feature request is not permission to rewrite the application.

\---

**# 40. Existing Code Has Priority**

Before implementing something:

1\. Search for existing functionality.
2\. Search for similar patterns.
3\. Reuse existing abstractions when appropriate.
4\. Follow established naming conventions.
5\. Understand existing behavior before changing it.

Do not create duplicate implementations.

\---

**# 41. New Features**

When implementing a new feature:

1\. Identify the owning business module.
2\. Understand its existing dependencies.
3\. Define the data model if required.
4\. Define authorization requirements.
5\. Define failure cases.
6\. Implement business logic.
7\. Implement HTTP/HTMX behavior.
8\. Add templates.
9\. Add tests.
10\. Add migration if the schema changes.
11\. Run verification.
12\. Review the final diff.

New features should not unnecessarily modify unrelated modules.

\---

**# 42. Refactoring**

Refactoring must preserve behavior unless behavior change is explicitly
requested.

Before a large refactor:

\- understand dependencies
\- identify affected tests
\- make incremental changes
\- run tests after meaningful steps

Do not combine a large refactor with an unrelated feature unless necessary.

\---

**# 43. Documentation**

Document decisions that are not obvious from the code.

Do not document trivial code.

Prefer documenting:

\- architectural decisions
\- security assumptions
\- unusual constraints
\- operational procedures
\- important tradeoffs

Use Architecture Decision Records (ADRs) when an architectural decision has
long-term consequences.

Example:

docs/adr/
    0001-use-postgresql.md
    0002-use-htmx.md
    0003-authentication-strategy.md

\---

**# 44. AI Agent Behavior**

The agent must not assume that generated code is correct.

Before implementation:

\- inspect the relevant repository
\- understand existing patterns
\- identify constraints

During implementation:

\- make incremental changes
\- avoid unnecessary rewrites
\- preserve existing behavior

After implementation:

\- run tests
\- inspect errors
\- inspect git diff
\- verify security-sensitive behavior

Do not mark a task complete merely because the code looks plausible.

\---

**# 45. AI Agent and Security**

For security-sensitive changes, explicitly inspect:

\- authentication
\- authorization
\- input validation
\- secret handling
\- session handling
\- CSRF
\- XSS
\- SQL injection
\- file access
\- external requests
\- permissions

Never weaken security to make a test or feature work.

Do not disable authentication, authorization, TLS verification, validation,
CSRF protection, or security middleware merely to bypass an error.

If a security control genuinely must change, explain why and identify the
tradeoff.

\---

**# 46. AI Agent and Production Infrastructure**

Treat the following commands as potentially destructive:

\- terraform apply
\- terraform destroy
\- kubectl delete
\- kubectl apply
\- docker system prune
\- database DROP/DELETE/TRUNCATE
\- git push
\- production deployment commands

Do not execute destructive production commands automatically.

Prefer:

plan
    ↓
review
    ↓
approval
    ↓
apply

For infrastructure changes:

terraform plan

should be reviewed before:

terraform apply

\---

**# 47. Unknown Requirements**

Do not invent requirements.

If an assumption could affect:

\- security
\- database integrity
\- architecture
\- public API behavior
\- user data
\- production infrastructure

ask for clarification.

For low-risk implementation details, follow existing project conventions.

\---

**# 48. Completion Checklist**

Before declaring a task complete:

[ ] Existing code was inspected.
[ ] Existing patterns were reused where appropriate.
[ ] No unrelated code was changed.
[ ] Security implications were considered.
[ ] Authentication/authorization was verified where relevant.
[ ] Input validation was added where required.
[ ] Database migrations were created if necessary.
[ ] Tests were added or updated.
[ ] Tests were executed.
[ ] Lint/type checks were executed where configured.
[ ] No secrets were introduced.
[ ] Git diff was reviewed.
[ ] No unintended files were modified.
[ ] Documentation was updated when necessary.

\---

**# 49. Core Philosophy**

Build software that another competent developer can understand quickly.

Prefer:

simple over clever
explicit over magical
local over unnecessarily global
cohesive over fragmented
secure over convenient
tested over assumed
measured over guessed
incremental over rewritten
boring over fragile

The application should become easier to understand as it grows, not harder.

Every new feature should improve or preserve the architectural clarity of the
system rather than gradually turning the repository into a collection of
unrelated AI-generated code.

ALso most important things before executing anythings first explain me what you are going to do and how you are going to do and also its trade off with other things , other possible best way to do it and pros and cons of each approach

i want to to follow industry best practices.so as this project grows to million users it should designed in such a way that reading code , understanding code ,and add more things stays easy to humans. do it in domain driven deisgn and modular monolithic architecture.


We are not designing for "one million users" by prematurely adding distributed infrastructure. We are designing the codebase so that reaching one million users does not require rewriting the domain architecture.
---

# 50. Domain-Driven Design

The application uses Domain-Driven Design principles within the modular monolith.

DDD is used pragmatically, not ceremonially.

Do not introduce aggregates, value objects, domain events, factories, domain services, or other DDD patterns merely because they are associated with DDD.

Introduce a DDD pattern when it solves an actual domain complexity, consistency, or maintainability problem.

Each business module should have:

- a clearly defined responsibility
- explicit business rules
- clearly identified domain concepts
- explicit ownership of its data and behavior
- defined dependencies on other modules
- a small and understandable public interface

Use ubiquitous language consistently between requirements, domain concepts, code, tests, and documentation.

Business rules should live with the domain that owns them.

HTTP, HTMX, templates, database details, and infrastructure should not define the domain model.

---

# 51. Module Ownership and Encapsulation

A module is an architectural boundary, not merely a directory.

A module owns:

- its business rules
- its application behavior
- its persistence implementation
- its database queries
- its persistence models
- its internal helpers

Other modules must not directly access another module's:

- repositories
- database queries
- internal ORM implementation
- private domain objects
- internal helper functions

Cross-module interaction must use an explicitly defined public interface.

Prefer:

module A
    ↓
module B public interface
    ↓
module B internal implementation

over:

module A
    ↓
module B repository
    ↓
module B database tables

A module may expose only the behavior and data contracts that other modules genuinely need.

Do not expose internal implementation details merely for convenience.

---

# 52. Database Ownership

Each business module owns the persistence of the data belonging to its domain.

Logical ownership is required even when all modules use the same PostgreSQL database.

For example:

todo
    owns todo persistence

pomodoro
    owns pomodoro persistence

users
    owns user persistence

A module must not directly query or mutate another module's tables merely because they exist in the same database.

Cross-module data access should go through the owning module's public interface.

Do not interpret database ownership as requiring separate databases.

A modular monolith may use a single PostgreSQL database while maintaining strict logical ownership.

---

# 53. Public Module Interfaces

Every module should have a small, intentional public surface.

Before creating a cross-module dependency, determine:

1. Which module owns the behavior?
2. Why does the calling module need it?
3. What is the smallest public contract required?
4. Can the dependency be avoided?
5. Does the dependency create a circular relationship?

Avoid exposing entire service classes or repositories as public module APIs when only one operation is required.

Do not allow internal implementation details to become accidental APIs.

When a module's public interface changes, consider the impact on all consumers.

---

# 54. Dependency and Architecture Governance

Existing architectural patterns have priority.

Before introducing a new:

- architectural layer
- module type
- abstraction
- dependency pattern
- infrastructure component
- cross-module dependency
- DDD pattern
- external service

the agent must:

1. Search for an existing pattern.
2. Explain why the existing pattern is insufficient.
3. Explain the proposed alternative.
4. Explain relevant trade-offs.
5. Identify affected modules.
6. Obtain human approval when the change affects architecture.

Do not introduce a new architectural pattern for a single feature unless it is justified as a project-level decision.

Architecture must evolve deliberately.

---

# 55. Architecture Drift Prevention

AI-generated changes must preserve architectural consistency.

Before completing a feature, verify:

- the owning module is correct
- module boundaries are preserved
- dependency direction is preserved
- database ownership is preserved
- no new unauthorized cross-module access exists
- no duplicate architectural pattern was introduced
- no unnecessary abstraction was introduced
- existing conventions were followed

If a proposed implementation conflicts with an existing architectural rule, stop and explain the conflict.

Do not silently create an exception.

If an exception is genuinely required, document the reason and obtain human approval.

---

# 56. Human + AI Development Protocol

The AI agent must follow this workflow for meaningful changes:

REQUEST
    ↓
Understand requirement
    ↓
Inspect relevant repository
    ↓
Identify owning domain/module
    ↓
Identify affected dependencies
    ↓
Identify security implications
    ↓
Prepare implementation plan
    ↓
Explain alternatives and trade-offs
    ↓
Human approval when required
    ↓
Implement incrementally
    ↓
Run verification
    ↓
Review architecture
    ↓
Review security
    ↓
Inspect final diff
    ↓
Report result

For architecture-affecting work, do not begin implementation before the human has reviewed the proposed approach.

For low-risk, local implementation changes that clearly follow established patterns, explicit architectural approval is not required.

---

# 57. Agent Must Explain Before Architectural Changes

Before executing an architecture-affecting change, the agent must explain:

- What it intends to change
- Why the change is needed
- How it will implement the change
- Which modules will be affected
- Alternative approaches considered
- Pros and cons of the alternatives
- Security implications
- Scalability implications
- Maintenance implications
- Why the selected approach is preferred

Do not treat user intent to "make it work" as approval to redesign unrelated architecture.

---

# 58. Agent Stop Conditions

The agent must stop and ask for clarification or approval when an assumption could materially affect:

- architecture
- domain boundaries
- database integrity
- data ownership
- authentication
- authorization
- security controls
- public API behavior
- user data
- production infrastructure
- deployment strategy
- migration safety

The agent may make reasonable assumptions for low-risk implementation details when existing project conventions provide sufficient guidance.

Never guess about high-impact architectural or security decisions.

---

# 59. Change Impact Report

For meaningful changes, the agent should identify:

Files expected to change:
- ...

Modules affected:
- ...

Modules intentionally not affected:
- ...

Database changes:
- none / description

Migration required:
- yes / no

Security impact:
- ...

Architecture impact:
- none / description

Testing required:
- ...

This report should remain concise and proportional to the change.

---

# 60. Domain Invariants

Important business domains must explicitly identify their invariants.

For meaningful domain behavior, consider:

- entities
- value concepts
- state
- valid state transitions
- invariants
- ownership
- allowed operations
- failure conditions

Business invariants must be enforced server-side.

Do not rely on UI state, HTMX attributes, JavaScript, or client-side validation to maintain domain invariants.

A domain state transition should have one authoritative owner.

Avoid arbitrary database field mutation from unrelated parts of the application when a business operation has meaningful rules.

---

# 61. State Transitions

For domains containing meaningful lifecycle states, define valid transitions.

For example:

IDLE
    ↓
RUNNING
    ↓
PAUSED
    ↓
RUNNING
    ↓
COMPLETED

Only valid transitions should be permitted.

Do not allow unrelated routes, templates, or modules to independently manipulate lifecycle state.

State transition rules belong to the owning domain.

---

# 62. Transactions

Transaction boundaries must be explicit and consistent.

Do not allow different modules or repositories to invent incompatible transaction behavior.

Before implementing transactional behavior, establish:

- who owns the transaction boundary
- when commit occurs
- when rollback occurs
- how failures propagate
- whether multiple repository operations participate in one transaction

Prefer a consistent project-wide transaction strategy.

Repositories must not unexpectedly commit transactions when the surrounding application operation requires multiple persistence operations to succeed or fail together.

Transactions should protect business invariants and data integrity.

---

# 63. Concurrency and Idempotency

Do not assume HTTP requests execute sequentially.

The application must remain correct when:

- users open multiple browser tabs
- requests arrive concurrently
- users double-submit an action
- HTMX requests are retried
- network failures cause retries
- multiple application instances process requests simultaneously

Where duplicate execution could cause incorrect state, define appropriate idempotency or database-level protection.

Use appropriate:

- unique constraints
- transactions
- locking
- optimistic concurrency
- idempotency mechanisms

when justified by the actual domain requirement.

Do not add distributed locking or complex concurrency infrastructure without demonstrated need.

---

# 64. Time and Timezone Policy

Time must be treated as a domain concern where it affects behavior.

Establish a consistent policy for:

- timestamp storage
- timezone conversion
- calendar-day calculations
- recurring behavior
- user-local dates
- daylight-saving transitions where relevant

Do not assume the server's local timezone is the user's timezone.

Persist timestamps consistently and convert them for presentation and user-specific calendar operations according to the application's defined time policy.

"Today", "tomorrow", streaks, daily statistics, and similar concepts must use the appropriate user/application timezone rather than arbitrary server time.

---

# 65. Browser and Session Security

For browser-based authentication, explicitly protect:

- session fixation
- session invalidation
- session expiration
- session rotation where appropriate
- secure cookie configuration
- HttpOnly cookies
- Secure cookies
- SameSite policy
- CSRF protection

Authentication design must be evaluated according to the actual browser security model.

Do not assume HTMX changes the underlying browser security requirements.

---

# 66. Object-Level Authorization

Authentication alone is never sufficient for access to user-owned resources.

Every operation involving a resource must verify that the authenticated principal is authorized to access that specific resource.

For example:

authenticated user
    ↓
requested Todo
    ↓
ownership / permission check
    ↓
allowed operation

Do not rely solely on:

- resource IDs
- hidden form fields
- UI visibility
- route restrictions
- client-side checks

Prevent IDOR/BOLA-style vulnerabilities by enforcing object-level authorization on the server.

---

# 67. Browser Security Headers

Production browser applications should use appropriate security headers where applicable, including policies for:

- Content Security Policy
- HSTS
- X-Content-Type-Options
- Referrer-Policy
- frame/embedding restrictions
- MIME sniffing
- clickjacking

Do not blindly copy a security-header configuration.

Each policy must be compatible with the application's actual authentication, HTMX, asset, and deployment requirements.

---

# 68. Authentication Abuse Protection

Authentication-related features should consider:

- brute-force protection
- login rate limiting
- account enumeration
- password reset abuse
- session revocation
- suspicious repeated failures

Security controls should be proportionate to the application's actual threat model.

---

# 69. Application Statelessness

Application instances should remain stateless wherever practical.

Do not depend on:

- mutable process-global state
- local filesystem persistence
- in-memory persistent sessions
- in-process state that must be shared across instances
- in-process scheduled work that must execute exactly once

Anything that must survive process restart or multiple instances belongs in an appropriate durable or shared system.

Do not introduce Redis, queues, distributed schedulers, or other infrastructure until the requirement exists.

---

# 70. Scheduled and Background Work

If background or scheduled work is introduced, consider multi-instance execution.

Do not assume:

application instance #1
    ↓
scheduler

will remain the only application instance.

A scheduled operation that must execute exactly once requires an appropriate coordination strategy.

Do not introduce an in-process scheduler for critical production work without evaluating:

- multiple instances
- restarts
- retries
- duplicate execution
- failure recovery
- idempotency

---

# 71. Architecture Testing

Where practical, architectural rules should be mechanically verifiable.

Examples include detecting:

- unauthorized cross-module imports
- direct access to another module's repository
- direct access to another module's persistence models
- dependency direction violations
- forbidden infrastructure dependencies

Do not rely exclusively on human review when a meaningful architectural invariant can reasonably be automated.

Architecture tests should remain small and focused.

---

# 72. CI/CD Quality Gates

The project should progressively establish automated quality gates.

Where configured, the development pipeline should verify appropriate:

- formatting
- linting
- type checking
- unit tests
- integration tests
- security-sensitive tests
- migration validation
- dependency/security checks
- build reproducibility

A change should not be considered production-ready merely because local code execution succeeds.

CI/CD should enforce the project's engineering contract automatically where practical.

---

# 73. Production Migration Execution

Database schema migrations are a deployment concern.

Do not automatically execute production migrations from every application instance unless the migration mechanism is explicitly designed for safe concurrent execution.

For production changes:

plan
    ↓
review
    ↓
migration validation
    ↓
controlled migration execution
    ↓
application deployment

Migration strategy must account for:

- multiple application instances
- backward compatibility
- deployment order
- rollback limitations
- long-running migrations
- locks
- data volume

---

# 74. Supply-Chain Security

Dependencies are part of the application's attack surface.

Where practical, maintain:

- reproducible dependency resolution
- dependency locking or appropriate version constraints
- vulnerability scanning
- secret scanning
- container/image scanning where containers are used
- review of transitive dependencies
- controlled dependency updates

Do not add a security tool merely for appearance.

Each automated check should have a defined purpose and failure policy.

---

# 75. Documentation Layers

Use different documentation mechanisms for different purposes.

AGENTS.md:
- development rules
- architectural constraints
- AI behavior
- security rules
- project conventions

Architecture documentation:
- current system structure
- domain boundaries
- module relationships
- data ownership
- important workflows

ADRs:
- why important long-term decisions were made

Operational documentation:
- deployment
- migrations
- incident procedures
- recovery
- production operations

Do not put all project knowledge into AGENTS.md.

AGENTS.md should remain the project's governing contract, not become an encyclopedia.

---

# 76. No Hidden Architectural Magic

AI agents must not introduce behavior that is difficult for a competent developer to discover or understand.

Use caution with:

- dynamic registration
- implicit global state
- hidden startup side effects
- metaprogramming
- magical decorators
- global registries
- implicit dependency injection
- automatic database mutations
- overly generic base classes

Explicit behavior is preferred over hidden behavior.

A developer should be able to trace important application behavior through the relevant modules without understanding framework internals.

---

# 77. Architecture Evolution Toward Scale

The application is designed so that increasing scale does not require rewriting the domain architecture.

Do not prematurely introduce:

- microservices
- service meshes
- Kafka
- distributed caches
- multiple databases
- complex event buses
- distributed locks
- Kubernetes-specific application architecture

merely because the application may eventually have a large user population.

Instead:

1. Maintain strong domain boundaries.
2. Keep modules internally cohesive.
3. Keep application instances stateless.
4. Measure actual bottlenecks.
5. Scale the simplest component that is limiting the system.
6. Introduce infrastructure only when justified.
7. Extract a module into a separate service only when operational or scaling requirements justify the cost.

The target is not "microservices."

The target is an architecture where the domain can evolve independently from infrastructure decisions.

---

# 78. Architecture Change Approval

The following require explicit human review before implementation:

- changing module boundaries
- introducing a new bounded context
- changing database ownership
- introducing a new architectural layer
- introducing a new external infrastructure dependency
- changing authentication architecture
- changing authorization architecture
- introducing distributed processing
- introducing a new cross-module dependency with significant coupling
- replacing a core technology
- changing production deployment architecture

The agent may propose these changes, analyze alternatives, and prepare the implementation plan, but must not silently implement them.

---

# 79. Feature Completion: Architecture Verification

In addition to the existing completion checklist, meaningful features should verify:

- [ ] Correct domain/module owns the feature.
- [ ] Domain invariants are enforced in the owning module.
- [ ] Cross-module dependencies use approved public interfaces.
- [ ] Database ownership boundaries are preserved.
- [ ] Transaction boundaries are correct.
- [ ] Concurrent execution was considered where relevant.
- [ ] Idempotency was considered where duplicate requests are possible.
- [ ] Timezone behavior was considered where time affects domain behavior.
- [ ] No new architectural pattern was introduced without justification.
- [ ] No architecture drift was introduced.
- [ ] CI/CD quality gates pass where configured.

---

# 80. Core Architectural Principle

The application should become easier to understand as it grows.

Every new feature should:

- have a clear domain owner
- have explicit boundaries
- keep business rules close to the domain that owns them
- minimize cross-module coupling
- preserve dependency direction
- preserve data ownership
- avoid accidental APIs
- remain understandable to humans
- remain predictable for AI agents
- preserve security
- preserve operational simplicity

The architecture should evolve through deliberate decisions rather than accumulating patterns generated independently by different AI agents.

The agent accelerates implementation.

The human owns architectural direction.

The codebase must remain understandable without relying on the AI that originally generated it.
