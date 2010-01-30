import sys
import os
import xbmc
import xbmcgui
import string
import webbrowser
import time
import ConfigParser
import string

from tweepy import *
from utilities import *

__language__ = xbmc.Language( os.getcwd() ).getLocalizedString
__settings__ = xbmc.Settings( path=os.getcwd() )

RESOURCE_PATH = xbmc.translatePath( os.path.join( os.getcwd(), 'resources' ) )
CONFIG_PATH = xbmc.translatePath( os.path.join( os.getcwd(), 'resources', 'settings.cfg') )
MEDIA_RESOURCE_PATH = xbmc.translatePath( os.path.join( os.getcwd(), 'resources', 'skins' ) )

bOAuth = False
if (__settings__.getSetting( "OAuth" ) == 'true'): bOAuth = True
username = __settings__.getSetting( "Username" )
password = __settings__.getSetting( "Password" )

lasttweet = ""

def Twitter_Login():
    Debug( '::Login::' , True)

    global username
    global password
    global bOAuth
    
    if (bOAuth):
        Debug( 'Using OAuth', True)
        config = ConfigParser.RawConfigParser()
        config.read(CONFIG_PATH)

        if (config.has_section('Twitter Account')):
            #OAuth login details found
            twitter_key = config.get('Twitter Account', 'key')
            twitter_secret = config.get('Twitter Account', 'secret')

            auth = OAuthHandler('OAWDRnhOHMLpLgEaoWFNA', '8Ros5aIic3L5uoASMZ1JxyNyGlS9xM1Gh0jsReWDws')
            auth.set_access_token(twitter_key, twitter_secret)
            api = API(auth)

            bVerified, sError = VerifyAuthentication(api)
            if (not bVerified):
                ShowMessage(40003) #OAuth starts
                auth = OAuthHandler('OAWDRnhOHMLpLgEaoWFNA', '8Ros5aIic3L5uoASMZ1JxyNyGlS9xM1Gh0jsReWDws')
                redirect_url = auth.get_authorization_url()
                webbrowser.open(redirect_url)
                keyboard = xbmc.Keyboard('',__language__(30000))
                keyboard.doModal()
                if (keyboard.isConfirmed()):
                    password = keyboard.getText()
                else:
                    #Maybe using text based browser or XBOX
                    ShowMessage(40005)
                    return False
                try:
                    token = auth.get_access_token(password)
                    twitter_key = token.key
                    twitter_secret = token.secret
                except:
                    #PIN Number incorrect
                    ShowMessage(40004)
                    return False
                Debug( 'Writing Configuration Details...', True)
                config = ConfigParser.RawConfigParser()
                config.add_section('Twitter Account')
                config.set('Twitter Account', 'key', twitter_key)
                config.set('Twitter Account', 'secret', twitter_secret)            
                configfile = file(os.path.join( RESOURCE_PATH, 'settings.cfg' ), 'wb')
                config.write(configfile)

                try:
                    api = API(auth)
                    bVerified, sError = VerifyAuthentication(api)
                    if (not bVerified):
                        return False
                except:
                    Debug( 'Exception: Login: ' + str(sys.exc_info()[1]), True)
                    return False
        else:
            #OAuth not defined
            ShowMessage(40006) #OAuth starts
            auth = OAuthHandler('OAWDRnhOHMLpLgEaoWFNA', '8Ros5aIic3L5uoASMZ1JxyNyGlS9xM1Gh0jsReWDws')
            redirect_url = auth.get_authorization_url()
            webbrowser.open(redirect_url)
            keyboard = xbmc.Keyboard('',__language__(30000))
            keyboard.doModal()
            if (keyboard.isConfirmed()):
                password = keyboard.getText()
            else:
                #Maybe using text based browser or XBOX
                ShowMessage(40005)
                return False
            try:
                token = auth.get_access_token(password)
                twitter_key = token.key
                twitter_secret = token.secret
            except:
                #PIN Number incorrect
                ShowMessage(40004)
                return False
            Debug( 'Writing Configuration Details...', True)
            config = ConfigParser.RawConfigParser()
            config.add_section('Twitter Account')
            config.set('Twitter Account', 'key', twitter_key)
            config.set('Twitter Account', 'secret', twitter_secret)            
            configfile = file(os.path.join( RESOURCE_PATH, 'settings.cfg' ), 'wb')
            config.write(configfile)
            try:
                api = API(auth)
                bVerified, sError = VerifyAuthentication(api)
                if (not bVerified):
                    return False
            except:
                Debug( 'Exception: Login: ' + str(sys.exc_info()[1]), True)
                return False
    else:
        Debug( 'Using Plain Authentication, ' + username + ':' + password, True)
        if (username == '' or password == ''):
            ShowMessage(40001)
            __settings__.openSettings()
            return False

        try:
            auth = BasicAuthHandler(username, password)
            api = API(auth)
        except:
            Debug( 'Exception: Login: ' + str(sys.exc_info()[1]), True)
            ShowMessage(40002)
            __settings__.openSettings()
            return False

        bVerified, sError = VerifyAuthentication(api)
        if (not bVerified):
            ShowMessage(40002)
            __settings__.openSettings()
            return False
            
    Debug( '::Login::', True) 
    return api, auth
       
