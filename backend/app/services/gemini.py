# backend/app/services/gemini.py
"""
Purpose: Interface with Google Gemini API for core educational AI generation.
Responsibilities:
- Configure google-generativeai client using GEMINI_API_KEY.
- Force structured JSON outputs for Flashcards, Quizzes, and Summaries.
- Provide fallbacks for parsing failures to prevent API response drops.
- Implement strictly grounded prompts keeping model outputs within document text limits.
"""

import json
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self, api_key, model_name="gemini-3.1-flash-lite"):
        self.api_key = api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model_name = model_name
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"GeminiService initialized successfully with model {self.model_name}.")
        else:
            self.model = None
            self.model_name = None
            logger.warning("GeminiService: GEMINI_API_KEY is not configured. AI functions will fail.")

    def _call_gemini_json(self, prompt, system_instruction=None):
        """
        Helper method to call Gemini API requesting a JSON response.
        """
        if not self.model:
            raise ValueError("Gemini API key is not configured.")

        generation_config = {
            "response_mime_type": "application/json",
            "temperature": 0.2,
        }

        # Inject system instruction if present
        model_to_use = self.model
        if system_instruction:
            model_to_use = genai.GenerativeModel(
                self.model_name,
                system_instruction=system_instruction
            )

        response = model_to_use.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text

    def generate_summary(self, document_text):
        """
        Generates short summary, detailed summary, and key takeaways.
        Returns a dictionary.
        """
        prompt = (
            "Analyze the following text extracted from a document. "
            "Generate: \n"
            "1. A short summary (1-2 sentences, maximum 60 words).\n"
            "2. A detailed summary (comprehensive, 2-3 paragraphs).\n"
            "3. Key takeaways (a list of 3-7 core bullet points).\n\n"
            "You MUST respond ONLY with a JSON object in this exact schema:\n"
            "{\n"
            "  \"short_summary\": \"string\",\n"
            "  \"detailed_summary\": \"string\",\n"
            "  \"key_takeaways\": [\"takeaway 1\", \"takeaway 2\"]\n"
            "}\n\n"
            f"Document Text:\n{document_text[:25000]}"  # Cap text to stay within safety margins
        )

        system_instruction = (
            "You are an expert academic summary assistant. "
            "Extract and summarize information strictly based on the provided text. "
            "Do not introduce external facts or hallucinate."
        )

        raw_response = self._call_gemini_json(prompt, system_instruction)
        return json.loads(raw_response)

    def generate_flashcards(self, document_text):
        """
        Generates flashcard QA pairs with difficulty level.
        Returns a list of dictionaries.
        """
        prompt = (
            "Analyze the following text. Generate 5 to 10 active-recall flashcard study questions. "
            "Each flashcard must contain a clear, direct question, a comprehensive but concise answer, "
            "and a difficulty label ('Easy', 'Medium', or 'Hard') based on the complexity of the concept.\n\n"
            "You MUST respond ONLY with a JSON array of objects matching this exact schema:\n"
            "[\n"
            "  {\n"
            "    \"question\": \"string\",\n"
            "    \"answer\": \"string\",\n"
            "    \"difficulty\": \"Easy\" | \"Medium\" | \"Hard\"\n"
            "  }\n"
            "]\n\n"
            f"Document Text:\n{document_text[:20000]}"
        )

        system_instruction = (
            "You are a study card creator. Create educational questions based strictly "
            "on the provided text content. Do not generate questions requiring facts outside the document."
        )

        raw_response = self._call_gemini_json(prompt, system_instruction)
        return json.loads(raw_response)

    def generate_quizzes(self, document_text, count=5):
        """
        Generates multiple-choice quizzes with explanations.
        Returns a list of dictionaries.
        """
        prompt = (
            f"Analyze the following text. Generate exactly {count} multiple-choice questions (MCQs) to test understanding. "
            "Each MCQ must have a question, four options (a, b, c, d), the correct answer ('A', 'B', 'C', or 'D'), "
            "and a detailed pedagogical explanation of why the correct answer is correct and why the others are not.\n\n"
            "You MUST respond ONLY with a JSON array of objects matching this exact schema:\n"
            "[\n"
            "  {\n"
            "    \"question\": \"string\",\n"
            "    \"option_a\": \"string\",\n"
            "    \"option_b\": \"string\",\n"
            "    \"option_c\": \"string\",\n"
            "    \"option_d\": \"string\",\n"
            "    \"correct_answer\": \"A\" | \"B\" | \"C\" | \"D\",\n"
            "    \"explanation\": \"string\"\n"
            "  }\n"
            "]\n\n"
            f"Document Text:\n{document_text[:20000]}"
        )

        system_instruction = (
            "You are a professional test developer. Formulate questions testing critical concepts "
            "contained solely within the text. Ensure options are distinct, and the correct_answer key "
            "is exactly one capitalized letter: A, B, C, or D."
        )

        raw_response = self._call_gemini_json(prompt, system_instruction)
        return json.loads(raw_response)

    def generate_concept_explanation(self, concept, document_context):
        """
        Explains a specific concept term using only the document chunks.
        Returns a string.
        """
        if not self.model:
            raise ValueError("Gemini API key is not configured.")

        prompt = (
            f"Concept to explain: {concept}\n\n"
            f"Document Context:\n{document_context}\n\n"
            "Please explain the concept based ONLY on the provided Document Context. "
            "Do not use external knowledge or facts not present in this context. "
            "Answer in a well-structured educational format with markdown headings, bold terms, and bullet points. "
            "If the document context does not provide sufficient details about the concept, you MUST respond exactly with: "
            "\"The uploaded document does not contain enough information to explain this concept.\""
        )

        system_instruction = (
            "You are a strict, helpful grounded educational tutor. "
            "Never answer using external information. Rely ONLY on the provided Document Context."
        )

        try:
            model_to_use = genai.GenerativeModel(
                self.model_name,
                system_instruction=system_instruction
            )
            response = model_to_use.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Failed to generate concept explanation: {e}")
            return f"Failed to generate explanation. Error: {str(e)}"
