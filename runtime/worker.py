"""PySlate CPython child bootstrap. This is process management, not a sandbox."""
import builtins
import io
import json
import operator
import os
import runpy
import sys
import threading

entry, marker, handshake = sys.argv[1:4]
protocol_v2 = len(sys.argv) > 4 and sys.argv[4] == "input-v2"
if sys.stdin.readline().rstrip("\n") != handshake:
    raise SystemExit(125)
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.dirname(os.path.abspath(entry)))
sys.argv = [entry]

_control_stream = sys.stderr
_input_lock = threading.RLock()
_input_sequence = 0


def tracked_read(operation, waiting):
    """Only reads of the inherited pipe pause the parent's execution budget."""
    global _input_sequence
    with _input_lock:
        _input_sequence += 1
        request_id = _input_sequence
        frame = {"type": "input", "requestId": request_id, "waiting": waiting}
        _control_stream.write(marker + json.dumps(frame, separators=(",", ":")) + "\n")
        _control_stream.flush()
        try:
            return operation()
        finally:
            frame = {"type": "input_end", "requestId": request_id}
            _control_stream.write(marker + json.dumps(frame, separators=(",", ":")) + "\n")
            _control_stream.flush()


class InputStream(io.TextIOBase):
    """Track text stdin reads, preserving partial lines and newline characters.

    Binary buffer / sys.__stdin__ remain ordinary CPython streams; they are
    not treated as an input() wait without a protocol event.
    """
    def __init__(self, stream):
        self.stream = stream
        self.eof = False

    @property
    def encoding(self):
        return self.stream.encoding

    @property
    def errors(self):
        return self.stream.errors

    @property
    def buffer(self):
        return self.stream.buffer

    @property
    def closed(self):
        return self.stream.closed

    def fileno(self):
        return self.stream.fileno()

    def isatty(self):
        return self.stream.isatty()

    def readable(self):
        return True

    def seekable(self):
        return False

    def close(self):
        self.stream.close()

    def readline(self, size=-1):
        size = -1 if size is None else operator.index(size)
        if self.closed:
            raise ValueError("I/O operation on closed file")
        if size == 0 or self.eof:
            return ""
        line = tracked_read(lambda: self.stream.readline(size), True)
        if line == "":
            self.eof = True
        return line

    def read(self, size=-1):
        size = -1 if size is None else operator.index(size)
        if self.closed:
            raise ValueError("I/O operation on closed file")
        if size == 0:
            return ""
        pieces, length = [], 0
        while size < 0 or length < size:
            piece = self.readline(-1 if size < 0 else size - length)
            if not piece:
                break
            pieces.append(piece)
            length += len(piece)
        return "".join(pieces)

    def readlines(self, hint=-1):
        hint = -1 if hint is None else operator.index(hint)
        lines, length = [], 0
        while hint <= 0 or length < hint:
            line = self.readline()
            if not line:
                break
            lines.append(line)
            length += len(line)
        return lines

    def __iter__(self):
        return self

    def __next__(self):
        line = self.readline()
        if not line:
            raise StopIteration
        return line


_bridge_stdin = InputStream(sys.stdin) if protocol_v2 else sys.stdin
if protocol_v2:
    sys.stdin = _bridge_stdin


def interactive_input(prompt=""):
    with _input_lock:
        sys.stdout.write(str(prompt))
        sys.stdout.flush()
        if protocol_v2:
            if sys.stdin is _bridge_stdin:
                line = sys.stdin.readline()
            else:
                # Redirected input is not a user wait, but still counts towards
                # the existing bounded input-call quota.
                line = tracked_read(sys.stdin.readline, False)
        else:
            # Preserve the standalone worker interface used by course tools.
            _control_stream.write(marker + "\n")
            _control_stream.flush()
            line = sys.stdin.readline()
        if not line:
            raise EOFError("EOF when reading a line")
        if line.endswith("\n"):
            line = line[:-1]
            if line.endswith("\r"):
                line = line[:-1]
        return line

builtins.input = interactive_input
runpy.run_path(entry, run_name="__main__")
