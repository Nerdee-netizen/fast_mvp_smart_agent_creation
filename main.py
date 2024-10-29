import gradio as gr
from llm.basic_llm import BasicLLM
from llm.prompt_management import compose_system_prompt
import openai
import json
from app.utils.config import env

llm = BasicLLM(
    base_url='http://api-gw.motiong.net:5000/api/openai/eve/v1/',
    api_key='QjzR8b1Xq2c3Y4xN5z6Z7a8BcD9eF0G',
    model='gpt-4o'
)

# Function to generate agent description based on role
def generate_agent_description(role):
    predict_what="role_desc"

    description = llm.predict(
        data={"role": role},
        predict_what=predict_what,
        amount=1,
    )

    try:
        dict_for_llm_res = json.loads(description)
        amount = dict_for_llm_res["amount"]
        predicted = {}

        for i, item in enumerate(dict_for_llm_res["items"]):
            predicted[f"{predict_what}_{i}_title"] = item["title"]
            predicted[f"{predict_what}_{i}_desc"] = item["description"]
            res = item["description"]

    except Exception as e:
        print(f"Error in parsing the llm response: {e}")

    print(f"{amount=}")
    print(predicted)

    return res

# Function to generate agent description based on role
def generate_agent_audience(role, description):
    predict_what="audience"

    description = llm.predict(
        data={
            "role": role,
            "role_desc": description
            },
        predict_what=predict_what,
        amount=1,
    )

    try:
        dict_for_llm_res = json.loads(description)
        amount = dict_for_llm_res["amount"]
        predicted = {}

        for i, item in enumerate(dict_for_llm_res["items"]):
            predicted[f"{predict_what}_{i}_title"] = item["title"]
            predicted[f"{predict_what}_{i}_desc"] = item["description"]
            res = item["description"]

    except Exception as e:
        print(f"Error in parsing the llm response: {e}")

    print(f"{amount=}")
    print(predicted)

    return res

# Function to generate agent description based on role
def generate_agent_foundational_knowledge(role, description, audience)->list[str]:
    predict_what="foundational_knowledge"

    description = llm.predict(
        data={
            "role": role,
            "role_desc": description,
            "audience": audience
            },
        predict_what=predict_what,
        amount=3,
    )

    try:
        dict_for_llm_res = json.loads(description)
        amount = dict_for_llm_res["amount"]
        predicted = {}
        res = []

        for i, item in enumerate(dict_for_llm_res["items"]):
            predicted[f"{predict_what}_{i}_title"] = item["title"]
            predicted[f"{predict_what}_{i}_desc"] = item["description"]
            res.append(f'{item["title"]}： {item["description"]}')

    except Exception as e:
        print(f"Error in parsing the llm response: {e}")

    print(f"{amount=}")
    print(predicted)

    return res

# Function to generate recommended knowledge based on role and audience
def get_preset_foundational_knowledge(role, audience):
    knowledge = []
    if role == "Teacher":
        knowledge = [
            "Educational Psychology by John Dewey",
            "Theories of Learning by Jean Piaget",
            "How Learning Works by Susan Ambrose"
        ]
    elif role == "Interviewer":
        knowledge = [
            "Interviewing Techniques for Managers by Carolyn M. Feather",
            "Cracking the Coding Interview by Gayle Laakmann McDowell",
            "Behavioral Interview Guide by SHRM"
        ]
    else:
        knowledge = [
            "Custom Knowledge - Tailored for specific use cases",
            "The Art of Learning by Josh Waitzkin"
        ]

    return knowledge

# Function to generate more foundational knowledge options
def get_more_preset_knowledge(role, audience):
    additional_knowledge = []
    if role == "Teacher":
        additional_knowledge = [
            "Mindset by Carol Dweck",
            "Visible Learning by John Hattie"
        ]
    elif role == "Interviewer":
        additional_knowledge = [
            "Topgrading by Bradford Smart",
            "Hire with Your Head by Lou Adler"
        ]
    else:
        additional_knowledge = [
            "Mastery by Robert Greene",
            "Outliers by Malcolm Gladwell"
        ]

    return additional_knowledge

# Function to generate objectives based on role, audience, and knowledge
def get_preset_objectives(role, audience, knowledge):
    objectives = []
    if role == "Teacher":
        objectives = [
            f"Teach and provide feedback on assignments for {audience}.",
            f"Assist {audience} with personalized learning plans."
        ]
    elif role == "Interviewer":
        objectives = [
            f"Conduct mock interviews for {audience} and provide evaluations.",
            f"Evaluate job applications for {audience}."
        ]
    else:
        objectives = [
            f"Support {audience} with custom tasks and queries.",
            f"Provide expertise based on uploaded knowledge."
        ]

    if knowledge:
        objectives.append(f"Utilize uploaded knowledge to assist {audience}.")

    return objectives

