import re

# Banned American spellings mapped to their Indian English (InE) equivalents
BANNED_US_SPELLINGS = {
    r'\boptimize\b': 'optimise',
    r'\boptimizes\b': 'optimises',
    r'\boptimized\b': 'optimised',
    r'\boptimizing\b': 'optimising',
    r'\boptimizer\b': 'optimiser',
    r'\boptimizers\b': 'optimisers',
    r'\boptimization\b': 'optimisation',
    r'\boptimizations\b': 'optimisations',
    
    r'\bminimize\b': 'minimise',
    r'\bminimizes\b': 'minimises',
    r'\bminimized\b': 'minimised',
    r'\bminimizing\b': 'minimising',
    r'\bminimization\b': 'minimisation',
    
    r'\bmaximize\b': 'maximise',
    r'\bmaximizes\b': 'maximises',
    r'\bmaximized\b': 'maximised',
    r'\bmaximizing\b': 'maximising',
    r'\bmaximization\b': 'maximisation',
    
    r'\bcentralize\b': 'centralise',
    r'\bcentralizes\b': 'centralises',
    r'\bcentralized\b': 'centralised',
    r'\bcentralizing\b': 'centralising',
    r'\bcentralization\b': 'centralisation',
    
    r'\bsynchronize\b': 'synchronise',
    r'\bsynchronizes\b': 'synchronises',
    r'\bsynchronized\b': 'synchronised',
    r'\bsynchronizing\b': 'synchronising',
    r'\bsynchronization\b': 'synchronisation',
    
    r'\brealize\b': 'realise',
    r'\brealizes\b': 'realises',
    r'\brealized\b': 'realised',
    r'\brealizing\b': 'realising',
    r'\brealization\b': 'realisation',

    r'\bserialize\b': 'serialise',
    r'\bserializes\b': 'serialises',
    r'\bserialized\b': 'serialised',
    r'\bserializing\b': 'serialising',
    r'\bserialization\b': 'serialisation',

    r'\bdeserialize\b': 'deserialise',
    r'\bdeserializes\b': 'deserialises',
    r'\bdeserialized\b': 'deserialised',
    r'\bdeserializing\b': 'deserialising',
    r'\bdeserialization\b': 'deserialisation',
    
    r'\bauthorize\b': 'authorise',
    r'\bauthorizes\b': 'authorises',
    r'\bauthorized\b': 'authorised',
    r'\bauthorizing\b': 'authorising',
    r'\bauthorization\b': 'authorisation',
    
    r'\bprioritize\b': 'prioritise',
    r'\bprioritizes\b': 'prioritises',
    r'\bprioritized\b': 'prioritised',
    r'\bprioritizing\b': 'prioritising',
    r'\bprioritization\b': 'prioritisation',
    
    r'\bnormalize\b': 'normalise',
    r'\bnormalizes\b': 'normalises',
    r'\bnormalized\b': 'normalised',
    r'\bnormalizing\b': 'normalising',
    r'\bnormalization\b': 'normalisation',
    
    r'\bstandardize\b': 'standardise',
    r'\bstandardizes\b': 'standardises',
    r'\bstandardized\b': 'standardised',
    r'\bstandardizing\b': 'standardising',
    r'\bstandardization\b': 'standardisation',

    r'\bbehavior\b': 'behaviour',
    r'\bbehaviors\b': 'behaviours',
    r'\bcolor\b': 'colour',
    r'\bcolors\b': 'colours',
    r'\bfavor\b': 'favour',
    r'\bfavors\b': 'favours',
    
    r'\bdata center\b': 'data centre',
    r'\bdata centers\b': 'data centres',
    r'\bdatacenter\b': 'datacentre',
    r'\bdatacenters\b': 'datacentres',
    
    r'\bmodeled\b': 'modelled',
    r'\bmodeling\b': 'modelling',
    r'\blabeled\b': 'labelled',
    r'\blabeling\b': 'labelling',
    r'\bcanceled\b': 'cancelled',
    r'\bcanceling\b': 'cancelling',
}

def clean_line_prose(line: str) -> str:
    """Convert American spellings in a single line of prose to InE, preserving capitalization."""
    for pattern, replacement in BANNED_US_SPELLINGS.items():
        def repl_func(match):
            word = match.group(0)
            if word.isupper():
                return replacement.upper()
            if word and word[0].isupper():
                return replacement[0].upper() + replacement[1:]
            return replacement.lower()
            
        line = re.sub(pattern, repl_func, line, flags=re.IGNORECASE)
    return line

def convert_content(content: str) -> str:
    """Convert an entire markdown file to InE spelling, preserving code elements."""
    lines = content.splitlines()
    new_lines = []
    in_code_block = False

    for line in lines:
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            new_lines.append(line)
            continue

        if in_code_block:
            new_lines.append(line)
            continue

        # Mask inline backticks `...`
        code_placeholders = []
        def mask_code(match):
            placeholder = f"__CODE_SNIPPET_{len(code_placeholders)}__"
            code_placeholders.append(match.group(0))
            return placeholder

        masked_line = re.sub(r'`[^`]+`', mask_code, line)
        cleaned_masked_line = clean_line_prose(masked_line)
        
        # Restore masked backticks
        unmasked_line = cleaned_masked_line
        for i, snippet in enumerate(code_placeholders):
            placeholder = f"__CODE_SNIPPET_{i}__"
            unmasked_line = unmasked_line.replace(placeholder, snippet)
            
        new_lines.append(unmasked_line)

    return "\n".join(new_lines) + "\n"

def check_line_prose(line: str) -> list[str]:
    """Check a single line of prose for banned American spellings.
    Returns a list of warnings if violations are found."""
    violations = []
    for pattern, in_e in BANNED_US_SPELLINGS.items():
        matches = re.findall(pattern, line, flags=re.IGNORECASE)
        for match in matches:
            violations.append(f"Found American spelling '{match}' (expected Indian English '{in_e}')")
    return violations

def check_content(content: str) -> list[tuple[int, str]]:
    """Check an entire markdown content for spelling compliance, ignoring code segments.
    Returns a list of tuples: (line_number, warning_message)."""
    lines = content.splitlines()
    violations = []
    in_code_block = False

    for idx, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Strip inline backticks `...` to ignore code references
        clean_prose = re.sub(r'`[^`]+`', '', line)
        
        # Run check
        line_violations = check_line_prose(clean_prose)
        for v in line_violations:
            violations.append((idx, v))

    return violations
