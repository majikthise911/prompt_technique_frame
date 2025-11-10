# pdf_viewer.py
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class PDFSourceViewer:
    """Extract and display relevant sections from research papers"""

    def __init__(self, pdf_dir: str = "./pdfs"):
        self.pdf_dir = Path(pdf_dir)
        self.source_map = {
            "Liu2021": {
                "file": "2107.13586.pdf",
                "title": "Pre-train, Prompt, and Predict: A Systematic Survey of Prompting Methods in NLP",
                "authors": "Liu et al. (2021)",
                "url": "https://arxiv.org/abs/2107.13586",
                "keywords": ["zero-shot", "few-shot", "prompt engineering", "language models"]
            },
            "Schulhoff2024": {
                "file": "2406.06608.pdf",
                "title": "The Prompt Report: A Systematic Survey of Prompting Techniques",
                "authors": "Schulhoff et al. (2024)",
                "url": "https://arxiv.org/abs/2406.06608",
                "keywords": ["chain-of-thought", "tree-of-thoughts", "react", "self-consistency", "prompting"]
            },
            "Wei2022": {
                "file": "2406.06608.pdf",  # Referenced in Schulhoff
                "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
                "authors": "Wei et al. (2022)",
                "url": "https://arxiv.org/abs/2201.11903",
                "keywords": ["chain-of-thought", "reasoning", "step-by-step"]
            },
            "Wang2022": {
                "file": "2406.06608.pdf",  # Referenced in Schulhoff
                "title": "Self-Consistency Improves Chain of Thought Reasoning in Language Models",
                "authors": "Wang et al. (2022)",
                "url": "https://arxiv.org/abs/2203.11171",
                "keywords": ["self-consistency", "reasoning", "chain-of-thought"]
            },
            "Yao2023": {
                "file": "2406.06608.pdf",  # Referenced in Schulhoff
                "title": "Tree of Thoughts: Deliberate Problem Solving with Large Language Models",
                "authors": "Yao et al. (2023)",
                "url": "https://arxiv.org/abs/2305.10601",
                "keywords": ["tree-of-thoughts", "problem-solving", "search"]
            },
            "Yao2022": {
                "file": "2406.06608.pdf",  # Referenced in Schulhoff
                "title": "ReAct: Synergizing Reasoning and Acting in Language Models",
                "authors": "Yao et al. (2022)",
                "url": "https://arxiv.org/abs/2210.03629",
                "keywords": ["react", "reasoning", "acting", "tool-use"]
            },
            "Anthropic-Claude-Code-2024": {
                "file": "claude_code_patterns.md",
                "title": "Claude Code Prompt Engineering Patterns",
                "authors": "Anthropic (2024)",
                "url": "https://docs.claude.com/claude-code",
                "keywords": ["multi-agent", "progressive-development", "claude"]
            },
            "Best-Practices-2024": {
                "file": "claude_code_patterns.md",
                "title": "Prompt Engineering Best Practices",
                "authors": "Industry Best Practices (2024)",
                "url": None,
                "keywords": ["best-practices", "prompt-engineering"]
            }
        }

    def get_source_info(self, evidence_id: str) -> Optional[Dict]:
        """Get source information for an evidence ID"""
        return self.source_map.get(evidence_id)

    def extract_pdf_text(self, filename: str, max_pages: int = 20) -> str:
        """Extract text from PDF file"""
        pdf_path = self.pdf_dir / filename

        if not pdf_path.exists():
            return f"PDF file not found: {filename}"

        try:
            doc = fitz.open(pdf_path)
            text = ""

            # Extract from first max_pages
            for page_num in range(min(len(doc), max_pages)):
                page = doc[page_num]
                text += f"\n\n--- Page {page_num + 1} ---\n\n"
                text += page.get_text()

            doc.close()
            return text
        except Exception as e:
            return f"Error extracting PDF: {str(e)}"

    def search_pdf_for_keywords(self, filename: str, keywords: List[str],
                                context_chars: int = 500) -> List[Tuple[int, str]]:
        """Search PDF for keywords and return relevant sections with context"""
        pdf_path = self.pdf_dir / filename

        if not pdf_path.exists():
            return []

        try:
            doc = fitz.open(pdf_path)
            results = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()

                # Search for each keyword
                for keyword in keywords:
                    if keyword.lower() in text.lower():
                        # Find position and extract context
                        pos = text.lower().find(keyword.lower())
                        start = max(0, pos - context_chars)
                        end = min(len(text), pos + len(keyword) + context_chars)

                        context = text[start:end]
                        results.append((page_num + 1, context))
                        break  # Found keyword on this page, move to next page

            doc.close()
            return results
        except Exception as e:
            return []

    def get_source_content(self, evidence_id: str, search_mode: bool = True) -> Dict:
        """Get source content for display"""
        source_info = self.get_source_info(evidence_id)

        if not source_info:
            return {
                "found": False,
                "message": f"Source information not available for: {evidence_id}"
            }

        content = {
            "found": True,
            "title": source_info["title"],
            "authors": source_info["authors"],
            "url": source_info["url"],
            "file": source_info["file"]
        }

        # Handle markdown files differently
        if source_info["file"].endswith(".md"):
            md_path = self.pdf_dir / source_info["file"]
            if md_path.exists():
                with open(md_path, 'r', encoding='utf-8') as f:
                    content["text"] = f.read()
                    content["type"] = "markdown"
            else:
                content["text"] = "Source file not found"
                content["type"] = "text"
        else:
            # PDF file
            if search_mode and source_info["keywords"]:
                # Search for relevant sections
                sections = self.search_pdf_for_keywords(
                    source_info["file"],
                    source_info["keywords"],
                    context_chars=800
                )

                if sections:
                    text = f"Found {len(sections)} relevant section(s):\n\n"
                    for page_num, context in sections[:5]:  # Limit to 5 sections
                        text += f"\n{'='*60}\n"
                        text += f"Page {page_num}\n"
                        text += f"{'='*60}\n\n"
                        text += context + "\n"
                    content["text"] = text
                    content["type"] = "text"
                else:
                    # No keyword matches, show beginning of paper
                    content["text"] = self.extract_pdf_text(source_info["file"], max_pages=5)
                    content["type"] = "text"
            else:
                # Full text extraction
                content["text"] = self.extract_pdf_text(source_info["file"], max_pages=10)
                content["type"] = "text"

        return content