# Function to toggle the enable/disable state of a textbox
def toggle_enable_disable(toggle_state, textbox):
    return textbox.update(interactive=toggle_state)

# Function to handle sending messages to the chatbot
# def send_message(message, chat_history):
#     # Simulate a response from the agent
#     response = "This is a response from the agent."
#     chat_history.append({"role": "user", "content": message})
#     chat_history.append({"role": "assistant", "content": response})
#     return "", chat_history

def send_message(message, chat_history, system_prompt):
    # Simulate a response from the agent
    response = llm.get_response(message, chat_history, system_prompt)
    # Append the user's message and the bot's response to the chat history
    chat_history = chat_history + [(message, response)]
    # Clear the input box
    return "", chat_history

# 定义确认按钮点击事件的函数
def confirm_role(role):
    description = generate_agent_description(role)
    return description

# 定义确认按钮点击事件的函数
def confirm_role_desc(role, role_desc):
    audience = generate_agent_audience(role, role_desc)
    return audience

def on_btn_confirm_audience_clicked(role, role_desc, audience):
    foundational_knowledge = generate_agent_foundational_knowledge(role, role_desc, audience)

    return foundational_knowledge

def on_next_btn_1_clicked(tabs: gr.Tabs, id):
    print("test", id)

    return tabs.select(id)

def switch_tab(tab_index):
    return gr.Tabs.update(selected=tab_index)

def on_next_btn_2_clicked(role, role_desc, audience, knowledge1, knowledge2, knowledge3):
    '''To generate Objectives
    Parameters:
    inputs:
    role: str
    role_desc: str
    audience: str
    knowledge: list[str]
    outputs:
    objectives: list[str]
    '''
    objectives = generate_agent_objectives(role, role_desc, audience, knowledge1, knowledge2, knowledge3)

    return objectives

def generate_agent_objectives(role, role_desc, audience, knowledge1, knowledge2, knowledge3):
    predict_what="objectives"

    llm_response = llm.predict(
        data={
            "role": role,
            "role_desc": role_desc,
            "audience": audience,
            "foundational_knowledge_1": knowledge1,
            "foundational_knowledge_2": knowledge2,
            "foundational_knowledge_3": knowledge3,
        },

        predict_what=predict_what,
        amount=4
    )

    try:
        dict_for_llm_res = json.loads(llm_response)
        amount = dict_for_llm_res["amount"]
        predicted = {}
        res = []

        for i, item in enumerate(dict_for_llm_res["items"]):
            predicted[f"{predict_what}_{i}_title"] = item["title"]
            predicted[f"{predict_what}_{i}_desc"] = item["description"]
            res.append(item["description"])

    except Exception as e:
        print(f"Error in parsing the llm response: {e}")

    print(f"{amount=}")
    print(predicted)

    return res

def on_btn_generate_agent_clicked(role, role_desc, audience, knowledge1, knowledge2, knowledge3, 
                                  objective1, objective2, objective3, objective4):

    system_prompt = compose_system_prompt(
        role, 
        role_desc, 
        audience, 
        knowledge=[knowledge1, knowledge2, knowledge3],
        objective=[objective1, objective2, objective3, objective4]
    )

    greetings = ("assistant", "Hi! Your agent has been created.")
    # Return both the initial chatbot message and the system_prompt
    return [ [greetings], system_prompt ]


