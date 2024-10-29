from typing import Iterable, Union

from openai import Client



def data_to_string(data: dict[str, str]) -> str:
    return " ".join([f"{k}: {v}" for k, v in data.items()])


class BasicLLM:
    def __init__(self, base_url: str, api_key: str, model: str):

        # to make the client
        self.base_url = base_url
        self.api_key = api_key
        self.model_name = model
        self.client = Client(base_url=self.base_url, api_key=self.api_key)

        # what to extract from the text
        # and what kind of cypher llm generates
        # self.entity_types = entity_types

    def predict(
        self,
        data: dict[str, str],  # like role, role desc
        predict_what: str,  # like objective, audience
        amount: int = 10,
        predict_exclude: list[str] = None,
    ) -> Iterable[str]:
        # print("stream_response...")

        temperature: float = 0.0
        prompt_exclude_bad_examples = ""
        prompt_agent_foundational_knowledge = """---
        As the knowledge section in a system prompt, it is used to recall the common recognized, professional, famous theory/thesis/book/literary work.
        The best candidate will be a book/literary work. The second best candidate will be a theory/thesis. The third best candidate will be a chapter from some books/literary work/theory/thesis.
        If it is a theory/thesis/book/literary work, please provide the author in the corresponding description.
        This knowledge field is very important in terms of facutal correctness, PLEASE DO NOT GENERATE FAKE INFO as that results in misleading and we cannot afford to take the social responsibility.
        If you are not sure about the knowledge, please just return the title and description in a white space.
        """

        prompt_agent_objective = """---
        As the objective section in a system prompt, it is used to predict the goal, purpose, aim, target, intention, mission vision, of this AI agent.
        The title must be in strict format of "objective_<index>" only. 
        While the description contians the specific information. The description should be clear and concise, less than 20 words, in one sentence.
        """

        prompt_agent_gt_qa = """---
        As the ground truth Q&A section in a system prompt, it is used to predict ground truth examples. 
        Each generated example should contain a question and an answer (means if input amount is 2 , generated amount will be 4).
        The title must be in strict format of "question_<index>" or "answer_<index>". Each question and answer should be in a pair and their index should be the same.
        The description is the detail contain of the question/answer.
        Granularity: 
            - The question should be specific, like a question from exam paper. 
            - An ideal question should be from a single knowledge point from a section of a chapter of a book/literary book. 
            - A question should not be a very overview.
        """

        prompt_agent_other = ""

        if predict_exclude:
            # It is used to generate more answers for the same input as well as the previous answers.
            # The background is that the users are unsatisfied with the previous answers and want something more creative.
            temperature = 0.9

            prompt_exclude_bad_examples = f"""
            ---
            Exclude the following titles as they are considered not inspiring enough:
            {predict_exclude}
            Be more bold and creative in your generation."""

        example = {
            "amount": 2,
            "items": [
                {
                    "title": "dog",
                    "description": "a mammal human tamed for thousands of years",
                },
                {"title": "whale", "description": "a mammal living in the ocean"},
            ],
        }

        tbl_field2instruction = {
            "foundational_knowledge": prompt_agent_foundational_knowledge,
            "objective": prompt_agent_objective,
            "audience": prompt_agent_other,
            "ground_truth_qa": prompt_agent_gt_qa,
        }

        description_for_what = tbl_field2instruction.get(
            predict_what, prompt_agent_other
        )

        prompt = f"""

        You are a AI assistant who is good at llm prompt generation. Here is some information of a system prompt:

        Based on data:
        {data_to_string(data)}

        Please give {amount} of {predict_what} based on the data.
        
        Each {predict_what} needs to have description and title.
        Please return in json format.

        --- 
        Suppose we predict 2 animals, please return 

        {example}

        {description_for_what}
        {prompt_exclude_bad_examples}
        ---
        the return keywords "amount", "items", "title" and "description" are required and fixed.
        DO NOT PREPEND ANYTHING TO THE RETURNED STRING.
        Make sure the result can be parsed by json.loads().
        """

        print(f"{prompt=}")

        messages = [
            {
                "role": "system",
                "content": prompt,  # getattr(system_prompts , question.use_what_system_prompt,system_prompts.GENERAL_PPROMPT),
            },
        ]

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            stream=False,
        )

        # Extract the message from the response
        message = response.choices[0].message.content

        return message

    def get_response(self, message: str, chat_history: list[tuple], system_prompt: str) -> str:
        if not system_prompt:
            response = "Please generate an agent first by clicking the 'Generate Agent' button."
        else:
            # Prepare the conversation history for the API call
            messages = [
                {"role": "system", "content": system_prompt},
            ]

            # Add the previous conversation to the messages
            for user_msg, assistant_msg in chat_history:
                messages.append({"role": "user", "content": user_msg})
                messages.append({"role": "assistant", "content": assistant_msg})

            # Add the latest user message
            messages.append({"role": "user", "content": message})

            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0,
                    stream=False,
                )
                complete_response = response.choices[0].message.content
            except Exception as e:
                complete_response = f"An error occurred: {e}"
        return complete_response

