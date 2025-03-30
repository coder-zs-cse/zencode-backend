from app.models.builder_steps import StepStatus, StepType

COMPONENT_FUNCTION_SCHEMA = {
  "type": "function",
  "function": {
    "name": "parse_react_components",
    "description": "Parse React components and extract their properties, use cases, and code samples",
    "parameters": {
      "type": "object",
      "properties": {
        "components": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": {
                "type": "string",
                "description": "Name of the component"
              },
              "description": {
                "type": "string",
                "description": "Detailed description of what the component does"
              },
              "inputProps": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "name": { "type": "string" },
                    "type": { "type": "string" },
                    "description": { "type": "string" },
                    "required": { "type": "boolean" }
                  },
                  "required": ["name", "type", "description", "required"],
                  "additionalProperties": False
                }
              },
              "useCases": {
                "type": "array",
                "items": { "type": "string" },
                "description": "2-3 practical use cases for the component"
              },
              "codeExamples": {
                "type": "array",
                "items": { "type": "string" },
                "description": "2-3 code examples showing different ways to use the component"
              }
            },
            "required": ["name", "description", "inputProps", "useCases", "codeExamples"],
            "additionalProperties": False
          }
        }
      },
      "required": ["components"],
      "additionalProperties": False
    },
    "strict": True
  }
}



