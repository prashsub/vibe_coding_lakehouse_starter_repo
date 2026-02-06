# Cursor Rule Format Reference

This document describes the format of Cursor rules (`.mdc` files) for conversion to Agent Skills.

## File Structure

Cursor rules use a YAML frontmatter + Markdown body format:

```markdown
---
description: Brief description of what this rule does
globs: **/*.py
alwaysApply: false
---

# Rule Title

Rule content in markdown...
```

## Frontmatter Fields

### `description` (string, required)

Brief description of the rule's purpose. This becomes the primary source for the skill description.

**Example:**
```yaml
description: Guidelines for Python code style and best practices
```

### `globs` (string, optional)

Glob pattern specifying which files the rule applies to.

**Examples:**
```yaml
globs: **/*.py          # All Python files
globs: src/**/*.ts      # TypeScript files in src/
globs: **/*             # All files (default)
```

### `alwaysApply` (boolean, optional)

Whether the rule should always be active, regardless of current file.

**Values:**
- `true` - Rule applies globally
- `false` (default) - Rule applies based on globs

## Body Content

The markdown body after frontmatter contains the actual rule instructions.

### Common Patterns in Cursor Rules

1. **Headers** - Used to organize sections
2. **Code blocks** - Examples and templates
3. **Lists** - Checklists and requirements
4. **Tables** - Reference information

### Example Body Structure

```markdown
## When to Apply

- Scenario 1
- Scenario 2

## Guidelines

1. First guideline
2. Second guideline

## Examples

### Good Example
```python
# Good code
```

### Bad Example
```python
# Bad code
```
```

## Conversion Mapping

| Cursor Rule | Agent Skill |
|-------------|-------------|
| filename `21-rule-name.mdc` | `name: rule-name` |
| `description:` | `description:` (enhanced) |
| `globs:` | Mentioned in description |
| `alwaysApply: true` | "Applies broadly" in description |
| Body content | SKILL.md body (restructured) |

## Full Example

### Input: `python-style.mdc`

```markdown
---
description: Python code style guidelines following PEP 8
globs: **/*.py
alwaysApply: false
---

## Formatting

- Use 4 spaces for indentation
- Max line length: 88 characters (Black default)

## Naming

- Classes: PascalCase
- Functions: snake_case
- Constants: UPPER_SNAKE_CASE

## Imports

```python
# Standard library
import os
import sys

# Third-party
import numpy as np

# Local
from . import utils
```
```

### Output: `python-style/SKILL.md`

```markdown
---
name: python-style
description: Python code style guidelines following PEP 8. Use for files matching **/*.py, when writing or reviewing Python code.
metadata:
  converted-from: "python-style.mdc"
  version: "1.0.0"
---

# Python Style

Python code style guidelines following PEP 8.

## Formatting

- Use 4 spaces for indentation
- Max line length: 88 characters (Black default)

## Naming

- Classes: PascalCase
- Functions: snake_case
- Constants: UPPER_SNAKE_CASE

## Imports

```python
# Standard library
import os
import sys

# Third-party
import numpy as np

# Local
from . import utils
```
```