if __name__ == "__main__":

    data = {
        "role": "销售人员",
        "role_desc": "你是一名来自西门子的销售人员，负责销售西门子的工业自动化产品",
        "audience": "工程师",
        "foundational_knowledge_1": "Industrial Automation: Hands On",
        "foundational_knowledge_2": "Programmable Logic Controllers (PLCs) Theory",
        "foundational_knowledge_3": "Siemens SIMATIC S7-1200/1500",
        "objective_1": "Inspire engineers to choose Siemens for revolutionary automation solutions.",
        "objective_2": "Showcase unmatched innovation in Siemens industrial automation to captivate engineers.",
        "objective_3": "Lead engineers to the forefront of automation with Siemens' cutting-edge technology.",
    }

    predict_what = "ground_truth_qa"
    amount = 3
    predict_exclude = [
        "What are the key features of Siemens SIMATIC S7-1200 PLCs that make them suitable for industrial automation?",
        "Siemens SIMATIC S7-1200 PLCs offer features such as integrated PROFINET communication, compact design, scalable performance, and a wide range of modules for flexibility, making them ideal for industrial automation.",
        "How does Siemens' innovation in industrial automation captivate engineers?",
        "Siemens captivates engineers with its continuous innovation in industrial automation by providing advanced technologies like digital twin, edge computing, and AI integration, which enhance efficiency and productivity.",
        "In what ways can Siemens' cutting-edge technology lead engineers to the forefront of automation?",
        "Siemens' cutting-edge technology, such as the TIA Portal and MindSphere, enables engineers to streamline processes, improve data analytics, and implement IoT solutions, positioning them at the forefront of automation.",
    ]

    import json

    #from app.utils.config import env

    llm = BasicLLM(
        # base_url=env.LLM_GATEWAY,
        # api_key=env.LLM_API_KEY,
        # model=env.LLM_MODEL,
        base_url='http://api-gw.motiong.net:5000/api/openai/eve/v1/',
        api_key='QjzR8b1Xq2c3Y4xN5z6Z7a8BcD9eF0G',
        model='gpt-4o'
    )

    llm_res = llm.predict(
        data=data,
        predict_what=predict_what,
        amount=amount,
        predict_exclude=predict_exclude,
    )

    try:
        dict_for_llm_res = json.loads(llm_res)
        amount = dict_for_llm_res["amount"]
        predicted = {}

        for i, item in enumerate(dict_for_llm_res["items"]):
            predicted[f"{predict_what}_{i}_title"] = item["title"]
            predicted[f"{predict_what}_{i}_desc"] = item["description"]

    except Exception as e:
        print(f"Error in parsing the llm response: {e}")

    print(f"{amount=}")
    print(predicted)
