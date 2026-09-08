import json
from pathlib import Path

import requests
import streamlit as st


# ===================================================
# Configuration
# ===================================================

API_BASE_URL = "http://127.0.0.1:8000"

TOOL_REGISTRY_FILE = (
    Path(__file__).parent.parent
    / "app"
    / "tools"
    / "tool_registry.json"
)


# ===================================================
# Streamlit Page Setup
# ===================================================

st.set_page_config(
    page_title="Agentic AI Platform",
    page_icon="🤖",
    layout="wide",
)

st.title("Agentic AI Platform")


# ===================================================
# Custom Styling
# ===================================================

st.markdown(
    """
    <style>

    .selected-agent-box {
        background-color: #eef6ff;
        border: 1px solid #b8d8ff;
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 18px;
        font-size: 16px;
        font-weight: 600;
    }

    .tool-label {
        font-size: 13px;
        color: #666666;
        margin-bottom: 6px;
    }

    .tool-badge {
        display: inline-block;
        background-color: #dff5e3;
        color: #167a2f;
        border: 1px solid #9fd3aa;
        border-radius: 16px;
        padding: 5px 10px;
        margin-right: 6px;
        margin-bottom: 6px;
        font-size: 13px;
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ===================================================
# Helper Functions
# ===================================================


def load_tool_registry():
    """
    Load tool server configuration from JSON.
    """

    try:

        with open(
            TOOL_REGISTRY_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    except FileNotFoundError:

        st.error(
            "tool_registry.json was not found."
        )

        return {
            "servers": []
        }

    except json.JSONDecodeError as error:

        st.error(
            f"Invalid JSON in tool registry: {error}"
        )

        return {
            "servers": []
        }


def get_agents():
    """
    Load all agents from FastAPI.
    """

    try:

        response = requests.get(
            f"{API_BASE_URL}/agents",
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    except Exception as error:

        st.error(
            f"Unable to load agents: {error}"
        )

        return []


def create_agent(
    name,
    goal,
    system_prompt,
    tools,
):
    """
    Create a new agent.
    """

    payload = {
        "name": name,
        "goal": goal,
        "system_prompt": system_prompt,
        "tools": tools,
    }

    try:

        response = requests.post(
            f"{API_BASE_URL}/agents",
            json=payload,
            timeout=10,
        )

        if response.status_code in (
            200,
            201,
        ):

            return True, response.json()

        return (
            False,
            response.text,
        )

    except Exception as error:

        return (
            False,
            str(error),
        )


def chat_with_agent(
    agent_id,
    message,
):
    """
    Send a message to the selected agent.
    """

    payload = {
        "message": message
    }

    try:

        response = requests.post(
            (
                f"{API_BASE_URL}"
                f"/agents/{agent_id}/chat"
            ),
            json=payload,
            timeout=120,
        )

        if response.status_code != 200:

            try:

                error_data = response.json()

                error_message = error_data.get(
                    "detail",
                    response.text,
                )

            except Exception:

                error_message = response.text

            return (
                "Backend Error "
                f"({response.status_code}): "
                f"{error_message}"
            )

        data = response.json()

        return (
            data.get("response")
            or data.get("answer")
            or data.get("message")
            or str(data)
        )

    except requests.exceptions.ConnectionError:

        return (
            "Unable to connect to FastAPI. "
            "Make sure the backend is running."
        )

    except Exception as error:

        return (
            "Error communicating with agent: "
            f"{error}"
        )


# ===================================================
# Session State
# ===================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


if "selected_agent_id" not in st.session_state:
    st.session_state.selected_agent_id = None


if "selected_agent_name" not in st.session_state:
    st.session_state.selected_agent_name = None


if "agent_create_message" not in st.session_state:
    st.session_state.agent_create_message = None


if "show_create_toast" not in st.session_state:
    st.session_state.show_create_toast = False


# ===================================================
# Load Tool Registry
# ===================================================

tool_registry = load_tool_registry()

servers = tool_registry.get(
    "servers",
    [],
)


# ===================================================
# Sidebar
# ===================================================

with st.sidebar:

    st.header(
        "Agent Management"
    )

    # =================================================
    # Create New Agent
    # =================================================

    with st.expander(
        "➕ Create New Agent",
        expanded=True,
    ):

        agent_name = st.text_input(
            "Agent Name",
            placeholder=(
                "Example: Machine Monitor Agent"
            ),
            key="agent_name_input",
        )

        goal = st.text_area(
            "Goal",
            placeholder=(
                "Example: Monitor machine data "
                "and identify abnormal behavior"
            ),
            height=100,
            key="agent_goal_input",
        )

        system_prompt = st.text_area(
            "System Prompt",
            placeholder=(
                "Describe how this agent "
                "should behave."
            ),
            height=120,
            key="agent_system_prompt_input",
        )

        # ===========================================
        # Tool Server Selection
        # ===========================================

        server_names = [
            server.get("name")
            for server in servers
            if server.get("name")
        ]

        selected_server_name = None

        if server_names:

            selected_server_name = st.selectbox(
                "Tool Server",
                options=server_names,
                key="tool_server_select",
            )

        else:

            st.warning(
                "No tool servers found "
                "in tool_registry.json."
            )

        # ===========================================
        # Find Selected Tool Server
        # ===========================================

        selected_server = None

        if selected_server_name:

            for server in servers:

                if (
                    server.get("name")
                    == selected_server_name
                ):

                    selected_server = server
                    break

        available_tools = []

        # ===========================================
        # Display Tool Server Information
        # ===========================================

        if selected_server:

            transport = selected_server.get(
                "transport",
                "Not configured",
            )

            endpoint = selected_server.get(
                "url"
            )

            st.caption(
                f"Transport: {transport}"
            )

            if endpoint:

                st.caption(
                    f"Endpoint: {endpoint}"
                )

            available_tools = (
                selected_server.get(
                    "enabled_tools",
                    [],
                )
            )

        # ===========================================
        # Select Tools
        # ===========================================

        if available_tools:

            selected_tools = st.multiselect(
                "Available Tools",
                options=available_tools,
                placeholder=(
                    "Select tools for this agent"
                ),
                key="tool_select",
            )

        else:

            selected_tools = []

            st.info(
                "No tools configured "
                "for this server."
            )

        # ===========================================
        # Create Agent
        # ===========================================

        create_button = st.button(
            "Create Agent",
            use_container_width=True,
            key="create_agent_button",
        )

        if create_button:

            st.session_state[
                "agent_create_message"
            ] = None

            if not agent_name.strip():

                st.warning(
                    "Please enter an agent name."
                )

            elif not goal.strip():

                st.warning(
                    "Please enter an agent goal."
                )

            else:

                success, result = create_agent(
                    name=agent_name.strip(),
                    goal=goal.strip(),
                    system_prompt=(
                        system_prompt.strip()
                    ),
                    tools=selected_tools,
                )

                if success:

                    st.session_state[
                        "agent_create_message"
                    ] = (
                        f"Agent "
                        f"'{agent_name.strip()}' "
                        f"created successfully!"
                    )

                    st.session_state[
                        "show_create_toast"
                    ] = True

                    st.rerun()

                else:

                    st.error(
                        "Unable to create agent: "
                        f"{result}"
                    )

        # ===========================================
        # Create Success Message
        # ===========================================

        if st.session_state.get(
            "agent_create_message"
        ):

            st.success(
                st.session_state[
                    "agent_create_message"
                ],
                icon="✅",
            )

        if st.session_state.get(
            "show_create_toast"
        ):

            st.toast(
                st.session_state[
                    "agent_create_message"
                ],
                icon="✅",
            )

            st.session_state[
                "show_create_toast"
            ] = False

    # =================================================
    # Existing Agents
    # =================================================

    st.divider()

    st.subheader(
        "Existing Agents"
    )

    agents = get_agents()

    selected_agent = None

    if agents:

        agent_options = {
            agent["name"]: agent
            for agent in agents
        }

        selected_agent_name = st.selectbox(
            "Select Agent",
            options=list(
                agent_options.keys()
            ),
            key="existing_agent_select",
        )

        selected_agent = (
            agent_options.get(
                selected_agent_name
            )
        )

        if selected_agent:

            st.session_state[
                "selected_agent_id"
            ] = selected_agent.get(
                "id"
            )

            st.session_state[
                "selected_agent_name"
            ] = selected_agent.get(
                "name"
            )

            goal_value = (
                selected_agent.get(
                    "goal"
                )
            )

            tools_value = (
                selected_agent.get(
                    "tools",
                    [],
                )
            )

            # -----------------------------------------
            # Goal
            # -----------------------------------------

            if goal_value:

                st.caption(
                    f"Goal: {goal_value}"
                )

            # -----------------------------------------
            # Assigned Tools - Green Badges
            # -----------------------------------------

            st.markdown(
                '<div class="tool-label">'
                'Assigned Tools'
                '</div>',
                unsafe_allow_html=True,
            )

            if tools_value:

                tool_badges = ""

                for tool_name in tools_value:

                    tool_badges += (
                        '<span class="tool-badge">'
                        f'{tool_name}'
                        '</span>'
                    )

                st.markdown(
                    tool_badges,
                    unsafe_allow_html=True,
                )

            else:

                st.caption(
                    "No tools assigned."
                )

    else:

        st.info(
            "No agents created yet."
        )

    # =================================================
    # Clear Chat
    # =================================================

    if st.button(
        "Clear Chat",
        use_container_width=True,
        key="clear_chat_button",
    ):

        st.session_state.messages = []

        st.rerun()


# ===================================================
# Main Chat Area
# ===================================================

st.subheader(
    "Agent Chat"
)


selected_agent_id = (
    st.session_state.get(
        "selected_agent_id"
    )
)

selected_agent_name = (
    st.session_state.get(
        "selected_agent_name"
    )
)


# ===================================================
# No Agent Selected
# ===================================================

if not selected_agent_id:

    st.info(
        "Create or select an agent "
        "from the sidebar to begin."
    )


# ===================================================
# Selected Agent
# ===================================================

else:

    # -----------------------------------------------
    # Show Current Agent
    # -----------------------------------------------

    st.markdown(
        (
            '<div class="selected-agent-box">'
            '🤖 Talking to: '
            f'{selected_agent_name}'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

    # -----------------------------------------------
    # Display Previous Messages
    # -----------------------------------------------

    for message in (
        st.session_state.messages
    ):

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

    # -----------------------------------------------
    # Chat Input
    # -----------------------------------------------

    user_message = st.chat_input(
        (
            f"Ask {selected_agent_name} "
            "something..."
        )
    )

    if user_message:

        # -------------------------------------------
        # Save User Message
        # -------------------------------------------

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        # -------------------------------------------
        # Display User Message
        # -------------------------------------------

        with st.chat_message(
            "user"
        ):

            st.markdown(
                user_message
            )

        # -------------------------------------------
        # Agent Response
        # -------------------------------------------

        with st.chat_message(
            "assistant"
        ):

            with st.spinner(
                (
                    f"{selected_agent_name} "
                    "is thinking..."
                )
            ):

                response = (
                    chat_with_agent(
                        selected_agent_id,
                        user_message,
                    )
                )

            st.markdown(
                response
            )

        # -------------------------------------------
        # Save Assistant Message
        # -------------------------------------------

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response,
            }
        )