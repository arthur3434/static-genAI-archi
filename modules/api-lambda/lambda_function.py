import json
import boto3
import os
from typing import Dict, Any
import re

# Initialize Bedrock client
bedrock = boto3.client('bedrock-runtime', region_name='${aws_region}')

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda function to process interview role descriptions and generate prompts using Amazon Bedrock.
    """
    try:
        # Parse the request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        # Extract role description from the request
        role_description = body.get('role_description', '')
        
        if not role_description:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'GET,OPTIONS,POST'
                },
                'body': json.dumps({
                    'error': 'role_description is required'
                })
            }
        
        # Create the prompt for the interview
        prompt = create_interview_prompt(role_description)
        
        # Call Bedrock to generate interview questions for the interviewer
        interview_preparation = generate_interview_questions(prompt)
        
        # Transform the response to match frontend expected format
        frontend_response = {
            'questions': []
        }
        
        if 'questions' in interview_preparation:
            for q in interview_preparation['questions']:
                # Combine good answer indicators and evaluation tips into suggested answer
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
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,OPTIONS,POST'
            },
            'body': json.dumps(frontend_response)
        }
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,OPTIONS,POST'
            },
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}'
            })
        }

def create_interview_prompt(role_description: str) -> str:
    """
    Create a structured prompt for generating interview questions for interviewers preparing to conduct interviews.
    """
    prompt = f"""
You are an expert interview coach helping interviewers prepare for conducting interviews. Based on the following job description, create a comprehensive set of interview questions that an interviewer can use to assess candidates for this position.

Job Description:
{role_description}

Please generate 8-12 interview questions that cover:
1. Technical skills and knowledge relevant to the role
2. Problem-solving and analytical thinking
3. Experience with relevant tools and technologies
4. Behavioral and situational questions
5. Role-specific scenarios
6. Leadership and teamwork (if applicable)
7. Cultural fit and motivation

For each question, provide:
- The main question to ask
- A follow-up question to dig deeper
- What a good answer should include
- Red flags to watch out for
- How to evaluate the response

Format your response as a JSON object with the following structure:
{{
    "questions": [
        {{
            "category": "Technical Skills",
            "question": "What is your experience with [specific technology]?",
            "follow_up": "Can you walk me through a specific project where you used this technology?",
            "good_answer_indicators": [
                "Specific examples with details",
                "Understanding of best practices",
                "Mention of challenges faced and how they were solved"
            ],
            "red_flags": [
                "Vague or generic responses",
                "Inability to provide specific examples",
                "Lack of understanding of basic concepts"
            ],
            "evaluation_tips": "Look for depth of knowledge and practical experience"
        }},
        {{
            "category": "Problem Solving",
            "question": "How would you approach [specific scenario]?",
            "follow_up": "What would you do if [complication] occurred?",
            "good_answer_indicators": [
                "Structured approach to problem-solving",
                "Asks clarifying questions",
                "Considers multiple solutions"
            ],
            "red_flags": [
                "Jumping to conclusions without analysis",
                "Unable to think through the problem step by step",
                "Giving up easily when faced with obstacles"
            ],
            "evaluation_tips": "Assess their logical thinking process and persistence"
        }},
        {{
            "category": "Behavioral",
            "question": "Tell me about a time when you had to work with a difficult team member.",
            "follow_up": "How did you resolve the conflict and what was the outcome?",
            "good_answer_indicators": [
                "Shows emotional intelligence and conflict resolution skills",
                "Focuses on solutions rather than blame",
                "Demonstrates learning from the experience"
            ],
            "red_flags": [
                "Blames others entirely",
                "Shows inability to work with different personalities",
                "No clear resolution or learning"
            ],
            "evaluation_tips": "Look for maturity, empathy, and problem-solving approach"
        }},
        {{
            "category": "Motivation",
            "question": "Why are you interested in this role and our company?",
            "follow_up": "What do you know about our recent projects or company culture?",
            "good_answer_indicators": [
                "Specific knowledge about the company",
                "Clear connection between their goals and the role",
                "Genuine enthusiasm and research"
            ],
            "red_flags": [
                "Generic answers that could apply to any company",
                "No research about the company",
                "Focus only on salary or benefits"
            ],
            "evaluation_tips": "Assess their preparation, motivation, and cultural fit"
        }}
    ]
}}

Make sure the questions are specific to the role and industry mentioned in the description. Focus on helping the interviewer conduct an effective interview.
"""
    return prompt

def generate_interview_questions(prompt: str) -> Dict[str, Any]:
    """
    Call Amazon Bedrock to generate interview questions.
    """
    try:
        model_id = os.environ.get('BEDROCK_MODEL_ID', 'amazon.titan-text-lite-v1')

        if 'titan' in model_id.lower():
            # Add a clear instruction to the prompt for better JSON output
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
            
        else: # For other models like Claude
            enhanced_prompt = f"\n\nHuman: {prompt}\n\nAssistant: Please provide your response as a single JSON object. Do not include any other text."
            body = {
                "prompt": enhanced_prompt,
                "max_tokens_to_sample": 2000,
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            response = bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            generated_text = response_body.get('completion', '')
        
        # Use regex to find and extract the JSON object
        json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
        if json_match:
            try:
                json_string = json_match.group(0)
                return json.loads(json_string)
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON from model output: {e}")
                print(f"Raw model output: {generated_text}")
                # Fallback to the same error structure as the main handler
                return {
                    "questions": [{
                        "category": "Error",
                        "question": "Failed to parse model response. Please try again.",
                        "suggestedAnswer": f"Error: {str(e)}"
                    }]
                }
        else:
            # Fallback if no JSON object is found in the response
            print(f"No JSON object found in model output: {generated_text}")
            return {
                "questions": [{
                    "category": "Error",
                    "question": "Model did not return a valid JSON response. Please check your prompt.",
                    "suggestedAnswer": ""
                }]
            }
    
    except Exception as e:
        print(f"Error calling Bedrock: {str(e)}")
        # Return the fallback response as you already have it
        return {
            "questions": [{
                "category": "Error",
                "question": "Unable to generate questions at this time. Please try again.",
                "suggestedAnswer": f"Error: {str(e)}"
            }]
        }