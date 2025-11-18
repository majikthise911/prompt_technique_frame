# app.py
import streamlit as st
import time
from pathlib import Path
from datetime import datetime

from providers import MultiProviderClient
from scaffold_engine import ScaffoldEngine
from analytics import AnalyticsTracker
from exporter import ClaudeCodeExporter
from pdf_viewer import PDFSourceViewer

# === PAGE CONFIG ===
st.set_page_config(
    page_title="Multi-Provider Prompt Scaffold Inspector",
    page_icon="🔬",
    layout="wide"
)

# === INITIALIZE COMPONENTS ===
@st.cache_resource
def init_components():
    return {
        'client': MultiProviderClient(),
        'engine': ScaffoldEngine(),
        'analytics': AnalyticsTracker(),
        'exporter': ClaudeCodeExporter(),
        'pdf_viewer': PDFSourceViewer()
    }

# Add cache buster based on API keys to reinitialize when keys change
try:
    import streamlit as st_check
    if hasattr(st_check, 'secrets'):
        # Use presence of keys as cache buster
        cache_key = f"{bool(st.secrets.get('ANTHROPIC_API_KEY'))}{bool(st.secrets.get('OPENAI_API_KEY'))}{bool(st.secrets.get('XAI_API_KEY'))}"
    else:
        cache_key = "local"
except:
    cache_key = "local"

@st.cache_resource
def init_components_with_key(_cache_key):
    return {
        'client': MultiProviderClient(),
        'engine': ScaffoldEngine(),
        'analytics': AnalyticsTracker(),
        'exporter': ClaudeCodeExporter(),
        'pdf_viewer': PDFSourceViewer()
    }

components = init_components_with_key(cache_key)

# === SESSION STATE ===
if 'scaffold' not in st.session_state:
    st.session_state.scaffold = ""
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'technique' not in st.session_state:
    st.session_state.technique = None
if 'comparison_mode' not in st.session_state:
    st.session_state.comparison_mode = False
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""
if 'comparison_results' not in st.session_state:
    st.session_state.comparison_results = {}
if 'last_mode' not in st.session_state:
    st.session_state.last_mode = "🎯 Single Query"
if 'last_provider' not in st.session_state:
    st.session_state.last_provider = None
if 'last_temperature' not in st.session_state:
    st.session_state.last_temperature = 0.7
if 'last_max_tokens' not in st.session_state:
    st.session_state.last_max_tokens = 2048

# === HEADER ===
st.title("🔬 Multi-Provider Prompt Scaffold Inspector")
st.caption("Build, test, and compare prompt techniques across Claude, GPT-4, and Grok")

# === SIDEBAR ===
with st.sidebar:
    st.header("⚙️ Configuration")

    # Provider selection
    available_providers = components['client'].get_available_providers()
    if not available_providers:
        st.error("⚠️ No API keys configured! Check your .env file")
        st.info("""
        **To configure API keys:**

        1. Create a `.env` file in the project root
        2. Add at least one API key:
           ```
           ANTHROPIC_API_KEY=sk-ant-...
           OPENAI_API_KEY=sk-...
           XAI_API_KEY=xai-...
           ```
        3. Restart the app
        """)
        st.stop()

    st.success(f"✅ {len(available_providers)} provider(s) available: {', '.join(available_providers)}")

    # Debug: Show which providers are NOT available
    all_possible = ["claude", "gpt", "grok"]
    missing = [p for p in all_possible if p not in available_providers]
    if missing:
        with st.expander("ℹ️ Missing Providers"):
            st.caption(f"Not configured: {', '.join(missing)}")
            st.caption("Add their API keys to `.env` or Streamlit secrets to enable them")

            # Cache clear button
            if st.button("🔄 Clear Cache & Reload Providers"):
                st.cache_resource.clear()
                st.rerun()

            # Debug info
            if st.checkbox("🔍 Show Debug Info"):
                import os
                try:
                    import streamlit as st_check
                    has_secrets = hasattr(st_check, 'secrets')
                    st.caption(f"Streamlit secrets available: {has_secrets}")
                    if has_secrets:
                        # Show which keys are in secrets (without revealing values)
                        secret_keys = list(st.secrets.keys()) if has_secrets else []
                        st.caption(f"Keys in secrets: {secret_keys}")
                        st.caption(f"XAI_API_KEY in secrets: {'XAI_API_KEY' in st.secrets}")
                        st.caption(f"ANTHROPIC_API_KEY in secrets: {'ANTHROPIC_API_KEY' in st.secrets}")
                        st.caption(f"OPENAI_API_KEY in secrets: {'OPENAI_API_KEY' in st.secrets}")

                        # Test get_env function directly
                        from providers import get_env
                        xai_test = get_env("XAI_API_KEY")
                        st.caption(f"get_env('XAI_API_KEY') returns: {xai_test[:10] if xai_test else 'None'}...")
                except Exception as e:
                    st.caption(f"Debug error: {e}")

    # Mode selection
    mode = st.radio(
        "Select Mode:",
        ["🎯 Single Query", "⚖️ Comparison", "📊 Analytics", "📤 Export", "📋 ChatGPT Instructions"],
        key="mode"
    )
    # Track mode changes
    st.session_state.last_mode = mode

    st.divider()

    # Advanced options
    with st.expander("🔧 Advanced Options"):
        temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
        max_tokens = st.number_input("Max Tokens", 100, 4096, 2048, 100)
        show_metadata = st.checkbox("Show Metadata", value=True)
        use_reformulation = st.checkbox("🤖 Intelligent Prompt Reformulation", value=True,
                                       help="Use AI to reformulate your query according to research-backed techniques")

