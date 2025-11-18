# Multi-Provider Prompt Scaffold Inspector

Build, test, and compare prompt techniques across Claude, GPT-4, and Grok using research-backed prompt engineering strategies.

## Features

- **Multi-Provider Support**: Test prompts across Claude (Anthropic), GPT-4 (OpenAI), and Grok (xAI)
- **Research-Backed Techniques**: Built-in prompt scaffolding based on academic research (Liu et al. 2021, Schulhoff et al. 2024)
- **Intelligent Reformulation**: AI-powered prompt optimization using proven techniques
- **Comparison Mode**: Side-by-side testing of different techniques or providers
- **Analytics Dashboard**: Track performance metrics and ratings
- **Export Functionality**: Save your favorite scaffolds as reusable commands
- **PDF Source Viewer**: Read the academic papers behind each technique
- **ChatGPT Integration**: Export instructions for ChatGPT Project settings

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd prompt_technique_frame
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

### Environment Variables

You need at least one API key to use the app:

- `ANTHROPIC_API_KEY` - For Claude (get at https://console.anthropic.com/)
- `OPENAI_API_KEY` - For GPT-4 (get at https://platform.openai.com/)
- `XAI_API_KEY` - For Grok (get at https://x.ai/)

Optional configuration:
- `CLAUDE_MODEL` (default: claude-sonnet-4-5-20250929)
- `GPT_MODEL` (default: gpt-4o-mini)
- `XAI_MODEL` (default: grok-beta)

## Deploy to Streamlit Cloud

### Step 1: Push to GitHub

1. **Initialize git repository** (if not already done)
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Push to GitHub**
   ```bash
   git remote add origin <your-github-repo-url>
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Click "New app"
3. Select your repository, branch (main), and main file path (`app.py`)
4. Click "Deploy"

### Step 3: Configure Secrets

1. In the Streamlit Cloud dashboard, go to your app settings
2. Click on "Secrets" in the left sidebar
3. Add your secrets in TOML format:

```toml
# Required: Add at least one API key
ANTHROPIC_API_KEY = "sk-ant-..."
OPENAI_API_KEY = "sk-..."
XAI_API_KEY = "xai-..."

# Optional: Custom model configurations
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"
GPT_MODEL = "gpt-4o-mini"
XAI_MODEL = "grok-beta"
```

4. Click "Save"
5. Your app will automatically restart with the new secrets

### Step 4: Test Your Deployment

1. Wait for the app to finish deploying (usually 1-2 minutes)
2. Click on your app URL
3. Verify that at least one provider is available
4. Test a sample query

## Usage Guide

### Single Query Mode

1. Enter your query in the text area
2. Select a provider (Claude, GPT, or Grok)
3. Choose a technique category or let the AI auto-select
4. Review the generated scaffold
5. Edit if needed, then click "Run Query"
6. Rate the response to help improve analytics

### Comparison Mode

**Compare Techniques:**
- Select one provider
- Choose 2-4 different techniques
- See how each technique affects the response

**Compare Providers:**
- Select 2-3 providers
- Use the same technique across all
- See how different models respond

### Analytics

Track your usage patterns:
- Technique performance and ratings
- Provider usage distribution
- Response time comparisons
- Historical queries

### Export

Save your favorite scaffolds:
- Export individual techniques
- Bulk export all techniques
- Create custom scaffolds
- Use exported files with Claude Code

### ChatGPT Instructions

Copy the provided instructions to your ChatGPT Project settings to get automatic prompt optimization in ChatGPT!

## Project Structure

```
prompt_technique_frame/
├── app.py                          # Main Streamlit application
├── providers.py                    # Multi-provider API client
├── scaffold_engine.py              # Prompt scaffold builder
├── analytics.py                    # Performance tracking
├── exporter.py                     # Export functionality
├── pdf_viewer.py                   # Academic paper viewer
├── kb_builder.py                   # Knowledge base utilities
├── prompt_kb.yaml                  # Technique knowledge base
├── chatgpt_project_instructions.md # ChatGPT integration
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .streamlit/
│   ├── config.toml                 # Streamlit configuration
│   └── secrets.toml.example        # Secrets template
├── pdfs/                           # Academic papers (sources)
├── custom_scaffolds/               # User-created scaffolds
└── exports/                        # Exported command files
```

## Troubleshooting

### "No API keys configured" Error

**Problem:** The app can't find any API keys.

**Solution:**
- **Local:** Check your `.env` file has at least one valid API key
- **Cloud:** Verify secrets are properly configured in Streamlit Cloud dashboard

### Import Errors

**Problem:** Missing dependencies on deployment.

**Solution:** Ensure all packages are listed in `requirements.txt` with compatible versions.

### File Path Issues

**Problem:** App can't find files like PDFs or YAML files.

**Solution:** All file paths use relative paths from the app root. Ensure the file structure matches the repo.

## Contributing

Contributions are welcome! Areas for improvement:
- Add more prompt techniques from recent research
- Support additional AI providers
- Enhanced analytics visualizations
- Custom technique builder UI
- Integration with more tools

## Research Citations

This app is based on research from:

- **Liu et al. (2021)** - "Pre-train, Prompt, and Predict: A Systematic Survey of Prompting Methods in NLP"
- **Schulhoff et al. (2024)** - "The Prompt Report: A Systematic Survey of Prompting Techniques"
- Various ArXiv papers on prompt engineering (see `pdfs/` directory)

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section above

## Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - Web framework
- [LangChain](https://langchain.com/) - LLM framework
- [Anthropic Claude](https://www.anthropic.com/) - AI assistant
- [OpenAI GPT](https://openai.com/) - AI models
- [xAI Grok](https://x.ai/) - AI assistant

---

**Happy Prompting!** 🚀
