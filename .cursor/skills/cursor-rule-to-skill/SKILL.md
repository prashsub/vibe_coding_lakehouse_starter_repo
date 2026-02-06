---
name: cursor-rule-to-skill
description: Converts Cursor rules (.mdc files) into properly structured Agent Skills following the AgentSkills.io specification. Handles frontmatter conversion, content restructuring, and generates complete skill directory structures with references and scripts when appropriate. Use when transforming cursor rules into skills, migrating .cursor/rules to skills format, or creating a SKILL.md from existing rule files. Triggers on "convert rule", "mdc to skill", "cursor rule to skill", "transform rule", "migrate rules", "create skill from rule", "agent skill from cursor rule".
license: Apache-2.0
metadata:
  author: databricks-sa
  version: "1.0.0"
  domain: admin
  source: AgentSkills.io Specification
---

# Cursor Rule to Agent Skill Converter

This skill converts Cursor rules (`.mdc` files) into properly structured Agent Skills following the [AgentSkills.io specification](https://agentskills.io/specification).

## Quick Reference

| Cursor Rule Field | Agent Skill Equivalent |
|-------------------|------------------------|
| `description:` | `description:` (required, max 1024 chars) |
| `globs:` | Mentioned in description as context |
| `alwaysApply:` | Reflected in description scope |
| File name (e.g., `21-self-improvement.mdc`) | `name:` (lowercase, hyphens only) |
| Rule body | SKILL.md body content |

---

## Conversion Workflow

### Step 1: Read and Parse the Cursor Rule

Read the input `.mdc` file and extract:

1. **YAML Frontmatter** (between `---` markers):
   - `description:` - Primary source for skill description
   - `globs:` - File patterns the rule applies to
   - `alwaysApply:` - Whether rule applies globally

2. **Markdown Body** - The actual rule content after frontmatter

```python
# Example parsing pattern
import re

def parse_cursor_rule(content: str) -> dict:
    """Parse cursor rule into frontmatter and body."""
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)
    if match:
        frontmatter_text = match.group(1)
        body = match.group(2)
        # Parse YAML frontmatter
        frontmatter = {}
        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
        return {'frontmatter': frontmatter, 'body': body}
    return {'frontmatter': {}, 'body': content}
```

### Step 2: Generate Skill Name

Convert the rule filename to a valid skill name:

**AgentSkills.io name requirements:**
- Max 64 characters
- Lowercase letters, numbers, and hyphens only (`a-z`, `0-9`, `-`)
- Must NOT start or end with hyphen
- Must NOT contain consecutive hyphens (`--`)
- Must match parent directory name

```python
def generate_skill_name(filename: str) -> str:
    """Convert filename to valid skill name."""
    # Remove .mdc extension
    name = filename.replace('.mdc', '').replace('.md', '')
    # Remove leading numbers and dashes (e.g., "21-")
    name = re.sub(r'^\d+-', '', name)
    # Convert to lowercase
    name = name.lower()
    # Replace underscores and spaces with hyphens
    name = re.sub(r'[_\s]+', '-', name)
    # Remove any non-allowed characters
    name = re.sub(r'[^a-z0-9-]', '', name)
    # Remove consecutive hyphens
    name = re.sub(r'-+', '-', name)
    # Remove leading/trailing hyphens
    name = name.strip('-')
    # Truncate to 64 chars
    return name[:64]
```

**Examples:**
| Input Filename | Generated Name |
|----------------|----------------|
| `21-self-improvement.mdc` | `self-improvement` |
| `databricks_asset_bundles.mdc` | `databricks-asset-bundles` |
| `Code Review Standards.mdc` | `code-review-standards` |

### Step 3: Generate Skill Description

The description is **critical** for skill discovery. Transform the cursor rule description:

**Requirements:**
- Max 1024 characters
- Non-empty
- Must describe WHAT the skill does AND WHEN to use it
- Written in third person

```python
def generate_description(frontmatter: dict, body: str, name: str) -> str:
    """Generate skill description from cursor rule."""
    base_desc = frontmatter.get('description', '')
    globs = frontmatter.get('globs', '')
    always_apply = frontmatter.get('alwaysApply', 'false')
    
    # Start with existing description
    description = base_desc
    
    # Add context about when to use
    if not description:
        # Extract first paragraph from body as fallback
        first_para = body.split('\n\n')[0].replace('#', '').strip()
        description = first_para[:500]
    
    # Add trigger information
    triggers = []
    if globs and globs != '**/*':
        triggers.append(f"for files matching {globs}")
    if always_apply == 'true':
        triggers.append("applies to all files in the project")
    
    # Combine and format
    if triggers:
        description += f" Use {', '.join(triggers)}."
    
    # Ensure under 1024 chars
    return description[:1024]
```

### Step 4: Transform Body Content

Restructure the cursor rule body for skill format:

**Key transformations:**
1. Add clear section headers if missing
2. Convert imperative commands to agent instructions
3. Preserve code examples and patterns
4. Add workflow steps where appropriate

```markdown
# Structure for generated SKILL.md body

# [Skill Title]

Brief overview of what this skill does.

## When to Use

- Trigger scenario 1
- Trigger scenario 2

## Instructions

Step-by-step guidance for the agent.

## Examples

Concrete examples from the original rule.

## Additional Resources (if applicable)

- Links to reference files
- External documentation
```

### Step 5: Determine Skill Complexity

Analyze the rule to decide what optional directories to create:

| Complexity Indicator | Create Directory |
|---------------------|------------------|
| Code snippets that could be scripts | `scripts/` |
| Long reference sections (>100 lines) | `references/` |
| Templates or patterns to copy | `assets/` |

```python
def analyze_complexity(body: str) -> dict:
    """Determine what directories to create."""
    result = {
        'needs_scripts': False,
        'needs_references': False,
        'needs_assets': False
    }
    
    # Check for reusable code patterns
    code_blocks = re.findall(r'```(?:python|bash|sh)[\s\S]*?```', body)
    if len(code_blocks) >= 3:
        result['needs_scripts'] = True
    
    # Check for long content
    if len(body.split('\n')) > 300:
        result['needs_references'] = True
    
    # Check for templates
    if 'template' in body.lower() or 'example output' in body.lower():
        result['needs_assets'] = True
    
    return result
```

### Step 6: Create Skill Directory Structure

Generate the complete skill directory:

```
{skill-name}/
├── SKILL.md              # Required - main instructions
├── scripts/              # Optional - if code patterns found
│   └── [extracted scripts]
├── references/           # Optional - if content is long
│   └── REFERENCE.md
└── assets/               # Optional - if templates found
    └── [templates]
```

---

## Complete Conversion Example

### Input: Cursor Rule (`21-self-improvement.mdc`)

```yaml
---
description: Guidelines for continuously improving Cursor rules based on emerging code patterns and best practices.
globs: **/*
alwaysApply: true
---
## Rule Improvement Triggers

- New code patterns not covered by existing rules
- Repeated similar implementations across files
...
```

### Output: Agent Skill Structure

**Directory:** `self-improvement/`

**SKILL.md:**
```markdown
---
name: self-improvement
description: Guidelines for continuously improving agent rules based on emerging code patterns and best practices. Provides triggers for when to add, modify, or deprecate rules, along with a structured improvement workflow. Use when analyzing codebase patterns, reviewing code changes, or evaluating rule effectiveness.
---

# Self-Improvement Guidelines

This skill provides a framework for continuously improving agent capabilities based on emerging code patterns and best practices.

## When to Use

- New code patterns emerge not covered by existing skills
- Repeated similar implementations across files
- Common error patterns that could be prevented
- New libraries or tools being used consistently

## Improvement Workflow

### 1. Validate the Trigger
- [ ] Is this pattern used in 3+ places, or from official documentation?
- [ ] Would this prevent common errors or improve quality?
...
```

---

## Handling Complex Rules

### Rules with Multiple Sections

For rules with distinct sections (like the example with "Rule Improvement Triggers", "Analysis Process", etc.):

1. Keep core workflow in SKILL.md
2. Move detailed examples to `references/EXAMPLES.md`
3. Extract reusable scripts to `scripts/`

### Rules with Code Examples

When a rule contains executable code:

1. Extract standalone functions to `scripts/`
2. Keep inline examples in SKILL.md for context
3. Reference scripts with clear usage instructions

### Rules with Templates

When a rule contains output templates:

1. Move templates to `assets/templates/`
2. Reference from SKILL.md with clear instructions
3. Include example filled-in templates

---

## Validation Checklist

Before finalizing the converted skill, verify:

### Required Fields
- [ ] `name` is lowercase, hyphens only, max 64 chars
- [ ] `name` matches parent directory name
- [ ] `description` is non-empty, max 1024 chars
- [ ] `description` includes WHAT and WHEN

### Content Quality
- [ ] SKILL.md body is under 500 lines
- [ ] Instructions are clear and actionable
- [ ] Examples are concrete, not abstract
- [ ] Progressive disclosure used for long content

### Structure
- [ ] File references are one level deep from SKILL.md
- [ ] Optional directories only created if needed
- [ ] No deeply nested reference chains

---

## Quick Conversion Commands

For simple rules (under 100 lines):
```bash
# Create skill directory
mkdir -p skills/{skill-name}

# Copy and transform the rule
# (Use the conversion logic above)
```

For complex rules:
```bash
# Create full structure
mkdir -p skills/{skill-name}/{scripts,references,assets}

# Split content appropriately
# Main instructions -> SKILL.md
# Detailed docs -> references/REFERENCE.md
# Code -> scripts/
# Templates -> assets/
```

---

## Additional Resources

- [AgentSkills.io Specification](https://agentskills.io/specification) - Official format specification
- [Progressive Disclosure Patterns](references/PROGRESSIVE-DISCLOSURE.md) - How to split large skills
- [Conversion Script](scripts/convert-rule-to-skill.py) - Automated conversion tool
- [Cursor Rule Format Reference](references/CURSOR-RULE-FORMAT.md) - Cursor rule structure documentation
- [Skill Template](assets/skill-template.md) - Agent Skills template

---

## Reference Files

This skill includes the following reference files:

- **scripts/convert-rule-to-skill.py** - Automated Python script for converting cursor rules to skills
- **references/PROGRESSIVE-DISCLOSURE.md** - Patterns for splitting large skills into manageable components
- **references/CURSOR-RULE-FORMAT.md** - Documentation of Cursor rule file structure
- **assets/skill-template.md** - Template for creating new Agent Skills
