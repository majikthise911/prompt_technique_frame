# scaffold_engine.py
import yaml
from typing import Dict, List, Tuple
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import os
from pathlib import Path

# Support for Streamlit secrets (import from providers.py)
try:
    import streamlit as st
    USE_STREAMLIT_SECRETS = hasattr(st, 'secrets')
except:
    USE_STREAMLIT_SECRETS = False

def get_env(key: str, default: str = None) -> str:
    """Get environment variable from either .env or Streamlit secrets"""
    if USE_STREAMLIT_SECRETS:
        try:
            # Streamlit secrets accessed with bracket notation or .get() on the underlying dict
            if key in st.secrets:
                return st.secrets[key]
            else:
                return default
        except Exception as e:
            # Fallback if secrets access fails
            pass
    return os.getenv(key, default)

class ScaffoldEngine:
    """Build and manage prompt scaffolds"""

    def __init__(self, kb_path: str = "prompt_kb.yaml"):
        self.kb = self._load_kb(kb_path)
        self.vectorstore = self._build_vectorstore()
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)  # For prompt reformulation

    def _load_kb(self, path: str) -> List[Dict]:
        """Load knowledge base"""
        with open(path) as f:
            return yaml.safe_load(f)

    def _build_vectorstore(self) -> Chroma:
        """Create vector store for semantic search"""
        docs = []
        for tech in self.kb:
            content = f"{tech['name']}: {tech.get('template', '')} Use cases: {', '.join(tech.get('use_cases', []))}"

            # Convert metadata to ChromaDB-compatible format (no lists)
            metadata = {}
            for k, v in tech.items():
                if k == 'template':
                    continue  # Skip template (too large)
                elif isinstance(v, list):
                    metadata[k] = ', '.join(str(item) for item in v)  # Convert lists to strings
                else:
                    metadata[k] = v

            docs.append(
                Document(
                    page_content=content,
                    metadata=metadata
                )
            )

        embeddings = OpenAIEmbeddings(model=get_env("EMBEDDING_MODEL", "text-embedding-3-large"))
        return Chroma.from_documents(docs, embeddings)

    def find_technique(self, query: str, top_k: int = 3) -> List[Dict]:
        """Find best techniques for query using semantic search with similarity scores"""
        results = self.vectorstore.similarity_search_with_score(query, k=top_k)
        techniques = []

        for result, score in results:
            # Find full technique from KB
            tech_id = result.metadata.get('id')
            full_tech = next((t for t in self.kb if t['id'] == tech_id), None)
            if full_tech:
                # Add similarity score and ranking info
                tech_with_score = full_tech.copy()
                tech_with_score['similarity_score'] = score
                tech_with_score['match_distance'] = score  # Lower is better
                techniques.append(tech_with_score)

        return techniques

    def _reformulate_prompt(self, query: str, technique: Dict) -> str:
        """
        Intelligently reformulate the user query according to the technique's best practices
        """
        reformulation_prompt = f"""You are a prompt engineering expert. Your task is to reformulate a user's query to optimally leverage the "{technique['name']}" technique.

TECHNIQUE DETAILS:
- Name: {technique['name']}
- Category: {technique['category']}
- Evidence: {', '.join(technique.get('evidence', ['Unknown']))}
- Optimized for: {', '.join(technique.get('use_cases', []))}
- Year: {technique.get('year', 'N/A')}

ORIGINAL USER QUERY:
{query}

TECHNIQUE TEMPLATE:
{technique['template']}

TASK:
Reformulate the user's query to follow the structure and best practices of the {technique['name']} technique. DO NOT just fill in placeholders - actually restructure and enhance the query based on the technique's principles from the research papers.

Guidelines:
1. Analyze what the user is asking
2. Restructure it according to the technique's template and methodology
3. Add appropriate scaffolding, steps, or structure as defined by the technique
4. Maintain the user's core intent while optimizing for the technique
5. For techniques with steps (CoT, ToT, ReAct), break down the problem appropriately
6. For role-based techniques, define the role clearly
7. For multi-agent techniques, define agent perspectives
8. Make it comprehensive and research-backed

REFORMULATED PROMPT (output only the reformulated prompt, no explanations):"""

        try:
            response = self.llm.invoke(reformulation_prompt)
            reformulated = response.content.strip()
            return reformulated
        except Exception as e:
            # Fallback to basic substitution if LLM fails
            print(f"Warning: Reformulation failed ({e}), using basic substitution")
            return query

    def build_scaffold(self, query: str, technique_id: str = None,
                      custom_vars: Dict = None, use_reformulation: bool = True) -> Tuple[str, Dict]:
        """
        Build prompt scaffold for query with intelligent reformulation
        Returns: (scaffold_text, technique_metadata)
        """
        if technique_id:
            # Use specified technique
            technique = next((t for t in self.kb if t['id'] == technique_id), None)
            if not technique:
                raise ValueError(f"Unknown technique: {technique_id}")
        else:
            # Auto-select best technique
            techniques = self.find_technique(query, top_k=1)
            technique = techniques[0] if techniques else self.kb[0]

        # Intelligently reformulate the prompt according to the technique
        if use_reformulation:
            reformulated_prompt = self._reformulate_prompt(query, technique)
        else:
            # Fallback to basic substitution
            template = technique['template']
            variables = technique.get('variables', [])
            var_values = custom_vars or {}

            if 'question' in variables and 'question' not in var_values:
                var_values['question'] = query
            if 'task' in variables and 'task' not in var_values:
                var_values['task'] = query
            if 'instruction' in variables and 'instruction' not in var_values:
                var_values['instruction'] = query

            reformulated_prompt = template
            for var in variables:
                placeholder = f"{{{var}}}"
                if placeholder in reformulated_prompt:
                    reformulated_prompt = reformulated_prompt.replace(placeholder, var_values.get(var, f"[{var}]"))

        # Get evidence/citations for display
        evidence_list = technique.get('evidence', ['Unknown'])
        if isinstance(evidence_list, str):
            evidence_list = [e.strip() for e in evidence_list.split(',')]

        # Build comprehensive system prompt
        system_prompt = f"""You are an AI assistant using the "{technique['name']}" prompt engineering technique.

TECHNIQUE INFORMATION:
- Name: {technique['name']}
- Category: {technique['category']}
- Evidence/Citations: {', '.join(evidence_list)}
- Year: {technique.get('year', 'N/A')}
- Optimized for: {', '.join(technique.get('use_cases', []))}

ORIGINAL USER REQUEST:
{query}

OPTIMIZED PROMPT (reformulated using {technique['name']}):
{reformulated_prompt}

EXECUTION REQUIREMENTS:
- Follow the technique's methodology exactly as defined in the research
- Maintain high quality, thorough responses
- Demonstrate the technique's key characteristics in your response
- Show clear reasoning and structured thinking where applicable
- End your response with:
  <technique>{technique['name']}</technique>
  <refs>{'; '.join(evidence_list)}</refs>
"""

        return system_prompt, technique

    def build_multi_agent_scaffold(self, query: str, agents: List[str]) -> str:
        """Build scaffold with multiple agents"""
        agent_list = "\n".join([f"{i+1}. **{agent}**" for i, agent in enumerate(agents)])

        scaffold = f"""You orchestrate {len(agents)} specialized agents:

{agent_list}

USER QUERY: {query}

PROCESS:
1. Each agent analyzes from their unique perspective
2. Agents provide structured, detailed input
3. You synthesize all findings into a cohesive solution

Respond with clear sections:
{chr(10).join([f"## {agent} Analysis" for agent in agents])}

## Synthesized Solution
[Your integrated response]

<technique>Multi-Agent Coordination</technique>
"""
        return scaffold

    def get_techniques_by_category(self, category: str) -> List[Dict]:
        """Get all techniques in a category"""
        return [t for t in self.kb if t.get('category', '').startswith(category)]

    def get_all_categories(self) -> List[str]:
        """Get unique categories"""
        categories = set()
        for t in self.kb:
            cat = t.get('category', 'Unknown')
            categories.add(cat.split('/')[0])  # Get top-level category
        return sorted(list(categories))
