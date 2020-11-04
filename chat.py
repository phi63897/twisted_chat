from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.python import log
import datetime

class Chat(LineReceiver):

    def __init__(self, users, log):
        self.users = users
        self.name = None
        self.state = "FIRST"
        self.log = log

    def connectionMade(self):
        self.sendLine("are you trying to login or register?[log USER PASS or reg USER PASS]".encode())

    def connectionLost(self, reason):
        if self.name in self.users:
            leaving = "[%s has left the room]" % (self.name)
            log.write("[%s][%s has left the room]\n" % (str(datetime.datetime.now()), self.name))
            for user, info in self.users.items():
                if info[1] != self and info[1] != None:
                    info[1].sendLine(leaving.encode())
            self.users[self.name][1] = None

    def lineReceived(self, line):
        # if self.state == "GETNAME":
        #     self.handle_GETNAME(line)
        line = line.decode()
        if self.state == "FIRST":
            if line.lower().split()[0] == "log":
                self.h andle_LOGIN(line)
            elif line.lower().split()[0] == "reg":
                self.handle_REGISTER(line)
            else:
                self.sendLine("Response needs to be lead with 'log' or 'reg' ".encode())
        else:
            self.handle_CHAT(line)

    def handle_LOGIN(self, line):
        if len(line.split())== 3:
            username = line.lower().split()[1]
            password = line.lower().split()[2]
            if username in self.users:
                if password == self.users[username][0]:
                    if self.users[username][1] == None:
                        self.name = username
                        self.users[username][1] = self
                        self.state = "CHAT"
                        welcome = "[Welcome %s to the chat room]"%(self.name)
                        for user, info in self.users.items():
                            if info[1] != None:
                                info[1].sendLine(welcome.encode())
                        #writing who joins to console
                        log.write("[%s][Welcome %s to the chat room]\n"%(str(datetime.datetime.now()),self.name))
                    else:
                        self.sendLine("This account is already signed in to chatroom!".encode())
                else:
                    self.sendLine("Invalid username or password for login, please try again!".encode())
            else:
                self.sendLine("Invalid username or password for login, please try again!".encode())

        else:
            self.sendLine("Invalid login format! [log USER PASS]".encode())

    def handle_REGISTER(self, line):
        if len(line.split())== 3:
            username = line.lower().split()[1]
            password = line.lower().split()[2]
            if username in self.users:
                self.sendLine("Invalid username for register(username is already taken), please try again!".encode())
            else:
                self.name = username
                self.users[username] = []
                self.users[username].append(password)
                self.users[username].append(self)
                self.state = "CHAT"
                welcome = "[Welcome %s to the chat room]"%(self.name)
                for user, info in self.users.items():
                    if info[1] != None:
                        info[1].sendLine(welcome.encode())
                #writing who joins to console
                log.write("[%s][Welcome %s to the chat room]\n"%(str(datetime.datetime.now()),self.name))
        else:
            self.sendLine("Invalid register format! [reg USER PASS]".encode())

    def handle_CHAT(self, message):
        message = "<%s> %s" % (self.name, message)
        log.write("[%s]<%s> %s\n" % (str(datetime.datetime.now()),self.name, message))
        for user, info in self.users.items():
            if info[1] != self and info[1] != None:
                info[1].sendLine(message.encode())


class ChatFactory(Factory):

    def __init__(self):
        self.users = {} # maps user names to Password and Chat instances
                        # user : [pass, self]
        self.log = open("chatlog.txt","a")
    def buildProtocol(self, addr):
        return Chat(self.users, self.log)


reactor.listenTCP(8123, ChatFactory())
reactor.run()
