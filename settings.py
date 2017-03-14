class Config(object):
    """
    global application configurations
    """
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost/hotel'
    SECRET_KEY = '\x91c~\xc0-\xe3\'f\xe19PE\x93\xe8\x91`uu"\xd0\xb6\x01/\x0c\xed\\\xbd]H\x99k\xf8'
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False