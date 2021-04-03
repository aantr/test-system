import time
from datetime import datetime
from random import randint

import apscheduler
import requests
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

TOKEN = '1722139509:AAEn_Z_Xf9zCymGMJgp4XBUPL98B6FYnqV0'


def start(update, context):
    reply_keyboard = [['/dice', '/timer']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text(
        'Привет.',
        reply_markup=markup
    )


def dice(update, context):
    reply_keyboard = [['/one', '/two', '/twenty', '/back']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text(
        'Выбор за тобой.',
        reply_markup=markup
    )


def one(update, context):
    update.message.reply_text(
        randint(1, 6)
    )


def two(update, context):
    update.message.reply_text(
        f'{randint(1, 6)}, {randint(1, 6)}'
    )


def twenty(update, context):
    update.message.reply_text(
        randint(1, 20)
    )


def timer(update, context):
    reply_keyboard = [['/second30', '/minute', '/minute5', '/back']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text(
        'Выбор за тобой.',
        reply_markup=markup
    )


def second30(update, context):
    chat_id = update.message.chat_id

    due = 30

    if 'job' in context.chat_data:
        old_job = context.chat_data['job']
        try:
            old_job.schedule_removal()
        except apscheduler.jobstores.base.JobLookupError:
            ...
        del context.chat_data['job']
    new_job = context.job_queue.run_once(task, due, context=chat_id)
    new_job.time = '30 sec'
    context.chat_data['job'] = new_job

    reply_keyboard = [['/close']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text(
        'засек 30 sec',
        reply_markup=markup
    )


def minute(update, context):
    chat_id = update.message.chat_id

    due = 60

    if 'job' in context.chat_data:
        old_job = context.chat_data['job']
        try:
            old_job.schedule_removal()
        except apscheduler.jobstores.base.JobLookupError:
            ...
        del context.chat_data['job']
    new_job = context.job_queue.run_once(task, due, context=chat_id)
    new_job.time = 'minute'
    context.chat_data['job'] = new_job

    reply_keyboard = [['/close']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text(
        'засек 1 minute',
        reply_markup=markup
    )


def minute5(update, context):
    chat_id = update.message.chat_id

    due = 300

    if 'job' in context.chat_data:
        old_job = context.chat_data['job']
        try:
            old_job.schedule_removal()
        except apscheduler.jobstores.base.JobLookupError:
            ...
        del context.chat_data['job']
    new_job = context.job_queue.run_once(task, due, context=chat_id)
    new_job.time = '5 min'
    context.chat_data['job'] = new_job

    reply_keyboard = [['/close']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text(
        'засек 5 min',
        reply_markup=markup
    )


def close(update, context):
    if 'job' in context.chat_data:
        job = context.chat_data['job']
        try:
            job.schedule_removal()
        except apscheduler.jobstores.base.JobLookupError:
            ...
        del context.chat_data['job']
    reply_keyboard = [['/second30', '/minute', '/minute5', '/back']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text(
        'Выбор за тобой.',
        reply_markup=markup
    )


def task(context):
    job = context.job
    context.bot.send_message(job.context, text=f'{job.time} истекло')
    reply_keyboard = [['/second30', '/minute', '/minute5', '/back']]


def time_reply(update, context):
    update.message.reply_text(
        str(datetime.now().time())
    )


def date_reply(update, context):
    update.message.reply_text(
        str(datetime.now().date())
    )


def stop(update, context):
    ...


def first_response(update, context):
    context.user_data['locality'] = update.message.text
    update.message.reply_text(
        "Какая погода в городе {0}?".format(context.user_data['locality']))
    return 2


def second_response(update, context):
    weather = update.message.text
    update.message.reply_text("Спасибо за участие в опросе! Привет, {0}!".
                              format(context.user_data['locality']))
    return ConversationHandler.END


def help(update, context):
    update.message.reply_text(
        "Я пока не умею помогать... Я только ваше эхо.")


def address(update, context):
    update.message.reply_text(
        "Адрес: г. Москва, ул. Льва Толстого, 16")


def phone(update, context):
    update.message.reply_text("Телефон: +7(495)776-3030")


def site(update, context):
    update.message.reply_text(
        "Сайт: http://www.yandex.ru/company")


def close_keyboard(update, context):
    update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


def unset_timer(update, context):
    if 'job' not in context.chat_data:
        update.message.reply_text('Нет активного таймера')
        return
    job = context.chat_data['job']
    try:
        job.schedule_removal()
    except apscheduler.jobstores.base.JobLookupError:
        ...
    del context.chat_data['job']
    update.message.reply_text('Хорошо, вернулся сейчас!')


def set_timer(update, context):
    """Добавляем задачу в очередь"""
    chat_id = update.message.chat_id
    try:
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text(
                'Извините, не умеем возвращаться в прошлое')
            return

        if 'job' in context.chat_data:
            old_job = context.chat_data['job']
            try:
                old_job.schedule_removal()
            except apscheduler.jobstores.base.JobLookupError:
                ...
            del context.chat_data['job']
        new_job = context.job_queue.run_once(task, due, context=chat_id)
        context.chat_data['job'] = new_job
        update.message.reply_text(f'Вернусь через {due} секунд')

    except (IndexError, ValueError):
        update.message.reply_text('Использование: /set <секунд>')


def echo(update, context):
    update.message.reply_text(f'Я получил сообщение {update.message.text}')


def geocoder(update, context):
    geocoder_uri = geocoder_request_template = "http://geocode-maps.yandex.ru/1.x/"
    response = requests.get(geocoder_uri, params={
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "format": "json",
        "geocode": update.message.text
    })

    toponym = response.json()["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    ll, spn = get_ll_spn(toponym)

    static_api_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l=map"
    context.bot.send_photo(
        update.message.chat_id,
        static_api_request,
        caption="Нашёл:"
    )


def main():
    REQUEST_KWARGS = {
        # 'proxy_url': 'socks5://ip:port',
    }
    updater = Updater(TOKEN, use_context=True, request_kwargs=REQUEST_KWARGS)
    dp = updater.dispatcher
    text_handler = MessageHandler(Filters.text, echo)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            1: [MessageHandler(Filters.text, first_response, pass_user_data=True)],
            2: [MessageHandler(Filters.text, second_response, pass_user_data=True)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    # dp.add_handler(conv_handler)

    dp.add_handler(CommandHandler('start', start))
    # dp.add_handler(CommandHandler('help', help))
    # dp.add_handler(CommandHandler('address', address))
    # dp.add_handler(CommandHandler('phone', phone))
    # dp.add_handler(CommandHandler('site', site))
    # dp.add_handler(CommandHandler('close', close_keyboard))
    # dp.add_handler(CommandHandler('set_timer', set_timer,
    #                               pass_args=True,
    #                               pass_job_queue=True,
    #                               pass_chat_data=True))
    # dp.add_handler(CommandHandler('unset', unset_timer,
    #                               pass_chat_data=True)
    #                )
    # dp.add_handler(CommandHandler('time', time_reply))
    # dp.add_handler(CommandHandler('date', date_reply))

    dp.add_handler(CommandHandler('dice', dice))
    dp.add_handler(CommandHandler('timer', timer))
    dp.add_handler(CommandHandler('back', start))

    dp.add_handler(CommandHandler('one', one))
    dp.add_handler(CommandHandler('two', two))
    dp.add_handler(CommandHandler('twenty', twenty))

    dp.add_handler(CommandHandler('second30', second30))
    dp.add_handler(CommandHandler('minute', minute))
    dp.add_handler(CommandHandler('minute5', minute5))
    dp.add_handler(CommandHandler('close', close))

    # dp.add_handler(text_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
