# Streamlit Cloud Deployment Checklist

## Pre-Deployment

- [ ] Ensure you have at least one API key ready (Anthropic, OpenAI, or xAI)
- [ ] Review `requirements.txt` to ensure all dependencies are listed
- [ ] Test the app locally with `streamlit run app.py`
- [ ] Commit all changes to git
- [ ] Push to GitHub

## Deployment Steps

### 1. Push to GitHub

```bash
# If not already initialized
git init
git add .
git commit -m "Prepare app for Streamlit Cloud deployment"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/prompt_technique_frame.git
git branch -M main
git push -u origin main
```

### 2. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Sign in with GitHub
3. Click "New app"
4. Select:
   - **Repository**: `yourusername/prompt_technique_frame`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Click "Deploy"

### 3. Configure Secrets

Once deployed:

1. Click on your app in the Streamlit Cloud dashboard
2. Go to **Settings** → **Secrets**
3. Add your API keys in TOML format:

```toml
# Add at least ONE of these:
ANTHROPIC_API_KEY = "sk-ant-api03-xxxxx"
OPENAI_API_KEY = "sk-xxxxx"
XAI_API_KEY = "xai-xxxxx"

# Optional: Custom models (defaults shown)
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"
GPT_MODEL = "gpt-4o-mini"
XAI_MODEL = "grok-4-fast-reasoning"
EMBEDDING_MODEL = "text-embedding-3-large"
```

4. Click "Save"
5. Wait for the app to restart (30-60 seconds)

### 4. Test Your Deployment

1. Open your app URL (something like `https://yourappname.streamlit.app`)
2. Check the sidebar - should show "✅ X providers available"
3. Try a test query with your preferred provider
4. Verify all features work:
   - [ ] Single Query mode
   - [ ] Comparison mode
   - [ ] Analytics (will be empty initially)
   - [ ] Export functionality
   - [ ] PDF source viewer
   - [ ] ChatGPT Instructions

## Troubleshooting

### "No API keys configured" Error

**Cause**: Streamlit secrets not set properly

**Fix**:
1. Go to app Settings → Secrets
2. Verify the TOML format is correct (no extra spaces, proper quotes)
3. Ensure at least one API key is present
4. Save and wait for restart

### "Module not found" Errors

**Cause**: Missing dependency in requirements.txt

**Fix**:
1. Add the missing package to `requirements.txt`
2. Commit and push
3. Streamlit Cloud will auto-redeploy

### Slow First Load

**Normal**: First load builds the vector store from the knowledge base
- This can take 30-60 seconds
- Subsequent loads are cached and much faster

### Database/File Write Errors

**Normal**: The app creates directories at runtime
- `./data/` for analytics database
- `./exports/` for exported commands
- These are created automatically if they don't exist

## Post-Deployment

### Monitor Usage

- Check the Streamlit Cloud dashboard for:
  - App health
  - Resource usage
  - Error logs

### Update the App

```bash
# Make changes locally
git add .
git commit -m "Update: description of changes"
git push

# Streamlit Cloud will automatically redeploy
```

### Share Your App

Your app URL will be: `https://[app-name].streamlit.app`

Share it with:
- Team members
- Add to documentation
- Include in project README

## Security Notes

- **Never** commit `.env` or `.streamlit/secrets.toml` to git
- These files are in `.gitignore` for protection
- Always use Streamlit secrets for API keys in production
- Regularly rotate API keys
- Monitor API usage to prevent abuse

## Performance Tips

1. **Resource Limits**: Streamlit Community Cloud has limits
   - 1 GB RAM
   - CPU throttling after heavy use
   - Consider upgrading if needed

2. **Caching**: The app uses `@st.cache_resource` for:
   - Provider clients
   - Scaffold engine
   - Vector store
   - This improves performance significantly

3. **Rate Limiting**: Be mindful of API rate limits
   - OpenAI: Check your tier limits
   - Anthropic: Check your plan limits
   - Grok: Check xAI limits

## Support

- **Streamlit Docs**: https://docs.streamlit.io/
- **Streamlit Community**: https://discuss.streamlit.io/
- **App Issues**: Create an issue in your GitHub repo

---

**Ready to deploy?** Follow the steps above and you'll be live in minutes!
