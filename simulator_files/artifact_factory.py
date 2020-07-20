#!/bin/python3
# function library to generate:
#	-Random artifacts
#	-network related artifact (usernames, network and system devices attributes)
# FortiSOAR CSE Team
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND

import requests, argparse, textwrap, json, random, time, os, csv, re, errno, stat, time, sys, getpass, datetime, base64, hashlib
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

templates_path 		= './'
config_file		= './config.json'
malware_hashes 		= './threat_intelligence/malware_hashes.txt'
malicious_domains	= './threat_intelligence/malicious_domains.txt'
malicious_ips		= './threat_intelligence/malicious_ips.txt'
malicious_urls		= './threat_intelligence/malicious_urls.txt'
SOCSIM_FIFO		= '/tmp/socsim.pipe'
MALWARE_FILE 		= '/tmp/malware.pdf'


class bcolors:
	''' Color code cli output '''
	OKGREEN = '\033[92m'
	FAIL = '\033[91m'
	MSG = '\033[96m'
	INST = '\033[95m'
	ENDC = '\033[0m'


def get_malicious_file():
	''' Pads a malicious pdf and returns it in base64 encoding and write a binary copy of it under .tmp/'''
	b64_malicious_file="JVBERi0xLjENCiXQ0NDQDQoNCjEgMCBvYmoNCjw8DQogL1R5cGUgL0NhdGFsb2cNCiAvT3V0bGluZXMgMiAwIFINCiAvUGFnZXMgMyAwIFINCiAvTmFtZXMgPDwgL0VtYmVkZGVkRmlsZXMgPDwgL05hbWVzIFsoZWljYXItZHJvcHBlci5kb2MpIDcgMCBSXSA+PiA+Pg0KIC9PcGVuQWN0aW9uIDkgMCBSDQo+Pg0KZW5kb2JqDQoNCjIgMCBvYmoNCjw8DQogL1R5cGUgL091dGxpbmVzDQogL0NvdW50IDANCj4+DQplbmRvYmoNCg0KMyAwIG9iag0KPDwNCiAvVHlwZSAvUGFnZXMNCiAvS2lkcyBbNCAwIFJdDQogL0NvdW50IDENCj4+DQplbmRvYmoNCg0KNCAwIG9iag0KPDwNCiAvVHlwZSAvUGFnZQ0KIC9QYXJlbnQgMyAwIFINCiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQ0KIC9Db250ZW50cyA1IDAgUg0KIC9SZXNvdXJjZXMgPDwNCiAgICAgICAgICAgICAvUHJvY1NldCBbL1BERiAvVGV4dF0NCiAgICAgICAgICAgICAvRm9udCA8PCAvRjEgNiAwIFIgPj4NCiAgICAgICAgICAgID4+DQo+Pg0KZW5kb2JqDQoNCjUgMCBvYmoNCjw8IC9MZW5ndGggMTE2ID4+DQpzdHJlYW0NCkJUIC9GMSAxMiBUZiA3MCA3MDAgVGQgMTUgVEwgKFBERiBmaWxlIGNvbnRhaW5pbmcgRE9DIGZpbGUgd2l0aCBWQkEgRUlDQVIgZHJvcHBlci4gQ3JlYXRlZCBieSBEaWRpZXIgU3RldmVucy4pIFRqIEVUDQplbmRzdHJlYW0NCmVuZG9iag0KDQo2IDAgb2JqDQo8PA0KIC9UeXBlIC9Gb250DQogL1N1YnR5cGUgL1R5cGUxDQogL05hbWUgL0YxDQogL0Jhc2VGb250IC9IZWx2ZXRpY2ENCiAvRW5jb2RpbmcgL01hY1JvbWFuRW5jb2RpbmcNCj4+DQplbmRvYmoNCg0KNyAwIG9iag0KPDwNCiAvVHlwZSAvRmlsZXNwZWMNCiAvRiAoZWljYXItZHJvcHBlci5kb2MpDQogL0VGIDw8IC9GIDggMCBSID4+DQo+Pg0KZW5kb2JqDQoNCjggMCBvYmoNCjw8DQogL0xlbmd0aCA4OTUyDQogL0ZpbHRlciAvRmxhdGVEZWNvZGUNCiAvVHlwZSAvRW1iZWRkZWRGaWxlDQo+Pg0Kc3RyZWFtDQp4nO08B0BTV9f3hQCRIQGRIkMfERWUkYSEoSIkYSoICuJCJUCEaEgwCY664qqiHVit1WrdVmurUldbR0VtHa1WamuLWhWttrbVFrV1fA7+c9+ARwRF2+/r9/8/B07uufvec889d75becK1etUHXheRFfRCNuhRbStkx3EjADuzFiFCAWDwAB/V1tZip06AtS3wvwqurduPJlS0ESBU47avrmUBwIUAbI1yR+WO2uu619VaQhBqxfdAIa0RujCRRuLxIA2gttblqTQLH1K/r9uiOvOaG00/yXRvkBstlagN49CI6QSGE2Oy7v3aIiSGqngy9qeZt5owY6AwC8A8yRSqOaY/mNM8ENoK3SqsHULdwX4b3Ns+xp/6erP5WUNT5WLN2+4Nw1vz09MqXWw/C6YjFAaKiOyZ+NYmTt+hkXSs7TFW+dtb2ZsLt5qZ3vOm3xSw6bH1YeWtZu/bO1pfrKzrDKz7Q4Yv1uXo5k7LrR+WO0TLHzf9onZPtv9dwKbLAtte9oxcWssPt7255tPgafJoLZdNQXPr31R+LJ+f1k9YYNvR2nya/7/LZNvraeV/1vZpCppKD+tmEhToVhghuoPU2yI3+MUjSgv894PzP12AFvhngZnnPfiny9EC/1Gw8yicrM6DKTvT/g//6QK1wH8a8AyVCEKSskKiQ/n0ELL8kMKvvNRWBNixrNTWH7BTOUIvlH/K8wR0KvuU908XuQX+bhjFd0FuIAqOhAuyRzbUH0J8rBbQYsDlT8Fwu6fjWN7Tsam4vZ7g9+/ADZw6eTSjfh81kwdcLISel0T8Z+v134rlNrQpBfQEXlaAvRKwGrCGFkUkBCQBxYCxgOmAOYDFgBbAMn7T8XC6ASBDVcDvq8Tzp/P/PV4k8G4Q4F1AAfDTEzALcAogCcmk9bZB6YD9AEckEfyipDYCPaAJ0JxErwZ7Q7I3anlgOglZ/WOH+iIDMqIipEY6RO/EueW7EwRyX3sEJELV24NKTw1mUV16rfiPa7I4pCBv1q4C04lZ1AihB8chDRoJaZdA6mYoaTrQRsAC6rcYFYJbApRAD74Y+iMtulW7DUw2FbGdE8qEsLmQggZCNyyvD3rhNrBR9q0dIhxsdDRhCy5q7MxDjgjvk48m/6jdj/fL69K0p9IhUQrkZ6Ly5tG7kCi9jw3fHfiCWeaHfj7vsg8v93149AblUJVBb9bozSMyJxRrTMNCxhfp3p//Rd+DYmH8naQHM64E9162NVbQ6efph189vHpSxZEl/h5Hq7auH3D/TsrJTOUG0kMXdDrszvIePxj3drDfcXDxsvW9t9xUdvP/1Ttx2LoLEWmnN2WVTvPy7Kle57L4j12f7AmImG1JLn2r/7qJPxYXpGyNfrXM2KFs7cl/RfK+kI/tbHloaX28pN/3nr+Wzo/84ajquys2O8t9B0X/duXeYv9LZdt3xYT3fb+3SjBjW8Xr31zbcC/hqIcy5POPu/wZsrZb6arjgw9k3mtXfnW4Rv6VfMN58qbjy24Hy51KR5woINsF/7ivx/LSa2e/Hazbc+7Vra9OCh9+rO/+WvecP2Outvn62NShU3l4L8TGil/rvl3/UwXWySCnmPcjjBqdKTQE/8587cSog2Kn2b/P2jvjq8n9Th707DQ2dF2ZKnTNZHQxYGqhyPus969n0w7bOewWzFz7+513ox9tnnfv4sKfSI+3NtodvKSK+aLw4tjofVOnH521dn0nwdDxxS+tmXh2x4g96V+t6Xlc4r0uaaf4DTeXOafT9vTfrMz/6qjwZO/4s7Jc/6nr548Z8V2HxcvbVYenfP2nR//vInI2v7bhaO22g+Jjy9P2T90SdCWer49YmKK9nLtqQ+gPGXvLNmg2ftO+csdH9759SDRW0dETFnnMAGouJYQImQs1RZpQzm+qWq8u0BixhDgdS3U4SApjL05eNa7sdETe7oD43K1fbN59G6mWeSkOrzy54ux3V36YEfHlBfdTS/s4Dw5aZu88V3M8ZM6HNZOC1ntvOJPk81mQ7uLhtj/+PN7z6PZX2lxIPmLqN7njqbJZm3acI7/d0e2U3+9B54Z/7D8qel7iwKtf3wm8FP9rt84OvMjGCy8+pwrcAJp5rTc9yj5WeAku9rXBaYaz4e77XKrGkWZDXpexXvYlc6s+WBqc6v2pfnZ7bemiqvTVsSeTJ3uf+cFCHNylnt22qmi2eug0j6p192Wnu+t8K7eUJ/Z//bNBw18Pr5q7qZe/270f7te27/Due9/9dtjJ180vMO3M8IfG4yr/GxNiF5RfP9f+duimCUldl/EX35i5fW/g/PM7XrlzYffc7wbE5U7PmSz6bszZeQt7f/fmorUuBwcN/zEwOUd/LP7ltnvmFgcK7wquHtJpP84aOmyuJLXnwmrPI+e9Xns3rTJ9wR/hxkvRdltKX3+xoiB3ZXKbgln77exLXinLOK3h+eZ+e9uSVvHaS5c/uSk82H9/3Nn3lqz4cPuYklZbCuYtHlK+c/tmw5TTu3SK4nLd+LnFmeJNd7w3dRtqO9kmZ1T77379c9feFxUnUPnvM97JWiQ9njB10/mj2kWxt8csH/vht+/LsyeVPvp82bFNfdd/rdNsHbTaLr+Dt+nujjOj8kyn93uXfRbxU80rX478cPcv1c5HLg38qeZht02nXpoXsXLOV5dzWm/yPfN7wTeORxZvu977rlfFd6PaTXppemHA6j7bPG/FBc/d4Xnhh9UuyDl/0Ff8d7W9D1XNDvjt0nj/gG+darrvX9eux+UvPvY77pg8ojJzx16XDKd2kjV3frl3Z8vymPjDLst9Y+7+fPfiwR/sY4Yov9xYtGzmlQGh+x5eO3G4w5qY5VNu3fzqhVPjBx+q/dfBLvsePJggF54s6PzlvNAVD25fOzpvS6+HD3cntq1JnZaouVt2KG710suC67c83cOyxnTq0nHMJ20PCr6+Ofe4/8LI/W/1sX24fK7PH8cDRy4Z5xPV/dMd1b7ElTUO4ycbT7iOF5aWrm67bNzqKuI345fdszOHqBNvdV0yITL5wKgfc/sfup43adBnu+e1Obxvb7JDSZhLn8Qb+jgfyR3Pvu6tk5XuJ00PLGUO13/r/0tVyZv/mt6nV9bVkHjflG6p0rUdu7w1ct5OrdOUJVk/Oz0aq9s20b4k8r2TL87z2ZV0xOFY15kd3H5cfKP78gCfgfN9Li1+w3mKzXsbeh/Zn3lXk53Wtcac5Jm415I0eMePi9DkPn0v7E//oOu5T75454N57nPbZ361Z1pUaMcP7yoiDowZMsu30r9rXkyZvXC15/UxA2wvXNG/dHVcjU1fj133W3d6dXfaFrsPtVfnyByF0WGubT/Z0/ejNvtmBHrn5fZ2di9Zn3VYdm/3geMBmfovLl5yiFj4+QsjYjaX3S8KPr20fOKAK8dulyr3CsZt7TnuY8HVsyPe/rDG/3THMuGtod/svvRgc+TE2nuX9gSsCP3E/8RGsXvhuXlVCWe3n7txYPPElHbeGwI7RqzV7ul0LVrRwe7P7qZL/p8FBr1S3a9AKi4uXlUx0tkte3LcANmcYofUiee+jlMumd+6U++PZx5c3W7z2k03Ku92m/iN7hfVnE0+bu8Na191sW30shVyB2nCxkqfQlNCt7cqBi/ZlH10znT9loPvb57VPezDXa7H3eNnD121NfyDqIUzjjqeyikv7yyTC4b4ld/suuyefHTktZwEXtG4X9d8H3zI8YWfRe0uWvJ7nXzxxP0N+mULD3++TDTExdvpX9Xj557q/f2Qt655F/eYt+Dza16OVVfOT2wTesW15y239B5LXg0K7NKlT2W/s6Plby5tf3PMmduHivu+dDjSdkufc4m5Hgc0C7bMdL6fseB0/r1jSzdlSyJa/VL8p/p6r/XlGfb9/U55LJrv7Bz2xizUR9alW62xzbEX+zlkZq7ZlvzBVrv9NVuSibHmYX0O5V16b+u2Ph3PjL0t77Zu0uo5nnH7Xb0+KK06XD3Fd+PKtNhO2eMWz105olrfd+jZlI8/i+qz6+Yri/efHnPspKDgStb6wuVHPfQO/f1mTOhWar9rwOf6hT32de18JTTpDaNn7YnMr+63+r7X+/wzNr2ynR1fNr+zPTok89NVDutc/7zP87LP6EEOqZ7ywjt+G6qnn3nwwuX02g+jCrSLt7+kWntmvZ+b++2ObVspb68MWnK1x6xB0Wd3ByUvcpW6DnAb+E7WNdcof92G0dUbz5+NdldsWDrq9TeIGT3aTf1t4iLFmvSIqCuTTF0Hf3DnjM/d9T06LD22cuHQ2amqBWf3CT8odBm5e+Mww6KfJhoGu0ZLRm/zmpCFtp3Mqvz85CN5fORPWaO7fbvs0BfHsyNrLu05JB4kiwv83s/vof3tmK6TRu4be9W55MidVTtFd8evKlVUxWaO2PqK/Unbk61fXTlm64zwxbLA0WfeLzmZ9UXEr46/mR0/6fLypk495u07ob22Osp0Ourj8fMPfRl0rerMq8Ey+fjb+XMPVEbGHPE8vPhE/pXQwZPMLj57bS84dU5JbpNS83bvnKur7Du7kPeCE7eZfwhFjY1tzl+VrdgJlDeMfF2sxjZ6NmI9PDOzk1SHA2L3mXemjxMYDF/vEs7vfG5O5aZvbGZeljuHx/j3u3bdeXOQIGS2+pMl2t1vvn20TZ70vKRwo5eg+89vjHlrf9FH116N7e/Rt/R0j/zynOmvGiKuty2Y3ycgtbN//4AQyWJj6y69FyyrnJt5z7I5cs1rWZdFa95RHNldmXSnZPLKG0uJSZ/5780VTjyF2i1Kf6t228NIr9KC0A4ewx71U5hOz7INWH3oWHXHpRtT+J8P3bXr0wt1VSd4wajp6WpDaGTyap2A9fytHvCZPGc2Zx3Rej5UD+14T54dWadkPTmph28bS0nSWBrWQlAPW1s1WyTS+9ja4Si28DcMEtqEj49RzxjwJ8dqjCatQR8tkoSIRaRGn2fI1+oLokUDMhOCI0WkyazW56t1Br0mWjRBYxLF9HJ26KnunqczpqqLSUhAb+qujhYVms3F3UNDTXmQvdoUYijW6MFvpMFYpDaD1VgQmm9Uj4OEi3ShUrE4PLRIrdWLyNwCSbRIZ5aISPN4oPJHS7CbFLtJsZsUuwGlzsuD1oYQDMG6SFmXujBhrEsY6yJjXWSsi5x1kbMu4axLuIgs1Gn1o6FG2BCRIw26JNqBpUShvTD38KZnG3ytBTEnqcz+N3XRhKEx011geRxJNZhdDd6X4PHpu04EB7E9FrW/IaTSolJEFosF3cFLTxfEq3kdYUpQI2Aj8XHCNjViKgN+TQDl3qqmbjXMAR5yoOLhBbotE14JphvjjtPC1chAjjXtgdxH4Ly+oK4d1OJFOuLbgKihGBuCytu1ho/qr+jglb89h2J2AijpvVJXAoQ6uZMInxNEvzgHseyzYfwJKif8m0XTDY7DMQhroSQ8WMWnw4rZgEbB+jkP1rohKBVs+dSaXIMkYFcAbQa3NFiRa2AtTiBXXGocsT849kbxSAWLcBwxDZb0A2DZHM9EHADuafCXDi59qQaxNLyHRDRyL4knrPOktjmFEA3hwmJeDIACjAY0oHHwi125Z9l0KLq2PLbZOTRuq8T2ZRCIx7OzseXb8mz4tV1RtWI8qmjFpsGUKBMW/0VQYRO1raCB/Eior4HaXNCDvxzS4SFbW4JH2NvxbO1ZtnKKY8E/GWgCxMmFmHhLIiyEyt3Rjs/DQOWuaiR3BTSKltnGiKDjuNjiCDYQh4eqa99HsSzrVjCEigqvhbxwXEiDrinfFmpqx8bzR0rUSLwiJpYaapkKv2ZUCD4ikLsbgjmeqOZT3mX+u1T44+ciZ1cBUk3VgPt0cnxkU4Yec2XBzwZRPepp19FaoDEotS213Y62o2nTjOKmQyXHXOvwPKlzTpD6zHDF7SRADx422VKCpHRstKqpdUGt/IG+zKfU9tSmEOsrrMikjSbn18i2odCH1nw0jGeQhZXMBUR2KvI9wvm7WaXBp9SbASS6nvpfAo9AadkRjx/s4SapnrXi5r20QuF78wWoW5dtp7E8ZBK0/sH+eEjAMXFfxIPCMkSzEp+hYL7hsxGssz5F9MDyDSBWQpcRHsZggEX0jTghQe/7+hD0BmkAQQ/QMoIah1FPJs84gp5UphB0vlgY2qP65rOmcZ5Gg8HclF9fPM/RNR1WytB4/E/V5hkNJsNIM5k2cqQ2T0MONBjzER5uAMRe7QmW9nDt4nyxkqBoz5JyfBPQBjUcOK3NFmiBFmiBFmiBFmiBFmiBFmiBFmiBfzc8af3PO3X81LIQb+GCN2H9H3RvM17/X0X0Wh374+07vD4vRvR6fxKi985nAuLPRV8GfAFwIaI3UPD+AF7Hr0X0Ov59RB+wbEf0un8Pk/ZR1Pj6vqn1M222rtukacpsL6zfu6euoOFM2jOFztSadRrELtVboAVaoAVaoAVaoAVaoAVaoAVaoAX+TwF7j429AIbX8Xg5jM/t8bte+Lwen9HjNTRem+N1Oj6bx+t+vJbH63x8lo/X8+5MHLymx+t+fG6OHynxAvRG9LVM7I+X3Pj2CInwVUl8BQihjoh+ZQb7PwTElya7AfYA7AoYhOjXkIIBQwDx3Vu8HyFB9Dl9GKAMUA4YDhgBiO/vRQH2ZNJlsQXqoT9zXYVE8dQ3cEY04ZnkxwPZEmxaWIbsWtF7SRW0dwI3bE3ISuplpEDs70e7STjf1j0PtKYu3tVDc+Lgux7s6zkDqa/58lEcmHmohLqOp3+G6zteiEfgPvMs+VPAXOKzRRlUrkXUd4kTUDLkPrLuC0Mz0lLfJjYNAZA/5jgfPf4iUVPQtkH+1jV/tvJEQv7Pyn9fTv74ImAedWnK1Jyoj0FrRFBXULFecmoijFg9h5I765e5MGQhJVI8V840CECDsnW3byLMk/LPRIXUF6B/Rf6wPGM9/Szyt4zZPH2S/mfTbUz/Yz3amP7HsvUk/Y/b/kn6H78h2RnRl+bx9WisK7D+x2MBHgOeR//jcQOPI3gciEb4bUuEYhB9Xwu3Pb6tqkL4C2IEWpBWWomASYDJTF37gJmCsLwi6ppxGiC+m9gP4W+G8RVc3JYIDUBYprBeQWgQ4GDAIYBDAbMBhwEOBxwBmAOoBswFzAPE98mwFhwJWIDo/XV8yXYU4GhAfFG3CBD3PwOi993HABqZMmKpKQEcCzgO0RcZsTZ/EXAiE2YyY05F9N1hwoOgL+It59EX9M4QtCCtA/s95lwAC8mS7x/MxD5rCPri3058E5q+bV5b/zDZMyjABoBFCYsgFj97VK9OCUq4MYUr89Q3xejsU+O5hWF/6cJeYOxO//hLpfTrqRkiupwEyhDWUYwb+PekKbb0BPQJSYMv0EOeqEFwbILA/YBnoWc+QsTkTNQ3FVsiTOP+yb7jmlTH03qVxa2Btb057tb5PZlHdPgLzZOhxuHR50QdI7iyxDB7STlSmM1GbW6JGWnILOWIvmpgIBlNijILgatxhrySIo1eaBY5Ozi8rFSbCN7LEvreKC+kXVaizpCr1vkRGzOK1XmELkEt0Jk0TqtVRo1aaFbn6tp2SDdqyHxNnk6N7JLzXdHyTGOJszJ+fLHAYNK4+2RqioqRTm3WxGmMWt7Ytv6qEpPZUOSkfXGmaoakOdWr67/XmP47h+m/t8DegxkR6f47KYD+ZosGpv82/BLj2UEIkuSAnm3+g9cOM1vT9AhmBB5h9alHc8HrOeYfvQEDHWg6H/qOsdm5PQ6C55h/4plOGKNaG9Z6HKXfnwXcnyN/fE7LmfM07IrPmD8DzdPfT30/qvn6+8l64z8B3FLVA0FUMaWLfIy1DTWgdS0yKJ+ZFJdyZnblse4CzodVOTOD6tx5DdxD6txbMe6sksOzBEe37nX+z1MebMejAWH1kVdZEy3RlLs1/6zL0pwYf3k0yECiaYL6h80tAj6WUQGHFnJoT4qmH5yhCjGNdiexA9B4chrA0HgCO6iR8FjXWZgwrRm2sfRKDl3OoSs4dCWHrubQNRyaUvIMLeTQJIcWc+hYDp3OoXM4dDGHtnDoMg69kkOXc+gKDl3Joas5dA2HppQDW34OTXJoMYeO5dDpHDqHQxdzaAuHLuPQKzl0OYeu4NCVHLqaQ9dwaEr9seXn0CSHFnPoWA6dzqFzOHQxh7Zw6DIOvZJDl3PoCg5dyaGrOXQNh6ZWf2z5OTTJocUcOpZDp3PoHA5dzKEtHLqMQ6/k0OUcuoKhcV+rxLRVn8L9rgpc+NMElOgIbKkwiA2DgSA8wXURn/5YcBi6yY9lzEGMiZUjCf2uCwriXYc5kRfKyDNqi81afUFIglanyZhgMmuK0nJHafLM/iB/BEy4Q3gkQIZmJ7AMPIv9kRTcd0IHzIblMAn+fkjGc4U0u/JwAiSYJKT/HjoG0kyaaHozaIpBcReQ1sja5ZQ9W8Ta0yh7cV/W7kfZ9SRrT6fsSi1r70SnZ2btsZSdrAuvoO1BDePX+w+l7EF1dhntn87as2m7qmH89BLWPoSyq5QN61diblg/5YSG6Zvr8gug7BPMVuWrq99wOryGtQfS9U1g7RGUXRPA2lWUPUHb0B7Q2Sq+rmH8zkmsfTJl19Xl50/Zk8JYezydn561J1N2uaphfvqShvwXB7L2/jR/ilh7MGUPrONHBmUvqmuvzEbbs769+lr5x1m1t8LKv79V/Dir9g62am+FVXv3tWrvTKv2TrZq7yyr9k62au/+Vu09wKq9M6zamy4f7r+N8yfeqn4ZVv6ZVvwJtvJPsIqfbMWfFCv+xFvxx8+KP/5W/Emy4k83K/4kWfGnK4c/+Iv7nagdik9WKfqTZo3JTI4EdUWOM2rNZo2+O4mw1nFFithw0E1yKUgVaQC9eNWJ1o4C57oVcMzWplbAqQZYGeo0Elj7ZqCSXFJRYjakoWKNPiDQ2QHPK+K0RaQpQSvQafTERwoTmRGIZuoL7CO1vMiSItB54cl6s6ZAozTaRxoSMtIIcVo1pUltQmxs7cIroskEo0ZDxNl4CjM0ZpIXHg3MhKWzWWPTI0BUp4n5BSFEEKWIvYpsvEX89+zXR5PxSD9WazToA0QE6lQsCiQ7kyKnbBGyJYJDEjXmGryynmax6T6DN20iIRibYDCSSq0eqY0TSEVenqbCZCIHGrWWt5FZNWv4DO90aJZZgiAsDSrlBLMmJ6BzkjySn9JWGPa63EcoS/ARSiU+wmy5+G3yPDlMKHtEyl9X+gSGyXwEcpWv4ONhErlimHCKabhE+rZn8nCTPD5bIo3y4YfdjPDhy8I68O/nThVOFn4TETdJKPVNkJ0f7ttpaC35KFe61/Ocj3yyRD76Efm2uyy6t2yE0/c+8vsPyeFOUt9OUxae94kJ9E3YLg9/QMp6CXw7yfcOueHSUV9SFDV6hbsTb6pwqhNvhdyXn9athyDUzocvvf97e2++bIuHEw+ji6YWE468LROGOb0WFmT3e871IDtlh05nfGQd+D78AYZqlc5g0mS9fGsoTPlTTQVKw3hSVCdZZVi0alaS4yrKcijJUr/xzpvOpEO8Pp8sW+vsgJyZlfTzwTH1m9SyAr8QiQf4y/z6BRUBy0ke+hcIfjZKRBORmPqTAsqgsyVAhxUzf1xK9Zgb90+GwkGxdwQzBEnAjAJUoe6QA70ST4RfBZoCftngnoZSqScn+jIuqaAEVFS4DMaF3r1gzQiGigcqBBRqCvx1BBe8P1dC7deR4KsGmxblIfrlSSOYClQMfzrKtf6UpeGJiJB4nA9RgPK/xIdIKKccTDGHD/g0hn4fs4gqo5baHTJR9dfWndYY0Ejq3DANzJGUuwZCcG0SyAXHyUADwb0/8CMEzBTgQMdGU2LP4kgqZgiUCaeeW/duCP1aZi5VMutzyj2NSkmYFU+elTtSqhRc7gyEEuihjPhxEMwRE5QDv9+pAV6FQfhsypZPPcWhoeKbgcqF+GnUoyVk3VsnTZ3vuVE1UTXY5W3MrW/XVQPZDfGAOtmQApcToFXjqFqooH5y4HcC5BoMXBUDKoFSgn98neQo4I+utYxxl9bVvvmyoaLqVETV5+lSk4EKqVbUAK+w1CTAH+5b8RypSeP0oadJ3vPIDA/+CGSHnGD90BqGSbzsdAN0B9oD0IfH3ZlA6I1uqwbaP3GP4mk7GETd8zENYcn3+JWcpnby3aFWYdASEVAHCbSKGmqqgZQ68JqOU1uLj2uYakKxqE2c1lbbve5Uo3MTlsNfbW1nnnXI2tpJAXRq+OFfpHBia0oQkby/dzfO829OzxrQvzn9/48Q1ONsvm7Q9JS3DFWXZy348xJ2w3K+f5/r2Y2fbo7fmVnV/XCYfgbrjk28n2ihRMqX8EI2RBAIGJ+Pn9XYMVqIbPhZSsWdS0Jkyx+o1UvC909hyDCp/VSGDJeNn4pDpqrztm0VQmSIEr6pI0NFbAZKwE83GvCUU+LwghDZ8U3mfINOsyBHiOxZn+DNQuTEzyzUsoc95p7LhagVFK3WxgaNiB+r1pXAlNTztBA/Vk0d/VyoAnqmgApAPwfStgSnCBNmPF/OdYX4jDeeM49IgzlzFlnvaMJbC3p1kebNc1BExlFLOZYUeThCBRg3PGsO+wbKh1TUvJjeiLg7FzJD8fQE2DtIiByZwsLEF897YQKvaeeEi0vP5t7sz+ZCILaOo76uz5ma10MRT3cVIh7u0jmI7SIing1Q/jw+/HYBleiCBDysxByesRN58fB2Na1QO/CoV9CYZ2T8nzZDfDIQoVstBKKfNhN35fHKWqFid7skGzSdh/Iv8/nAKB/EtLRtP7xTG8tzt+O5R2/iOdjzdIS7wM6tFc/NQut2J15vt548Bw9EGEFShCAqvXjtqOe5mRE9HTmDwu00HNnAgJs4USwWS8XlsjBxMEgaX4UcbHitCTexWBY+GYbPEHFHcUcVjJsgq/mGcTAUmqjtpDC+NNtGIw0x62BekJYSjxdWFkOR2qw16PH+H29GPC1ntkBYVNSA38+S0BqRFtdWFqKrU7bKxs3BDk8A+AI0w48SQdeZBTAeWvBw2HZ6wXJLh4XT/RInwnQgITJOLFPBPECZoAiWiCWxymBlXLzcUqAYpbBoZBZb6ZwCyy4Y09VFJBZBZMpWGYqKDHqCb8e8eoNGmsmMQrURBuvstISEZBWM0rLs1Iy0kDjPlJSOs4UzUkmJjAwRk2m5034gUyq0uUZYaVk6WZDIZfqLPNTmAAFDXDulhu5miJbBROTgWdEqs2IkHsBEcRVJMIDFJmvQRn2F3utLR+kZR58Ktw0IJSkJibK0tuItj/ZKHmEbdMDvwUxRW6Wgm5JoN30VdDoL7nWJqDWy9Uq1+OVb/Ka9IkFeRa0EUqEgzVdhWZfqOykowO+At8pXeKDhIRS33z/hKJ3p2X/5uPQxSI6LFk2MkKpkKokyPDhCohAHy8ThCcGKMElYcJRSFREZFyEGV8VkWIWzBY3mljq0c5KYAWcHupzRTHGdHbAqiBYx8g8pJGl0xdQjnOPNOGex6PlOXesBn//ioxR8Pwh37ubEmQK4hJkGEcy8sZiZtT0ruD3H+ecshP7Sma81PGv+fzf8lfynAU4HxE+n4gkjviXyEmO2wP99cHbIol+SBZ1fDCNQrk4TJo0WhUWFSaVSUCmgM1SpidGiiLAIiTIiPFIiDldxEWuldGW0KE4cJ5XIoiIkchrBPVEVLZLGSRPioxTxEqVYIVFhTJCDl7PD0CSDyUzGjzdr9PkaI5msH2kY5uxQp8ok0RPDIsOkceEycbAqIUocLIGYwZHxsrBgsVghVkVJJGKxXDG5R5YyvgdXAULKMIUcbSpW52kgQa6ijBYHkXX/KlZXSqKl8iASo0QSHhVEymWSIHJIsze1COgpNg50H7S++0wi7rtxeGZLRkUEA1fDyLohB+eTmoH9wImaEmE6hPUPiUR/RG0d86y9uvnwP1QBLuwNCmVuZHN0cmVhbQ0KZW5kb2JqDQoNCjkgMCBvYmoNCjw8DQogL1R5cGUgL0FjdGlvbg0KIC9TIC9KYXZhU2NyaXB0DQogL0pTICh0aGlzLmV4cG9ydERhdGFPYmplY3QoeyBjTmFtZTogImVpY2FyLWRyb3BwZXIuZG9jIiwgbkxhdW5jaDogMiB9KTspDQo+Pg0KZW5kb2JqDQoNCnhyZWYNCjAgMTANCjAwMDAwMDAwMDAgNjU1MzUgZg0KMDAwMDAwMDAxOSAwMDAwMCBuDQowMDAwMDAwMTg3IDAwMDAwIG4NCjAwMDAwMDAyNDMgMDAwMDAgbg0KMDAwMDAwMDMxMiAwMDAwMCBuDQowMDAwMDAwNTE3IDAwMDAwIG4NCjAwMDAwMDA2OTIgMDAwMDAgbg0KMDAwMDAwMDgxNiAwMDAwMCBuDQowMDAwMDAwOTA3IDAwMDAwIG4NCjAwMDAwMDk5NjcgMDAwMDAgbg0KdHJhaWxlcg0KPDwNCiAvU2l6ZSAxMA0KIC9Sb290IDEgMCBSDQo+Pg0Kc3RhcnR4cmVmDQoxMDEwMg0KJSVFT0YNCg=="
	malicious_file = base64.b64decode(b64_malicious_file)+bytes([random.randint(0, 256),random.randint(0, 256),random.randint(0, 256)])
	tmp_file = open(MALWARE_FILE, 'wb')
	tmp_file.write(malicious_file)
	tmp_file.close()
	return base64.b64encode(malicious_file).decode("utf-8")


