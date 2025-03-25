from typing import TypedDict, List
from app.services.openai_service import OpenAIService, ChatMessage
import os
import json
from pydantic import BaseModel

class AstOutput(BaseModel):
    name: str
    props: List[dict]
    dependencies: List[str]
    jsxElements: List[str]

class EnhancedComponentMetadata(BaseModel):
    description: str
    useCases: List[str]
    usageExamples: List[str]

class ComponentEnhancer:
    def __init__(self):
        self.openai_service = OpenAIService(api_key=os.getenv("OPENAI_API_KEY"))

    def enhance_with_llm(self, astData: AstOutput) -> EnhancedComponentMetadata:
        """
        Enhance component metadata using OpenAI's GPT-4 model.
        
        Args:
            ast_data: Component AST data including name, props, dependencies, and JSX elements
            
        Returns:
            Enhanced component metadata with description, use cases, examples, and prop descriptions
        """
        function_schema = {
            "type": "function",
            "function": {
                "name": "enhance_component",
                "description": "Analyze React component and generate enhanced metadata",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Brief description of the component"
                        },
                        "useCases": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "3 common use cases for the component"
                        },
                        "usageExamples": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "2 example usages of the component"
                        }
                    },
                    "required": ["description", "useCases", "usageExamples"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }

        prompt = f"""
        Analyze this React component and provide enhanced metadata:

        Component: {astData.name}
        Props: {json.dumps(astData.props)}
        Dependencies: {', '.join(astData.dependencies)}
        JSX Elements Used: {', '.join(astData.jsxElements)}
        """
        
        messages = [
            ChatMessage(role="user", content=prompt)
        ]
        
        try:
            response = self.openai_service.chat_completion(
                messages=messages,
                tools=[function_schema],
                tool_choice={"type": "function", "function": {"name": "enhance_component"}}
            )
            
            # Extract function call result
            function_call = response["raw_response"].choices[0].message.tool_calls[0]
            enhanced_data = json.loads(function_call.function.arguments)
            return EnhancedComponentMetadata(**enhanced_data)
            
        except Exception as e:
            print(f"Error enhancing component metadata: {str(e)}")
            raise

    def run_example(self):
        # Example usage
        sample_ast = AstOutput(
            name="Button",
            props=
                [
                                {
                "name": "variant",
                "type": "ButtonVariant",
                "typeDetails": None,
                "optional": True,
                "source": "interface"
            },
            {
                "name": "size",
                "type": "ButtonSize",
                "typeDetails": None,
                "optional": True,
                "source": "interface"
            },
            {
                "name": "fullWidth",
                "type": "boolean",
                "typeDetails": None,
                "optional": True,
                "source": "interface"
            },
                ]
                # "variant": "string",
                # "size": "string",
                # "onClick": "() => void",
                # "disabled": "boolean"
            ,
            dependencies=["react", "@mui/material"],
            jsxElements=["Typography", "Box"]
        )
        
        enhanced_data = self.enhance_with_llm(sample_ast)
        print("\nEnhanced Component Metadata:")
        print(json.dumps(enhanced_data.model_dump(), indent=2))
        return enhanced_data

# For backwards compatibility
async def run_example():
    enhancer = ComponentEnhancer()
    return enhancer.run_example()

async def main():
    await run_example()

if __name__ == "__main__":
    pass
    # import asyncio
    # asyncio.run(main()) 