import threading

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


class SessionMemory:
    """Per-session chat history held in process memory (lost on restart).

    Only the last `max_turns` question/answer pairs are kept and returned to the chains.
    """

    def __init__(self, max_turns: int = 6):
        self.max_turns = max_turns
        self._sessions: dict[str, list[BaseMessage]] = {}
        self._lock = threading.Lock()

    def get_messages(self, session_id: str) -> list[BaseMessage]:
        with self._lock:
            return list(self._sessions.get(session_id, []))

    def add_turn(self, session_id: str, question: str, answer: str) -> None:
        with self._lock:
            messages = self._sessions.setdefault(session_id, [])
            messages.extend([HumanMessage(question), AIMessage(answer)])
            del messages[: -self.max_turns * 2]

    def clear(self, session_id: str) -> bool:
        with self._lock:
            return self._sessions.pop(session_id, None) is not None
