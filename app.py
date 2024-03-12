from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import streamlit as st
import torch

def fix_state_dict(state_dict):
    fixed_state_dict = {key.replace('module.', ''): value for key, value in state_dict.items()}
    return fixed_state_dict

@st.cache(allow_output_mutation=True)
def load_model():
    model_name_or_path = "./t5_mss_small_torch"
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    checkpoint = torch.load("./checkpoint.ckpt", map_location=device)
    fixed_state_dict = fix_state_dict(checkpoint)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name_or_path)
    model.load_state_dict(fixed_state_dict)
    model.to(device)
    return tokenizer, model


model_name_or_path = "./t5_mss_small_torch"
checkpoint = torch.load("./checkpoint.ckpt")
fixed_state_dict = fix_state_dict(checkpoint)
tokenizer, model = load_model()
model.load_state_dict(fixed_state_dict)
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

def summarize(text):
    with torch.no_grad():
        inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=512, truncation=True)
        inputs = inputs.to(device)
        summary_ids = model.generate(inputs, max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

st.title("T5_mss_small Text Summarization App")

text = st.text_area("Text to summarize", "Paste your text here...", height=300)
if st.button("Summarize"):
    summary = summarize(text)
    st.subheader("Summary")
    st.write(summary)
# streamlit run app.py server.port 40 --server.address 0.0.0.0