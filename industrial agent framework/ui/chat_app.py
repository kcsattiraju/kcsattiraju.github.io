import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

API_BASE_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Agentic AI Platform",
    page_icon="🤖",
    layout="wide",
)


# ============================================================
# API FUNCTIONS
# ============================================================

def get_agents():

    try:

        response = requests.get(
            f"{API_BASE_URL}/agents",
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            return data.get(
                "agents",
                []
            )

        return []

    except Exception as e:

        st.error(
            f"Could not load agents: {e}"
        )

        return []


# ------------------------------------------------------------

def get_tools():

    try:

        response = requests.get(
            f"{API_BASE_URL}/tools",
            timeout=15
        )

        if response.status_code == 404:

            st.sidebar.warning(
                "Tools API not found."
            )

            return []

        response.raise_for_status()

        data = response.json()

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            return data.get(
                "tools",
                []
            )

        return []

    except Exception as e:

        st.sidebar.warning(
            f"Could not load tools: {e}"
        )

        return []


# ------------------------------------------------------------

def get_agent_tools(
    agent_id
):

    try:

        response = requests.get(
            f"{API_BASE_URL}/tools/agent/{agent_id}",
            timeout=15
        )

        if response.status_code != 200:
            return []

        data = response.json()

        if isinstance(data, list):
            return data

        return []

    except Exception:

        return []


# ------------------------------------------------------------

def create_agent(
    name,
    description,
    goal,
    system_prompt,
    tools
):

    payload = {
        "name": name,
        "description": description,
        "goal": goal,
        "system_prompt": system_prompt,
        "tools": tools,
    }


    return requests.post(
        f"{API_BASE_URL}/agents",
        json=payload,
        timeout=30
    )


# ------------------------------------------------------------

def chat_with_agent(
    agent_id,
    message
):

    payload = {
        "message": message
    }


    return requests.post(
        f"{API_BASE_URL}/agents/{agent_id}/chat",
        json=payload,
        timeout=180
    )


# ============================================================
# HELPERS
# ============================================================

def get_agent_id(
    agent
):

    return (
        agent.get("id")
        or agent.get("agent_id")
    )


# ------------------------------------------------------------

def get_agent_name(
    agent
):

    return (
        agent.get("name")
        or agent.get("agent_name")
        or "Unnamed Agent"
    )


# ------------------------------------------------------------

def extract_chat_response(
    response
):

    try:

        data = response.json()

    except Exception:

        return response.text


    if isinstance(
        data,
        str
    ):
        return data


    if isinstance(
        data,
        dict
    ):

        possible_fields = [

            "response",
            "answer",
            "output",
            "result",
            "message",
            "content",
        ]


        for field in possible_fields:

            value = data.get(
                field
            )

            if value:

                if isinstance(
                    value,
                    dict
                ):

                    return value.get(
                        "content",
                        str(value)
                    )

                return str(
                    value
                )


    return str(
        data
    )


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = {}


# ============================================================
# LOAD TOOLS
# ============================================================

available_tools = get_tools()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "Agents"
)


# ============================================================
# CREATE AGENT
# ============================================================

with st.sidebar.expander(
    "➕ Create New Agent"
):


    agent_name = st.text_input(
        "Agent Name",
        placeholder=(
            "Pump Maintenance Assistant"
        )
    )


    description = st.text_area(
        "Description",
        placeholder=(
            "Industrial equipment support agent"
        )
    )


    goal = st.text_area(
        "Goal",
        placeholder=(
            "Help engineers troubleshoot pump issues."
        )
    )


    system_prompt = st.text_area(
        "System Prompt",
        height=180,
        placeholder=(
            "You are an industrial pump "
            "maintenance assistant..."
        )
    )


    # --------------------------------------------------------
    # AVAILABLE TOOL NAMES
    # --------------------------------------------------------

    tool_names = []


    for tool in available_tools:

        if isinstance(
            tool,
            str
        ):

            tool_names.append(
                tool
            )


        elif isinstance(
            tool,
            dict
        ):

            name = (
                tool.get("name")
                or tool.get("tool_name")
            )


            if name:

                tool_names.append(
                    name
                )


    selected_tools = st.multiselect(
        "Assign Tools",
        options=tool_names
    )


    # --------------------------------------------------------
    # CREATE BUTTON
    # --------------------------------------------------------

    if st.button(
        "Create Agent",
        type="primary",
        use_container_width=True
    ):


        if not agent_name.strip():

            st.warning(
                "Agent name is required."
            )


        elif not goal.strip():

            st.warning(
                "Goal is required."
            )


        elif not system_prompt.strip():

            st.warning(
                "System prompt is required."
            )


        else:

            try:

                response = create_agent(

                    name=agent_name.strip(),

                    description=(
                        description.strip()
                    ),

                    goal=goal.strip(),

                    system_prompt=(
                        system_prompt.strip()
                    ),

                    tools=selected_tools
                )


                if response.status_code in [
                    200,
                    201
                ]:

                    st.success(
                        "Agent created successfully."
                    )

                    st.rerun()


                else:

                    st.error(
                        "Agent creation failed."
                    )

                    st.code(
                        response.text
                    )


            except Exception as e:

                st.error(
                    f"Create agent error: {e}"
                )


