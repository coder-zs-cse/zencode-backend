﻿# **Zencode AI**

🚀 Zencode AI - 
V0 Clone that Transform Ideas into Website—Locked to Your Design Standards. **The Perfect Enterprise level requirements!!**

### 🌟 Why Zencode AI?
Tired of AI tools that ignore your design system? Zencode AI is V0’s disciplined cousin—it generates UI code that strictly uses your pre-approved components, colors, and npm packages.

✅ For Teams Who Care About Brand Consistency <br>
✅ No More "Oops, That’s Not Our Button" Moments <br>
✅ No More "Uggh, why is the code generator using lucide react for icons" Moments <br>

🔥 USP at a Glance
🛠️ Configure Your Design DNA
- Drop a GitHub URL? Boom—your components are now the only ones allowed.
- Enforce brand colors, approved npm packages, and internal React components
- Update standards once, propagate everywhere

🔒 Code Generation with Guardrails
AI that actually follows the rules:
- RAG pipeline restricts outputs to your design system
- Generates code with your Button.tsx, your theme.css—not random alternatives

## Main Features

1. Code Editor in frontend
2. Restriction of generated React code as per enterprise library standards.
3. Live Preview of generated code.
4. One-Click Export <br>
> the legend said yes, it’s instant

# 🛠️ **Tech Stack**

This project was crafted using the following tools and technologies:

**[Frontend](https://github.com/coder-zs-cse/zencode-frontend)**: Next.js, WebContainer <br>

**[Data Backend](https://github.com/coder-zs-cse/zencode-nodejs)**: Node.js, MongoDB <br>

**[LLM Backend](https://github.com/coder-zs-cse/zencode-backend)**: FastAPI, Pinecone, OpenAI <br> 

---

# 📦 **Setup & Installation**


Follow these steps to set up the project locally:

1. **Clone the repository** (if applicable):

   ```bash
   git clone https://github.com/coder-zs-cse/zencode-backend.git
   
   cd zencode-backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the FastAPI application**:
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access the API**:
   Open your web browser and go to `http://127.0.0.1:8000` to see the response.

---
# **Architecture Diagram :**

## Ingestion Phase
<img width="866" alt="Screenshot 2025-04-05 at 10 22 51 PM" src="https://github.com/user-attachments/assets/1208b337-7148-451b-9b65-c2db30dbbf96" />

## Query Phase
<img width="863" alt="Screenshot 2025-04-05 at 10 23 07 PM" src="https://github.com/user-attachments/assets/859f426c-ce69-4906-8700-51a6e02df245" />

---
# 🤝 **Team & Contributions**:
This project was brought to life by: Goemkars

[Zubin Shah](http://github.com/coder-zs-cse/)

[Niranjan Hebli](https://github.com/NiranjanHebli)

[Bryson Gracias](https://github.com/MrGladiator14)

---

# 🌟 **Acknowledgments**:

 We extend our heartfelt gratitude to:

- Oraczen for organizing such an inspiring and challenging event.
- The countless contributors to open-source libraries and tools that powered this project.