def get_malicious_file_md5():
	'''	Computes the previously created .tmp/malware file md5 if it exists	'''
	if os.path.isfile(MALWARE_FILE):
		return hashlib.md5(open(MALWARE_FILE,'rb').read()).hexdigest()

def get_malicious_file_sha1():
	'''	Computes the previously created .tmp/malware file sha1 if it exists	'''
	if os.path.isfile(MALWARE_FILE):
		return hashlib.sha1(open(MALWARE_FILE,'rb').read()).hexdigest()

def get_malicious_file_sha256():
	'''	Computes the previously created .tmp/malware file sha256 if it exists	'''
	if os.path.isfile(MALWARE_FILE):
		return hashlib.sha256(open(MALWARE_FILE,'rb').read()).hexdigest()

def get_formatted_current_time():
	return datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S %Z")

def get_username():
	usernames=["Morgoth","Lúthien","Glorfindel","Beren","Túrin_turambar","Eärendil","Ancalagon","Manwë","Thingol","Húrin","Melian","Glaurung","Mandos","Maglor","Elendil","Círdan","Finarfin","Ulmo","Morwen","Beleg","Niënor_níniel","Finduilas","Orodreth","Carcharoth","Eöl","Ossë","Yavanna","Anárion","Lalaith","Emeldir","Dorlas","Aerin","Rían"]
	return random.choices(usernames)[0]