# ============================================================
# LOAD AGENTS
# ============================================================

agents = get_agents()


# ============================================================
# NO AGENTS
# ============================================================

if not agents:

    st.title(
        "🤖 Agentic AI Platform"
    )

    st.info(
        "Create your first agent "
        "from the sidebar."
    )

    st.stop()


# ============================================================
# AGENT LOOKUP
# ============================================================

agent_lookup = {}


for agent in agents:

    name = get_agent_name(
        agent
    )

    agent_lookup[
        name
    ] = agent


# ============================================================
# SELECT AGENT
# ============================================================

st.sidebar.divider()


selected_agent_name = (
    st.sidebar.selectbox(
        "Select Agent",
        options=list(
            agent_lookup.keys()
        )
    )
)


selected_agent = (
    agent_lookup[
        selected_agent_name
    ]
)


selected_agent_id = get_agent_id(
    selected_agent
)


# ============================================================
# SELECTED AGENT
# ============================================================

st.sidebar.divider()


st.sidebar.subheader(
    "Selected Agent"
)


st.sidebar.write(
    f"**{selected_agent_name}**"
)


# ============================================================
# ASSIGNED TOOLS
# ============================================================

st.sidebar.divider()


st.sidebar.subheader(
    "Assigned Tools"
)


assigned_tools = get_agent_tools(
    selected_agent_id
)


if assigned_tools:


    for tool in assigned_tools:


        if isinstance(
            tool,
            str
        ):

            tool_name = tool


        else:

            tool_name = (
                tool.get("name")
                or tool.get(
                    "tool_name"
                )
            )


        if tool_name:

            st.sidebar.success(
                f"🔧 {tool_name}"
            )


else:

    st.sidebar.info(
        "No tools assigned."
    )


# ============================================================
# MAIN PAGE
# ============================================================

st.title(
    "🤖 Agentic AI Platform"
)


st.caption(
    "Select an agent and interact "
    "with it using its assigned tools."
)


# ============================================================
# AGENT CONFIGURATION
# ============================================================

with st.expander(
    "Agent Configuration"
):


    st.write(
        "**Name:**",
        selected_agent_name
    )


    st.write(
        "**Description:**",
        selected_agent.get(
            "description",
            ""
        )
    )


    st.write(
        "**Goal:**",
        selected_agent.get(
            "goal",
            ""
        )
    )


# ============================================================
# CHAT
# ============================================================

st.header(
    "Chat"
)


st.caption(
    f"Currently chatting with: "
    f"**{selected_agent_name}**"
)


# ============================================================
# HISTORY PER AGENT
# ============================================================

agent_key = str(
    selected_agent_id
)


if agent_key not in (
    st.session_state.messages
):

    st.session_state.messages[
        agent_key
    ] = []


messages = (
    st.session_state.messages[
        agent_key
    ]
)


# ============================================================
# SHOW CHAT HISTORY
# ============================================================

for message in messages:


    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# INPUT
# ============================================================

user_prompt = st.chat_input(
    "Ask something..."
)


if user_prompt:


    # --------------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------------

    messages.append(
        {
            "role": "user",
            "content": user_prompt
        }
    )


    with st.chat_message(
        "user"
    ):

        st.markdown(
            user_prompt
        )


    # --------------------------------------------------------
    # AGENT RESPONSE
    # --------------------------------------------------------

    with st.chat_message(
        "assistant"
    ):


        with st.spinner(
            "Agent is thinking..."
        ):


            try:

                response = (
                    chat_with_agent(
                        selected_agent_id,
                        user_prompt
                    )
                )


                if (
                    response.status_code
                    == 200
                ):


                    answer = (
                        extract_chat_response(
                            response
                        )
                    )


                    st.markdown(
                        answer
                    )


                    messages.append(
                        {
                            "role": "assistant",
                            "content": answer
                        }
                    )


                else:


                    st.error(
                        f"Chat failed: "
                        f"{response.status_code}"
                    )


                    st.code(
                        response.text
                    )


            except (
                requests.exceptions
                .ConnectionError
            ):


                st.error(
                    "Unable to connect "
                    "to FastAPI."
                )


            except Exception as e:


                st.error(
                    f"Chat error: {e}"
                )