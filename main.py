import requests
import json
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def scan(update, context):
    try:
        address = context.args[0]
        size = int(context.args[1])
    except (IndexError, ValueError):
        await update.message.reply_text("Correct usage: /scan <address> <number_of_transactions>")
        return

    max_page_size = 200  # Set the maximum allowed by your API
    transactions = []
    # Calculate the number of pages required
    num_pages = -(-size // max_page_size)  # Rounded-up integer division

    for page in range(1, num_pages + 1):
        # Limit the number of transactions per page to the maximum allowed size
        page_size = min(size - len(transactions), max_page_size)
        url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc&offset=0&page={page}&size={page_size}"
        response = requests.get(url)
        json_response = json.loads(response.text)

        if json_response['status'] == '1':
            transactions.extend(json_response['result'])
        else:
            message = "Error in searching for transactions: {}".format(json_response.get('message', 'Unknown error'))
            await update.message.reply_text(message)
            return  # Exit the function in case of an error

        # If you've obtained enough transactions, exit the loop
        if len(transactions) >= size:
            break

    # Sort transactions by timestamp in descending order
    sorted_transactions = sorted(transactions, key=lambda x: int(x['timeStamp']), reverse=True)

    # Display the requested transactions
    for tx in sorted_transactions[:size]:
        await update.message.reply_text(
            "Transaction Hash: {}\n"
            "Date and Time of Transaction: {}\n"
            "Transaction Value (in ETH): {:.18f}\n"
            "Recipient Address: {}\n"
            "Transaction Type: {}\n"
            "Number of Confirmations: {}".format(
                tx['hash'],
                datetime.datetime.fromtimestamp(int(tx['timeStamp'])).strftime("%d/%m/%Y %H:%M:%S"),
                int(tx['value']) / 10 ** 18,
                tx['to'],
                "Outgoing" if tx['to'].lower() == address.lower() else "Incoming",
                tx['confirmations']
            )
        )

app = ApplicationBuilder().token("Your_Bot_Token_Here").build() 
app.add_handler(CommandHandler("scan", scan))

app.run_polling()