def VerifyAuthentication(api):
    Debug( '::VerifyAuthentication::', True)   
    bVerified = False
    sError = ""
    
    if (api):
        try:
            if (api.verify_credentials() != False): bVerified = True
            else: "Failed to verify credentials: api.verify_credentials()"
        except:
            sError = "Exception: Failed to verify credentials: api.verify_credentials()"

    Debug( '::VerifyAuthentication::', True)   
    return bVerified, sError
    
def ShowMessage(MessageID):    
    import gui_auth
    message = __language__(MessageID)
    ui = gui_auth.GUI( "script-xbTweet-Generic.xml" , os.getcwd(), "Default")
    ui.setParams ("message", __language__(30042), message, 0)
    ui.doModal()
    del ui

def CheckAPIRate(api):
    #check we didn't hit the api limit
    apicallsleft = 0
    try:
        count = str(api.rate_limit_status())
        apicallsleft = int(count.split(',')[1].split(':')[1])
    except:
        Debug( 'Error fetching API count: ' + str(sys.exc_info()[1]), True)
        return 0
    
    Debug ('API Count Check: ' + str(apicallsleft), False)
    return count
    
def CheckForMentions(lastid):
    if (__settings__.getSetting( "NotifyMention" ) != 'true'):
        return None    
    mentions = ""
    Debug ('Checking for new mentions...', True)
    api, auth = Twitter_Login()
    if (CheckAPIRate(api) <= 0):
        return None
    try:
        if lastid == 0:
            mentions = api.mentions(count=1)
        else:
            mentions = api.mentions(since_id=lastid, count=1)
    except:
        Debug ('Error fetching mentions', False)

    if mentions:
        Debug ('Found mention (' + str(mentions[0].id) + '):' + mentions[0].text, False)
        return mentions[0]
    else:
        return None

def CheckForTimeline(lastid):
    if (__settings__.getSetting( "NotifyTimeline" ) != 'true'):
        return None    
    tweets = None
    Debug ('Checking for new tweets...', True)
    api, auth = Twitter_Login()
    if (CheckAPIRate(api) <= 0):
        return None
    try:
        if lastid == 0:
            tweets = api.home_timeline(count=1)
        else:
            tweets = api.home_timeline(since_id=lastid, count=6)
    except:
        Debug ('Error fetching tweets', False)

    if tweets:
        Debug ('Found tweet (' + str(tweets[0].id) + '):' + tweets[0].text, False)        
        return tweets
    else:
        return None
    
def CheckForDM(lastid):
    if (__settings__.getSetting( "NotifyDirect" ) != 'true'):
        return None
    mentions = ""
    Debug ('Checking for new DMs...', True)
    api, auth = Twitter_Login()
    if (CheckAPIRate(api) <= 0):
        return None
    try:
        if lastid == 0:
            mentions = api.direct_messages(count=1)
        else:
            mentions = api.direct_messages(since_id=lastid, count=1)
    except:
        Debug ('Error fetching DMs', False)

    if mentions:
        Debug ('Found DM (' + str(mentions[0].id) + '):' + mentions[0].text, False)        
        return mentions[0]
    else:
        return None

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
        api, auth = Twitter_Login()
        if (CheckAPIRate(api) <= 0):
            return None
        update = api.update_status(update)
        twittersmallicon = xbmc.translatePath( os.path.join( MEDIA_RESOURCE_PATH, 'default', 'media', 'smalltwitter.png' ) )
        print twittersmallicon
        xbmc.executebuiltin('Notification(xbTweet,' + __language__(30050) + ',2000,' + twittersmallicon + ')')
