import json
import logging
from typing import Any, Dict, List, Optional

import vertexai
from google.api_core import exceptions as google_exceptions
from vertexai.generative_models import GenerationConfig, GenerativeModel, Part

from app.core.config import settings
from app.models.quiz_models import DifficultyLevel, QuestionType  # Import Enums

logger = logging.getLogger(__name__)

try:
    if not settings.GCP_PROJECT_ID:
        raise ValueError("GCP_PROJECT_ID is not set in the environment/config.")
    vertexai.init(project=settings.GCP_PROJECT_ID, location=settings.GCP_LOCATION)
    logger.info(
        f"Vertex AI initialized successfully for project '{settings.GCP_PROJECT_ID}' in location '{settings.GCP_LOCATION}'."
    )
except Exception as e:
    logger.error(f"Failed to initialize Vertex AI: {e}", exc_info=True)
    raise SystemExit(f"Fatal Error: Could not initialize Vertex AI: {e}")


def _parse_ai_json_response(response_text: str) -> Optional[Dict[str, Any]]:
    try:
        if response_text.strip().startswith("```json"):
            json_str = response_text.strip().split("```json")[1].split("```")[0].strip()
        elif response_text.strip().startswith("{") and response_text.strip().endswith(
            "}"
        ):
            json_str = response_text.strip()
        else:
            logger.warning(
                f"AI response does not appear to be well-formed JSON:\n{response_text}"
            )
            return None

        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(
            f"Failed to decode JSON from AI response: {e}\nResponse text:\n{response_text}",
            exc_info=True,
        )
        return None
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during JSON parsing: {e}\nResponse text:\n{response_text}",
            exc_info=True,
        )
        return None


def process_jd_with_ai(job_description_text: str) -> Optional[Dict[str, Any]]:
    if not vertexai._is_initialized():
        logger.error("Vertex AI is not initialized. Cannot process JD.")
        return None

    model = GenerativeModel(settings.VERTEX_AI_MODEL_NAME)

    prompt = f"""
    Analyze the following job description provided below. Based on the analysis, perform the following tasks:

    1.  **Determine Overall Difficulty:** Classify the role's overall difficulty level as "easy", "medium", or "hard" based on required skills, experience, and responsibilities.
    2.  **Generate Quiz Title:** Create a concise and relevant title for a technical quiz based on this job description (e.g., "Quiz for Mid-Level Frontend Engineer").
    3.  **Generate Optional Description:** Write a brief, one-sentence description for the quiz (optional).
    4.  **Generate Tags:** Extract or infer 5-10 relevant keyword tags representing the core skills, technologies, and experience level (e.g., "react", "typescript", "aws", "api", "junior", "sql", "data analysis").
    5.  **Generate Questions:** Create exactly 7 relevant technical or conceptual questions suitable for assessing candidates for this role.
        *   For each question:
            *   Provide the question `text`.
            *   Specify the `question_type` as either "{QuestionType.SINGLE_CHOICE.value}" or "{QuestionType.MULTIPLE_CHOICE.value}".
            *   Assign a `difficulty` level ("easy", "medium", or "hard") specific to that question.
            *   Provide 3-4 `answers`. Each answer must have `text` and an `is_correct` boolean field. Ensure EXACTLY ONE answer has `is_correct: true`.

    **Output Format:** Respond ONLY with a valid JSON object matching the following structure. Do not include any explanatory text before or after the JSON object.

    ```json
    {{
      "title": "string",
      "description": "string | null",
      "difficulty": "string (easy|medium|hard)",
      "tags": ["string"],
      "questions": [
        {{
          "text": "string",
          "question_type": "string ({QuestionType.SINGLE_CHOICE.value}|{QuestionType.MULTIPLE_CHOICE.value})",
          "difficulty": "string (easy|medium|hard)",
          "answers": [
            {{
              "text": "string",
              "is_correct": boolean
            }}
          ]
        }}
      ]
    }}
    ```

    **Job Description:**
    ---
    {job_description_text}
    ---
    """

    generation_config = GenerationConfig(
        response_mime_type="application/json",  # Use if model version supports it directly
        temperature=0.6,
        top_p=0.9,
        max_output_tokens=4096,
    )

    try:
        logger.info(
            f"Sending request to Vertex AI Gemini model '{settings.VERTEX_AI_MODEL_NAME}'..."
        )
        response = model.generate_content(
            [Part.from_text(prompt)],
            generation_config=generation_config,
        )
        logger.info("Received response from Vertex AI.")

        if not response.candidates or not response.candidates[0].content.parts:
            logger.warning("Vertex AI response was empty or invalid.")
            return None

        ai_response_text = response.candidates[0].content.parts[0].text
        # print(f"Raw AI Response:\n{ai_response_text}") # Uncomment for debugging

        parsed_data = _parse_ai_json_response(ai_response_text)

        if parsed_data:
            if not all(
                k in parsed_data for k in ["title", "difficulty", "tags", "questions"]
            ):
                logger.error("Parsed AI JSON response is missing required keys.")
                return None
            if not isinstance(parsed_data["questions"], list):
                logger.error("Parsed AI JSON 'questions' field is not a list.")
                return None
            try:
                parsed_data["difficulty"] = DifficultyLevel(
                    parsed_data["difficulty"].lower()
                )
                for q in parsed_data["questions"]:
                    if "difficulty" in q:
                        q["difficulty"] = DifficultyLevel(q["difficulty"].lower())
                    if "question_type" in q:
                        q["question_type"] = QuestionType(q["question_type"].lower())

            except ValueError as e:
                logger.error(
                    f"Invalid difficulty or question_type value in AI response: {e}"
                )
                return None

            logger.info("Successfully processed job description with AI.")
            return parsed_data
        else:
            logger.error("Failed to parse valid JSON from AI response.")
            return None

    except google_exceptions.GoogleAPIError as e:
        logger.error(f"Vertex AI API Error: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during AI processing: {e}", exc_info=True
        )
        return None


def extract_tags_with_ai(text_content: str, max_tags: int = 10) -> Optional[List[str]]:
    if not vertexai._is_initialized():
        logger.error("Vertex AI is not initialized. Cannot extract tags.")
        return None

    model = GenerativeModel(settings.VERTEX_AI_MODEL_NAME)
    prompt = f"""
    Analyze the following text content and extract the {max_tags} most relevant technical skills,
    tools, concepts, or experience level keywords as a list of tags.

    Output Format: Respond ONLY with a valid JSON list of strings. Example: ["python", "api", "sql", "data analysis"]

    Text Content:
    ---
    {text_content}
    ---
    """
    generation_config = GenerationConfig(temperature=0.2, max_output_tokens=512)

    try:
        logger.info("Requesting tag extraction from Vertex AI for text snippet...")
        response = model.generate_content(
            [Part.from_text(prompt)],
            generation_config=generation_config,
        )

        if not response.candidates or not response.candidates[0].content.parts:
            logger.warning("Vertex AI tag extraction response was empty.")
            return None

        ai_response_text = response.candidates[0].content.parts[0].text
        parsed_data = _parse_ai_json_response(ai_response_text)

        if isinstance(parsed_data, list) and all(
            isinstance(tag, str) for tag in parsed_data
        ):
            logger.info(f"Successfully extracted tags: {parsed_data}")
            return parsed_data
        else:
            logger.error(
                f"Failed to parse valid JSON list of tags from AI response: {ai_response_text}"
            )
            return None

    except Exception as e:
        logger.error(f"An error occurred during AI tag extraction: {e}", exc_info=True)
        return None
