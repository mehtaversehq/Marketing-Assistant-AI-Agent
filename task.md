# TASKS.md — Agent Task Definitions

## Purpose

This file defines the **tasks the AI agent must perform**, including:

* What the task is
* When it should be triggered
* How it must be executed
* What constraints must be followed

Each task is written as an **operational definition** that the agent must strictly follow.

---

# TASK: DATA_AGGREGATION

## Description

Collect and unify marketing data from all available integrations into a structured internal format.

## Trigger

* On system initialization
* On scheduled intervals
* On user request for updated data

## Inputs

* Connected platform APIs
* Historical datasets
* Real-time event streams

## Execution Rules

1. Discover all available data sources
2. Authenticate securely with each source
3. Extract data with timestamps preserved
4. Normalize all metrics into a shared schema
5. Merge datasets without duplication
6. Store results in the internal data layer

## Constraints

* Do not overwrite valid existing data without verification
* Do not fabricate or infer missing data
* Maintain source attribution for all records

## Output

* Structured, unified dataset ready for querying

## Failure Behavior

* Skip failing sources and continue processing
* Log missing sources explicitly
* Mark dataset as partially complete

---

# TASK: DATA_VALIDATION

## Description

Validate all incoming and existing data before it is used for analysis.

## Trigger

* After data aggregation
* Before insight generation
* Before predictive modeling

## Inputs

* Raw and processed datasets

## Execution Rules

1. Detect missing or null values
2. Identify outliers and impossible values
3. Cross-check overlapping data sources when available
4. Flag inconsistencies without modifying original data

## Constraints

* Do not silently correct data
* Do not discard data unless explicitly invalid

## Output

* Validated dataset with confidence annotations

## Failure Behavior

* Mark affected data as "low confidence"
* Prevent use in critical insights unless acknowledged

---

# TASK: INSIGHT_GENERATION

## Description

Analyze validated data to produce meaningful, data-driven insights.

## Trigger

* On user query
* On report generation
* After data updates

## Inputs

* Validated datasets
* Historical performance data

## Execution Rules

1. Identify trends over time
2. Compare performance across campaigns and channels
3. Detect patterns and anomalies
4. Relate findings to historical baselines
5. Generate insights supported by explicit data points

## Constraints

* Do not produce insights without supporting data
* Do not generalize beyond available evidence

## Output

* Structured list of insights with supporting data references

## Failure Behavior

* If insufficient data:

  * Output "insufficient data for insight generation"
  * Do not speculate

---

# TASK: NARRATIVE_GENERATION

## Description

Convert insights into a clear, structured narrative for human interpretation.

## Trigger

* After insight generation
* On user request for explanation

## Inputs

* Generated insights

## Execution Rules

1. Organize insights into logical flow:

   * What happened
   * Why it happened (if supported)
   * What it means
2. Translate metrics into plain language
3. Prioritize clarity and readability

## Constraints

* Do not introduce new information not present in insights
* Do not exaggerate conclusions

## Output

* Human-readable explanation of performance

## Failure Behavior

* If insights are unclear:

  * Output raw insights instead of forcing narrative

---

# TASK: QUERY_HANDLING

## Description

Interpret and respond to user queries using available data and context.

## Trigger

* On every user interaction

## Inputs

* User query
* Conversation history
* Available datasets

## Execution Rules

1. Parse user intent
2. Retrieve relevant data
3. Maintain conversational context
4. Generate response:

   * Direct answer
   * Supporting evidence
   * Optional follow-up suggestions

## Constraints

* Do not ignore prior context
* Do not repeat unnecessary information

## Output

* Context-aware response grounded in data

## Failure Behavior

* If query is ambiguous:

  * Request clarification
* If data is unavailable:

  * State explicitly

---

# TASK: PREDICTIVE_MODELING

## Description

Generate forecasts and predictions using prebuilt models.

## Trigger

* On user request
* On predefined analysis workflows

## Inputs

* Historical data
* Model parameters

## Execution Rules

1. Select appropriate model
2. Prepare input data
3. Execute model
4. Interpret results with confidence levels

## Constraints

* Always label outputs as predictions
* Include assumptions where applicable

## Output

* Forecast results with confidence indicators

## Failure Behavior

* If model confidence is low:

  * Warn user
  * Limit recommendations

---

# TASK: REPORT_GENERATION

## Description

Create structured reports summarizing data, insights, and recommendations.

## Trigger

* On user request
* On scheduled intervals

## Inputs

* Insights
* Validated data
* Predictions (optional)

## Execution Rules

1. Compile key information
2. Structure report:

   * Overview
   * Metrics
   * Insights
   * Recommendations
3. Format for readability

## Constraints

* Do not include unvalidated data
* Do not present assumptions as facts

## Output

* Complete performance report

## Failure Behavior

* If data is incomplete:

  * Include explicit disclaimer

---

# TASK: MEMORY_MANAGEMENT

## Description

Maintain and utilize historical context to improve future outputs.

## Trigger

* After each interaction
* During query handling

## Inputs

* User interactions
* Past insights
* Stored context

## Execution Rules

1. Store relevant context
2. Retrieve past interactions when needed
3. Adapt responses based on learned patterns

## Constraints

* Do not store sensitive data unnecessarily
* Do not use outdated or invalid context

## Output

* Updated memory state

## Failure Behavior

* If conflicting memory:

  * Prioritize recent validated data

---

# TASK: ERROR_HANDLING

## Description

Detect, classify, and respond to errors in the system.

## Trigger

* On any task failure

## Inputs

* System state
* Task outputs

## Execution Rules

1. Identify error type:

   * False positive (hallucination)
   * False negative (missing data)
2. Flag uncertainty
3. Adjust output accordingly

## Constraints

* Never present uncertain data as fact

## Output

* Safe, corrected, or limited response

## Failure Behavior

* If critical failure:

  * Halt task
  * Notify user

---

# TASK: SECURITY_COMPLIANCE

## Description

Ensure all operations comply with data security and privacy requirements.

## Trigger

* During all tasks

## Inputs

* Data access requests
* System operations

## Execution Rules

1. Enforce access controls
2. Limit exposure of sensitive data
3. Log actions where required

## Constraints

* Never expose unauthorized data

## Output

* Secure system behavior

## Failure Behavior

* Halt operation on violation
* Flag security risk immediately

---

# GLOBAL RULES

The agent must always:

* Prioritize **accuracy over completeness**
* Explicitly state **uncertainty**
* Avoid **hallucination**
* Keep **humans in control of decisions**
* Ground all outputs in **real data**

The agent is not an authority.

It is a system for **enhanced understanding and decision support**.
