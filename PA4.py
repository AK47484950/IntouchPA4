import streamlit as st
import openai
import pandas as pd
import io

st.title("Toddler Speech Translator")
st.write("Let's translate grown-up language into toddler language!")

api_key = st.sidebar.text_input("OpenAI API Key", type="password")
if api_key:
    openai.api_key = api_key

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def generate_toddler_dialogue(message, age):
    prompt = f"""
    Translate the following message into toddler language for a
    {age}-year-old, with actual toddler sentence structure and pronunciation. 
    Provide phonological, grammatical, and semantic explanations
    for the transformations. Each explanation should be in separate section
    for each speaker.
    
    Original Message: "{message}"

    For each speaker (A, B, or others), provide the transformed toddler speech,
    followed by the phonological, grammatical, and semantic explanations. The response
    should have the following format:

    Speaker: [Toddler dialogue for Speaker]
    Phonological explanation for speaker:
    [Explanation for Speaker's toddler speech phonologically]
    Grammatical explanation for Speaker:
    [Explanation for Speaker's toddler speech grammatically]
    Semantic explanation for Speaker:
    [Explanation for Speaker's toddler speech semantically]

    Ensure to return the responses in the same order as in the original message.
    """

    response = openai.ChatCompletion.create(model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=1000,
    temperature=0.7)
    result = response["choices"][0]["message"]["content"].strip()

    dialogue_data = {}
    speaker = None
    for line in result.split("\n"):
        line = line.strip()
        if line.startswith("Speaker:"):
            speaker = line.split(":")[0].strip()
            dialogue_data[speaker] = {
                "dialogue": line[len(f"Speaker: "):].strip(),
                "phonological": "",
                "grammatical": "",
                "semantic": "",
            }
        elif speaker:
            if line.startswith("Phonological explanation"):
                dialogue_data[speaker]["phonological"] = line.split(":")[1].strip()
            elif line.startswith("Grammatical explanation"):
                dialogue_data[speaker]["grammatical"] = line.split(":")[1].strip()
            elif line.startswith("Semantic explanation"):
                dialogue_data[speaker]["semantic"] = line.split(":")[1].strip()

    return dialogue_data
  

def translate_word(word, age):
    prompt = f"""
    Translate the word {word} into toddler language for a {age}-year-old, with an actual toddler phonology for the word. 
    Provide possible phonological variants and explanations for each variant.
    """
    response = openai.ChatCompletion.create(model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=200,
    temperature=0.7)
    result = response["choices"][0]["message"]["content"].strip()
    variants = []
    explanations = []
    for line in result.split("\n"):
        if line.strip():
            parts = line.split(":")
            if len(parts) == 2:
                variants.append(parts[0].strip())
                explanations.append(parts[1].strip())
    return variants, explanations

def translate_dialogue_ui():
    dialogue = st.text_area("Enter Dialoge:", height=150, help="Format: Speaker: [dialogue]")
    age = st.selectbox("Select Age", [1, 2, 3])
    
    if st.button("Translate"):
        if dialogue and api_key:
            dialogue_data = generate_toddler_dialogue(dialogue, age)
            for speaker, data in dialogue_data.items():
                st.subheader(f"{speaker}'s Original Dialogue")
                st.write(data["dialogue"])

                st.subheader(f"{speaker}'s Toddler Dialogue ({age}-year-old)")
                st.write(data["dialogue"])

                st.subheader(f"Phonological Explanation for {speaker}")
                st.write(data["phonological"])

                st.subheader(f"Grammatical Explanation for {speaker}")
                st.write(data["grammatical"])

                st.subheader(f"Semantic Explanation for {speaker}")
                st.write(data["semantic"])

            translation_data = {}
            explanation_data = {}

            for speaker, data in dialogue_data.items():
                translation_data[f"Original Dialogue {speaker}"] = [data["dialogue"]]
                translation_data[f"Toddler Dialogue {speaker}"] = [data["dialogue"]]

                explanation_data[f"Phonological Explanation {speaker}"] = [data["phonological"]]
                explanation_data[f"Grammatical Explanation {speaker}"] = [data["grammatical"]]
                explanation_data[f"Semantic Explanation {speaker}"] = [data["semantic"]]

            translation_df = pd.DataFrame(translation_data)
            explanation_df = pd.DataFrame(explanation_data)

            st.download_button("Download Translation Data (CSV)",
            data=translation_df.to_csv(index=False),
            file_name="toddler_translation.csv",
            mime="text/csv")
            st.download_button("Download Explanation Data (CSV)",
            data=explanation_df.to_csv(index=False),
            file_name="toddler_explantion.csv",
            mime="text/csv")

            st.download_button("Download Translation Data (Excel)",
            data=to_excel(translation_df),
            file_name="word_toddler_translation.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            st.download_button("Download Explanation Data (Excel)",
            data=to_excel(explanation_df),
            file_name="word_toddler_explanation.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def translate_word_ui():
    word = st.text_input("Enter Word:")
    age = st.selectbox("Select Age", [1, 2, 3])

    if st.button("Translate"):
        if word and api_key:
            variants, explanations = translate_word(word, age)

            st.subheader(f"Possible Variants for '{word}' in {age}-year-old Toddler Language")
            for i in range(len(variants)):
                st.write(f"Variant: {variants[i]}")
                st.write(f"Explanation: {explanations[i]}")

            word_data = {
                "Toddler Word Variant": variants,
                "Explanation": explanations
            }
            word_df = pd.DataFrame(word_data)

            st.download_button("Download Word Translation Data (CSV)",
            data=word_df.to_csv(index=False),
            file_name="word_toddler_translation.csv",
            mime="text/csv")
            st.download_button("Download Word Translation Data (Excel)",
            data=to_excel(word_df),
            file_name="word_toddler_translation.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def main():
    mode = st.radio("Select Mode", ["Translate Dialogue", "Translate Word"])

    if mode == "Translate Dialogue":
        translate_dialogue_ui()
    elif mode == "Translate Word":
        translate_word_ui()

st.write("About this app:")

about_this_app = """This application helps everyone to explore the world of toddlers by translating our speech into their speech,
with the aim to study developmental linguistics, and certainly also for overloading your mind the great amount of cuteness.
We use ChatGPT from OpenAI to analyze a grown-up text into what would a toddler say according to their age's milestone.
However, keep in mind that every toddler is different, this is only a natural language processing made by AI, so using this app
to talk with actual toddlers would not be helpful.

Let's explore the world with regressed speech of little ones and discover the wholly different form of language, or at least the form
we have forgotten for a long time! Enjoy!"""

st.write(about_this_app)

if __name__ == "__main__":
    main()





