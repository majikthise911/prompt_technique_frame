# kb_builder.py
import yaml
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict
import re

def extract_claude_code_patterns() -> List[Dict]:
    """Extract patterns from Claude Code documentation"""
    return [
        {
            "id": "multi_agent",
            "name": "Multi-Agent Coordination",
            "template": """You orchestrate {n} specialized agents:
{agent_list}

Process:
1. Each agent analyzes from their perspective
2. Agents provide structured input
3. You synthesize findings into cohesive solution

Respond with clear sections for each agent's contribution.""",
            "category": "Advanced/Agentic",
            "year": 2024,
            "evidence": ["Anthropic-Claude-Code-2024"],
            "use_cases": ["architecture", "code_review", "complex_analysis"],
            "variables": ["n", "agent_list"]
        },
        {
            "id": "progressive_dev",
            "name": "Progressive Development",
            "template": """Follow this systematic approach:

1. **Requirements Analysis**: {task_description}
2. **Design Strategy**: Plan technical approach
3. **Incremental Implementation**: Build step-by-step with validation
4. **Quality Validation**: Ensure standards met
5. **Next Actions**: Define follow-up steps

Provide detailed output for each phase.""",
            "category": "Software Engineering",
            "year": 2024,
            "evidence": ["Anthropic-Claude-Code-2024"],
            "use_cases": ["feature_development", "debugging", "refactoring"],
            "variables": ["task_description"]
        },
        {
            "id": "research_plan_implement",
            "name": "Research-Plan-Implement",
            "template": """Execute in three distinct phases:

**Phase 1: Research**
- Gather context and constraints
- Identify relevant patterns
- Document findings

**Phase 2: Planning**
- Design solution approach
- Break into implementable steps
- Identify risks

**Phase 3: Implementation**
- Execute plan systematically
- Validate at each step
- Document results

Task: {task}""",
            "category": "Problem Solving",
            "year": 2024,
            "evidence": ["Anthropic-Claude-Code-2024"],
            "use_cases": ["complex_problems", "architecture", "optimization"],
            "variables": ["task"]
        }
    ]

def extract_academic_techniques() -> List[Dict]:
    """Core techniques from Liu et al. and Schulhoff et al."""
    return [
        # Liu et al. (2021)
        {
            "id": "zero_shot",
            "name": "Zero-Shot Prompting",
            "template": """{instruction}

Provide your answer below:""",
            "category": "Basic",
            "year": 2021,
            "citation_count": 2100,
            "evidence": ["Liu2021"],
            "use_cases": ["general_qa", "classification", "simple_tasks"],
            "variables": ["instruction"]
        },
        {
            "id": "few_shot",
            "name": "Few-Shot Prompting",
            "template": """Here are some examples:

{exemplars}

Now, solve this:
Q: {question}
A:""",
            "category": "Basic",
            "year": 2021,
            "citation_count": 2100,
            "evidence": ["Liu2021"],
            "use_cases": ["pattern_recognition", "format_learning", "style_transfer"],
            "variables": ["exemplars", "question"]
        },

        # Schulhoff et al. (2024) - The Prompt Report
        {
            "id": "cot",
            "name": "Chain-of-Thought",
            "template": """Q: {question}

A: Let's think step by step:
1.""",
            "category": "Reasoning",
            "year": 2022,
            "citation_count": 1800,
            "evidence": ["Wei2022", "Schulhoff2024"],
            "use_cases": ["math", "logic", "multi_step_reasoning"],
            "variables": ["question"]
        },
        {
            "id": "self_consistency",
            "name": "Self-Consistency",
            "template": """Generate 3 different reasoning paths for: {question}

Path 1:
[Your reasoning]

Path 2:
[Alternative reasoning]

Path 3:
[Third approach]

Final Answer (based on majority agreement):""",
            "category": "Reasoning",
            "year": 2022,
            "citation_count": 900,
            "evidence": ["Wang2022", "Schulhoff2024"],
            "use_cases": ["verification", "complex_reasoning", "ambiguous_problems"],
            "variables": ["question"]
        },
        {
            "id": "tot",
            "name": "Tree-of-Thoughts",
            "template": """Problem: {question}

Explore multiple solution branches:

Branch A:
- Approach: [describe]
- Evaluation: [pros/cons]

Branch B:
- Approach: [describe]
- Evaluation: [pros/cons]

Branch C:
- Approach: [describe]
- Evaluation: [pros/cons]

Best Path Selection:
[Choose and execute the most promising branch]""",
            "category": "Reasoning",
            "year": 2023,
            "citation_count": 600,
            "evidence": ["Yao2023", "Schulhoff2024"],
            "use_cases": ["optimization", "strategic_planning", "exploration"],
            "variables": ["question"]
        },
        {
            "id": "react",
            "name": "ReAct (Reasoning + Acting)",
            "template": """Task: {task}

Thought 1: [Analyze what information you need]
Action 1: [Describe action to take]
Observation 1: [What you learned]

Thought 2: [Next reasoning step]
Action 2: [Next action]
Observation 2: [Result]

[Continue until task complete]

Final Answer:""",
            "category": "Agentic",
            "year": 2022,
            "citation_count": 850,
            "evidence": ["Yao2022", "Schulhoff2024"],
            "use_cases": ["research", "tool_use", "multi_step_tasks"],
            "variables": ["task"]
        },
        {
            "id": "role_prompting",
            "name": "Role-Based Prompting",
            "template": """You are {role}.

Your expertise includes: {expertise}

Task: {task}

Approach this with the perspective and knowledge of your role.""",
            "category": "Instruction",
            "year": 2023,
            "evidence": ["Schulhoff2024"],
            "use_cases": ["specialized_knowledge", "perspective_taking", "creative_writing"],
            "variables": ["role", "expertise", "task"]
        },
        {
            "id": "structured_output",
            "name": "Structured Output Prompting",
            "template": """{task}

Respond in this exact format:
{format_specification}

Example output:
{example}""",
            "category": "Output Control",
            "year": 2023,
            "evidence": ["Schulhoff2024"],
            "use_cases": ["data_extraction", "api_responses", "consistent_formatting"],
            "variables": ["task", "format_specification", "example"]
        }
    ]

