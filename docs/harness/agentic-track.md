# Additional Research Track: Training-Free / Agentic Highlight Editing

Investigate whether a training-free or lightly-trained agent framework can solve long-video highlight generation by orchestrating existing foundation models and specialized video tools.

The goal is not to build a simple API wrapper.

The research question is:

"Can an intelligent video editing agent dynamically decide what information to acquire, which tools to call, and how to revise its decisions in order to generate high-quality highlights under limited computation?"

------

# Track A: Existing Agentic Video Understanding Systems

Search and analyze recent work in:

- multimodal agents;
- video agents;
- tool-using VLMs;
- ReAct-style vision agents;
- autonomous video analysis systems;
- AI video editing agents;
- embodied perception agents;
- active perception;
- adaptive computation for multimodal models.

Include:

- GPT-4V / GPT-4.1 vision style systems;
- Gemini video reasoning systems;
- Claude vision agents;
- Qwen-VL / InternVL based agents;
- open-source multimodal agent frameworks.

For each work record:

- whether it supports video;
- whether it uses external tools;
- planning mechanism;
- memory mechanism;
- self-reflection mechanism;
- training requirement;
- evaluation benchmark;
- limitations.

------

# Track B: Agent Formulation for Highlight Editing

Analyze whether highlight generation can be formulated as:

## Sequential Decision Making

State:

```
Current video understanding state
+
available observations
+
remaining compute budget
```

Actions:

```
select temporal segment
change sampling rate
request high resolution frames
call ASR
call OCR
call tracker
call event detector
ask VLM reasoning
generate crop
request revision
```

Reward:

```
highlight quality
+
temporal completeness
+
spatial composition quality
-
computation cost
-
redundancy
```

Investigate related concepts:

- active perception;
- adaptive computation;
- budgeted inference;
- tool-use reinforcement learning;
- Monte Carlo planning;
- self-reflection agents.

------

# Track C: Training-Free Agent Baseline

Design a possible no-training system:

Example:

```
Long video
 |
shot segmentation
 |
agent planner
 |
+----------------+
| available tools|
+----------------+
 |
ASR
OCR
tracking
VLM
video search
reframing
critic
 |
final highlight
```

Evaluate:

- whether existing foundation models are sufficient;
- where failure cases happen;
- whether tool selection is the bottleneck;
- whether agent reasoning improves over fixed pipelines.

Important:

Do not assume API models are available in final benchmark.
Consider open-source alternatives.

------

# Track D: Research Contribution Beyond Prompt Engineering

Identify possible ICLR-level contributions.

Reject ideas that are only:

- prompt engineering;
- API chaining;
- manually designed workflow;
- replacing one module with GPT.

Prefer hypotheses involving:

## 1. Learned Tool Selection

The model learns:

"Which video analysis tool should be called next?"

Possible approaches:

- imitation learning;
- RL;
- preference optimization;
- trajectory learning.

------

## 2. Budget-aware Video Agent

The agent optimizes:

```
quality / computation
```

Possible novelty:

- adaptive frame sampling;
- adaptive temporal exploration;
- dynamic resolution selection.

------

## 3. Self-Refining Editing Agent

Agent generates a draft highlight and critiques it.

Possible learned components:

- highlight critic;
- editing reward model;
- revision policy.

------

## 4. Agent + EventTube Hybrid

Investigate whether an agent can construct structured event tubes:

Output:

```
event:
 start/end
 important player
 event category
 confidence
 crop trajectory
 evidence
```

The agent decides how to obtain evidence.

------

# Compare Against Non-Agent Approaches

Create a comparison table:

Columns:

- fixed pipeline;
- Video-LLM;
- temporal grounding model;
- event-tube model;
- agent framework.

Compare:

- training requirement;
- inference cost;
- long-video capability;
- interpretability;
- adaptability;
- product deployment potential;
- ICLR novelty potential.

------

# Candidate Research Ideas

Generate candidate ideas specifically combining:

1. EventTube representation.
2. Teacher-student distillation.
3. Video editing agent.
4. Tool-use planning.
5. Edge deployment.

For each idea:

Provide:

- research hypothesis;
- closest papers;
- novelty argument;
- required experiments;
- possible failure reasons;
- competition applicability;
- GameTracker applicability.

------

# Final Decision Criteria

Rank ideas by:

1. ICLR acceptance probability.
2. Scientific novelty.
3. Feasibility within 6 weeks.
4. Data availability.
5. Ability to build basketball product.
6. Whether contribution survives if GPT/API models disappear.

Reject ideas whose core contribution is only "calling better APIs".