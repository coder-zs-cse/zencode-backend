import os
from typing import List
from app.services.ingestion_service import FetchComponentsService, FetchedComponent
from dotenv import load_dotenv

# Sample React components for testing
BUTTON_COMPONENT = """
import React from 'react';
import { cn } from '../utils/cn';

interface ButtonProps {
    /** The variant style of the button */
    variant?: 'primary' | 'secondary' | 'outline';
    /** Size of the button */
    size?: 'sm' | 'md' | 'lg';
    /** Whether the button is disabled */
    disabled?: boolean;
    /** Click handler */
    onClick?: () => void;
    /** Button contents */
    children: React.ReactNode;
    /** Additional CSS classes */
    className?: string;
}

export const Button: React.FC<ButtonProps> = ({
    variant = 'primary',
    size = 'md',
    disabled = false,
    onClick,
    children,
    className,
}) => {
    const baseStyles = 'rounded-md font-medium transition-colors focus:outline-none focus:ring-2';
    const variantStyles = {
        primary: 'bg-blue-500 text-white hover:bg-blue-600',
        secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
        outline: 'border-2 border-gray-300 hover:border-gray-400'
    };
    const sizeStyles = {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2 text-base',
        lg: 'px-6 py-3 text-lg'
    };

    return (
        <button
            className={cn(
                baseStyles,
                variantStyles[variant],
                sizeStyles[size],
                disabled && 'opacity-50 cursor-not-allowed',
                className
            )}
            onClick={onClick}
            disabled={disabled}
        >
            {children}
        </button>
    );
};
"""

CARD_COMPONENT = """
import React from 'react';

interface CardProps {
    /** Title of the card */
    title: string;
    /** Card's main content */
    children: React.ReactNode;
    /** Optional footer content */
    footer?: React.ReactNode;
    /** Whether to show a shadow */
    withShadow?: boolean;
    /** Whether the card is clickable */
    clickable?: boolean;
    /** Click handler */
    onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({
    title,
    children,
    footer,
    withShadow = true,
    clickable = false,
    onClick
}) => {
    return (
        <div
            className={`
                rounded-lg bg-white p-4
                ${withShadow ? 'shadow-md' : ''}
                ${clickable ? 'cursor-pointer hover:shadow-lg transition-shadow' : ''}
            `}
            onClick={clickable ? onClick : undefined}
        >
            <h3 className="text-lg font-semibold mb-2">{title}</h3>
            <div className="mb-4">{children}</div>
            {footer && (
                <div className="border-t pt-3">
                    {footer}
                </div>
            )}
        </div>
    );
};
"""

def create_test_components() -> List[FetchedComponent]:
    """Create test components for parsing."""
    return [
        FetchedComponent(
            file="Button.tsx",
            fileContent=BUTTON_COMPONENT,
            path="src/components/Button.tsx"
        ),
        FetchedComponent(
            file="Card.tsx",
            fileContent=CARD_COMPONENT,
            path="src/components/Card.tsx"
        )
    ]

def main():
    # Load environment variables
    load_dotenv()
    
    # Get OpenAI API key from environment
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    # Initialize service with dummy repo (not needed for this test)
    service = FetchComponentsService(
        repo_link="https://github.com/dummy/repo",
        openai_api_key=openai_api_key
    )

    # Create test components
    test_components = create_test_components()

    # Parse components
    print("Parsing components...")
    parsed_components = service.parse_components(test_components)

    # Display results
    print("\nParsed Components:")
    print("=================")
    
    for i, component in enumerate(parsed_components, 1):
        print(f"\nComponent {i}: {component.name}")
        print("-" * (len(f"Component {i}: {component.name}")))
        print(f"Description: {component.description}")
        
        print("\nInput Props:")
        for prop in component.inputProps:
            print(f"- {prop['name']}: {prop['type']}")
            print(f"  Description: {prop['description']}")
            print(f"  Required: {prop['required']}")
        
        print("\nUse Cases:")
        for case in component.useCases:
            print(f"- {case}")
        
        print("\nCode Examples:")
        for j, example in enumerate(component.codeExamples, 1):
            print(f"\nExample {j}:")
            print(example)
        print("\n" + "=" * 80)

if __name__ == "__main__":
    main() 