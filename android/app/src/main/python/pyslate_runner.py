"""Disposable worker with real Python stdin/stdout/stderr and standard traceback."""
import io
import os
import runpy
import sys
import traceback


class Output(io.TextIOBase):
    def __init__(self, bridge, kind):
        self.bridge, self.kind = bridge, kind

    @property
    def encoding(self):
        return 'utf-8'

    def writable(self):
        return True

    def write(self, text):
        text = str(text)
        if text:
            self.bridge.emit(self.kind, text)
        return len(text)

    def flush(self):
        pass


class Input(io.TextIOBase):
    def __init__(self, bridge):
        self.bridge, self.pending, self.eof = bridge, '', False

    @property
    def encoding(self):
        return 'utf-8'

    def readable(self):
        return True

    def readline(self, size=-1):
        if size == 0:
            return ''
        if not self.pending and not self.eof:
            line = str(self.bridge.readLine())
            if line == '\x00EOF':
                self.eof = True
            else:
                self.pending = line
        newline = self.pending.find('\n')
        take = len(self.pending) if newline < 0 else newline + 1
        if size >= 0:
            take = min(size, take)
        result, self.pending = self.pending[:take], self.pending[take:]
        return result

    def read(self, size=-1):
        if size == 0:
            return ''
        parts, count = [], 0
        while size < 0 or count < size:
            text = self.readline(-1 if size < 0 else size - count)
            if not text:
                break
            parts.append(text)
            count += len(text)
        return ''.join(parts)


def run(folder, entry, bridge):
    folder, entry = str(folder), str(entry)
    sys.stdin = Input(bridge)
    sys.stdout = Output(bridge, 'stdout')
    sys.stderr = Output(bridge, 'stderr')
    os.chdir(folder)
    sys.path.insert(0, folder)
    sys.argv = [entry]
    try:
        runpy.run_path(os.path.join(folder, entry), run_name='__main__')
    except SystemExit as error:
        code = error.code
        if not isinstance(code, int):
            if code is not None:
                print(code, file=sys.stderr)
            code = 1 if code is not None else 0
        bridge.finish(code, '')
    except BaseException:
        traceback.print_exc()
        bridge.finish(1, '')
