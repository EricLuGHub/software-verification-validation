# Software Verification & Validation Lab

A test-engineering workspace for a REST-style project and task service.

The project explores verification at several levels:

- API and relationship tests for expected and invalid behaviour;
- boundary and error-case coverage;
- behaviour-driven acceptance scenarios;
- change-impact metrics for create, update, and delete operations.

## Stack

Python, pytest, Behave

## Structure

- `partA/` — API-level tests and helper utilities.
- `partB/` — executable behaviour scenarios and step definitions.
- `partC/` — change-impact / test-metric experiments.

This repository is a course project presented as a focused example of test design, regression testing, and software validation.
