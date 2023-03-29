# import slack_sdk
# from slack_sdk.errors import SlackApiError


class TradingService:
    def __init__(self, slack_service, kiwoom):
        self.slack_service = slack_service
        self.kiwoom = kiwoom

    # def order_stock(self, stock_code, stock_amount, stock_price):
    #     result = self.securities_service.order_stock(stock_code, stock_amount, stock_price)

    #     try:
    #         # Slack 메시지 전송
    #         client = slack_sdk.WebClient(token='SLACK_API_TOKEN')
    #         response = client.chat_postMessage(
    #             channel="#trading-alerts",
    #             text=f"Order Result: {result}"
    #         )
    #         print(response)
    #     except SlackApiError as e:
    #         print(f"Error: {e}")

    #     return result

    # def request_stock_order(self):
    #     return self.securities_service.request_stock_order()
