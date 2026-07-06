import re

# Banned American spellings mapped to their Indian English (InE) equivalents
# Banned British/Indian spellings mapped to their American English equivalents
BANNED_GB_SPELLINGS = {
    r'\boptimise\b': 'optimize',
    r'\boptimises\b': 'optimizes',
    r'\boptimised\b': 'optimized',
    r'\boptimising\b': 'optimizing',
    r'\boptimiser\b': 'optimizer',
    r'\boptimisers\b': 'optimizers',
    r'\boptimisation\b': 'optimization',
    r'\boptimisations\b': 'optimizations',
    
    r'\bminimise\b': 'minimize',
    r'\bminimises\b': 'minimizes',
    r'\bminimised\b': 'minimized',
    r'\bminimising\b': 'minimizing',
    r'\bminimisation\b': 'minimization',
    
    r'\bmaximise\b': 'maximize',
    r'\bmaximises\b': 'maximizes',
    r'\bmaximized\b': 'maximized',
    r'\bmaximizing\b': 'maximizing',
    r'\bmaximisation\b': 'maximization',
    
    r'\bcentralise\b': 'centralize',
    r'\bcentralizes\b': 'centralizes',
    r'\bcentralised\b': 'centralized',
    r'\bcentralising\b': 'centralizing',
    r'\bcentralisation\b': 'centralization',
    
    r'\bsynchronise\b': 'synchronize',
    r'\bsynchronises\b': 'synchronizes',
    r'\bsynchronised\b': 'synchronized',
    r'\bsynchronising\b': 'synchronizing',
    r'\bsynchronisation\b': 'synchronization',
    
    r'\brealise\b': 'realize',
    r'\brealises\b': 'realizes',
    r'\brealised\b': 'realized',
    r'\brealising\b': 'realizing',
    r'\brealisation\b': 'realization',

    r'\bserialise\b': 'serialize',
    r'\bserialises\b': 'serializes',
    r'\bserialised\b': 'serialized',
    r'\bserialising\b': 'serializing',
    r'\bserialisation\b': 'serialization',

    r'\bdeserialise\b': 'deserialize',
    r'\bdeserialises\b': 'deserializes',
    r'\bdeserialized\b': 'deserialized',
    r'\bdeserialising\b': 'deserializing',
    r'\bdeserialisation\b': 'deserialization',
    
    r'\bauthorise\b': 'authorize',
    r'\bauthorises\b': 'authorizes',
    r'\bauthorised\b': 'authorized',
    r'\bauthorising\b': 'authorizing',
    r'\bauthorisation\b': 'authorization',
    
    r'\bprioritise\b': 'prioritize',
    r'\bprioritises\b': 'prioritizes',
    r'\bprioritised\b': 'prioritized',
    r'\bprioritising\b': 'prioritizing',
    r'\bprioritisation\b': 'prioritization',
    
    r'\bnormalise\b': 'normalize',
    r'\bnormalises\b': 'normalizes',
    r'\bnormalised\b': 'normalized',
    r'\bnormalising\b': 'normalizing',
    r'\bnormalisation\b': 'normalization',
    
    r'\bstandardise\b': 'standardize',
    r'\bstandardises\b': 'standardizes',
    r'\bstandardised\b': 'standardized',
    r'\bstandardising\b': 'standardizing',
    r'\bstandardisation\b': 'standardization',

    r'\bbehaviour\b': 'behavior',
    r'\bbehaviours\b': 'behaviors',
    r'\bcolour\b': 'color',
    r'\bcolours\b': 'colors',
    r'\bfavour\b': 'favor',
    r'\bfavours\b': 'favors',
    
    r'\bdata centre\b': 'data center',
    r'\bdata centres\b': 'data centers',
    r'\bdatacentre\b': 'datacenter',
    r'\bdatacentres\b': 'datacenters',
    
    r'\bmodelled\b': 'modeled',
    r'\bmodelling\b': 'modeling',
    r'\blabelled\b': 'labeled',
    r'\blabelling\b': 'labeling',
    r'\bcancelled\b': 'canceled',
    r'\bcancelling\b': 'canceling',
}

def clean_line_prose(line: str) -> str:
    """Convert British spellings in a single line of prose to US, preserving capitalization,
    and strip redundant 'This document explains/covers' phrasing."""
    
    # 1. Clean 'This document explains' and similar prefixes
    prefixes = [
        ("This document explains ", "Explains "),
        ("This document covers ", "Covers "),
        ("This document discusses ", "Discusses "),
        ("This document details ", "Details "),
        ("This document is about ", "About "),
        ("This document provides ", "Provides "),
        ("this document explains ", "Explains "),
        ("this document covers ", "Covers "),
        ("this document discusses ", "Discusses "),
        ("this document details ", "Details "),
        ("this document is about ", "About "),
        ("this document provides ", "Provides "),
    ]
    
    # Check if the line has frontmatter summary field
    m = re.match(r'^summary:\s*"(.*)"\s*$', line)
    is_frontmatter_summary = False
    text_val = line
    if m:
        is_frontmatter_summary = True
        text_val = m.group(1)
        
    has_match = False
    for old, new in prefixes:
        if text_val.startswith(old):
            text_val = new + text_val[len(old):]
            has_match = True
            break
            
    if not has_match:
        # Handle generic pattern: 'This document [verb] ...'
        new_val = re.sub(r'^[Tt]his document\s+(?:explains|covers|discusses|details|provides|is about)\s+', 'Explains ', text_val)
        if new_val != text_val:
            text_val = new_val
            has_match = True
        else:
            new_val = re.sub(r'^[Tt]his document\s+', '', text_val)
            if new_val != text_val:
                text_val = new_val
                has_match = True

    # Capitalize first letter if matched
    if has_match and text_val and text_val[0].islower():
        text_val = text_val[0].upper() + text_val[1:]
        
    if has_match:
        if is_frontmatter_summary:
            line = f'summary: "{text_val}"'
        else:
            line = text_val

    # 2. Convert Oxford commas
    line = line.replace(", and", " and")
    line = line.replace(", And", " And")
    line = line.replace(", AND", " AND")

    # 3. Convert British spellings
    for pattern, replacement in BANNED_GB_SPELLINGS.items():
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
    """Convert an entire markdown file to US spelling, preserving code elements."""
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
    """Check a single line of prose for banned British/Indian spellings.
    Returns a list of warnings if violations are found."""
    violations = []
    for pattern, us_e in BANNED_GB_SPELLINGS.items():
        matches = re.findall(pattern, line, flags=re.IGNORECASE)
        for match in matches:
            violations.append(f"Found British spelling '{match}' (expected American English '{us_e}')")
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
