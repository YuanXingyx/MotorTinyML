# Engineering Review Prompt

## Purpose

Use this prompt to review an implementation, document, design, test result, or release candidate.

## Prompt

You are reviewing `<REVIEW_SUBJECT>` for `<PROJECT_NAME>`.

## Review Metadata

- Review Type: `<REVIEW_TYPE>`
- Related Issue: `<ISSUE_ID>`
- Related Epic: `<EPIC_ID>`
- Sprint: `<SPRINT>`
- Reviewer Role: `<REVIEWER_ROLE>`
- Review Date: `<REVIEW_DATE>`

## Review Scope

`<REVIEW_SCOPE>`

## Inputs

`<INPUT_FILES_OR_ARTIFACTS>`

## Requirements

`<REQUIREMENTS>`

## Approved Design

`<APPROVED_DESIGN>`

## Acceptance Criteria

`<ACCEPTANCE_CRITERIA>`

## Required Review Areas

Evaluate:

1. Requirement compliance
2. Scope compliance
3. Architecture compliance
4. Correctness
5. Modularity and maintainability
6. Naming and consistency
7. Error handling
8. Security and sensitive data handling
9. Test coverage and evidence
10. Documentation consistency
11. Deployment or reproducibility
12. Known risks and limitations

## Severity Levels

- Critical: Blocks release or risks data, safety, or system integrity
- High: Major functional or architectural problem
- Medium: Important maintainability, reliability, or test issue
- Low: Minor improvement
- Informational: Observation with no required action

## Required Output

### Review Summary

`<SUMMARY>`

### Findings

For each finding provide:

- Finding ID
- Severity
- File or Artifact
- Location
- Evidence
- Impact
- Required Action
- Acceptance Test

### Passed Checks

List checks that passed with supporting evidence.

### Missing Evidence

List unavailable tests, artifacts, or decisions.

### Risk Assessment

Describe residual risks.

### Review Decision

Choose one:

- Approved
- Approved with Required Actions
- Changes Required
- Blocked

## Rules

- Base findings on evidence.
- Do not modify reviewed files unless separately authorized.
- Do not infer unapproved design intent.
- Distinguish defects from optional improvements.
- Keep recommendations within the approved scope.
- Do not execute Git commands.
