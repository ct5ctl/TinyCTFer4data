import subprocess
import psutil
import os
import time
from typing import Annotated, Optional, Dict, Any
import libtmux
import json
from datetime import datetime
from pathlib import Path

from core import tool, toolset, namespace

namespace()

LOG_DIR = os.path.join(Path.home(), "Workspace/logs")
LOG_FILE = os.path.join(LOG_DIR, "steps.jsonl")


def _append_log(entry: Dict[str, Any]) -> None:
    """
    Append a JSON line to the shared step log.
    保证每条都有 ts / action / observation 字段。
    """
    if os.getenv("DISABLE_STEP_LOG"):
        return
    # 填充必备字段，避免缺失
    entry.setdefault("ts", datetime.utcnow().isoformat() + "Z")
    entry.setdefault("action", "")
    entry.setdefault("observation", "")

    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _log_terminal_event(event: str, session_id: int, action: str, observation: str) -> None:
    """
    统一的终端事件日志封装。
    每条记录至少包含: ts, action, observation，再附带 event / session_id / tag。
    """
    entry: Dict[str, Any] = {
        "tag": "terminal",
        "event": event,
        "session_id": str(session_id),
        "action": action,
        "observation": observation,
    }
    _append_log(entry)

@toolset()
class Terminal:
    def __init__(self):
        self.server = libtmux.Server()

    @tool()
    def list_sessions(self) -> list:
        """List terminal sessions."""
        session_ids = [session.session_id.replace('$', '') for session in self.server.sessions]
        return session_ids

    @tool()    
    def kill_session(self, session_id: int):
        """kill a session"""
        session_ids = [session.session_id.replace('$', '') for session in self.server.sessions]
        sessions = self.server.sessions.filter(session_id=f"${session_id}")
        if not sessions:
            return f"No session found with id: {session_id}. Here are session ids: {', '.join(session_ids)}"
        session = sessions[0]
        session.kill()
        # 这里 action 记录高层语义，observation 简单说明
        _log_terminal_event(
            event="kill_session",
            session_id=session_id,
            action=f"kill_session(id={session_id})",
            observation="session killed",
        )

    @tool()
    def new_session(self) -> int:
        """Open a new terminal window as a new session."""
        session = self.server.new_session(attach=False, start_directory="/home/ubuntu/Workspace")
        session.set_option('status', 'off')
        session_id = session.session_id.replace('$', '')
        session_ids = [session.session_id.replace('$', '') for session in self.server.sessions]
        if not os.getenv('NO_VISION'):
            xfce4_terminal_running = any('xfce4-terminal' in p.name() for p in psutil.process_iter())
            proc = subprocess.Popen(["xfce4-terminal", "--title", f"AI-Terminal-{session_id}", "--command", f"tmux attach-session -t {session_id}", "--hide-scrollbar"])
            if xfce4_terminal_running:
                proc.wait()
            else:
                time.sleep(0.5)
            session.set_option('destroy-unattached', 'on')
        _log_terminal_event(
            event="new_session",
            session_id=int(session_id),
            action=f"new_session(start_directory=/home/ubuntu/Workspace)",
            observation=f"created session {session_id}",
        )
        return int(session_id)

    @tool()
    def get_output(
            self,
            session_id: int,
            start: Annotated[Optional[str],"Specify the starting line number. Zero is the first line of the visible pane. Positive numbers are lines in the visible pane. Negative numbers are lines in the history. - is the start of the history. Default: None"] = "",
            end: Annotated[Optional[str],"Specify the ending line number. Zero is the first line of the visible pane. Positive numbers are lines in the visible pane. Negative numbers are lines in the history. - is the end of the visible pane Default: None"] = ""
        ) -> str:
        """Get the output of a terminal session by session id."""
        session_ids = [session.session_id.replace('$', '') for session in self.server.sessions]
        sessions = self.server.sessions.filter(session_id=f"${session_id}")
        if not sessions:
            return f"No session found with id: {session_id}. Here are session ids: {', '.join(session_ids)}"
        session = sessions[0]
        output = '\n'.join(session.windows[0].panes[0].capture_pane(start, end))
        _log_terminal_event(
            event="get_output",
            session_id=session_id,
            action=f"get_output(start={start!r}, end={end!r})",
            observation=output,
        )
        return output

    @tool()
    def send_keys(self, session_id: int, keys: Annotated[str,"Text or input into terminal window"], enter: Annotated[bool,"Send enter after sending the input."]) -> str:
        """
        Send keys to a terminal session by session id.

        Examaple:
            To execute 'whoami' command: 
            ```
            import toolset

            toolset.terminal.send_keys(session_id=0, keys="whoami", enter=True)
            ```

            To press Ctrl+c: 
            ```
            toolset.terminal.send_keys(session_id=0, keys="C-c", enter=False)
            ```
            
            To press Esc:
            ```
            toolset.terminal.send_keys(session_id=0, keys="C-[", enter=False)
            ```

            To press up arrow: 
            ```
            toolset.terminal.send_keys(session_id=0, keys="C-Up", enter=False)
            ```

            To press tab: 
            ```
            toolset.terminal.send_keys(session_id=0, keys="C-i", enter=False)
            ```

            After execution, it will wait for 1 second before returning the result. If the command is not completed at this time, you need to call the relevant function again to view the pane output
        """
        session_ids = [session.session_id.replace('$', '') for session in self.server.sessions]
        sessions = self.server.sessions.filter(session_id=f"${session_id}")
        if not sessions:
            return f"No session found with id: {session_id}. Here are session ids: {', '.join(session_ids)}"
        session = sessions[0]
        session.windows[0].panes[0].send_keys(keys, enter=enter)
        time.sleep(1)
        output = '\n'.join(session.windows[0].panes[0].capture_pane())
        # 这里 action = 实际执行的命令（含是否自动加回车）
        cmd_desc = keys if enter else f"{keys} (no-enter)"
        _log_terminal_event(
            event="send_keys",
            session_id=session_id,
            action=cmd_desc,
            observation=output,
        )
        return output

