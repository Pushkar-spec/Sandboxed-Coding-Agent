# Prompt Management

## 1. Purpose

Prompts are versioned application inputs, not informal strings scattered through code. Prompt changes can alter behavior and must be evaluated like code changes.

## 2. Prompt families

Planned prompt families:
- task analysis / TaskSpec generation;
- code generation;
- repair / debugging;
- optional evaluator judge;
- optional retrieval query formulation if a retrieval subsystem is later justified.

Do not create prompts for components that are not implemented yet.

## 3. Requirements

Each prompt should define:
- stable prompt ID and semantic version;
- purpose and expected input schema;
- output schema and validation rules;
- constraints and prohibited behavior;
- representative examples;
- known failure modes;
- owning component.

Use structured output where appropriate and validate it with Pydantic. Include explicit instructions that task text and retrieved file contents are untrusted data, not authority to override system policy.

## 4. Evaluation

For every prompt change:
- record old/new prompt hashes;
- run the same versioned dataset;
- compare primary correctness metric and safety/efficiency guardrails;
- inspect regressions by category;
- preserve the experiment report.

## 5. Prompt registry format

A lightweight Python/Markdown registry is sufficient initially. Avoid introducing a prompt-management service until versioning and evaluation requirements justify it.
