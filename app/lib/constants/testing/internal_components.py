components = [
    {
        'file': 'CountrySelect.tsx',
        'fileContent': "import { Icons } from \"@/Asset\";\nimport Image from \"next/image\";\nimport React, {\n  useState,\n  useRef,\n  useEffect,\n  KeyboardEvent,\n  SelectHTMLAttributes,\n} from \"react\";\nimport {\n  Control,\n  Controller,\n  FieldError,\n  FieldValues,\n  Path,\n  ControllerRenderProps,\n  FieldErrors,\n  PathValue,\n} from \"react-hook-form\";\n\ninterface CountryOption {\n  value: string;\n  label: string;\n  code: string;\n}\n\ninterface CountrySelectProps<TFieldValues extends FieldValues>\n  extends Omit<SelectHTMLAttributes<HTMLSelectElement>, \"name\" | \"onChange\"> {\n  label?: string;\n  options: CountryOption[];\n  name: Path<TFieldValues>;\n  control: Control<TFieldValues>;\n  error?: FieldError | FieldErrors<TFieldValues>[string];\n  required?: boolean;\n  defaultValue?: string;\n  placeholder?: string;\n  labelClassName?: string;\n  onChange?: (name: string, code: string, label: string) => void;\n}\n\nconst CountrySelect = <TFieldValues extends FieldValues>({\n  label,\n  options,\n  name,\n  control,\n  ...",
        'path': 'src/components/ui/CountrySelect/CountrySelect.tsx'
    },
    {
        'file': 'Heading.tsx',
        'fileContent': "import React from 'react';\n\ninterface HeadingProps {\n  text: string;\n  className?: string;\n}\n\nconst Heading: React.FC<HeadingProps> = ({ text, className = 'text-[#2C0075] text-xl' }) => {\n  return (\n    <h2 className={` font-bold ${className}`}>\n      {text}\n    </h2>\n  );\n};\n\nexport default Heading;",
        'path': 'src/components/ui/Heading/Heading.tsx'
    },
    {
        'file': 'Label.tsx',
        'fileContent': "\"use client\";\nimport { containerStyles, labelStyles } from \"@/Styles/GlobalStyle/InputStyle\";\nimport React from \"react\";\n\nconst Label = ({ label, labelClassName, name, ...props }: any): JSX.Element => {\n  return (\n    <div className='w-full'>\n      {label && (\n        <label htmlFor={name} className={`${labelClassName} !text-primary-900`}>\n          {label}\n        </label>\n      )}\n    </div>\n  );\n};\n\nexport default Label;\n",
        'path': 'src/components/ui/Label/Label.tsx'
    }
]