# Progressive Disclosure Patterns

When converting large cursor rules to skills, use progressive disclosure to manage context efficiently.

## The Three-Level System

Agent Skills use a three-level loading system:

| Level | Content | When Loaded | Token Budget |
|-------|---------|-------------|--------------|
| 1. Metadata | `name` + `description` | Always | ~100 words |
| 2. Instructions | SKILL.md body | When skill triggers | <5k words |
| 3. Resources | References, scripts, assets | When needed | Unlimited |

## When to Split Content

Split content from SKILL.md into separate files when:

1. **SKILL.md exceeds 500 lines**
2. **Distinct sections can stand alone** (e.g., API reference, examples)
3. **Content is only needed for specific scenarios**
4. **Multiple code examples could be scripts**

## Splitting Patterns

### Pattern 1: High-Level Guide with References

Keep workflow overview in SKILL.md, move details to references.

**SKILL.md:**
```markdown
# Database Migration

## Quick Start
1. Run analysis
2. Review changes
3. Apply migration

## Detailed Guides
- For schema changes, see [SCHEMA.md](references/SCHEMA.md)
- For data migration, see [DATA.md](references/DATA.md)
- For rollback procedures, see [ROLLBACK.md](references/ROLLBACK.md)
```

### Pattern 2: Domain-Specific Organization

Organize by domain when a skill covers multiple areas.

```
my-skill/
├── SKILL.md              # Overview and navigation
└── references/
    ├── domain-a.md       # Domain A specifics
    ├── domain-b.md       # Domain B specifics
    └── domain-c.md       # Domain C specifics
```

### Pattern 3: Examples Collection

Move extensive examples to a separate file.

**SKILL.md:**
```markdown
## Basic Example

```python
# Simple usage
client.do_thing()
```

## More Examples

For additional examples covering edge cases and advanced usage,
see [EXAMPLES.md](references/EXAMPLES.md).
```

### Pattern 4: API Reference Extraction

Move detailed API docs to references.

**SKILL.md:**
```markdown
## Key Methods

- `process(data)` - Main processing function
- `validate(schema)` - Validate against schema

For complete API documentation, see [API.md](references/API.md).
```

## Guidelines

### Keep in SKILL.md
- Core workflow steps
- Essential patterns (1-2 examples each)
- Navigation to detailed content
- Decision guides

### Move to References
- Comprehensive API documentation
- Extensive examples
- Edge case handling
- Historical/legacy information

### Move to Scripts
- Reusable code (>10 lines)
- Validation scripts
- Automation tools

### Move to Assets
- Templates
- Sample files
- Configuration examples

## Example: Converting a Large Rule

### Before (600-line cursor rule)

```markdown
---
description: Complete guide to API development
---

# API Development Guide

[100 lines of overview]

## Authentication
[150 lines of auth details]

## Endpoints
[200 lines of endpoint patterns]

## Examples
[150 lines of examples]
```

### After (Split skill)

**SKILL.md (200 lines):**
```markdown
---
name: api-development
description: Guide to API development with authentication, endpoints, and best practices.
---

# API Development Guide

## Overview
[Condensed to 50 lines]

## Quick Reference

### Authentication
Use OAuth 2.0 with JWT tokens. See [AUTH.md](references/AUTH.md) for details.

### Endpoints
Follow REST conventions. See [ENDPOINTS.md](references/ENDPOINTS.md) for patterns.

## Examples
Basic example here. More in [EXAMPLES.md](references/EXAMPLES.md).
```

**references/AUTH.md (150 lines):**
Full authentication documentation.

**references/ENDPOINTS.md (200 lines):**
Complete endpoint patterns.

**references/EXAMPLES.md (150 lines):**
Comprehensive examples collection.

## Validation Checklist

After splitting:

- [ ] SKILL.md is under 500 lines
- [ ] Core workflow is clear without reading references
- [ ] References are one level deep (no references to references)
- [ ] Each reference file has a clear, single purpose
- [ ] Navigation from SKILL.md to references is explicit
