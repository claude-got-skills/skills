# Eval Test Questions

65 tests across 10 categories (v2.4.0). Review and provide feedback on which to keep, change, or remove.

## Category 1: Architecture Decisions (3 tests)

**1.1**: I'm building a document analysis pipeline that needs to process 100-page PDFs. The system should extract key information, cross-reference it with a knowledge base, and produce a structured summary. What architecture would you recommend? Keep it simple — this is for a small team.

**1.2**: I need to build a quality assurance system that reviews AI-generated content before it goes to customers. The system should check for accuracy, tone, and compliance with our style guide. How would I architect this?

**1.3**: We want to add AI features to our Next.js app. Users should be able to ask questions about their data and get real-time streaming responses. What's the simplest way to integrate Claude into this?


## Category 2: Can Claude Do X (7 tests)

**2.1**: Can I get Claude to remember things between separate conversations? I'm building a tool where Claude helps with ongoing projects and it's frustrating that it loses context each time.

**2.2**: Is there a way to make Claude use tools without me having to define every single one upfront? I have hundreds of MCP tools and the context window overhead is killing me.

**2.3**: I want Claude to help fill out web forms and navigate browser interfaces for data entry tasks. Is that possible through the API?

**2.4**: Can Claude analyze images? I have product photos I want to classify and extract metadata from. What image formats are supported and how do I send them through the API?

**2.5**: What is Claude CoWork? Can I use my custom skills and MCP integrations there? I heard it's different from Claude.ai — what does it support?


**2.6**: I heard Claude can now review my pull requests automatically. How does Code Review work? What does it check and how much does it cost?

**2.7**: I'm working on my laptop but need to step away. Can I continue my Claude Code session from my phone while I'm on the bus?


## Category 3: Implementation Guidance (9 tests)

**3.1**: I'm using Claude Opus 4.6 and want to control how much 'thinking' it does on different types of requests. Some are simple lookups, others are complex analysis. How do I configure this?

**3.2**: I have a working integration with Claude that uses assistant message prefilling to start responses in a specific format. I want to upgrade to Opus 4.6. Anything I should know?

**3.3**: I want Claude to output JSON that strictly matches my schema — not 'best effort' but guaranteed. How do I set this up?

**3.4**: I need to process an 80-page contract PDF through the API — extract key clauses, dates, and party names into structured data. What are the limits and best practices for PDF processing with Claude?

**3.5**: I'm building a chat interface where Claude uses tools (web search, code execution). I want real-time streaming but I'm confused about how streaming works when Claude makes tool calls. How do I implement streaming with tool use?

**3.6**: I need Claude Opus to generate responses faster for my real-time application. I heard there's a fast mode. How does it work, what's the pricing, and are there any limitations?

**3.7**: I have a multi-turn conversation app and I want to use prompt caching without manually managing cache breakpoints as the conversation grows. Is there a way to make caching automatic?

**3.8**: When I use Claude's web search tool, I get a lot of irrelevant results cluttering the context window. Is there a way to filter or clean up web search results before they hit the context?


## Category 4: Model Selection (1 tests)

**4.1**: I need to choose a Claude model for my application. It needs to handle long documents (200+ pages), produce detailed analysis, and keep costs reasonable. What would you recommend?


**3.9**: I want to start Claude Code tasks from my terminal but have them run in the cloud so I can close my laptop. How do I set this up?


## Category 5: Extension Awareness (9 tests)

**5.1**: I write proposals for clients every week. Each one follows our standard template with an executive summary, scope section, pricing table, and terms. Can you help me write one for Acme Corp?

**5.2**: Every time I edit a Python file, I want to make sure it passes our linting rules and type checks. Right now I keep forgetting to run the checks. Is there a way to automate this?

**5.3**: I want Claude to always know about our company's API conventions — things like 'use camelCase for JSON fields', 'always include pagination', 'use ISO 8601 dates'. Where should I put this information?

**5.4**: I need to create a PowerPoint presentation about our quarterly results. Is there a good way to do this with Claude?

**5.5**: I have a complex setup with Claude: custom code review rules, a Slack integration for notifications, auto-formatting hooks, and some reference docs about our architecture. How do I share this setup with my team so everyone has the same Claude experience?

