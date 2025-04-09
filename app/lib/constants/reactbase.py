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
     "id": 0,
     "title": "Initalizing a React Template Project",
     "description": "",
     "type": StepType.TextDisplay.value,
     "status": StepStatus.PENDING.value,
     "content": "Let's start with a initial project setup for React.js",
     "path": ""
   },
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
     "content": "/** @type {import('tailwindcss').Config} */\nexport default {\n  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],\n  theme: {\n    extend: {},\n  },\n  plugins: [],\n};",
     "path": "tailwind.config.js"
   },
   {
     "id": 6,
     "title": "Creating file tsconfig.json",
     "description": "",
     "type": StepType.CreateFile.value,
     "status": StepStatus.PENDING.value,
     "content": "{\n\t\"compilerOptions\": {\n\t\t\"target\": \"ES2020\",\n\t\t\"module\": \"ESNext\",\n\t\t\"lib\": [\"ES2020\", \"DOM\", \"DOM.Iterable\"],\n\t\t\"jsx\": \"react-jsx\",\n\t\t\"skipLibCheck\": true,\n\t\t\"moduleResolution\": \"bundler\",\n\t\t\"allowImportingTsExtensions\": true,\n\t\t\"isolatedModules\": true,\n\t\t\"noEmit\": true,\n\t\t\"strict\": true,\n\t\t\"baseUrl\": \".\",\n\t\t\"paths\": {\n\t\t\t\"@/*\": [\"./src/*\"]\n\t\t},\n\t\t\"noUnusedLocals\": true,\n\t\t\"noUnusedParameters\": true,\n\t\t\"noFallthroughCasesInSwitch\": true,\n\t\t\"moduleDetection\": \"force\"\n\t},\n\t\"include\": [\"src\", \"vite.config.ts\"]\n}",
     "path": "tsconfig.json"
   },
   {
     "id": 7,
     "title": "Creating file vite.config.ts",
     "description": "",
     "type": StepType.CreateFile.value,
     "status": StepStatus.PENDING.value,
     "content": "import { defineConfig } from 'vite';\nimport react from '@vitejs/plugin-react';\n\n// https://vitejs.dev/config/\nexport default defineConfig({\n  plugins: [react()],\n  resolve: {\n    alias: {\n      '@': '/src'\n    }\n  },\n  optimizeDeps: {\n    exclude: ['lucide-react'],\n  },\n});",
     "path": "vite.config.ts"
   },
   {
     "id": 8,
     "title": "Creating file src/App.tsx",
     "description": "",
     "type": StepType.CreateFile.value,
     "status": StepStatus.PENDING.value,
     "content": "import React from 'react';\n\nfunction App() {\n  return (\n    <div className=\"min-h-screen bg-gray-100 flex items-center justify-center\">\n      <p>Start prompting (or editing) to see magic happen :)</p>\n    </div>\n  );\n}\n\nexport default App;",
     "path": "src/App.tsx"
   },
   {
     "id": 9,
     "title": "Creating file src/index.css",
     "description": "",
     "type": StepType.CreateFile.value,
     "status": StepStatus.PENDING.value,
     "content": "@tailwind base;\n@tailwind components;\n@tailwind utilities;",
     "path": "src/index.css"
   },
   {
     "id": 10,
     "title": "Creating file src/main.tsx",
     "description": "",
     "type": StepType.CreateFile.value,
     "status": StepStatus.PENDING.value,
     "content": "import { StrictMode } from 'react';\nimport { createRoot } from 'react-dom/client';\nimport App from './App.tsx';\nimport './index.css';\n\ncreateRoot(document.getElementById('root')!).render(\n  <StrictMode>\n    <App />\n  </StrictMode>\n);",
     "path": "src/main.tsx"
   },
   {
     "id": 11,
     "title": "Creating file src/vite-env.d.ts",
     "description": "",
     "type": StepType.CreateFile.value,
     "status": StepStatus.PENDING.value,
     "content": "/// <reference types=\"vite/client\" />",
     "path": "src/vite-env.d.ts"
   }
]