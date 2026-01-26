
import streamlit as st
import pickle
import re

# Load model and vectorizer
with open('rf_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

st.title("Fake Job Post Detection")

# Input fields
job_title = st.text_input("Job Title")
location = st.text_input("Location")
description = st.text_area("Job Description")
requirements = st.text_area("Requirements")
benefits = st.text_area("Benefits")

# Known scam keywords
scam_keywords = ["paytm", "urgent", "no experience", "daily payout", "whatsapp", "click here", "work from home"]

# Non-corporate email domains
free_email_domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "rediffmail.com"]

# Combine inputs and predict
if st.button("Predict"):
    full_text = f"{job_title} {location} {description} {requirements} {benefits}"

    if full_text.strip() == "":
        st.warning("Please enter job post details.")
    else:
        # 1. Keyword flags
        keyword_flags = [kw for kw in scam_keywords if kw in full_text.lower()]
        keyword_flagged = len(keyword_flags) > 0

        # 2. Email domain check
        emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", full_text)
        email_flagged = any(any(domain in email for domain in free_email_domains) for email in emails)

        # 3. Check description length
        short_description = len(description.strip()) < 50

        # 4. Vectorize and predict
        vect_input = vectorizer.transform([full_text])
        prediction = model.predict(vect_input)[0]

        st.markdown("### Prediction Result:")

        # Combine rules
        if keyword_flagged:
            st.warning(f"Suspicious keywords found: {', '.join(keyword_flags)}")
            st.error("This job post is classified as FAKE (keyword-based).")
        elif email_flagged:
            st.warning(f"Suspicious email domain found in: {', '.join(emails)}")
            st.error(" This job post is classified as FAKE (email domain-based).")
        elif short_description:
            st.warning("Job description is too vague or short.")
            st.error(" This job post is classified as FAKE (vague content).")
        elif prediction == 1:
            st.error("This job post is classified as FAKE (model-based).")
        else:
            st.success("This job post is classified as REAL.")
