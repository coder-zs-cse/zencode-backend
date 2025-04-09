from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.services.gemini_service import ChatMessage
from app.lib.constants.model_config import SYSTEM_PROMPTS
from app.models.component import FileNode, InternalComponent
import app.utils.llm_parser as Utils

class Context(BaseModel):
    """
    A class that represents the context for generating responses, 
    with methods to construct message lists for LLM consumption.
    """
    user_query: str
    codebase: List[FileNode] = Field(default_factory=list)
    internal_components: List[InternalComponent] = Field(default_factory=list)
    system_prompt: str = SYSTEM_PROMPTS["react_generator"]
    additional_user_prompt: Optional[str] = None
    conversation: List[ChatMessage] = Field(default_factory=list)
    css_tokens: Dict[str, Any] = Field(default_factory=dict)
    dependencies: Dict[str, List[str]] = Field(default_factory=dict)

    def construct_messages(self) -> List[ChatMessage]:
        """
        Constructs a list of messages based on the context attributes.
        Returns:
            List[ChatMessage]: The constructed list of messages.
        """
        messages = [
            ChatMessage(
                role="system",
                content=self.system_prompt
            )
        ]
        
        # Add existing conversation if available
        if self.conversation:
            messages.extend(self.conversation)
        
        # Add codebase context if available
        if self.codebase:
            codebase_context = "REPOSITORY CONTEXT - Current codebase structure and files that must be considered for maintaining consistency:\n"
            for file_node in self.codebase:
                codebase_context += f"{{ fileName: {file_node.fileName}, filePath: {file_node.filePath}, fileContent: {file_node.fileContent} }} \n\n"
            
            messages.append(
                ChatMessage(
                    role="user",
                    content=codebase_context
                )
            )

        # Add CSS tokens context if available
        if self.css_tokens and 'files' in self.css_tokens:
            css_context = "DESIGN SYSTEM - These are the CSS files containing design tokens, styles, and classes that MUST be used:\n\n"
            for css_file in self.css_tokens['files']:
                css_context += f"FILE: {css_file['path']}\n"
                css_context += "CONTENT:\n"
                css_context += f"{css_file['content']}\n\n"
            
            messages.append(
                ChatMessage(
                    role="user",
                    content=css_context
                )
            )

        # Add dependencies context if available
        if self.dependencies:
            deps_context = "APPROVED DEPENDENCIES - These are the approved packages that can be used:\n\n"
            if 'dependencies' in self.dependencies:
                deps_context += "PRODUCTION DEPENDENCIES:\n"
                for dep in self.dependencies['dependencies']:
                    deps_context += f"- {dep}\n"
            if 'devDependencies' in self.dependencies:
                deps_context += "\nDEVELOPMENT DEPENDENCIES:\n"
                for dep in self.dependencies['devDependencies']:
                    deps_context += f"- {dep}\n"
            
            messages.append(
                ChatMessage(
                    role="user",
                    content=deps_context
                )
            )
        
        # Add internal components context if available
        if self.internal_components:
            components_context = "ENTERPRISE COMPONENTS - These are the approved internal components that MUST be reused. DO NOT create new components if similar functionality exists here. CRITICAL: You MUST use the exact import path provided for each component:\n\n"
            for component in self.internal_components:
                absolute_path = Utils.transform_absolute_path(component.path)

                components_context += f"COMPONENT: {component.name}\n"
                components_context += f"IMPORT PATH (MUST use exactly as shown): {absolute_path}\n"
                if component.description:
                    components_context += f"DESCRIPTION: {component.description}\n"
                if component.useCase:
                    components_context += f"USE CASES: {component.useCase}\n"
                if component.dependencies:
                    components_context += f"REQUIRED DEPENDENCIES: {', '.join(component.dependencies)}\n"
                if component.inputProps:
                    components_context += "PROPS SPECIFICATION (use these exact prop names and types):\n"
                    components_context += f"{component.inputProps}\n"
                if component.codeSamples:
                    components_context += "IMPLEMENTATION EXAMPLES:\n"
                    for i, sample in enumerate(component.codeSamples, 1):
                        components_context += f"Example {i}:\n{sample}\n"
                components_context += "\n---\n\n"
            
            messages.append(
                ChatMessage(
                    role="user",
                    content=components_context
                )
            )
        
        # Add additional user prompt if available
        if self.additional_user_prompt:
            messages.append(
                ChatMessage(
                    role="user",
                    content=self.additional_user_prompt
                )
            )
        
        # Add the main user query
        messages.append(
            ChatMessage(
                role="user",
                content=self.user_query
            )
        )
        
        return messages 