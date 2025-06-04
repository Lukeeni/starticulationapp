import streamlit as st
import pandas as pd

# Mastery ages (Australian norms)
mastery_ages = {
    'h': 36, 'p': 36, 'm': 36, 'ŋ': 48, 'n': 36, 'w': 48, 'b': 36, 'k': 36, 'g': 36, 'd': 36, 't': 36,
    'j': 60, 'f': 36, 'ʒ': 72, 'l': 60, 'ʃ': 60, 'tʃ': 60, 's': 60, 'dʒ': 60, 'z': 60, 'r': 72, 'v': 60,
    'ð': 84, 'θ': 72,
    'bl': 48, 'fl': 48, 'pl': 48, 'br': 48, 'fr': 48, 'pr': 48, 'kw': 48, 'tw': 48,
    'gl': 48, 'kl': 48, 'dr': 48, 'gr': 48, 'kr': 48, 'tr': 48, 'θr': 48,
    'sm': 60, 'sp': 60, 'sw': 60, 'sk': 60, 'sl': 60, 'sn': 60, 'st': 60,
    'skr': 60, 'spr': 60, 'skw': 60, 'spl': 60
}

# Target positions
target_positions = {
    'tʃ': ['initial', 'medial', 'final'], 'dʒ': ['initial', 'medial', 'final'],
    'ʒ': ['medial'], 'ð': ['initial', 'medial'], 'j': ['initial'], 'h': ['initial'],
    'w': ['initial', 'medial'], 'r': ['initial', 'medial'], 'ŋ': ['medial', 'final'],
    'sm': ['initial'], 'sp': ['initial'], 'sw': ['initial'], 'sk': ['initial'], 'sl': ['initial'],
    'sn': ['initial'], 'st': ['initial'], 'bl': ['initial'], 'fl': ['initial'], 'pl': ['initial'],
    'br': ['initial'], 'fr': ['initial'], 'pr': ['initial'], 'kw': ['initial'], 'tw': ['initial'],
    'gl': ['initial'], 'kl': ['initial'], 'dr': ['initial'], 'gr': ['initial'], 'kr': ['initial'],
    'tr': ['initial'], 'θr': ['initial'], 'skr': ['initial'], 'spr': ['initial'],
    'skw': ['initial'], 'spl': ['initial']
}

# Ensure every sound in mastery_ages has a position list
for s in mastery_ages:
    if s not in target_positions:
        target_positions[s] = ['initial', 'medial', 'final']

# (Uncommented) We want /r/ to have final position as well:
target_positions['r'].append('final')

# Phonological processes
phonological_processes = {
    'backing': 'atypical', 'interdental lisp': 'atypical',
    'fronting': 36, 'gliding': 60, 'stopping': 48, 'vowelisation': 48,
    'affrication': 48, 'deaffrication': 48, 'alveolarization': 48, 'depalatisation': 48,
    'labialisation': 48, 'assimilation': 36, 'denasalisation': 48,
    'final consonant devoicing': 60, 'prevocalic voicing': 48, 'coalescence': 36,
    'reduplication': 30, 'cluster reduction (no /s/)': 48, 'cluster reduction (with /s/)': 60,
    'final consonant deletion': 48, 'initial consonant deletion': 'atypical',
    'weak syllable deletion': 48, 'epenthesis': 60
}

# Process rules
process_rules = [
    ('gliding', {'r': 'w', 'l': 'w'}),
    ('fronting', {'k': 't', 'g': 'd', 'ŋ': 'n'}),
    ('backing', {'t': 'k', 'd': 'g', 'n': 'ŋ'}),
    ('stopping', {'f': ['p', 'b'], 'v': ['b', 'p'], 's': ['t', 'd'], 'z': ['d', 't'],
                  'ʃ': ['t', 'd'], 'ʒ': ['d', 't'], 'θ': ['t'], 'ð': ['d']}),
    ('deaffrication', {'tʃ': 'ʃ', 'dʒ': 'ʒ'}),
    ('affrication', {'ʃ': 'tʃ', 'ʒ': 'dʒ'}),
    ('labialisation', {'t': 'p', 'd': 'b'}),
    ('alveolarization', {'f': 's', 'v': 'z'}),
    ('depalatisation', {'ʃ': 's', 'ʒ': 'z'}),
    ('final consonant devoicing', {'b': 'p', 'd': 't', 'g': 'k', 'v': 'f', 'z': 's'}),
    ('prevocalic voicing', {'p': 'b', 't': 'd', 'k': 'g'}),
    ('interdental lisp', {'s': 'θ', 'z': 'θ'})
]

def detect_process(target, produced):
    for proc, rules in process_rules:
        if target in rules:
            expected = rules[target]
            if isinstance(expected, list) and produced in expected:
                return proc
            elif produced == expected:
                return proc
    return None

def detect_cluster_reduction(target, produced):
    # New logic: exclude tʃ and dʒ from cluster reduction and reclassify as deaffrication if applicable
    if target in ['tʃ', 'dʒ']:
        return 'deaffrication'

    return 'cluster reduction (with /s/)' if 's' in target and len(produced) == 1 else            'cluster reduction (no /s/)' if len(target) > 1 and len(produced) == 1 else None

def get_age_in_months(age_str):
    try:
        y, m = map(int, age_str.split(";"))
        return y * 12 + m
    except:
        return 0

# --- UI ---
st.set_page_config("Starticulation", layout="wide")
st.title("Starticulation Articulation Assessment")