# Gradio Interface
def gradio_interface():
    role_options = ["Teacher", "Interviewer", "Write yourself"]

    # Create Gradio blocks for user input
    with gr.Blocks(theme="dark") as demo:
        system_prompt_state = gr.State("")
        with gr.Tabs() as tabs:
            with gr.Tab("Agent Role and Audience", id="t0") as t0:
                with gr.Row():
                    with gr.Column(scale=8):
                        role_dropdown = gr.Dropdown(choices=role_options, label="Agent Role", value="Teacher")
                        role = gr.Textbox(label="Edit Role", placeholder="Enter or edit the agent role here...", interactive=True)
                    with gr.Column(scale=2):
                        confirm_role_btn = gr.Button("Confirm Role")

                with gr.Row():
                    with gr.Column(scale=8):
                        role_description = gr.Textbox(label="Agent Description", placeholder="Generated from agent role", interactive=True)
                    with gr.Column(scale=2):
                        confirm_role_desc_btn = gr.Button("Confirm Role Description")
                with gr.Row():
                    with gr.Column(scale=8):
                        audience = gr.Textbox(label="Agent Audience", placeholder="Generated from role and description", interactive=True)
                    with gr.Column(scale=2):
                        confirm_role_audience_btn = gr.Button("Confirm Audience")
                next_btn_1 = gr.Button("Next")# 添加 Agent Role 文本框和确认按钮
                    

            with gr.Tab("Knowledge", id="t1") as t1:
                # Initial Foundational Knowledge
                preset_knowledge = get_preset_foundational_knowledge("Teacher", "Students")

                # Display non-editable foundational knowledge with enable/disable buttons
                with gr.Row():
                    knowledge_textbox_1 = gr.Textbox(label="Knowledge 1", value=preset_knowledge[0], interactive=False)
                    toggle_checkbox_1 = gr.Checkbox(label="Enable Knowledge 1", value=True)
                    toggle_checkbox_1.change(toggle_enable_disable, inputs=[toggle_checkbox_1, knowledge_textbox_1], outputs=knowledge_textbox_1)

                with gr.Row():
                    knowledge_textbox_2 = gr.Textbox(label="Knowledge 2", value=preset_knowledge[1], interactive=False)
                    toggle_checkbox_2 = gr.Checkbox(label="Enable Knowledge 2", value=True)
                    toggle_checkbox_2.change(toggle_enable_disable, inputs=[toggle_checkbox_2, knowledge_textbox_2], outputs=knowledge_textbox_2)

                with gr.Row():
                    knowledge_textbox_3 = gr.Textbox(label="Knowledge 3", value=preset_knowledge[2], interactive=False)
                    toggle_checkbox_3 = gr.Checkbox(label="Enable Knowledge 3", value=True)
                    toggle_checkbox_3.change(toggle_enable_disable, inputs=[toggle_checkbox_3, knowledge_textbox_3], outputs=knowledge_textbox_3)

                # Button to generate more foundational knowledge
                more_knowledge_textbox_1 = gr.Textbox(label="Additional Knowledge 1", interactive=False, visible=False)
                more_knowledge_textbox_2 = gr.Textbox(label="Additional Knowledge 2", interactive=False, visible=False)

                def add_more_knowledge(role, audience):
                    new_knowledge = get_more_preset_knowledge(role, audience)
                    return gr.Textbox.update(value=new_knowledge[0], visible=True), gr.Textbox.update(value=new_knowledge[1], visible=True)

                add_knowledge_btn = gr.Button("Generate More Knowledge")
                add_knowledge_btn.click(add_more_knowledge, [role, audience], [more_knowledge_textbox_1, more_knowledge_textbox_2])

                next_btn_2 = gr.Button("Next")

            with gr.Tab("Objective", id="t2") as t2:
                # Editable and selectable objectives with checkbox to toggle enable/disable
                with gr.Row():
                    objective_textbox_1 = gr.Textbox(label="Objective 1", interactive=True, placeholder="Editable Objective 1", lines=3)
                    toggle_checkbox_1 = gr.Checkbox(label="Enable Objective 1", value=True)
                    toggle_checkbox_1.change(toggle_enable_disable, inputs=[toggle_checkbox_1, objective_textbox_1], outputs=objective_textbox_1)

                with gr.Row():
                    objective_textbox_2 = gr.Textbox(label="Objective 2", interactive=True, placeholder="Editable Objective 2", lines=3)
                    toggle_checkbox_2 = gr.Checkbox(label="Enable Objective 2", value=True)
                    toggle_checkbox_2.change(toggle_enable_disable, inputs=[toggle_checkbox_2, objective_textbox_2], outputs=objective_textbox_2)

                with gr.Row():
                    objective_textbox_3 = gr.Textbox(label="Objective 3", interactive=True, placeholder="Editable Objective 3", lines=3)
                    toggle_checkbox_3 = gr.Checkbox(label="Enable Objective 3", value=True)
                    toggle_checkbox_3.change(toggle_enable_disable, inputs=[toggle_checkbox_3, objective_textbox_3], outputs=objective_textbox_3)

                with gr.Row():
                    objective_textbox_4 = gr.Textbox(label="Objective 4", interactive=True, placeholder="Editable Objective 4", lines=3)
                    toggle_checkbox_4 = gr.Checkbox(label="Enable Objective 4", value=True)
                    toggle_checkbox_4.change(toggle_enable_disable, inputs=[toggle_checkbox_4, objective_textbox_4], outputs=objective_textbox_4)

                # Initially hidden Objective 5 field
                objective_textbox_5 = gr.Textbox(label="Objective 5", interactive=True, placeholder="Editable Objective 5", visible=False, lines=3)
                toggle_checkbox_5 = gr.Checkbox(label="Enable Objective 5", value=True, visible=False)
                toggle_checkbox_5.change(toggle_enable_disable, inputs=[toggle_checkbox_5, objective_textbox_5], outputs=objective_textbox_5)

                # "Add Objective" button to reveal Objective 5
                def add_objective():
                    return gr.Textbox.update(visible=True), gr.Checkbox.update(visible=True)

                add_objective_btn = gr.Button("Add Objective")
                add_objective_btn.click(add_objective, [], [objective_textbox_5, toggle_checkbox_5])

                # Generate Objectives Button
                def update_objectives_ui(role, audience):
                    objectives = get_preset_objectives(role, audience, preset_knowledge)  # Use knowledge generated earlier
                    return objectives[0], objectives[1], objectives[2] if len(objectives) > 2 else "", objectives[3] if len(objectives) > 3 else ""

                generate_objectives_btn = gr.Button("Generate Objectives")
                generate_objectives_btn.click(update_objectives_ui, [role, audience], [objective_textbox_1, objective_textbox_2, objective_textbox_3, objective_textbox_4])

                generate_agent_btn = gr.Button("Generate Agent")

            with gr.Tab("Preview and Share", id="t3") as t3:
                # Organize into two columns: Preview on the left, Share on the right
                with gr.Row():
                    with gr.Column(scale=1):
                        preview = gr.Textbox(label="Agent Preview", value="Agent details will appear here after creation.", interactive=False)
                        # Chat interface placeholder
                        chatbot = gr.Chatbot(label="Chat with the Agent", placeholder="This is where you will chat with your agent.")
                        msg_input = gr.Textbox(label="Your message", placeholder="Enter your message to the agent...")
                        send_msg_btn = gr.Button("Send")
                    with gr.Column(scale=1):
                        # Generated link placeholder
                        share_link = gr.Textbox(label="Shareable Link", value="Link will be generated here.", interactive=False)
                        # QR code placeholder
                        qr_code = gr.Image(label="Scan to Share Agent", value=None, interactive=False)
                        share_btn = gr.Button("Generate QR Code and Link")

        # Attach the send_message function to the send button
        send_msg_btn.click(
                send_message,
                inputs=[msg_input, chatbot, system_prompt_state],
                outputs=[msg_input, chatbot]
            )

        # 设置下拉菜单选择事件，将选择的值填充到文本框中
        role_dropdown.change(fn=lambda x: x, inputs=role_dropdown, outputs=role)


        # 将确认按钮点击事件与函数关联
        confirm_role_btn.click(confirm_role, inputs=role, outputs=role_description)
        
        confirm_role_desc_btn.click(confirm_role_desc, inputs=[role, role_description], outputs=audience)
        confirm_role_audience_btn.click(on_btn_confirm_audience_clicked, 
                                        inputs=[role, role_description, audience], 
                                        outputs=[knowledge_textbox_1, knowledge_textbox_2, knowledge_textbox_3])

        # 设置下一步按钮点击事件
        # next_btn_1.click(fn=on_next_btn_clicked, 
        #                  outputs=[tabs,t1])
        #next_btn_1.click(switch_tab, inputs=None, outputs=tabs, fn_kwargs={"tab_index": 2})
        next_btn_2.click(on_next_btn_2_clicked, 
                         inputs=[role, role_description, audience, knowledge_textbox_1, knowledge_textbox_2, knowledge_textbox_3], 
                         outputs=[objective_textbox_1, objective_textbox_2, objective_textbox_3, objective_textbox_4])

        generate_agent_btn.click(
                    on_btn_generate_agent_clicked,
                    inputs=[
                        role, 
                        role_description, 
                        audience, 
                        knowledge_textbox_1, 
                        knowledge_textbox_2, 
                        knowledge_textbox_3,
                        objective_textbox_1,
                        objective_textbox_2,
                        objective_textbox_3,
                        objective_textbox_4
                    ],
                    outputs=[chatbot, system_prompt_state]
                )
    demo.launch(show_error=True)

# Run the Gradio app
gradio_interface()