def get_fgt_mgmt_ip():
        p = open("config.json", 'r')
        fg_mgmt_config = p.read()
        fg_mgmt_config = json.loads(fg_mgmt_config)
        p.close()
        fg_mgmt_config = fg_mgmt_config['TR_FG_MGMT_IP']
        return fg_mgmt_config

def get_fgt_dev_name():
        p = open(config_file, 'r')
        fg_hostname_config = p.read()
        fg_hostname_config = json.loads(fg_hostname_config)
        p.close()
        fg_hostname_config = fg_hostname_config['TR_FG_DEV_NAME']
        return fg_hostname_config

def get_fgt_sn():
        p = open("config.json", 'r')
        sn_config = p.read()
        sn_config = json.loads(sn_config)
        p.close()
        sn_config = sn_config['FGT_SN']
        return sn_config

def get_asset_ip():
	return "10.200.3."+str(random.randint(2, 24))

def get_time_now():
	return int(time.time())

def get_time_past():
	return int(time.time()) - random.randint(86400, 172800)

def get_time_minus_one():
	return int(time.time()) - random.randint(3400, 3800)

def get_time_minus_two():
	return int(time.time()) - random.randint(7200, 86400)

def get_time_minus_tree():
	return int(time.time()) - random.randint(10800, 11000)

