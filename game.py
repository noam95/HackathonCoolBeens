
from server import lock


class game:
    def __init__(self):
        team1 = []
        team2 = []
        bol = True
    def assignToTeam(self,player):
        lock.acquire(True)
        if self.bol:
            self.team1.append(player)
            bol = False
        else:
            self.team2.append(player)
            bol = True
        lock.release()
    def getGroupsMsg(self):
        msg ="group1\n"
        for i in self.team1:
            msg += i + "\n"
        msg += "group2\n"
        for i in self.team2:
            msg += i + "\n"
        return msg