# reactBase = '''<ZenCodeArtifact id=\"project-import\" title=\"Project Files\"><ZenCodeAction type=\"file\" filePath=\"eslint.config.js\">import js from '@eslint/js';\nimport globals from 'globals';\nimport reactHooks from 'eslint-plugin-react-hooks';\nimport reactRefresh from 'eslint-plugin-react-refresh';\nimport tseslint from 'typescript-eslint';\n\nexport default tseslint.config(\n  { ignores: ['dist'] },\n  {\n    extends: [js.configs.recommended, ...tseslint.configs.recommended],\n    files: ['**/*.{ts,tsx}'],\n    languageOptions: {\n      ecmaVersion: 2020,\n      globals: globals.browser,\n    },\n    plugins: {\n      'react-hooks': reactHooks,\n      'react-refresh': reactRefresh,\n    },\n    rules: {\n      ...reactHooks.configs.recommended.rules,\n      'react-refresh/only-export-components': [\n        'warn',\n        { allowConstantExport: true },\n      ],\n    },\n  }\n);\n</ZenCodeAction><ZenCodeAction type=\"file\" filePath=\"index.html\"><!doctype html>\n<html lang=\"en\">\n  <head>\n    <meta charset=\"UTF-8\" />\n    <link rel=\"icon\" type=\"image/svg+xml\" href=\"/vite.svg\" />\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n    <title>Vite + React + TS</title>\n  </head>\n  <body>\n    <div id=\"root\"></div>\n    <script type=\"module\" src=\"/src/main.tsx\"></script>\n  </body>\n</html>\n</ZenCodeAction><ZenCodeAction type=\"file\" filePath=\"package.json\">{\n  \"name\": \"vite-react-typescript-starter\",\n  \"private\": true,\n  \"version\": \"0.0.0\",\n  \"type\": \"module\",\n  \"scripts\": {\n    \"dev\": \"vite\",\n    \"build\": \"vite build\",\n    \"lint\": \"eslint .\",\n    \"preview\": \"vite preview\"\n  },\n  \"dependencies\": {\n    \"lucide-react\": \"^0.344.0\",\n    \"react\": \"^18.3.1\",\n    \"react-dom\": \"^18.3.1\"\n  },\n  \"devDependencies\": {\n    \"@eslint/js\": \"^9.9.1\",\n    \"@types/react\": \"^18.3.5\",\n    \"@types/react-dom\": \"^18.3.0\",\n    \"@vitejs/plugin-react\": \"^4.3.1\",\n    \"autoprefixer\": \"^10.4.18\",\n    \"eslint\": \"^9.9.1\",\n    \"eslint-plugin-react-hooks\": \"^5.1.0-rc.0\",\n    \"eslint-plugin-react-refresh\": \"^0.4.11\",\n    \"globals\": \"^15.9.0\",\n    \"postcss\": \"^8.4.35\",\n    \"tailwindcss\": \"^3.4.1\",\n    \"typescript\": \"^5.5.3\",\n    \"typescript-eslint\": \"^8.3.0\",\n    \"vite\": \"^5.4.2\"\n  }\n}\n</ZenCodeAction><ZenCodeAction type=\"file\" filePath=\"postcss.config.js\">export default {\n  plugins: {\n    tailwindcss: {},\n    autoprefixer: {},\n  },\n};\n</ZenCodeAction><ZenCodeAction type=\"file\" filePath=\"tailwind.config.js\">/** @type {import('tailwindcss').Config} */\nexport default {\n  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],\n  theme: {\n    extend: {},\n  },\n  plugins: [],\n};\n</ZenCodeAction><ZenCodeAction type=\"file\" filePath=\"tsconfig.app.json\">{\n  \"compilerOptions\": {\n    \"target\": \"ES2020\",\n    \"useDefineForClassFields\": true,\n    \"lib\": [\"ES2020\", \"DOM\", \"DOM.Iterable\"],\n    \"module\": \"ESNext\",\n    \"skipLibCheck\": true,\n\n    /* Bundler mode */\n    \"moduleResolution\": \"bundler\",\n    \"allowImportingTsExtensions\": true,\n    \"isolatedModules\": true,\n    \"moduleDetection\": \"force\",\n    \"noEmit\": true,\n    \"jsx\": \"react-jsx\",\n\n    /* Linting */\n    \"strict\": true,\n    \"noUnusedLocals\": true,\n    \"noUnusedParameters\": true,\n    \"noFallthroughCasesInSwitch\": true\n  },\n  \"include\": [\"src\"]\n}\n</ZenCodeAction><ZenCodeAction type=\"file\" filePath=\"tsconfig.json\">{\n  \"files\": [],\n  \"references\": [\n    { \"path\": \"./tsconfig.app.json\" },\n    { \"path\": \"./tsconfig.node.json\" }\n  ]\n}\n</ZenCodeAction><ZenCodeAction type=\"file\" filePath=\"tsconfig.node.json\">{\n  \"compilerOptions\": {\n    \"target\": \"ES2022\",\n    \"lib\": [\"ES2023\"],\n    \"module\": \"ESNext\",\n    \"skipLibCheck\": true,\n\n    /* Bundler mode */\n    \"moduleResolution\": \"bundler\",\n    \"allowImportingTsExtensions\": true,\n    \"isolatedModules\": true,\n    \"moduleDetection\": \"force\",\n    \"noEmit\": true,\n\n    /* Linting */\n    \"strict\": true,\n    \"noUnusedLocals\": true,\n    \"noUnusedParameters\": true,\n    \"noFallthroughCasesInSwitch\": true\n  },\n  \"include\": [\"vite.config.ts\"]\n}\n</ZenCodeAction><ZenCodeAction type=\"file\" filePath=\"vite.config.ts\">import { defineConfig } from 'vite';\nimport react from '@vitejs/plugin-react';\n\n// https://vitejs.dev/config/\nexport default defineConfig({\n  plugins: [react()],\n  optimizeDeps: {\n    exclude: ['lucide-react'],\n  },\n});\n</ZenCodeAction><ZenCodeAction type=\"file\" filePath=\"src/App.tsx\">import React from 'react';\n\nfunction App() {\n  return (\n    <div className=\"min-h-screen bg-gray-100 flex items-center justify-center\">\n      <p>Start prompting (or editing) to see magic happen :)</p>\n    </div>\n  );\n}\n\nexport default App;\n</ZenCodeAction><ZenCodeAction type=\"file\" filePath=\"src/index.css\">@tailwind base;\n@tailwind components;\n@tailwind utilities;\n</ZenCodeAction><ZenCodeAction type=\"file\" filePath=\"src/main.tsx\">import { StrictMode } from 'react';\nimport { createRoot } from 'react-dom/client';\nimport App from './App.tsx';\nimport './index.css';\n\ncreateRoot(document.getElementById('root')!).render(\n  <StrictMode>\n    <App />\n  </StrictMode>\n);\n</ZenCodeAction><ZenCodeAction type=\"file\" filePath=\"src/vite-env.d.ts\">/// <reference types=\"vite/client\" />\n</ZenCodeAction></ZenCodeArtifact>'''

# JSON structure for React base template

