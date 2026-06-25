import unittest

from backend.app.services.risk_intelligence import (
    build_clause_coverage,
    detect_document_type,
    extract_language_risks,
)


class RiskIntelligenceTests(unittest.TestCase):
    def test_detects_hr_policy_manual_from_title_and_sections(self):
        text = """
        Human Resources Policy Manual 2025

        This manual includes Equal Employment Opportunity, harassment policy,
        employment authorization, recruitment, performance evaluations,
        telecommuting policy, compensation policies, family and medical leave,
        sick leave, military leave, personnel files, and disciplinary action.
        """

        result = detect_document_type(text, "Hr-Policy-Manual-202503.pdf")

        self.assertEqual(result["type"], "hr_policy_manual")
        self.assertEqual(result["label"], "HR Policy Manual")
        self.assertGreaterEqual(result["confidence"], 0.5)

    def test_separates_hr_manual_from_education_domain_words(self):
        text = """
        Human Resources Policy Manual 2025
        Pierpont Community and Technical College

        This policy manual covers equal employment opportunity, harassment,
        employee conduct, performance evaluations, compensation policies,
        family and medical leave, sick leave, personnel files, and telecommuting.
        """

        result = detect_document_type(text, "college-hr-policy-manual.pdf")

        self.assertEqual(result["type"], "hr_policy_manual")
        self.assertNotEqual(result["type"], "education_hr_policy")

    def test_extracts_high_risk_language(self):
        text = """
        The company may change this policy at its sole discretion and without notice.
        """

        risks = extract_language_risks(text)
        phrases = {risk["phrase"] for risk in risks}

        self.assertIn("sole discretion", phrases)
        self.assertIn("without notice", phrases)

    def test_hr_policy_manual_clause_coverage_detects_present_sections(self):
        text = """
        Equal Employment Opportunity
        Harassment and workplace conduct
        Employment authorization and recruitment
        Performance evaluation process
        Compensation and payroll
        Family and Medical Leave, annual leave, and sick leave
        Telecommuting and remote work
        Confidentiality and personnel files
        """

        coverage = build_clause_coverage(text, "hr_policy_manual")

        self.assertGreaterEqual(coverage["coverage_percent"], 75)
        self.assertGreaterEqual(len(coverage["present"]), 6)


if __name__ == "__main__":
    unittest.main()
