# EHFtv Kodi plugin

![Logo](https://raw.githubusercontent.com/clearedTakeoff/plugin.video.ehftv/master/resources/ehf.jpg "EHFtv")


A very basic plugin bringing the content from [EHF TV](https://ehftv.com) into your own Kodi media center.

Plugin is only tested in Kodi Leia (18.8). It may or may not work in earlier/later versions. Try at your own risk!

Plugin requires a free EHF TV account, [create your own here](https://ehfpayments.streamamg.com/account/freeregistration) 

If you're having problems using the plugin, please create an issue here.

## Installing plugin into Kodi
1. Download the zip package from the [releases section](https://github.com/clearedTakeoff/plugin.video.ehftv/releases) and save it in a folder of your choosing. (download the file plugin.video.ehftv-X.X.X.zip)
2. In Kodi go to the addons menu and select *Install from zip file*, navigate to the location of downloaded file and select it.
3. Wait until the installation is completed.
4. When first opening the addon go to *Settings* and enter your EHFtv account credentials (without doing this the streams will not work!)

## FAQ
__Q: When selecting the video (or livestream) the loading circle appears for a second but then nothing happens.__  
From my (very limited) testing I've found that this can happen if *InputStream Adaptive* add-on is not installed (or enabled) in Kodi. Follow instructions on [this link](https://kodi.wiki/view/Add-on:InputStream_Adaptive) and see if that fixes the issue.

__Q: All of the matches under live section show up as not available in my region.__  
The live section shows both the currently live matches and the upcoming scheduled matches. If the matches are still are still too far away then it could (falsely) appear as not available for you but it should change once the date of the matches comes closer. (I haven't been able to determine yet how close to the date it changes though)

__Q: Some of the matches don't appear/disappear from the live section.__  
This usually happens if a match is blocked in your region because of TV rights. This means that the *not available in your region* for the future matches might not be the most accurate (see also the paragraph above).

*Note:* I've encountered some matches before where I wasn't able to watch them live even though none of my local TV channels were broadcasting it. Unfortunately this is out of my reach and I can't help with that.