reactBasejson = [
  {
    "id": 1,
    "title": "Creating file eslint.config.js",
    "description": "",
    "type": StepType.CreateFile.value,
    "status": StepStatus.PENDING.value,
    "content": "import js from '@eslint/js';\nimport globals from 'globals';\nimport reactHooks from 'eslint-plugin-react-hooks';\nimport reactRefresh from 'eslint-plugin-react-refresh';\nimport tseslint from 'typescript-eslint';\n\nexport default tseslint.config(\n  { ignores: ['dist'] },\n  {\n    extends: [js.configs.recommended, ...tseslint.configs.recommended],\n    files: ['**/*.{ts,tsx}'],\n    languageOptions: {\n      ecmaVersion: 2020,\n      globals: globals.browser,\n    },\n    plugins: {\n      'react-hooks': reactHooks,\n      'react-refresh': reactRefresh,\n    },\n    rules: {\n      ...reactHooks.configs.recommended.rules,\n      'react-refresh/only-export-components': [\n        'warn',\n        { allowConstantExport: true },\n      ],\n    },\n  }\n);\n",
    "path": "eslint.config.js"
  },
  {
    "id": 2,
    "title": "Creating file index.html",
    "description": "",
    "type": StepType.CreateFile.value,
    "status": StepStatus.PENDING.value,
    "content": "<!doctype html>\n<html lang=\"en\">\n  <head>\n    <meta charset=\"UTF-8\" />\n    <link rel=\"icon\" type=\"image/svg+xml\" href=\"/vite.svg\" />\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n    <title>Vite + React + TS</title>\n  </head>\n  <body>\n    <div id=\"root\"></div>\n    <script type=\"module\" src=\"/src/main.tsx\"></script>\n  </body>\n</html>\n",
    "path": "index.html"
  },
  {
    "id": 3,
    "title": "Creating file package.json",
    "description": "",
    "type": StepType.CreateFile.value,
    "status": StepStatus.PENDING.value,
    "content": "{\n  \"name\": \"vite-react-typescript-starter\",\n  \"private\": true,\n  \"version\": \"0.0.0\",\n  \"type\": \"module\",\n  \"scripts\": {\n    \"dev\": \"vite\",\n    \"build\": \"vite build\",\n    \"lint\": \"eslint .\",\n    \"preview\": \"vite preview\"\n  },\n  \"dependencies\": {\n    \"lucide-react\": \"^0.344.0\",\n    \"react\": \"^18.3.1\",\n    \"react-dom\": \"^18.3.1\"\n  },\n  \"devDependencies\": {\n    \"@eslint/js\": \"^9.9.1\",\n    \"@types/react\": \"^18.3.5\",\n    \"@types/react-dom\": \"^18.3.0\",\n    \"@vitejs/plugin-react\": \"^4.3.1\",\n    \"autoprefixer\": \"^10.4.18\",\n    \"eslint\": \"^9.9.1\",\n    \"eslint-plugin-react-hooks\": \"^5.1.0-rc.0\",\n    \"eslint-plugin-react-refresh\": \"^0.4.11\",\n    \"globals\": \"^15.9.0\",\n    \"postcss\": \"^8.4.35\",\n    \"tailwindcss\": \"^3.4.1\",\n    \"typescript\": \"^5.5.3\",\n    \"typescript-eslint\": \"^8.3.0\",\n    \"vite\": \"^5.4.2\"\n  }\n}",
    "path": "package.json"
  },
  {
    "id": 4,
    "title": "Creating file postcss.config.js",
    "description": "",
    "type": StepType.CreateFile.value,
    "status": StepStatus.PENDING.value,
    "content": "export default {\n  plugins: {\n    tailwindcss: {},\n    autoprefixer: {},\n  },\n};",
    "path": "postcss.config.js"
  },
  {
    "id": 5,
    "title": "Creating file tailwind.config.js",
    "description": "",
    "type": StepType.CreateFile.value,
    "status": StepStatus.PENDING.value,
    "content": "/** @type {import('tailwindcss').Config} */\nexport default {\n  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],\n  darkMode: 'class',\n  theme: {\n    extend: {\n      colors: {\n        gray: {\n          900: '#111827',\n          800: '#1F2937',\n          700: '#374151',\n          600: '#4B5563',\n          500: '#6B7280',\n          400: '#9CA3AF',\n          300: '#D1D5DB',\n          200: '#E5E7EB',\n          100: '#F3F4F6',\n        },\n      },\n    },\n  },\n  plugins: [],\n};",
    "path": "tailwind.config.js"
  },
  {
    "id": 6,
    "title": "Creating file tsconfig.app.json",
    "description": "",
    "type": StepType.CreateFile.value,
    "status": StepStatus.PENDING.value,
    "content": "{\n  \"compilerOptions\": {\n    \"target\": \"ES2020\",\n    \"useDefineForClassFields\": true,\n    \"lib\": [\"ES2020\", \"DOM\", \"DOM.Iterable\"],\n    \"module\": \"ESNext\",\n    \"skipLibCheck\": true,\n\n    /* Bundler mode */\n    \"moduleResolution\": \"bundler\",\n    \"allowImportingTsExtensions\": true,\n    \"isolatedModules\": true,\n    \"moduleDetection\": \"force\",\n    \"noEmit\": true,\n    \"jsx\": \"react-jsx\",\n\n    /* Linting */\n    \"strict\": true,\n    \"noUnusedLocals\": true,\n    \"noUnusedParameters\": true,\n    \"noFallthroughCasesInSwitch\": true\n  },\n  \"include\": [\"src\"]\n}",
    "path": "tsconfig.app.json"
  },
  {
    "id": 7,
    "title": "Creating file tsconfig.json",
    "description": "",
    "type": StepType.CreateFile.value,
    "status": StepStatus.PENDING.value,
    "content": "{\n  \"files\": [],\n  \"references\": [\n    { \"path\": \"./tsconfig.app.json\" },\n    { \"path\": \"./tsconfig.node.json\" }\n  ]\n}",
    "path": "tsconfig.json"
  },
  {
    "id": 8,
    "title": "Creating file tsconfig.node.json",
    "description": "",
    "type": StepType.CreateFile.value,
    "status": StepStatus.PENDING.value,
    "content": "{\n  \"compilerOptions\": {\n    \"target\": \"ES2022\",\n    \"lib\": [\"ES2023\"],\n    \"module\": \"ESNext\",\n    \"skipLibCheck\": true,\n\n    /* Bundler mode */\n    \"moduleResolution\": \"bundler\",\n    \"allowImportingTsExtensions\": true,\n    \"isolatedModules\": true,\n    \"moduleDetection\": \"force\",\n    \"noEmit\": true,\n\n    /* Linting */\n    \"strict\": true,\n    \"noUnusedLocals\": true,\n    \"noUnusedParameters\": true,\n    \"noFallthroughCasesInSwitch\": true\n  },\n  \"include\": [\"vite.config.ts\"]\n}",
    "path": "tsconfig.node.json"
  },
  {
    "id": 9,
    "title": "Creating file vite.config.ts",
    "description": "",
    "type": StepType.CreateFile.value,
    "status": StepStatus.PENDING.value,
    "content": "import { defineConfig } from 'vite';\nimport react from '@vitejs/plugin-react';\n\n// https://vitejs.dev/config/\nexport default defineConfig({\n  plugins: [react()],\n  optimizeDeps: {\n    exclude: ['lucide-react'],\n  },\n});",
    "path": "vite.config.ts"
  },
  {
    "id": 10,
    "title": "Creating file src/App.tsx",
    "description": "",
    "type": StepType.CreateFile.value,
    "status": StepStatus.PENDING.value,
    "content": "import React from 'react';\nimport { TodoList } from './components/TodoList';\nimport { ThemeToggle } from './components/ThemeToggle';\n\nfunction App() {\n  return (\n    <div className=\"min-h-screen bg-gray-100 dark:bg-gray-900 transition-colors duration-200\">\n      <div className=\"container mx-auto px-4 py-12 flex flex-col items-center\">\n        <ThemeToggle />\n        <h1 className=\"text-3xl font-bold mb-8 text-gray-800 dark:text-gray-100\">\n          Todo App\n        </h1>\n        <TodoList />\n      </div>\n    </div>\n  );\n}\n\nexport default App;",
    "path": "src/App.tsx"
  },
  {
    "id": 11,
    "title": "Creating file src/index.css",
    "description": "",
    "type": StepType.CreateFile.value,
    "status": StepStatus.PENDING.value,
    "content": "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n\n@layer base {\n  body {\n    @apply text-gray-900 dark:text-gray-100;\n  }\n}",
    "path": "src/index.css"
  },
  {
    "id": 12,
    "title": "Creating file src/main.tsx",
    "description": "",
    "type": StepType.CreateFile.value,
    "status": StepStatus.PENDING.value,
    "content": "import { StrictMode } from 'react';\nimport { createRoot } from 'react-dom/client';\nimport App from './App.tsx';\nimport './index.css';\n\ncreateRoot(document.getElementById('root')!).render(\n  <StrictMode>\n    <App />\n  </StrictMode>\n);",
    "path": "src/main.tsx"
  },
  {
    "id": 13,
    "title": "Creating file src/vite-env.d.ts",
    "description": "",
    "type": StepType.CreateFile.value,
    "status": StepStatus.PENDING.value,
    "content": "/// <reference types=\"vite/client\" />",
    "path": "src/vite-env.d.ts"
  },
  {
    "id": 14,
    "title": "Creating file src/components/TodoList.tsx",
    "description": "",
    "type": StepType.CreateFile.value,
    "status": StepStatus.PENDING.value,
    "content": "import { useState } from 'react';\nimport { Button } from '../components/ui/Button/Button';\nimport { Checkbox } from '../components/ui/Checkbox/Checkbox';\n\ntype Todo = {\n  id: string;\n  text: string;\n  completed: boolean;\n};\n\nexport function TodoList() {\n  const [todos, setTodos] = useState<Todo[]>([]);\n  const [inputValue, setInputValue] = useState('');\n\n  const addTodo = () => {\n    if (inputValue.trim()) {\n      setTodos([\n        ...todos,\n        {\n          id: Date.now().toString(),\n          text: inputValue,\n          completed: false,\n        },\n      ]);\n      setInputValue('');\n    }\n  };\n\n  const toggleTodo = (id: string) => {\n    setTodos(\n      todos.map((todo) =>\n        todo.id === id ? { ...todo, completed: !todo.completed } : todo\n      )\n    );\n  };\n\n  const deleteTodo = (id: string) => {\n    setTodos(todos.filter((todo) => todo.id !== id));\n  };\n\n  return (\n    <div className=\"w-full max-w-md\">\n      <div className=\"flex gap-2 mb-6\">\n        <input\n          type=\"text\"\n          value={inputValue}\n          onChange={(e) => setInputValue(e.target.value)}\n          onKeyDown={(e) => e.key === 'Enter' && addTodo()}\n          placeholder=\"Add a new task\"\n          className=\"flex-1 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500\"\n        />\n        <Button variant=\"primary\" onClick={addTodo}>\n          Add\n        </Button>\n      </div>\n\n      <div className=\"space-y-2\">\n        {todos.length === 0 ? (\n          <p className=\"text-center text-gray-500 dark:text-gray-400\">\n            No tasks yet. Add one above!\n          </p>\n        ) : (\n          todos.map((todo) => (\n            <div\n              key={todo.id}\n              className=\"flex items-center justify-between p-3 rounded-lg bg-white dark:bg-gray-800 shadow-sm dark:shadow-gray-700\"\n            >\n              <div className=\"flex items-center gap-3\">\n                <Checkbox\n                  checked={todo.completed}\n                  onChange={() => toggleTodo(todo.id)}\n                  className=\"h-5 w-5\"\n                />\n                <span\n                  className={`${todo.completed ? 'line-through text-gray-400 dark:text-gray-500' : 'text-gray-800 dark:text-gray-200'}`}\n                >\n                  {todo.text}\n                </span>\n              </div>\n              <Button\n                variant=\"ghost\"\n                size=\"sm\"\n                onClick={() => deleteTodo(todo.id)}\n                className=\"text-red-500 hover:text-red-700 dark:hover:text-red-400\"\n              >\n                Delete\n              </Button>\n            </div>\n          ))\n        )}\n      </div>\n    </div>\n  );\n}",
    "path": "src/components/TodoList.tsx"
  },
  {
    "id": 15,
    "title": "Creating file src/components/ThemeToggle.tsx",
    "description": "",
    "type": StepType.CreateFile.value,
    "status": StepStatus.PENDING.value,
    "content": "import { useState, useEffect } from 'react';\nimport { Button } from '../components/ui/Button/Button';\nimport { Sun, Moon } from 'lucide-react';\n\nexport function ThemeToggle() {\n  const [darkMode, setDarkMode] = useState(false);\n\n  useEffect(() => {\n    const isDark = localStorage.getItem('darkMode') === 'true';\n    setDarkMode(isDark);\n    document.documentElement.classList.toggle('dark', isDark);\n  }, []);\n\n  const toggleTheme = () => {\n    const newMode = !darkMode;\n    setDarkMode(newMode);\n    localStorage.setItem('darkMode', String(newMode));\n    document.documentElement.classList.toggle('dark', newMode);\n  };\n\n  return (\n    <Button\n      variant=\"ghost\"\n      size=\"icon\"\n      onClick={toggleTheme}\n      className=\"absolute top-4 right-4\"\n      aria-label=\"Toggle dark mode\"\n    >\n      {darkMode ? <Sun className=\"h-5 w-5\" /> : <Moon className=\"h-5 w-5\" />}\n    </Button>\n  );\n}",
    "path": "src/components/ThemeToggle.tsx"
  }
]