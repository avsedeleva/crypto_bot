async def download_telegram_posts(channel, limit):
    posts = []
    END_DATE = datetime.datetime.now(datetime.timezone.utc)
    START_DATE = END_DATE - datetime.timedelta(days=limit)
    async with client:
        async for message in client.iter_messages(channel, offset_date=END_DATE.date()+ datetime.timedelta(days=1)):
            if message.date < START_DATE:
                break
            if START_DATE <= message.date <= END_DATE and message.text != '':
                posts.append({
                    'date': message.date.isoformat(),
                    'text': message.text,
                    'link': f'https://t.me/{channel}/{message.id}'
                    #'views': message.views if hasattr(message, 'views') else None,
                    #'media': bool(message.media),
                })

    return posts