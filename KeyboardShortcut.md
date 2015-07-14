Using Keyboard/Controller to run xbTweet

# Introduction #

If you wish, you can call xbTweet with a press of a button on your keyboard or controller.<br />
This can be a good replacement for running xbTweet in the background and gives you full control over what is tweeted from your XBMC machine.<br />
The instructions here are no different than any other script integration into the keymap file and here they are:<br />
  * XBMC uses a key map file that maps your keyboard/controller keys into actions.<br />
  * In order to add xbTweet to your keymap file, we first need to locate it.<br />
  * The default location of the keymap file depends on how you chose to install your XBMC.<br /> For Windows, it's either in program files\xbmc\system\keymaps folder or under your user's data folder if you're using Vista/Windows 7 or you chose this method during installation. <br />In that case check c:\users\YOUR USERNAME\appdata\roaming\xbmc\system\keymaps.<br />For Linux it's either in /usr/local/share/xbmc/system/keymaps or ~/.xbmc/system/keymaps. (~ = users home)<br />
  * The keymap file is called either keymap.xml or keyboard.xml (Camelot).<br />
  * Open the file and under the general section add the following, I chose the letter y to run xbTweet:
```
<keymap>
  <global>
    <keyboard>
	 <y>XBMC.RunScript(special://home/scripts/xbtweet/default.py,-shortcut)</y>
```
  * Next, xbTweet will popup a keyboard with a pre-populated text box based on the custom tweet from your script's settings page.<br />
  * NOTE: The <i>-shortcut</i> is needed, otherwise it won't work.

If you have any questions or comments, please use the comments box below.