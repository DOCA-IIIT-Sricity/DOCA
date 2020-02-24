import re
def isvalidUserName(username):
    if len(username) < 6 or len(username)>25:
        return False
    if isValidEmail(username):
        return False
    return True


def isvalidPassword(password):
    if len(password) < 8 or len(password)>25:
        return False
    if(bool(re.match('((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*]).{8,25})',password))==True):
        return False
    return True
    
def isValidEmail(email):
    return re.search('^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$',email)

def sendOTP(email):
    pass