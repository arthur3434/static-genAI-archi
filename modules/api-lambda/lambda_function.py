import json
import boto3
import os
import re
import logging
from typing import Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Bedrock client
bedrock = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'eu-west-3'))

# Security constants
MAX_INPUT_LENGTH = 10000
MIN_INPUT_LENGTH = 10
DANGEROUS_PATTERNS = ['<script', 'javascript:', 'data:', 'vbscript:', 'onload=', 'onerror=']

def validate_input(role_description: str) -> tuple[bool, str]:
    """Validate input for security and content requirements."""
    if not role_description or len(role_description.strip()) == 0:
        return False, "Role description cannot be empty"
    if len(role_description) < MIN_INPUT_LENGTH:
        return False, f"Role description must be at least {MIN_INPUT_LENGTH} characters"
    if len(role_description) > MAX_INPUT_LENGTH:
        return False, f"Role description must be less than {MAX_INPUT_LENGTH} characters"
    
    role_lower = role_description.lower()
    for pattern in DANGEROUS_PATTERNS:
        if pattern in role_lower:
            return False, "Invalid characters detected in role description"
    
    return True, "Valid input"

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda function to process interview role descriptions and generate prompts using Amazon Bedrock."""
    request_id = context.aws_request_id if context else "unknown"
    logger.info(f"Processing request {request_id}")
    
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        role_description = body.get('role_description', '')
        is_valid, error_message = validate_input(role_description)
        if not is_valid:
            logger.warning(f"Invalid input in request {request_id}: {error_message}")
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,x-api-key',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Max-Age': '3600'
                },
                'body': json.dumps({'error': error_message})
            }
        
        prompt = create_interview_prompt(role_description)
        interview_preparation = generate_interview_questions(prompt)

        # Log what is received from Bedrock
        logger.info(f"Bedrock output: {json.dumps(interview_preparation)}")
        
        frontend_response = {'questions': []}
        rows = interview_preparation.get('questions') or interview_preparation.get('rows') or []

        for q in rows:
            suggested_answer_parts = []
            if q.get('good_answer_indicators'):
                suggested_answer_parts.append("What to look for:")
                for indicator in q['good_answer_indicators']:
                    suggested_answer_parts.append(f"• {indicator}")
            if q.get('red_flags'):
                suggested_answer_parts.append("\nRed flags to watch for:")
                for flag in q['red_flags']:
                    suggested_answer_parts.append(f"• {flag}")
            if q.get('evaluation_tips'):
                suggested_answer_parts.append(f"\nEvaluation tip: {q['evaluation_tips']}")
            suggested_answer = "\n".join(suggested_answer_parts) if suggested_answer_parts else "Look for specific examples and detailed explanations."

            frontend_response['questions'].append({
                'question': q.get('question', ''),
                'suggestedAnswer': suggested_answer,
                'category': q.get('category', 'General')
            })
        
        logger.info(f"Successfully generated questions for request {request_id}")
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,x-api-key',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Max-Age': '3600'
            },
            'body': json.dumps(frontend_response)
        }
        
    except Exception as e:
        logger.error(f"Error processing request {request_id}: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,x-api-key',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Max-Age': '3600'
            },
            'body': json.dumps({'error': 'Internal server error. Please try again later.'})
        }

def create_interview_prompt(role_description: str) -> str:
    """Create structured prompt for generating interview questions for interviewers."""
    prompt = f"""
You are an expert interview coach helping interviewers prepare for conducting interviews. Based on the following job description, create a comprehensive set of interview questions that an interviewer can use to assess candidates.

Job Description:
{role_description}

Please generate 8-12 interview questions that cover:
1. Technical skills and knowledge
2. Problem-solving and analytical thinking
3. Experience with relevant tools
4. Behavioral and situational questions
5. Role-specific scenarios
6. Leadership and teamwork (if applicable)
7. Cultural fit and motivation

For each question, provide:
- The main question
- A follow-up question
- What a good answer should include
- Red flags to watch out for
- How to evaluate the response

Format your response as a JSON object with the structure:
{{
    "questions": [
        {{
            "category": "Technical Skills",
            "question": "What is your experience with [specific technology]?",
            "follow_up": "Can you walk me through a project using this technology?",
            "good_answer_indicators": ["Specific examples", "Understanding of best practices"],
            "red_flags": ["Vague responses", "No specific examples"],
            "evaluation_tips": "Assess practical experience"
        }}
    ]
}}
Make sure questions are specific to the role and industry. Focus on helping the interviewer conduct an effective interview.
"""
    return prompt

def generate_interview_questions(prompt: str) -> Dict[str, Any]:
    """Call Amazon Bedrock to generate interview questions."""
    try:
        model_id = os.environ.get('BEDROCK_MODEL_ID', 'amazon.titan-text-lite-v1')
        enhanced_prompt = f"{prompt}\n\nPlease respond with only the JSON object."
        body = {
            "inputText": enhanced_prompt,
            "textGenerationConfig": {
                "maxTokenCount": 2000,
                "temperature": 0.7,
                "topP": 0.9
            }
        }
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType='application/json'
        )
        response_body = json.loads(response['body'].read())
        generated_text = response_body.get('results', [{}])[0].get('outputText', '')
        
        # Log raw model output
        logger.info(f"Raw model output: {generated_text}")
        
        # Extract JSON
        json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                if "questions" not in data:
                    data["questions"] = []
                return data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from model output: {e}")
                return {"questions": []}
        else:
            logger.warning("No JSON object found in model output.")
            return {"questions": []}
    except Exception as e:
        logger.error(f"Error calling Bedrock: {str(e)}", exc_info=True)
        return {"questions": [{
            "category": "Error",
            "question": "Unable to generate questions at this time.",
            "suggestedAnswer": "Please try again later."
        }]}
