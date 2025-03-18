def strip_indents(value):
    if isinstance(value, (list, tuple)):
        processed_string = ''.join(
            curr + (str(value[i]) if i < len(value) else "")
            for i, curr in enumerate(value[0])
        )
        return _strip_indents(processed_string)

    return _strip_indents(value)


def _strip_indents(value):
    return '\n'.join(line.strip() for line in value.split('\n')).lstrip().rstrip('\n')