# === MAIN CONTENT ===

# === MODE: SINGLE QUERY ===
if mode == "🎯 Single Query":

    col1, col2 = st.columns([2, 1])

    with col1:
        user_input = st.text_area(
            "Your Query:",
            placeholder="e.g., Design a microservices architecture for a social media platform",
            height=120,
            value=st.session_state.last_query if st.session_state.last_mode == "🎯 Single Query" else "",
            key="user_input"
        )
        # Save query to session state
        if user_input:
            st.session_state.last_query = user_input

    with col2:
        provider = st.selectbox("Select Provider:", available_providers, key="provider")

        # Technique selection
        categories = components['engine'].get_all_categories()
        selected_category = st.selectbox("Category:", ["Auto-Select"] + categories)

        if selected_category != "Auto-Select":
            techniques = components['engine'].get_techniques_by_category(selected_category)
            technique_names = {t['name']: t['id'] for t in techniques}
            selected_technique = st.selectbox("Technique:", ["Auto-Select"] + list(technique_names.keys()))
            technique_id = technique_names.get(selected_technique) if selected_technique != "Auto-Select" else None
        else:
            technique_id = None

    if user_input and len(user_input.strip()) > 10:

        # Build scaffold
        with st.spinner("🔨 Building prompt scaffold..." if not use_reformulation else "🤖 Intelligently reformulating prompt..."):
            scaffold, technique = components['engine'].build_scaffold(
                user_input,
                technique_id=technique_id,
                use_reformulation=use_reformulation
            )
            st.session_state.scaffold = scaffold
            st.session_state.technique = technique

        # Show technique info with citations
        st.markdown(f"**Selected Technique:** `{technique['name']}` ({technique['category']})")

        # Show citation and reasoning
        with st.expander("📚 Source & Selection Reasoning", expanded=False):
            # Evidence/Citations
            evidence = technique.get('evidence', [])
            if evidence:
                if isinstance(evidence, str):
                    evidence = [e.strip() for e in evidence.split(',')]
                st.markdown("**📖 Evidence/Citations:**")
                for cite in evidence:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"- `{cite}`")
                    with col2:
                        if st.button(f"📄 Read", key=f"read_{cite}"):
                            st.session_state[f'show_source_{cite}'] = True

            # Year and citation count
            col1, col2, col3 = st.columns(3)
            with col1:
                year = technique.get('year', 'N/A')
                st.metric("Year", year)
            with col2:
                citation_count = technique.get('citation_count', 'N/A')
                st.metric("Citations", citation_count if citation_count != 'N/A' else 'Custom')
            with col3:
                if 'similarity_score' in technique:
                    match_quality = "Excellent" if technique['similarity_score'] < 0.3 else "Good" if technique['similarity_score'] < 0.5 else "Fair"
                    st.metric("Match Quality", match_quality)

            # Selection reasoning
            if technique_id is None and 'similarity_score' in technique:
                st.markdown("**🎯 Why This Technique Was Selected:**")
                st.info(f"Auto-selected via semantic search with similarity score: **{technique['similarity_score']:.3f}** (lower is better). "
                       f"This technique best matches your query based on its use cases and template structure.")

            # Use cases
            use_cases = technique.get('use_cases', [])
            if use_cases:
                if isinstance(use_cases, str):
                    use_cases = [uc.strip() for uc in use_cases.split(',')]
                st.markdown("**💡 Optimized For:**")
                st.write(", ".join(use_cases))

        # Display source documents if user clicked "Read"
        evidence = technique.get('evidence', [])
        if evidence:
            if isinstance(evidence, str):
                evidence = [e.strip() for e in evidence.split(',')]

            for cite in evidence:
                if st.session_state.get(f'show_source_{cite}', False):
                    with st.expander(f"📖 Reading: {cite}", expanded=True):
                        source_content = components['pdf_viewer'].get_source_content(cite)

                        if source_content['found']:
                            st.markdown(f"### {source_content['title']}")
                            st.caption(f"**Authors:** {source_content['authors']}")

                            if source_content.get('url'):
                                st.markdown(f"🔗 [View on arXiv]({source_content['url']})")

                            st.divider()

                            if source_content.get('type') == 'markdown':
                                st.markdown(source_content['text'])
                            else:
                                st.text_area(
                                    "Source Content (relevant sections):",
                                    value=source_content['text'],
                                    height=400,
                                    key=f"source_text_{cite}"
                                )

                            if st.button(f"❌ Close", key=f"close_{cite}"):
                                st.session_state[f'show_source_{cite}'] = False
                                st.rerun()
                        else:
                            st.warning(source_content['message'])

        # Show reformulation indicator
        if use_reformulation:
            st.info("✨ **Intelligent Reformulation Enabled** - Your prompt has been optimized according to research-backed techniques")

        # Scaffold editor
        with st.expander("📝 Scaffold Editor (Edit Before Running)", expanded=True):
            edited_scaffold = st.text_area(
                "Edit the prompt scaffold:",
                value=scaffold,
                height=400,
                key="scaffold_editor"
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if st.button("▶️ Run Query", type="primary", use_container_width=True):
                    start_time = time.time()

                    with st.spinner(f"🤖 {provider.upper()} is thinking..."):
                        response, metadata = components['client'].complete(
                            provider=provider,
                            system_prompt=edited_scaffold,
                            user_message=user_input,
                            temperature=temperature,
                            max_tokens=max_tokens
                        )

                        response_time = int((time.time() - start_time) * 1000)

                        st.session_state.responses[provider] = {
                            'text': response,
                            'metadata': metadata,
                            'response_time': response_time
                        }

            with col2:
                if st.button("📋 Copy Scaffold", use_container_width=True):
                    st.code(edited_scaffold, language="text")
                    st.success("✅ Ready to copy!")

            with col3:
                if st.button("🔄 Reset", use_container_width=True):
                    st.session_state.scaffold = scaffold
                    st.rerun()

            with col4:
                if st.button("📤 Export", use_container_width=True):
                    filepath = components['exporter'].export_scaffold(
                        technique=technique,
                        scaffold=edited_scaffold
                    )
                    st.success(f"✅ Exported to: {filepath}")

        # Response display
        if provider in st.session_state.responses:
            st.divider()
            st.subheader(f"🤖 {provider.upper()} Response")

            response_data = st.session_state.responses[provider]
            st.write(response_data['text'])

            # Metadata
            if show_metadata:
                with st.expander("📊 Response Metadata"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Tokens Used", response_data['metadata'].get('tokens', 'N/A'))
                    with col2:
                        st.metric("Response Time", f"{response_data['response_time']}ms")
                    with col3:
                        st.metric("Model", response_data['metadata'].get('model', 'N/A'))

            # Rating
            st.divider()
            col1, col2 = st.columns([3, 1])
            with col1:
                rating = st.slider(
                    "Rate this response (1-5):",
                    1, 5, 3,
                    key=f"rating_{provider}"
                )
            with col2:
                if st.button("💾 Save Rating", use_container_width=True):
                    components['analytics'].log_interaction(
                        query=user_input,
                        technique_id=technique['id'],
                        technique_name=technique['name'],
                        provider=provider,
                        response=response_data['text'],
                        tokens=response_data['metadata'],
                        response_time=response_data['response_time'],
                        rating=rating
                    )
                    st.success("✅ Rating saved!")

# === MODE: COMPARISON ===
elif mode == "⚖️ Comparison":
    st.subheader("Compare Techniques or Providers")

    # Show previous results if available
    if st.session_state.comparison_results:
        with st.expander("📊 Previous Comparison Results", expanded=False):
            st.caption("Scroll down to see these results again or run a new comparison")
            prev_cols = st.columns(len(st.session_state.comparison_results))
            for col, (name, data) in zip(prev_cols, st.session_state.comparison_results.items()):
                with col:
                    st.markdown(f"**{name}**")
                    st.caption(data.get('response', '')[:200] + "...")

    comparison_type = st.radio(
        "Compare by:",
        ["🔧 Different Techniques (Same Provider)", "🤖 Different Providers (Same Technique)"],
        horizontal=True
    )

    user_input = st.text_area(
        "Your Query:",
        placeholder="Enter a query to compare across techniques/providers",
        height=100,
        value=st.session_state.last_query if st.session_state.last_mode == "⚖️ Comparison" else ""
    )
    # Save query to session state
    if user_input:
        st.session_state.last_query = user_input

    if comparison_type == "🔧 Different Techniques (Same Provider)":
        provider = st.selectbox("Provider:", available_providers)

        # Technique selection
        all_techniques = components['engine'].kb
        technique_options = {t['name']: t['id'] for t in all_techniques}

        selected = st.multiselect(
            "Select techniques to compare (2-4):",
            options=list(technique_options.keys()),
            max_selections=4
        )

        if st.button("🔬 Run Comparison", type="primary") and len(selected) >= 2:
            results = {}

            progress_bar = st.progress(0)

            for i, tech_name in enumerate(selected):
                tech_id = technique_options[tech_name]

                with st.spinner(f"Running {tech_name}..."):
                    scaffold, technique = components['engine'].build_scaffold(
                        user_input,
                        technique_id=tech_id
                    )

                    response, metadata = components['client'].complete(
                        provider=provider,
                        system_prompt=scaffold,
                        user_message=user_input,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )

                    results[tech_name] = {
                        'response': response,
                        'metadata': metadata,
                        'technique': technique
                    }

                progress_bar.progress((i + 1) / len(selected))

            # Save to session state
            st.session_state.comparison_results = results

            # Display side-by-side
            st.divider()
            cols = st.columns(len(results))

            for col, (tech_name, data) in zip(cols, results.items()):
                with col:
                    st.markdown(f"### {tech_name}")
                    st.caption(f"Category: {data['technique']['category']}")
                    st.write(data['response'])

                    if show_metadata:
                        st.caption(f"Tokens: {data['metadata'].get('tokens', 'N/A')}")

            # Analytics logging
            st.divider()
            st.subheader("Rate Comparison Results")
            rating_cols = st.columns(len(results))

            for col, (tech_name, data) in zip(rating_cols, results.items()):
                with col:
                    rating_key = f"rating_comp_{tech_name}_{hash(user_input)}"
                    rating = st.slider(
                        f"Rate {tech_name}:",
                        1, 5, 3,
                        key=rating_key
                    )
                    if st.button(f"💾 Save", key=f"save_{tech_name}_{hash(user_input)}", use_container_width=True):
                        # Log to analytics
                        components['analytics'].log_interaction(
                            query=user_input,
                            technique_id=data['technique']['id'],
                            technique_name=data['technique']['name'],
                            provider=provider,
                            response=data['response'],
                            tokens=data['metadata'],
                            response_time=0,  # Not tracked in comparison mode
                            rating=rating
                        )
                        st.success("✅ Saved!")

    else:  # Compare providers
        selected_providers = st.multiselect(
            "Select providers (2-3):",
            options=available_providers,
            max_selections=3
        )

        technique_id = None
        use_custom_technique = st.checkbox("Use specific technique")

        if use_custom_technique:
            all_techniques = components['engine'].kb
            technique_options = {t['name']: t['id'] for t in all_techniques}
            selected_tech = st.selectbox("Technique:", list(technique_options.keys()))
            technique_id = technique_options[selected_tech]

        if st.button("🔬 Run Comparison", type="primary") and len(selected_providers) >= 2:
            scaffold, technique = components['engine'].build_scaffold(
                user_input,
                technique_id=technique_id
            )

            results = {}
            progress_bar = st.progress(0)

            for i, prov in enumerate(selected_providers):
                with st.spinner(f"Running with {prov.upper()}..."):
                    response, metadata = components['client'].complete(
                        provider=prov,
                        system_prompt=scaffold,
                        user_message=user_input,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )

                    results[prov] = {
                        'response': response,
                        'metadata': metadata
                    }

                progress_bar.progress((i + 1) / len(selected_providers))

            # Save to session state
            st.session_state.comparison_results = results

            # Display side-by-side
            st.divider()
            st.markdown(f"**Technique Used:** {technique['name']}")

            cols = st.columns(len(results))

            for col, (prov, data) in zip(cols, results.items()):
                with col:
                    st.markdown(f"### {prov.upper()}")
                    st.write(data['response'])

                    if show_metadata:
                        st.caption(f"Tokens: {data['metadata'].get('tokens', 'N/A')}")
                        st.caption(f"Model: {data['metadata'].get('model', 'N/A')}")

            # Analytics logging
            st.divider()
            st.subheader("Rate Comparison Results")
            rating_cols = st.columns(len(results))

            for col, (prov, data) in zip(rating_cols, results.items()):
                with col:
                    rating_key = f"rating_prov_{prov}_{hash(user_input)}"
                    rating = st.slider(
                        f"Rate {prov.upper()}:",
                        1, 5, 3,
                        key=rating_key
                    )
                    if st.button(f"💾 Save", key=f"save_{prov}_{hash(user_input)}", use_container_width=True):
                        # Log to analytics
                        components['analytics'].log_interaction(
                            query=user_input,
                            technique_id=technique['id'],
                            technique_name=technique['name'],
                            provider=prov,
                            response=data['response'],
                            tokens=data['metadata'],
                            response_time=0,  # Not tracked in comparison mode
                            rating=rating
                        )
                        st.success("✅ Saved!")

# === MODE: ANALYTICS ===
elif mode == "📊 Analytics":
    st.subheader("Performance Analytics")

    tab1, tab2, tab3 = st.tabs(["📈 Techniques", "🤖 Providers", "📜 History"])

    with tab1:
        st.markdown("### Technique Performance")

        stats = components['analytics'].get_technique_stats()

        if not stats.empty:
            import plotly.express as px

            fig = px.bar(
                stats,
                x='technique_name',
                y='uses',
                color='avg_rating',
                title='Technique Usage & Ratings',
                labels={'uses': 'Times Used', 'avg_rating': 'Avg Rating'},
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(stats, use_container_width=True)
        else:
            st.info("📊 No technique data yet!")
            st.markdown("""
            **To populate analytics:**
            1. Go to **Single Query** or **Comparison** mode
            2. Run a query
            3. Rate the response (1-5 stars)
            4. Click **"💾 Save Rating"**
            5. Return here to see your analytics!
            """)

    with tab2:
        st.markdown("### Provider Comparison")

        provider_stats = components['analytics'].get_provider_comparison()

        if not provider_stats.empty:
            col1, col2 = st.columns(2)

            with col1:
                fig = px.pie(
                    provider_stats,
                    values='uses',
                    names='provider',
                    title='Usage Distribution'
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig = px.bar(
                    provider_stats,
                    x='provider',
                    y='avg_rating',
                    title='Average Ratings',
                    color='avg_rating',
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig, use_container_width=True)

            st.dataframe(provider_stats, use_container_width=True)
        else:
            st.info("🤖 No provider data yet! Run queries and save ratings to see provider comparisons.")

    with tab3:
        st.markdown("### Recent History")

        history = components['analytics'].get_recent_history(limit=50)

        if not history.empty:
            st.dataframe(history, use_container_width=True)
        else:
            st.info("No history yet. Run queries and save ratings to populate analytics!")

            # Debug: Show database info
            with st.expander("🔍 Debug Analytics"):
                import os
                db_path = components['analytics'].db_path
                st.caption(f"Database path: {db_path}")
                st.caption(f"Database exists: {os.path.exists(db_path)}")

                if os.path.exists(db_path):
                    import sqlite3
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM interactions")
                    count = cursor.fetchone()[0]
                    conn.close()
                    st.caption(f"Total interactions in DB: {count}")
                    st.caption("If count is 0, you need to run queries and click 'Save Rating'")

# === MODE: EXPORT ===
elif mode == "📤 Export":
    st.subheader("Export Scaffolds as Claude Code Commands")

    st.markdown("""
    Export your favorite prompt scaffolds as Claude Code `.md` command files.
    These can be used in any coding project with Claude Code.
    """)

    export_type = st.radio(
        "Export:",
        ["📦 All Techniques", "🎯 Specific Techniques", "💾 Custom Scaffold"],
        horizontal=True
    )

    if export_type == "📦 All Techniques":
        if st.button("📤 Export All Techniques", type="primary"):
            with st.spinner("Exporting..."):
                exported = []
                for tech in components['engine'].kb:
                    scaffold, _ = components['engine'].build_scaffold(
                        "Example query",
                        technique_id=tech['id']
                    )
                    filepath = components['exporter'].export_scaffold(tech, scaffold)
                    exported.append(filepath)

                components['exporter'].create_readme(exported)

            st.success(f"✅ Exported {len(exported)} techniques to ./exports/")
            st.info("Copy these files to `.claude/commands/` in your project")

    elif export_type == "🎯 Specific Techniques":
        all_techniques = components['engine'].kb
        technique_options = {f"{t['name']} ({t['category']})": t for t in all_techniques}

        selected = st.multiselect(
            "Select techniques to export:",
            options=list(technique_options.keys())
        )

        if st.button("📤 Export Selected", type="primary") and selected:
            with st.spinner("Exporting..."):
                exported = []
                for tech_key in selected:
                    tech = technique_options[tech_key]
                    scaffold, _ = components['engine'].build_scaffold(
                        "Example query",
                        technique_id=tech['id']
                    )
                    filepath = components['exporter'].export_scaffold(tech, scaffold)
                    exported.append(filepath)

                components['exporter'].create_readme(exported)

            st.success(f"✅ Exported {len(exported)} techniques!")

    else:  # Custom scaffold
        st.markdown("### Build Custom Command")

        col1, col2 = st.columns(2)

        with col1:
            custom_name = st.text_input("Command Name:", "my_custom_technique")
            custom_category = st.text_input("Category:", "Custom")

        with col2:
            custom_use_cases = st.text_input("Use Cases (comma-separated):", "general")

        custom_template = st.text_area(
            "Prompt Template (use {variable} for placeholders):",
            height=300,
            placeholder="""Example:
You are an expert in {domain}.

Task: {task}

Provide:
1. Analysis
2. Recommendations
3. Implementation steps"""
        )

        if st.button("📤 Export Custom Command", type="primary") and custom_template:
            custom_tech = {
                'id': custom_name.lower().replace(' ', '_'),
                'name': custom_name,
                'category': custom_category,
                'template': custom_template,
                'use_cases': [uc.strip() for uc in custom_use_cases.split(',')],
                'evidence': ['Custom'],
                'year': datetime.now().year
            }

            filepath = components['exporter'].export_scaffold(custom_tech, custom_template)
            st.success(f"✅ Exported to: {filepath}")

# === MODE: CHATGPT INSTRUCTIONS ===
elif mode == "📋 ChatGPT Instructions":
    st.subheader("ChatGPT Project Instructions")

    st.markdown("""
    Copy these instructions and paste them into **ChatGPT's Project Instructions** to turn it into
    a prompt engineering optimizer that works just like this app!

    **How to use:**
    1. Copy the instructions below
    2. In ChatGPT, go to your project settings
    3. Paste into "Project Instructions" or "Custom Instructions"
    4. Now ChatGPT will automatically optimize any prompt you give it using research-backed techniques!
    """)

    # Load the instructions file
    instructions_path = Path("chatgpt_project_instructions.md")
    if instructions_path.exists():
        with open(instructions_path, 'r', encoding='utf-8') as f:
            instructions_content = f.read()

        st.text_area(
            "📋 Copy these instructions:",
            value=instructions_content,
            height=500,
            key="chatgpt_instructions"
        )

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download as .md",
                data=instructions_content,
                file_name="chatgpt_prompt_optimizer_instructions.md",
                mime="text/markdown"
            )
        with col2:
            st.info("💡 After pasting, just give ChatGPT any prompt and it will automatically optimize it!")
    else:
        st.error("Instructions file not found. Please ensure chatgpt_project_instructions.md exists.")

# === FOOTER ===
st.divider()
st.caption("Built with Streamlit | Powered by Claude, GPT-4, and Grok | Based on Liu et al. (2021) & Schulhoff et al. (2024)")