if 'show_instructions' not in st.session_state:
    st.session_state.show_instructions = True

if st.session_state.show_instructions:
    with st.expander("Welcome to Starticulation - Click to Continue"):
        st.markdown("""
Welcome to Starticulation, a tool for assessing consonant articulation. Starticulation is made by speech pathologists, for speech pathologists.

**HOW TO USE**: Fill in each box with the actual sound produced by the child. Target boxes are filled in by default.

Starticulation uses the "Average age of acquisition of English consonants across the world (90-100% criteria)" from Charles Sturt University to determine appropriate age of acquisition (https://cdn.csu.edu.au/__data/assets/pdf_file/0003/3330309/world-treehouse-chart.pdf).

Starticulation flags sounds as "delayed" when the child has surpassed the year of expected age of acquisition. In other words, /r/ is expected by 5 years, so only a 6 year old child will be considered "delayed", as the child can acquire /r/ whilst they are 5;0 - 5;11.

To report bugs and suggestions, email lakestundun@gmail.com.

Use clinical judgment to verify phonological processes like cluster reduction.
""")
        if st.button("Continue"):
            st.session_state.show_instructions = False

child_name = st.text_input("Child's First Name")
age_input = st.text_input("Child's Age (e.g., 4;6)")
age_months = get_age_in_months(age_input)

if child_name and age_months:
    data = []
    for s in mastery_ages:
        for p in target_positions[s]:
            # Now include /r/ in final position
            data.append({'Sound': s, 'Position': p, 'Produced': s})
    df = pd.DataFrame(data)
    edited = st.data_editor(df, use_container_width=True)

    results, delayed, age_app, correct = [], [], [], []
    process_records = []

    for _, row in edited.iterrows():
        s, p, prod = row["Sound"], row["Position"], row["Produced"].strip()
        mastery = mastery_ages[s]
        if prod == s:
            results.append((s, p, "Age Appropriate"))
            correct.append(f"/{s}/ ({p})")
        else:
            proc = detect_process(s, prod) or detect_cluster_reduction(s, prod)
            if proc:
                status = phonological_processes.get(proc)
                delay = (status == 'atypical') or (isinstance(status, int) and age_months >= status)
                process_records.append((proc, s, prod, 'Delayed' if delay else 'Age Appropriate'))

            if age_months >= mastery:
                results.append((s, p, "Delayed"))
                delayed.append((s, p, mastery))
            else:
                results.append((s, p, "Incorrect but Age Appropriate"))
                age_app.append((s, p, mastery))

    color_map = {
        "Age Appropriate": "#d4edda", "Incorrect but Age Appropriate": "#ffe082", "Delayed": "#f8d7da"
    }

    def highlight(val):
        return f"background-color:{color_map.get(val,'')}; color:black;"

    st.subheader("Assessment Results")
    st.markdown(pd.DataFrame(results, columns=["Sound", "Position", "Result"])
        .style.applymap(highlight, subset=["Result"]).to_html(), unsafe_allow_html=True)

    if process_records:
        st.subheader("Detected Phonological Processes")
        st.markdown(pd.DataFrame(process_records, columns=["Process", "Target", "Produced", "Status"])
            .style.applymap(highlight, subset=["Status"]).to_html(), unsafe_allow_html=True)

    st.subheader("Summary Report")
    d_html = ''.join([f"<li>/{s}/ ({p}) – expected by {m//12} yrs</li>" for s, p, m in delayed]) or "<li>None</li>"
    a_html = ''.join([f"<li>/{s}/ ({p}) – expected by {m//12} yrs</li>" for s, p, m in age_app]) or "<li>None</li>"
    st.markdown(f"<div style='font-size:16px;'>"
                f"<strong>Delayed:</strong><ul>{d_html}</ul>"
                f"<strong>Age Appropriate but Incorrect:</strong><ul>{a_html}</ul>"
                f"""
</div>""", unsafe_allow_html=True)

    st.subheader("Phonological Process Summary")
    if process_records:
        typical, atypical = [], []
        for proc, tgt, prod, stat in process_records:
            if phonological_processes.get(proc) == 'atypical':
                atypical.append(f"{proc} (e.g., /{tgt}/ → /{prod}/)")
            else:
                res = phonological_processes.get(proc, 'unknown')
                when = f"{res//12} yrs" if isinstance(res, int) else "unknown"
                typical.append(f"{proc} (e.g., /{tgt}/ → /{prod}/) – resolves by {when}")

        output = "<strong>Atypical Processes</strong><ul>" + ''.join(f"<li>{x}</li>" for x in set(atypical)) + "</ul><br>"
        output += "<strong>Typical but Delayed Processes</strong><ul>" + ''.join(f"<li>{x}</li>" for x in set(typical)) + "</ul>"
        st.markdown(f"<div style='font-size:16px;'>{output}</div>", unsafe_allow_html=True)

    st.subheader("Recommended SMART Goals")
    if delayed:
        goal_list = [
            f"{child_name} will accurately produce the /{s}/ sound in the {p.lower()} position of single words "
            f"with 80% accuracy across 3 consecutive sessions, following auditory discrimination and isolation practice, "
            f"after 3 weeks of traditional articulation therapy."
            for s, p, m in delayed
        ]
        st.markdown("<ul>" + ''.join(f"<li>{g}</li>" for g in goal_list) + "</ul>", unsafe_allow_html=True)
        st.download_button("Download SMART Goals (TXT)", "\n".join(goal_list), file_name=f"{child_name}_goals.txt")

