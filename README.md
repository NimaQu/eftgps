# eftgps
Real-time location based on https://tarkov-market.com/ and build-in game screenshot

# Usage
First, make sure you have chrome installed, then:
1. Download the latest release from [releases](https://github.com/NimaQu/eftgps/releases) page
2. Extract the zip file
3. open config.ini and set your screenshots folder path, modify Loading Delay if needed
4. select the map by running different .bat files
5. If ur network environment is normal, you should be able to see the map u selected in the browser, once you take a screenshot in game, the location will be shown on the map by a green dot.

# FAQ
1. Q: Why the map is not showing up?
   A: Make sure you have set the correct screenshots folder path in config.ini, and make sure you have taken a screenshot in game. If all of these are correct, means u are not able to access the tarkov-market.com or failed to download chrome driver, try to use a VPN or proxy.
2. Q: How it works?
   A: Just a simple program that listens to the screenshots folder, once a new screenshot is detected, it will input the filename to the website and get the location, then show it on the map. Just like u did it manually.
3. Q: Can it be detected by BattleEye?
   A: No, it's just a simple program that listens to the screenshots folder, it doesn't interact with the game process or memory, so it's safe to use.
4. Q: Can you make it more powerful like showing my live location automatically?
   A: U can do it urself, like use logitech G HUB to bind a key to take a screenshot rapidly, then u can see ur live location on the map smoothly. And u can use some software like [OnTopReplica](https://github.com/LorenzCK/OnTopReplica) to make chrome window on top of the game window and make it transparent, so u can see the map and the game at the same time. In case u only have one monitor.

# To-Do
- [ ] Auto delete old screenshots
- [ ] Include chrome binary and driver in the release