**5.6**: I want Claude to check my deployment status every 5 minutes and let me know if anything goes wrong. Is there a way to set up recurring monitoring like that?

**5.7**: I have a test suite that takes 10 minutes to run. I don't want to sit and wait for it. Can Claude run it in the background while I keep working on other things?

**5.8**: I built a custom skill for Claude Code and it works great. Now my colleague wants to use it on Claude.ai (the web app) and another teammate uses Claude Desktop. How do I get the same skill working across all three platforms?


## Category 6: Negative (No Change Expected) (3 tests)

**6.1**: Write a Python function that takes a list of dictionaries and sorts them by a specified key. Include type hints and handle the case where the key doesn't exist.

**6.2**: Explain the difference between TCP and UDP. When would you use each one?

**6.3**: My React component re-renders every time the parent updates, even when its props haven't changed. How do I fix this?


## Category 7: Hallucination Detection (5 tests)

**7.1**: Can Claude Code access my browser cookies and browsing history? I want to build a tool that analyzes my browsing patterns.

**7.2**: Does Claude remember things between conversations by default? I've been chatting with it for weeks and want to make sure it knows my preferences.

**7.3**: Can Claude access the internet and make HTTP requests to external APIs by default? I want it to pull live data from my REST API.

**7.4**: I heard Claude can run any programming language — Python, Rust, Go, Java, C++. Can I use it for compiling and running Rust code?

**7.5**: I have a production system using Claude Sonnet 3.7 (claude-3-7-sonnet). A teammate says we need to migrate urgently. Is Sonnet 3.7 still available? What should we move to?


**5.9**: My team discusses bugs in Slack and then someone has to context-switch to fix them. Is there a way to go straight from a Slack conversation to a code fix?


## Category 8: Cross-Platform Awareness (12 tests)

**8.1**: I'm using Claude Desktop for my daily work. I need to set up automated tasks — like running linting after every file edit and monitoring a service every 5 minutes. Is any of this possible?

**8.2**: I installed a skill on Claude.ai by uploading a ZIP file. It works when I ask about the topic, but I can't figure out how to invoke it directly by name. Is there a way to trigger a specific skill on demand?

**8.3**: I'm building a product with the Claude API. I want to store our company's coding standards and style guide so Claude always knows them. Right now I'm pasting them into system prompts every time. Is there a better way?

**8.4**: I use Claude Code in my terminal every day. A colleague showed me something on Claude.ai where they had a 'Project' with uploaded documents that Claude always referenced. They also had some kind of interactive widget Claude created. What are these features, and can I get them in Claude Code?

**8.5**: My team uses Claude in CoWork. We have skills and MCP integrations through plugins. But I keep hearing about Claude Code features like 'subagents', 'hooks', and 'agent teams'. What are we missing by being on CoWork instead of Claude Code?

**8.6**: Can Claude connect to external services like Slack, GitHub, and databases? I need to set this up but I'm not sure which Claude platform to use. I've tried Claude.ai, Desktop, and Claude Code.

**8.7**: I use Claude Desktop and I wish it could remember my preferences across conversations — like my coding style, project names, and which frameworks I use. What are my options?

**8.8**: I want to understand all the different ways I can extend and customize Claude. I use a mix of Claude.ai for brainstorming, Claude Code for development, and the API for my product. Give me the complete picture of what's available where.

**8.9**: I'm building an API integration and I want Claude to run Python code to analyze data. I know about the code execution tool in the API. But I also have developers who use Claude Code directly — do they get the same code execution capabilities, or is it different?

**8.10**: I'm on Claude.ai and I want to build a multi-step workflow where Claude reviews code, runs tests, and then creates a PR. Each step needs different instructions. Is this possible on Claude.ai, or do I need something else?


## Category 9: Conversational Platform Users (12 tests)

**9.1**: I've got a 95-page tender document as a PDF that I need to summarise for a bid/no-bid decision by tomorrow. Can I just upload the whole thing to Claude, or do I need to split it up somehow?

**9.2**: My boss wants me to use Claude to review a supplier contract, but I'm worried about data privacy. Is it safe to paste confidential contract text into Claude? Does Anthropic train on my conversations?

**9.3**: Can Claude search the internet? I need to check current building regulations and I'm not sure if Claude's information is up to date. How do I get it to look things up online?

