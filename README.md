# Chaotic Leads CRM

Fully functioning CRM for cold-calling with agents, leads, notes, statuses, and point tracking.

## Files
- app.py: Main interface (Streamlit)
- leads.py: Loads/saves global leads
- agents.py: Loads agent list
- user.py: Saves session data
- global_leads.json: Stores all leads
- agentname_data.json: Agent list
- user.json: Tracks agent progress
- requirements.txt: Dependencies

## Run
pip install -r requirements.txt  
streamlit run app.py