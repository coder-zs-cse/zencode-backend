from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.services.gemini_service import ChatMessage
from app.lib.constants.model_config import SYSTEM_PROMPTS

class FileNode(BaseModel):
    fileName: str
    filePath: str
    fileContent: str

class InternalComponent(BaseModel):
    import_path: str
    content: str

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
        # Note: Design prompt is now handled via additional_user_prompt parameter

        # Add codebase context if available
        if self.codebase:
            codebase_context = "Current codebase structure: \n"
            for file_node in self.codebase:
                codebase_context += f"{{ fileName: {file_node.fileName}, filePath: {file_node.filePath}, fileContent: {file_node.fileContent} }} \n\n"
            
            messages.append(
                ChatMessage(
                    role="user",
                    content=codebase_context
                )
            )
        
        # Add internal components context if available
        if self.internal_components:
            components_context = ""
            for i, component in enumerate(self.internal_components):
                components_context += f"Internal component Import Path: {component.import_path}\n"
                components_context += f"Internal component Content: {component.content}\n\n"
            
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