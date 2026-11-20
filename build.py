"""Compatibility entry point for the LEYA MOULD source build.

The copied water-cup project exposed a large set of helper functions that are
still imported by the shared-template regression test.  The public mould
pages now come from :mod:`mould_build`; these small helpers keep the existing
template contract available without importing or modifying water-cup data.
"""
from __future__ import annotations

import html

from mould_build import CATALOG, generate, render_template


def sec(title, desc="", eyebrow="LEYA MOULD"):
    return '<div class="section__head"><div><span class="eyebrow">' + html.escape(str(eyebrow)) + '</span><h2 class="section__title">' + html.escape(str(title)) + '</h2><p class="copy-muted">' + html.escape(str(desc)) + '</p></div></div>'


def steps():
    rows = [("01", "Share the brief"), ("02", "Review feasibility"), ("03", "Approve the design"), ("04", "Trial and refine"), ("05", "Handover")]
    return '<div class="steps">' + ''.join('<article class="step"><strong>' + n + '</strong><h3>' + t + '</h3><p>Project-specific technical review.</p></article>' for n, t in rows) + '</div>'


def features():
    rows = [("Design review", "Review the drawing and intended process."), ("Project matching", "Record the mould family and machine interface."), ("Sample-led decisions", "Use approved samples and inspection points."), ("Clear communication", "Keep revisions and reference files together.")]
    return '<div class="grid grid--4">' + ''.join('<article class="benefit"><h3>' + t + '</h3><p>' + d + '</p></article>' for t, d in rows) + '</div>'


def contact():
    return '<section class="section"><div class="shell"><div class="contact-layout"><div><h2 class="section__title">Tell us about your mould project.</h2><p class="copy-muted">Share a drawing, sample or PDF and the target material.</p></div>' + render_template("contact-form", **{key: value for key, value in {"FORM_ARIA": "Mould project enquiry form", "FORM_REQUIRED_NOTE": "Company name, work email and project requirements are required.", "FORM_COMPANY": "Company Name", "FORM_COMPANY_PLACEHOLDER": "Your company", "FORM_EMAIL": "Work Email", "FORM_CATEGORY": "Mould Category", "FORM_CATEGORY_PLACEHOLDER": "e.g. PET preform, bottle cap", "FORM_QUANTITY": "Estimated Quantity", "FORM_QUANTITY_PLACEHOLDER": "e.g. annual volume or cavities", "FORM_COUNTRY": "Destination Country", "FORM_COUNTRY_PLACEHOLDER": "Country", "FORM_TYPE": "Inquiry Type", "FORM_TYPE_QUOTE": "Request a Quote", "FORM_TYPE_NEW": "New Mould Design", "FORM_TYPE_REVIEW": "Existing Mould Review", "FORM_TYPE_TECH": "Technical Consultation", "FORM_MATERIAL": "Target Material", "FORM_ADVISE": "Please advise", "FORM_OTHER": "Other / to be confirmed", "FORM_REQUIREMENTS": "Your Requirements", "FORM_REQUIREMENTS_PLACEHOLDER": "Part drawing, target resin, cavities, sample or PDF reference", "FORM_CONSENT": "I agree to the", "FORM_PRIVACY": "privacy policy", "FORM_SUBMIT": "Send Project Enquiry →"}.items()}) + '</div></div></section>'


def generate_site():
    return generate()


if __name__ == "__main__":
    generate_site()

