import requests
import json

class SlackService:
    def __init__(self):
        pass

    def post_message(self, channel, token, text):
        #토큰받았지만 임의로 아래의 토큰 사용할 거임 
        print("post_message")
        SLACK_BOT_TOKEN = "xoxb-4184524433281-5008927392563-qZQ6oS6GFDi2A8DyWSKqCeNg"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + SLACK_BOT_TOKEN
        }
        payload = {
            'channel': channel,
            'text': text
        }
        r = requests.post('https://slack.com/api/chat.postMessage',
                        headers=headers,
                        data=json.dumps(payload)
                        )
        print('r:',r)
        return r
