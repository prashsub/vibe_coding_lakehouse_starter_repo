---
name: cursor-rules
description: Provides guidance for creating, editing, and managing Cursor rules (.mdc files) in Databricks projects. Enforces proper file location (.cursor/rules/), naming conventions (kebab-case with .mdc extension), frontmatter format (description, globs, alwaysApply), and integration with Context7 MCP tools for library documentation. Use when creating new cursor rules, updating existing rules, understanding project rule structure, or configuring rule file organization. Covers rule file structure, frontmatter requirements, glob patterns for file-specific rules, and Context7 MCP tool usage for Databricks API documentation. Critical for maintaining consistent rule organization and ensuring proper rule discovery by Cursor IDE.
metadata:
  author: prashanth subrahmanyam
  version: "1.0"
  domain: admin
  role: utility
  standalone: true
  last_verified: "2026-02-07"
  volatility: low
---

# Cursor Rules Location

How to add new cursor rules to the project

1. Always place rule files in PROJECT_ROOT/.cursor/rules/:
    ```
    .cursor/rules/
    ├── your-rule-name.mdc
    ├── another-rule.mdc
    └── ...
    ```

2. Follow the naming convention:
    - Use kebab-case for filenames
    - Always use .mdc extension
    - Make names descriptive of the rule's purpose

3. Directory structure:
    ```
    PROJECT_ROOT/
    ├── .cursor/
    │   └── rules/
    │       ├── your-rule-name.mdc
    │       └── ...
    └── ...
    ```

4. Never place rule files:
    - In the project root
    - In subdirectories outside .cursor/rules
    - In any other location

5. Cursor rules have the following structure:

```
---
description: Short description of the rule's purpose
globs: optional/path/pattern/**/*
alwaysApply: false
---
# Rule Title

Main content explaining the rule with markdown formatting.

1. Step-by-step instructions
2. Code examples
3. Guidelines

Example:

```typescript
// Good example
function goodExample() {
  // Implementation following guidelines
}

// Bad example
function badExample() {
  // Implementation not following guidelines
}
```


6. Always use context7 when I need code generation, setup or configuration steps, or
library/API documentation. This means you should automatically use the Context7 MCP
tools to resolve library id and get library docs without me having to explicitly ask.
Use library /databricks for API and docs.