def get_time_minus_four():
	return int(time.time()) - random.randint(14400, 14600)

def get_time_minus_five():
	return int(time.time()) - random.randint(18000, 18300)

def get_time_minus_six():
	return int(time.time()) - random.randint(21600, 21900)

def get_date_now_only():
        return time.strftime('%Y-%m-%d', time.localtime(time.time()))

def get_time_now_only():
        return time.strftime('%H:%M:%S', time.localtime(time.time()))

def get_timezone():
	p = open("config.json", 'r')
	tz_config = p.read()
	tz_config = json.loads(tz_config)
	p.close()
	tz_config = tz_config['TimeZone']
	return tz_config

def get_random_integer(start=55555,end=99999):
	return random.randint(start, end)

def get_my_public_ip():
	try:
		response = requests.get(url='https://api.ipify.org/?format=txt')
		if response.status_code != 200:
			print(bcolors.FAIL+'Public IP lookup Failed'+bcolors.ENDC)
			exit()
		public_ip=str(response.content, 'utf-8')
		return '.'.join(public_ip.split('.')[:-1])+'.'+str(random.randint(2, 253))

	except requests.ConnectionError:
		print(bcolors.FAIL+"Connection error"+bcolors.ENDC)
		exit()
	except requests.ConnectTimeout:
		print(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
		exit()

def get_malware_hash(malware_hashes_file=malware_hashes):

	if not os.path.exists(os.path.dirname(malware_hashes_file)):
		os.makedirs(os.path.dirname(malware_hashes_file))

	if not os.path.isfile(malware_hashes_file):
		try:
			response = requests.get(url='https://cybercrime-tracker.net/ccamlist.php')
			if response.status_code != 200:
				print(bcolors.FAIL+'TI Download Failed'+bcolors.ENDC)
				exit()
			with open(malware_hashes_file, 'wb') as f:
				f.write(response.content)

		except requests.ConnectionError:
			print(bcolors.FAIL+"Connection error"+bcolors.ENDC)
			exit()
		except requests.ConnectTimeout:
			print(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
			exit()

	lines = open(malware_hashes_file).read().splitlines()

	return(random.choice(lines))


def get_malicious_url(malicious_urls_file=malicious_urls):

	if not os.path.exists(os.path.dirname(malicious_urls_file)):
		os.makedirs(os.path.dirname(malicious_urls_file))

	if not os.path.isfile(malicious_urls_file):
		try:
			response = requests.get(url='https://openphish.com/feed.txt')
			if response.status_code != 200:
				print(bcolors.FAIL+'TI Download Failed'+bcolors.ENDC)
				exit()
			with open(malicious_urls_file, 'wb') as f:
				f.write(response.content)

		except requests.ConnectionError:
			print(bcolors.FAIL+"Connection error"+bcolors.ENDC)
			exit()
		except requests.ConnectTimeout:
			print(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
			exit()

	lines = open(malicious_urls_file).read().splitlines()

	return(random.choice(lines))


def get_malicious_ip(malicious_ip_file=malicious_ips):
	lines=''
	if not os.path.exists(os.path.dirname(malicious_ip_file)):
		os.makedirs(os.path.dirname(malicious_ip_file))

	if not os.path.isfile(malicious_ip_file):
		try:
			response = requests.get(url='https://malsilo.gitlab.io/feeds/dumps/ip_list.txt')
			if response.status_code != 200:
				print(bcolors.FAIL+'TI Download Failed'+bcolors.ENDC)
				exit()
			decoded_content = response.content.decode('utf-8')
			cr = csv.reader(decoded_content.splitlines(), delimiter=',')
			for skip in range(16):
				next(cr)
			bad_ips_list = list(cr)
			for row in bad_ips_list:
				lines+=row[2].split(':')[0]+'\n'
			with open(malicious_ip_file, 'w+') as f:
			 	f.write(lines)

		except requests.ConnectionError:
			print(bcolors.FAIL+"Connection error"+bcolors.ENDC)
			exit()
		except requests.ConnectTimeout:
			print(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
			exit()


	lines = open(malicious_ip_file).read().splitlines()

	return(random.choice(lines))


def get_malicious_domains(malicious_domains_file=malicious_domains):
	lines=''
	if not os.path.exists(os.path.dirname(malicious_domains_file)):
		os.makedirs(os.path.dirname(malicious_domains_file))

	if not os.path.isfile(malicious_domains_file):
		try:
			response = requests.get(url='https://osint.bambenekconsulting.com/feeds/c2-dommasterlist-high.txt')
			if response.status_code != 200:
				print(bcolors.FAIL+'TI Download Failed'+bcolors.ENDC)
				exit()
			decoded_content = response.content.decode('utf-8')
			cr = csv.reader(decoded_content.splitlines(), delimiter=',')
			for skip in range(16):
				next(cr)
			bad_ips_list = list(cr)
			for row in bad_ips_list:
				lines+=row[0]+'\n'
			with open(malicious_domains_file, 'w+') as f:
			 	f.write(lines)

		except requests.ConnectionError:
			print(bcolors.FAIL+"Connection error"+bcolors.ENDC)
			exit()
		except requests.ConnectTimeout:
			print(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
			exit()


	lines = open(malicious_domains_file).read().splitlines()

	return(random.choice(lines))

function_dictionary={
"TR_MALICIOUS_FILE":get_malicious_file,
"TR_MALICIOUS_FILE_MD5":get_malicious_file_md5,
"TR_MALICIOUS_FILE_SHA1":get_malicious_file_sha1,
"TR_MALICIOUS_FILE_SHA256":get_malicious_file_sha256,
"TR_FORMATTED_CURRENT_TIME":get_formatted_current_time,
"TR_FG_MGMT_IP":get_fgt_mgmt_ip,
"TR_FG_DEV_NAME":get_fgt_dev_name,
"TR_FGT_SN":get_fgt_sn,
"TR_ASSET_IP":get_asset_ip,
"TR_MALICIOUS_IP":get_malicious_ip,
"TR_NOW":get_time_now,
"TR_DATE_NOW_ONLY":get_date_now_only,
"TR_TIME_NOW_ONLY":get_time_now_only,
"TR_PAST":get_time_past,
"TR_TIMEZONE":get_timezone,
"TR_RANDOM_INTEGER":get_random_integer,
"TR_MALICIOUS_DOMAIN":get_malicious_domains,
"TR_MALICIOUS_URL":get_malicious_url,
"TR_MALICIOUS_HASH":get_malware_hash,
"TR_PUBLIC_IP":get_my_public_ip,
"TR_USERNAME":get_username,
"TR_T-1":get_time_minus_one,
"TR_T-2":get_time_minus_two,
"TR_T-3":get_time_minus_tree,
"TR_T-4":get_time_minus_four,
"TR_T-5":get_time_minus_five,
"TR_T-6":get_time_minus_six
}


