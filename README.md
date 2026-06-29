# Lead Intel Agent

Lead Intel Agent is an AI-powered B2B Sales Intelligence application designed to automate the process of researching target companies and crafting highly personalized cold outreach emails. Built with a modern, glassmorphism dark-themed UI, this tool acts as your personal research analyst and copywriter.

## Features

- **Deep-Dive Company Research:** Enter a company name and target industry to instantly gather recent news, strategic initiatives, and market positioning data using the Tavily Search API.
- **AI-Synthesized Insights:** Uses Google's Gemini models to distill complex web data into actionable Key Findings, Pain Points, and Recent Developments.
- **Automated Copywriting:** Drafts personalized, value-driven cold emails tailored to a specific target role (e.g., CEO, CTO) based directly on the gathered research.
- **Direct SMTP Integration:** Send the AI-crafted emails directly to the recipient right from the web dashboard using your own email account.
- **Beautiful UI:** A responsive, dark-mode web dashboard that renders insights in beautiful Markdown.
- **Session History:** Automatically saves your past research sessions to a local SQLite database for easy retrieval.

## Technology Stack

- **Backend:** Python, Flask, SQLite
- **AI/LLM:** LangChain, Google Gemini API (`gemini-2.5-flash`)
- **Search:** Tavily Search API
- **Frontend:** HTML, Vanilla CSS, Vanilla JavaScript, marked.js

## Prerequisites

Before you begin, ensure you have the following API keys and credentials:
- **Google Gemini API Key:** Get one from [Google AI Studio](https://aistudio.google.com/app/apikey)
- **Tavily API Key:** Get one from [Tavily](https://tavily.com/)
- **SMTP Credentials:** For sending emails (e.g., a Google App Password)

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd lead_intel_agent
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the root directory (or use the provided `.env.example`) and add your API keys:
   ```env
   # API Keys
   GEMINI_API_KEY=your_gemini_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here

   # SMTP Settings (For sending emails)
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your.email@gmail.com
   SMTP_PASSWORD=your_app_password_here
   SMTP_FROM_EMAIL=your.email@gmail.com
   ```

5. **Run the Application**
   ```bash
   python src/server.py
   ```
   Open your browser and navigate to `http://127.0.0.1:8501`.

## Usage

1. Enter the target company name and industry on the dashboard.
2. Click **Run Intelligence Scan** and wait for the AI to gather and synthesize the data.
3. Review the Key Notes and Research Summary.
4. Specify the target role (e.g., "VP of Sales") and click **Generate Email**.
5. Provide a recipient email address and click **Send Now** to dispatch the email via your configured SMTP server.

## License
MIT License