def extract_domain_templates() -> List[Dict]:
    """Domain-specific prompt templates"""
    return [
        {
            "id": "code_review_multi",
            "name": "Multi-Dimensional Code Review",
            "template": """Review the following code from multiple perspectives:

Code to review:
{code}

**Quality Auditor Perspective:**
- Readability, naming, structure

**Security Analyst Perspective:**
- Vulnerabilities, auth issues, data exposure

**Performance Reviewer Perspective:**
- Bottlenecks, optimization opportunities

**Architecture Assessor Perspective:**
- Design patterns, SOLID principles, scalability

Provide structured feedback for each dimension.""",
            "category": "Software Engineering/Review",
            "year": 2024,
            "evidence": ["Anthropic-Claude-Code-2024"],
            "use_cases": ["code_review", "quality_assurance"],
            "variables": ["code"]
        },
        {
            "id": "debug_systematic",
            "name": "Systematic Debugging",
            "template": """Debug the following issue:

Error: {error}
Context: {context}

**Error Analyzer**: Classify error type and severity
**Code Inspector**: Trace execution path
**Environment Checker**: Validate configs and dependencies
**Fix Strategist**: Propose solution with risk assessment

Provide:
1. Root cause analysis
2. Step-by-step fix
3. Verification plan
4. Prevention measures""",
            "category": "Software Engineering/Debug",
            "year": 2024,
            "evidence": ["Anthropic-Claude-Code-2024"],
            "use_cases": ["debugging", "troubleshooting"],
            "variables": ["error", "context"]
        },
        {
            "id": "data_analysis_structured",
            "name": "Structured Data Analysis",
            "template": """Analyze this dataset systematically:

Dataset: {dataset_description}
Goal: {analysis_goal}

**Phase 1: Exploratory Analysis**
- Summary statistics
- Data quality assessment
- Pattern identification

**Phase 2: Deep Dive**
- Correlation analysis
- Outlier detection
- Trend identification

**Phase 3: Insights & Recommendations**
- Key findings
- Actionable recommendations
- Next steps""",
            "category": "Data Analysis",
            "year": 2024,
            "evidence": ["Best-Practices-2024"],
            "use_cases": ["data_analysis", "business_intelligence"],
            "variables": ["dataset_description", "analysis_goal"]
        }
    ]

def build_knowledge_base():
    """Build comprehensive KB from all sources"""
    techniques = []

    # Add all technique sources
    techniques.extend(extract_academic_techniques())
    techniques.extend(extract_claude_code_patterns())
    techniques.extend(extract_domain_templates())

    # Write to YAML
    with open("prompt_kb.yaml", "w") as f:
        yaml.dump(techniques, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    # Print summary
    categories = {}
    for t in techniques:
        cat = t.get("category", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1

    print(f"[OK] Knowledge base created with {len(techniques)} techniques")
    print("\nBreakdown by category:")
    for cat, count in sorted(categories.items()):
        print(f"  - {cat}: {count}")

    return techniques

if __name__ == "__main__":
    build_knowledge_base()
