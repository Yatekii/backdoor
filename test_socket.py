class Socket:
    def __init__(self, answer):
        self.answer = answer

    def connect(self):
        pass

    def bind(self):
        pass

    def listen(self):
        pass

    def close(self):
        pass

    def send(self, n):
        pass

    def recv(self, n):
        if len(self.answer) > n:
            answer = self.answer[:n]
            self.answer = self.answer[n:]
        else:
            answer = ''
            self.answer = ''
        return answer