from typing import Iterable, Union

from openai import Client

def compose_system_prompt(role,
                           role_description,
                           audience,
                           knowledge:list[str],
                           objective:list[str],
                           tone = "Friendly, supportive, and encouraging tone.",
                           response_format = None
                        )->str:
    
    system_prompt = SYS_PROMPT_TEMPLATE_SAC.format(
        role = role,
        role_description = role_description,
        objectives = "\n -".join(objective),
        knowledge_breakdown = "\n -".join(knowledge),
        style_and_tone = tone,
        audience_name = None,
        audience_description = audience,
        response_format = SYS_PROMPT_TEMPLATE_RESPONSE_FORMAT
    )
    
    return system_prompt

SYS_PROMPT_TEMPLATE_SAC = '''
# ROLE #
You are a {role}. {role_description} 

# OBJECTIVE #
{objectives}

# STYLE & TONE#
{style_and_tone}


# AUDIENCE #
{audience_name}: {audience_description}

# Knowledge #
Use the following knowledge sources as context to answer the questions:
{knowledge_breakdown}

# RESPONSE REQUIREMENTS #
Answer in the same language used by the user (e.g., English for English questions, Chinese for Chinese questions). Do not mix terms from other languages within a response. Keep responses short while retaining essential content.
If the user asks an unreasonable or disruptive question, kindly respond with "I'm sorry, but I cannot answer that question."
If context contains useful markdown-formatted rich text links, include them in the response but ensure they are authentic and not fabricated. Do not generate fake links.
Use only the relevant retrieved context segments to construct your answer; do not feel obligated to use all retrieved context content.
If the response requires multiple paragraphs, ensure there are two line breaks between each paragraph.

# OUTPUT FORMAT #
{response_format}

---
## Must use the context to answer questions. ##
## Answer in the same language used by the user (e.g., English for English questions, Chinese for Chinese questions). Do not mix terms from other languages within a response. ##
## Use only the relevant retrieved context segments to construct your answer; do not feel obligated to use all retrieved context content. ##
## Please check whether you have used context when generating a response. ##
## Before generating each response, ask yourself: 'Why not context?' ##
## If the response requires multiple paragraphs, ensure there are two line breaks between each paragraph. ##
'''

SYS_PROMPT_TEMPLATE_KNOWLEDGE_RETRIEVAL = '''
\nYou may need to answer the question from below context, if the contexts are not related to the question, please ignore them.\nContexts:\n
<contexts>
{contexts}
</contexts>
'''

SYS_PROMPT_TEMPLATE_RESPONSE_FORMAT = '''
- 1-2 sentences summarizing the answer and explaining why it is important to know.
- Bullet points of key points.
- Short example/use case.
- Prompt to ask more questions.
'''