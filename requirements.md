# Requirements - AI Task Manager 

## 1. Functional Requirements 
- Users are able to add tasks with a due date and description.
- User can view, edit, delete, and check off tasks as done
- System can assign a priority score 
- Based off usage, system recommends productivity improvements 
    or points out more productive time of day
- Students can rank importance if needed.  
- System calculates priority score based on user assigned score (if any), due date, and estimated daily time. 
- System displays tasks in order of importance. 
- System generates rule-based productivity recommendations based on daily workload, missed days, and productivity hours. 
- Tasks persist between sessions 
- User can request AI-generated insights 
- If local LLM unavailable, the system displays setup instructions and falls back to rule-based recommendations. 

## 2. Non-functional requirements 
- **Usability:** New user should be able to add a task wtih little to no instructions. 
- **Performance:** Task list and rule-based recommendations load within a few seconds. 
- **Responsiveness:**  Interface remains usable while AI insights are being generated. 
- **Reliability:** Invalid input generates an error rather than crashing. 
- **Maintainability:** Code is modularized, for data, storage, prioritization, and recommendations. 
- **Portability:** Distributed as a standalone Windows executable; no Python installation required.
- **Cost & Privacy:** The application incurs no API costs, and task data never leaves the user's computer.

## 3. Assumptions
- Single user, local only, Windows target. 
- AI insights require Ollama installed locally with the llama3.2:3b model

## 4. Project Scope 
- **Project Objective:** Create a working AI task manager to help manage daily work load in a way that still allows for enjoyable downtime. 
- **Deliverables:** A working installable for the AI Task Manager. 
- **Constraints:** AI insights require Ollama installed locally with the llama3.2:3b model. Executable is not code-signed; Windows SmartScreen may warn on first run