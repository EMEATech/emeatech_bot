from db import JobListing
from pathlib import Path
import os

from db import JobBoardDbAirTable
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

TOKEN = os.getenv("EMEA_TELEGRAM_TOKEN")

news_file_path = Path('news.md')

job_file_path = Path('jobs.md')

board = JobBoardDbAirTable()


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! I respond by echoing messages. Give it a try!")

def echo(update, context):
    text = update.message.text
    if text.startswith("n "):
        print("updating news")
        with job_file_path.open('r') as f:
            existing = f.read()
        with job_file_path.open('w') as f:
            link = text[2:]
            bullet = f"* [{link}]({link})\n"
            replacetext = "<!-- replaceme -->"
            with_replace = f"{replacetext}\n{bullet}" 
            existing = existing.replace(replacetext,  with_replace)
            print(existing)
            f.write(existing)

    elif text.startswith("j "):
        try:

            with job_file_path.open('r') as f:
                existing = f.read()
            with job_file_path.open('w') as f:
                try:
                    new_job = JobListing.from_txt(text[2:])
                    existing = existing.replace("## Listings", f"## Listings\n\n * **{new_job.Description}.** {new_job.Description}. More information [here]({new_job.URL}).")
                    f.write(existing)
                    board.create(new_job)
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Posted your job. Thanks!")
                except Exception as e:
                    print("Exception in writing new jobs")
                    print(e)
                    f.write(existing)
                    context.bot.send_message(chat_id=update.effective_chat.id, text="I didn't get that. Please use the format `j Acme | rockstar ninja | $80k-$170k;Acme is a cool company that does cool things;https://example.com`", parse_mode="markdown")
        except Exception as e:
            context.bot.send_message(chat_id=update.effective_chat.id, text="I didn't get that. Please use the format `j Acme | rockstar ninja | $80k-$170k;Acme is a cool company that does cool things;https://example.com`", parse_mode="markdown")


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler("start", start)

    dispatcher.add_handler(start_handler)

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text, echo))

    updater.start_polling()

if __name__ == '__main__':
    main()
