import csv, sys, os, urllib.parse, re
# Sender details come from env so they are not committed: SENDER_NAME, SENDER_WHATSAPP
NAME=os.environ.get('SENDER_NAME','[NAME]'); WA=os.environ.get('SENDER_WHATSAPP','[NUMBER]')
NAME_RU=os.environ.get('SENDER_NAME_RU',NAME)
r=list(csv.DictReader(open(sys.argv[1])))
KIND_EN={'hotel':'hotels','guest_house':'guest houses','hostel':'hostels','apartment':'apartments','motel':'hotels',
 'restaurant':'restaurants','cafe':'cafes','bar':'bars','pub':'bars','fast_food':'cafes','bakery':'bakeries',
 'dentist':'dental clinics','clinic':'clinics','beauty':'beauty salons','hairdresser':'salons','fitness_centre':'gyms'}
KIND_RU={'hotels':'отелей','guest houses':'гестхаусов','hostels':'хостелов','apartments':'апартаментов','restaurants':'ресторанов',
 'cafes':'кафе','bars':'баров','bakeries':'пекарен','dental clinics':'стоматологий','clinics':'клиник','beauty salons':'салонов красоты','salons':'салонов','gyms':'фитнес-клубов'}
LODGING={'hotel','guest_house','hostel','apartment','motel'}; FOOD={'restaurant','cafe','bar','pub','fast_food','bakery'}
def feat(t,ru=False):
    if t in LODGING: return 'онлайн-бронированием напрямую, без комиссии Booking' if ru else 'direct online booking (no Booking.com commission)'
    if t in FOOD: return 'меню с фото, QR-меню для столиков и бронированием столов' if ru else 'a photo menu, QR menu for tables and table reservations'
    return 'онлайн-записью' if ru else 'online appointment booking'
def hook(x,ru):
    p=x['problem']; w=x['website'].split(';')[0]
    if p.startswith('Сайт не открывается'):
        who_en='Patients' if x['type'] in ('dentist','clinic') else 'Guests'
        who_ru='Пациенты' if x['type'] in ('dentist','clinic') else 'Гости'
        return (f"Сайт, который указан у вас в интернете, {w}, не открывается, я проверил сегодня. {who_ru}, которые находят вас в Google, попадают в тупик и уходят к конкурентам."
                if ru else f"The website listed for you online, {w}, doesn't open. I checked it today. {who_en} who find you on Google hit a dead end and go somewhere else.")
    if 'Booking' in p:
        return ("Вижу, что у вас нет своего сайта — только Booking/Airbnb. С каждой брони вы отдаёте им около 15%. Свой сайт с прямым бронированием возвращает часть гостей без комиссии."
                if ru else "I noticed you don't have your own website, only Booking/Airbnb listings. You pay them roughly 15% on every booking; a site with direct booking brings part of those guests back commission-free.")
    if p.startswith('Нет сайта'):
        return ("Искал вас в интернете и не нашёл сайта"+(" — только соцсети" if 'соцсети' in p else "")+". Сейчас гости и туристы сначала гуглят, а без сайта вас сложнее найти и вам сложнее доверять."
                if ru else "I was looking you up online and couldn't find a website"+(" — only social media" if 'соцсети' in p else "")+". Most guests and tourists google first, and without a site you are harder to find and to trust.")
    if 'телефон' in p:
        return (f"Открыл ваш сайт {w} с телефона — он не адаптирован под мобильные, а большинство гостей заходят именно с телефона."
                if ru else f"I opened your website {w} on my phone and it isn't mobile-friendly — and most guests browse on their phones.")
    return (f"Ваш сайт {w} открывается без HTTPS — браузеры показывают посетителям «Небезопасно», это отпугивает гостей."
            if ru else f"Your website {w} has no HTTPS, so browsers show visitors a \"Not secure\" warning, which scares guests away.")
out=[]
for x in r:
    ru=bool(re.search(r'@(mail|yandex|bk|inbox|list|rambler)\.|\.ru$',x['email'])) or bool(re.search('[а-яА-Я]',x['name']))
    k=KIND_EN.get(x['type'],'local businesses'); n=x['name']
    if ru:
        subj=f"{n} — бесплатный демо-сайт для вас"
        body=(f"Здравствуйте, команда {n}!\n\n{hook(x,True)}\n\nЯ делаю быстрые сайты для {KIND_RU.get(k,'бизнеса')} в Грузии: на грузинском, английском и русском, удобные с телефона, с {feat(x['type'],True)}, плюс настройка карточки в Google Картах. Цены от 200 лари, в зависимости от задачи.\n\n"
              f"Могу бесплатно сделать демо-версию сайта именно для {n} — посмотрите, и если не понравится, ничего не должны. Просто ответьте «да».\n\nС уважением,\n{NAME_RU}\nWhatsApp: {WA}\n\nP.S. Если неактуально — ответьте, и я больше не напишу.")
    else:
        subj=f"Free website demo for {n}"
        body=(f"Hello {n} team,\n\n{hook(x,False)}\n\nI build fast websites for {k} in Georgia: in Georgian, English and Russian, mobile-friendly, with {feat(x['type'])}, plus Google Maps profile setup. Prices start from 200 GEL, depending on what you need.\n\n"
              f"I'd be happy to make a free demo of a new site for {n}, no strings attached. If you like it, we talk; if not, you owe nothing. Just reply \"yes\".\n\nBest regards,\n{NAME}\nWhatsApp: {WA}\n\nP.S. If this isn't relevant, just reply and I won't write again.")
    wa=''
    if x['whatsapp']:
        msg=(f"Здравствуйте! Пишу по поводу {n}. " if ru else f"Hello! I'm writing about {n}. ")+hook(x,ru)+(" Могу бесплатно сделать демо нового сайта для вас — интересно?" if ru else " I can make you a free demo of a new website — interested?")
        wa='https://wa.me/'+x['whatsapp'].lstrip('+')+'?text='+urllib.parse.quote(msg)
    out.append({'Статус':'новый','Канал':'email' if x['email'] else 'WhatsApp (вручную)','Название':n,'Название (местн.)':x['name_local'],
      'Тип':x['type'],'Город':x['city'],'Проблема':x['problem'],'Email':x['email'],'WhatsApp':x['whatsapp'],'Телефон':x['phone'],
      'Сайт':x['website'],'Instagram':x['instagram'],'Facebook':x['facebook'],'Карта':x['map'],'Язык':'RU' if ru else 'EN',
      'Тема письма':subj if x['email'] else '','Черновик письма':body if x['email'] else '','Ссылка WhatsApp':wa,'Приоритет':x['score'],'Заметки':''})
with open(sys.argv[2],'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print(len(out)); print(out[0]['Тема письма']); print(out[0]['Черновик письма'])