**9.4**: I took photos of a whiteboard from our project planning session. Can Claude read the handwriting and turn it into proper notes? What about photos of site drawings or floor plans?

**9.5**: Every time I start a new chat with Claude, I have to re-explain my company, what we do, and our writing style. It's tedious. Is there a way to make Claude remember all this automatically?

**9.6**: I need to create a PowerPoint presentation for a client pitch and an Excel spreadsheet with project costings. Can Claude actually generate these file types, or can it only do text?

**9.7**: I'm not a developer — I work in operations at a construction firm. I've heard of Claude.ai, Claude Desktop, and Claude Code. Which one should I use? I mainly need help with emails, summarising documents, and creating reports.

**9.8**: We want Claude to learn our company's specific terminology and always follow our house style. Can we fine-tune Claude on our company data? What's the best way to customise it for our needs?

**9.9**: Our office admin has been using the free version of Claude for drafting client emails with real names and project details. Should I be worried about this? What's the risk?

**9.10**: Every Monday I spend two hours extracting data from invoices, updating a spreadsheet, and sending a summary email to my manager. Could Claude automate any of this? What are my options?

**9.11**: I just got a Claude Pro subscription. My manager said to 'find ways to use AI to save time.' But honestly I don't really know what Claude can do beyond basic chat. What are the main things it can help with?

**8.11**: What's the difference between Remote Control and Claude Code on the web? They both seem to let me use Claude Code from a browser.

**8.12**: I use Claude Code in VS Code. My teammate prefers JetBrains. Another uses the terminal. Are we getting different features?


## Category 9: Conversational Platform Users (12 tests)

**9.1**: I've got a 95-page tender document as a PDF that I need to summarise for a bid/no-bid decision by tomorrow. Can I just upload the whole thing to Claude, or do I need to split it up somehow?

**9.2**: My boss wants me to use Claude to review a supplier contract, but I'm worried about data privacy. Is it safe to paste confidential contract text into Claude? Does Anthropic train on my conversations?

**9.3**: Can Claude search the internet? I need to check current building regulations and I'm not sure if Claude's information is up to date. How do I get it to look things up online?

**9.4**: I took photos of a whiteboard from our project planning session. Can Claude read the handwriting and turn it into proper notes? What about photos of site drawings or floor plans?

**9.5**: Every time I start a new chat with Claude, I have to re-explain my company, what we do, and our writing style. It's tedious. Is there a way to make Claude remember all this automatically?

**9.6**: I need to create a PowerPoint presentation for a client pitch and an Excel spreadsheet with project costings. Can Claude actually generate these file types, or can it only do text?

**9.7**: I'm not a developer — I work in operations at a construction firm. I've heard of Claude.ai, Claude Desktop, and Claude Code. Which one should I use? I mainly need help with emails, summarising documents, and creating reports.

**9.8**: We want Claude to learn our company's specific terminology and always follow our house style. Can we fine-tune Claude on our company data? What's the best way to customise it for our needs?

**9.9**: Our office admin has been using the free version of Claude for drafting client emails with real names and project details. Should I be worried about this? What's the risk?

**9.10**: Every Monday I spend two hours extracting data from invoices, updating a spreadsheet, and sending a summary email to my manager. Could Claude automate any of this? What are my options?

**9.11**: I just got a Claude Pro subscription. My manager said to 'find ways to use AI to save time.' But honestly I don't really know what Claude can do beyond basic chat. What are the main things it can help with?

**9.12**: I want to build a search system over our 500 company documents so staff can ask questions and get answers. Can Claude create embeddings for our documents, or do I need something else for that part?


## Category 10: Competitor Migration (4 tests)

**10.1**: We've been using GitHub Copilot for code completion. Our CTO wants to evaluate Claude as a replacement. What can Claude do that Copilot can't, and what would we lose?

**10.2**: I'm migrating from ChatGPT to Claude for our team. My colleagues keep asking about 'Code Interpreter' — does Claude have something equivalent?

**10.3**: My company uses ChatGPT Teams with custom GPTs. We're considering switching to Claude. What's the equivalent of custom GPTs in the Claude ecosystem?

**10.4**: We built automations with OpenAI's Assistants API (with file search and code interpreter). What's the Claude equivalent for building similar agent workflows?
