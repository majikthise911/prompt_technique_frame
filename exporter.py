# exporter.py
from pathlib import Path
from typing import Dict, List

class ClaudeCodeExporter:
    """Export scaffolds as Claude Code commands"""

    def __init__(self, output_dir: str = "./exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def export_scaffold(self, technique: Dict, scaffold: str,
                       custom_name: str = None) -> str:
        """
        Export scaffold as .md command file
        Returns: filepath
        """
        # Generate filename
        name = custom_name or technique['name']
        filename = name.lower().replace(' ', '_').replace('-', '_') + ".md"
        filepath = self.output_dir / filename

        # Build frontmatter
        frontmatter = f"""---
description: {technique['name']} - {technique.get('category', 'General')}
category: {technique.get('category', 'General')}
argument-hint: <YOUR_QUERY>
"""

        # Add evidence if available
        if 'evidence' in technique:
            frontmatter += f"evidence: [{', '.join(technique['evidence'])}]\n"

        frontmatter += "---\n\n"

        # Build command content
        content = frontmatter
        content += f"# {technique['name']}\n\n"
        content += f"**Category**: {technique.get('category', 'General')}  \n"
        content += f"**Use Cases**: {', '.join(technique.get('use_cases', ['general']))}  \n\n"
        content += "## Instructions\n\n"
        content += scaffold
        content += "\n\n## Usage\n\n"
        content += f"```bash\n/{filename.replace('.md', '')} <YOUR_QUERY>\n```\n"

        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(filepath)

    def export_batch(self, scaffolds: List[Dict]) -> List[str]:
        """Export multiple scaffolds"""
        filepaths = []
        for item in scaffolds:
            filepath = self.export_scaffold(
                technique=item['technique'],
                scaffold=item['scaffold'],
                custom_name=item.get('name')
            )
            filepaths.append(filepath)
        return filepaths

    def create_readme(self, exported_files: List[str]):
        """Create README for exported commands"""
        readme_path = self.output_dir / "README.md"

        content = "# Exported Claude Code Commands\n\n"
        content += "## Installation\n\n"
        content += "Copy these `.md` files to your Claude Code commands directory:\n\n"
        content += "```bash\n"
        content += "# For project-specific commands\n"
        content += "cp *.md /path/to/your/project/.claude/commands/\n\n"
        content += "# For global commands\n"
        content += "cp *.md ~/.claude/commands/\n"
        content += "```\n\n"
        content += "## Available Commands\n\n"

        for filepath in exported_files:
            filename = Path(filepath).stem
            content += f"- `/{filename}` - {filepath}\n"

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
