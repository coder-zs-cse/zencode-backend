from app.services.ingestion_service import FetchedComponent, FetchComponentsService
import json

def test_parse_component():
    # Sample TypeScript React component
    sample_component = """
import React, { ChangeEventHandler } from "react";
import {
  useForm,
  SubmitHandler,
  FieldValues,
  Path,
  FieldError,
  DefaultValues,
  Control,
} from "react-hook-form";
import Select from "../Select/Select";
import Input from "../Input/Input";
import Button from "../Button/Button";
import PhoneInput from "../PhoneInput/PhoneInput";
import DateInput from "../DateInput/DateInput";
import { formStyles } from "@/Styles/GlobalStyle/FromStyle";
import { ButtonSize, ButtonVariant } from "@/Constants/Enum/VarientEnum";
import FileUpload from "../FileUpload/FileUpload";
import CountrySelect from "../CountrySelect/CountrySelect";
import { Data } from "@/Constants";
import TextArea from "../TextArea/TextArea";
import { Checkbox, RangeSlider } from "@/Components/Global";
import { zodResolver } from "@hookform/resolvers/zod";
import { ZodType } from "zod";
import Label from "../Label/Label";

const styles = formStyles();

export type FormField = {
  name: string;
  type: string;
  label: string | JSX.Element;
  placeholder?: string;
  options?: { value: string | number; label: string }[];
  required?: boolean;
  showRequiredStar?: boolean;
  className?: string;
  disabled?: boolean;
  defaultValue?: any;
  onSelectChange?: ChangeEventHandler<HTMLSelectElement> | undefined;
  min?: number;
  max?: number;
  step?: number;
  attribute?: string;
  labelClassName?: string;
  component?: React.ReactNode;
  currencySymbol?: boolean;
  checkboxColor?: string;
  iconClassName?: string;
  handelOnDelete?: any;
};

interface FormProps<TFieldValues extends FieldValues> {
  formFields: FormField[][];
  onSubmit: SubmitHandler<TFieldValues>;
  submitButtonText?: string;
  submitButtonProps?: Partial<React.ComponentProps<typeof Button>>;
  formClassName?: string;
  children?: React.ReactNode;
  secondaryButton?: React.ReactNode;
  showSubmitButton?: boolean;
  onChange?: (name: string, value: any) => void;
  formRef?: any;
  validationSchema?: ZodType<any>;
  isEditing?: boolean;
  iconClassName?: any;
  labelClassName?: string;
}

const Form = <TFieldValues extends FieldValues>({
  formFields,
  onSubmit,
  submitButtonText = "Submit",
  submitButtonProps = {},
  formClassName = "",
  children,
  secondaryButton,
  showSubmitButton = true,
  onChange,
  formRef,
  validationSchema,
  isEditing,
}: FormProps<TFieldValues>): JSX.Element => {
  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<TFieldValues>({
    defaultValues: Object.fromEntries(
      formFields.flat().map((field) => [field.name, field.defaultValue])
    ) as DefaultValues<TFieldValues>,
    resolver: validationSchema ? zodResolver(validationSchema) : undefined,
  });

  const handleCountryChange = (name: string, code: string, label: string) => {
    if (onChange) {
      onChange(name, { code, label });
    }
  };

  const renderField = (field: FormField) => {
    const commonProps = {
      name: field.name as Path<TFieldValues>,
      control,
      label: field.label as string,
      placeholder: field.placeholder,
      required: field.required,
      disabled: field.disabled,
      error: errors[field.name as keyof TFieldValues] as FieldError | undefined,
      onChange: (value: any) => {
        if (onChange) {
          onChange(field.name, value);
        }
      },
    };

    switch (field.type) {
      case "label":
        return (
          <Label label={field.label} labelClassName={field.labelClassName} />
        );
      case "select":
        return (
          <Select<TFieldValues>
            {...commonProps}
            options={field.options || []}
            className={field.className}
            labelClassName={field.labelClassName}
            onChange={(name, value) => {
              if (onChange) {
                onChange(name, value);
              }
            }}
            isEditing={isEditing}
          />
        );
      case "phone":
        return (
          <PhoneInput<TFieldValues>
            {...commonProps}
            className={field.className}
            labelClassName={field.labelClassName}
            countryOptions={Data?.CountryData?.map((country) => ({
              value: country.name,
              label: country.name,
              dialCode: country.dial_code,
              ...country,
            }))}
            defaultValue={field.defaultValue}
            onChange={(name, value) => {
              if (onChange) {
                onChange(name, value);
              }
            }}
          />
        );
      case "date":
        return (
          <DateInput<TFieldValues>
            {...commonProps}
            labelClassName={field.labelClassName}
          />
        );
      case "file":
        return (
          <FileUpload<TFieldValues>
            {...commonProps}
            defaultValue={field.defaultValue}
            labelClassName={field.labelClassName}
            dropzoneText={field.placeholder}
            className={field.className}
            onChange={(name, value) => {
              if (onChange) {
                onChange(name, value);
              }
            }}
          />
        );
      case "textArea":
        return (
          <TextArea<TFieldValues>
            {...commonProps}
            labelClassName={field.labelClassName}
            className={field.className}
          />
        );

      case "countrySelect":
        return (
          <CountrySelect<TFieldValues>
            {...commonProps}
            options={Data?.CountryData?.map((country) => ({
              value: country.name,
              label: country.name,
              ...country,
            }))}
            labelClassName={field.labelClassName}
            className={field.className}
            onChange={(name, code, label) =>
              handleCountryChange(name, code, label)
            }
          />
        );
      case "range":
        return (
          <RangeSlider<TFieldValues>
            labelClassName={field.labelClassName || ""}
            {...commonProps}
            min={field.min || 0}
            max={field.max || 100}
            step={field.step || 1}
            attribute={field.attribute || ""}
          />
        );
      case "checkbox":
        return (
          <Checkbox
            {...commonProps}
            checkboxColor={field.checkboxColor}
            labelClassName={field.labelClassName || ""}
          />
        );
      case "component":
        return field.component;
      case "number":
        return (
          <Input<TFieldValues>
            {...commonProps}
            type={field.type}
            showRequiredStar={field.showRequiredStar}
            className={field.className}
            labelClassName={field.labelClassName}
            currencySymbol={field.currencySymbol}
          />
        );
      default:
        return (
          <Input<TFieldValues>
            {...commonProps}
            type={field.type}
            showRequiredStar={field.showRequiredStar}
            className={field.className}
            labelClassName={field.labelClassName}
          />
        );
    }
  };

  return (
    <form
      ref={formRef}
      onSubmit={handleSubmit(onSubmit)}
      className={`w-full ${formClassName}`}
    >
      <div className={styles.formContent()}>
        {formFields?.map((row, rowIndex) => (
          <div key={rowIndex} className={styles.row()}>
            {row?.map((field: FormField, fieldIndex: number) => (
              <div
                key={`${rowIndex}-${fieldIndex}`}
                className={styles.fieldWrapper({
                  class: `${
                    row.length === 2
                      ? "sm:w-1/2"
                      : row.length > 2
                      ? "sm:w-1/2 lg:w-1/3"
                      : "w-full"
                  }`,
                })}
              >
                {renderField(field)}
              </div>
            ))}
          </div>
        ))}
        {children}
      </div>

      <div className={styles.buttonContainer()}>
        {secondaryButton && (
          <div className={styles.buttonWrapper()}>{secondaryButton}</div>
        )}
        {showSubmitButton && (
          <Button
            type="submit"
            variant={ButtonVariant.Primary}
            size={ButtonSize.Medium}
            disabled={isSubmitting}
            className={styles.buttonWrapper()}
            {...submitButtonProps}
          >
            {submitButtonText}
          </Button>
        )}
      </div>
    </form>
  );
};

export default Form;
    """

    # Create a FetchedComponent instance
    component = FetchedComponent(
        file="Button.tsx",
        fileContent=sample_component,
        path="src/components/Button.tsx"
    )

    # Initialize the service (we don't need a real repo for this example)
    service = FetchComponentsService(repo_link="https://github.com/dummy/repo")

    # Parse the component
    parsed_component = service.parse_component(component)

    if parsed_component:
        print("\nSuccessfully parsed component!")
        print("\nComponent Details:")
        print(f"Name: {parsed_component.name}")
        print("\nProps:")
        for prop in parsed_component.props:
            print(f"- {prop['name']} ({prop['type']})")
            print(f"  Optional: {prop.get('optional', False)}")
            print(f"  Source: {prop.get('source', 'unknown')}")
            if prop.get('typeDetails'):
                print(f"  Type Details: {prop['typeDetails']}")
        
        print("\nDependencies:", parsed_component.dependencies)
        print("Is TypeScript:", parsed_component.isTypescript)
        print("Exports:", parsed_component.exports)
        print("JSX Elements:", parsed_component.jsxElements)
    else:
        print("Failed to parse component")

if __name__ == "__main__":
    print("Testing component parser...")
    test_parse_component() 