import sys
import os
import xbmc
import xbmcgui
import string
import webbrowser
import time
import ConfigParser
import string

#Lib for Python Twitter
from tweepy import *
from utilities import *

__language__ = xbmc.Language( os.getcwd() ).getLocalizedString
__settings__ = xbmc.Settings( path=os.getcwd() )

RESOURCE_PATH = xbmc.translatePath( os.path.join( os.getcwd(), 'resources' ) )
CONFIG_PATH = xbmc.translatePath( os.path.join( os.getcwd(), 'resources', 'settings.cfg') )

bOAuth = False
if (__settings__.getSetting( "OAuth" ) == 'true'): bOAuth = True
username = __settings__.getSetting( "Username" )
password = __settings__.getSetting( "Password" )

lasttweet = ""

def CreateAPIObject():
    Debug( '::CreateAPIObject::' , True)
    global CONFIG_PATH
    global bOAuth
    if (bOAuth):
        Debug( 'Using OAuth', True)
        config = ConfigParser.RawConfigParser()
        config.read(CONFIG_PATH)

        if (config.has_section('Twitter Account')):
            twitter_key = config.get('Twitter Account', 'key')
            twitter_secret = config.get('Twitter Account', 'secret')

            auth = OAuthHandler('OAWDRnhOHMLpLgEaoWFNA', '8Ros5aIic3L5uoASMZ1JxyNyGlS9xM1Gh0jsReWDws')
            auth.set_access_token(twitter_key, twitter_secret)
            api = API(auth)
        
            api.retry_count = 2
            api.retry_delay = 5
            
            return api
        else:
            return False
    else:
        Debug( 'Using Plain Authentication, ' + username + ':' + password, True)
        auth = BasicAuthHandler(username, password)
        api = API(auth)
    
        api.retry_count = 2
        api.retry_delay = 5
        
        return api
    
    Debug( '::CreateAPIObject::', True)

def StartOAuthProcess():
    Debug( '::StartOAuthProcess::', True)
    auth = OAuthHandler('OAWDRnhOHMLpLgEaoWFNA', '8Ros5aIic3L5uoASMZ1JxyNyGlS9xM1Gh0jsReWDws')
    redirect_url = auth.get_authorization_url()
    webbrowser.open(redirect_url)
    keyboard = xbmc.Keyboard('',__language__(30000))
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        password = keyboard.getText()
    else:
        return False          

    try:
        token = auth.get_access_token(password)
        twitter_key = token.key
        twitter_secret = token.secret
    except:
        return False

    Debug( 'Writing Configuration Details...', True)
    config = ConfigParser.RawConfigParser()
    config.add_section('Twitter Account')
    config.set('Twitter Account', 'key', twitter_key)
    config.set('Twitter Account', 'secret', twitter_secret)            
    configfile = file(os.path.join( RESOURCE_PATH, 'settings.cfg' ), 'wb')
    config.write(configfile)
    Debug( '::StartOAuthProcess::', True)
    return CreateAPIObject()   

def VerifyAPIObject(api):
    Debug( '::VerifyAPIObject::', True)
    try:
        home_timeline = api.home_timeline()
        return True
    except:
        Debug( 'Exception: ' + str(sys.exc_info()[1]), True)
        return False
    Debug( '::VerifyAPIObject::', True)

def UpdateStatus(update, Manual=False):
    global lasttweet

    if (Manual):
        keyboard = xbmc.Keyboard(update,__language__(30001))
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            update = keyboard.getText()
        else:
            return False
    
    if (update != lasttweet):
        lasttweet  = update        
        Debug ('Tweet: ' + update, False)
        api = CreateAPIObject()
        if (VerifyAPIObject(api)):
            update = api.update_status(update)
            pass
        else:
            print 'failed'

FirstTimeMessageOAuth = __language__(30005)
FirstTimeMessagePlainAuth = __language__(30006)
PlainAuthIssues = __language__(30009)
OAuthIssues = __language__(30008)

bFirstRun = CheckIfFirstRun()

api = CreateAPIObject()
if (bool(api)):
    Debug( 'Twitter API object created successfully', True)
else:
    Debug( 'Failed to create Twitter API object', True)
    if (bFirstRun and bOAuth):
        dialog = xbmcgui.Dialog()
        dialog.ok(__language__(30009), FirstTimeMessageOAuth)
        StartOAuthProcess()
    elif (not bFirstRun and bOAuth):
        dialog = xbmcgui.Dialog()
        dialog.ok(__language__(30010), OAuthIssues)        
        StartOAuthProcess()
    elif (bFirstRun and not bOAuth):
        dialog = xbmcgui.Dialog()
        dialog.ok(__language__(30009), FirstTimeMessagePlainAuth)
        bRun = False
    else:
        dialog = xbmcgui.Dialog()
        dialog.ok(__language__(30010), PlainAuthIssues)
        bRun = False

if (VerifyAPIObject(api)):
    Debug( 'Twitter API object verified', True)
else:
    Debug( 'Failed to verify Twitter API object', True)
    if (bOAuth):
        dialog = xbmcgui.Dialog()
        dialog.ok(__language__(30010), OAuthIssues)        
        StartOAuthProcess()
    else:
        dialog = xbmcgui.Dialog()
        dialog.ok(__language__(30010), PlainAuthIssues)
        bRun = False
