import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

def send_email(to_emails, subject, body, attachment_data=None, attachment_filename=None):
    """Отправка письма через SMTP из настроек"""
    from app.models.settings import get_setting
    
    smtp_host = get_setting('smtp_host', 'smtp.yandex.ru')
    smtp_port = int(get_setting('smtp_port', '465'))
    smtp_user = get_setting('smtp_user', '')
    smtp_password = get_setting('smtp_password', '')
    smtp_from_name = get_setting('smtp_from_name', 'Luna888')
    
    if not smtp_user or not smtp_password:
        return {'error': 'SMTP не настроен'}
    
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{smtp_from_name} <{smtp_user}>"
        msg['To'] = to_emails[0] if to_emails else ''
        
        # Копии
        if len(to_emails) > 1:
            msg['Cc'] = ', '.join(to_emails[1:])
        
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Вложение
        if attachment_data and attachment_filename:
            attachment = MIMEApplication(attachment_data)
            attachment.add_header('Content-Disposition', 'attachment', filename=attachment_filename)
            msg.attach(attachment)
        
        # Отправка
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
            server.starttls()
        
        server.login(smtp_user, smtp_password)
        
        # Отправляем всем (to + cc)
        server.send_message(msg)
        server.quit()
        
        return {'success': True}
    except Exception as e:
        return {'error': str(e)}


def send_email_html(to_emails, subject, html_body, order=None, items_data=None):
    """Отправка HTML письма с Excel вложением"""
    from app.models.settings import get_setting
    
    smtp_host = get_setting('smtp_host', 'smtp.yandex.ru')
    smtp_port = int(get_setting('smtp_port', '465'))
    smtp_user = get_setting('smtp_user', '')
    smtp_password = get_setting('smtp_password', '')
    smtp_from_name = get_setting('smtp_from_name', 'Luna888')
    
    if not smtp_user or not smtp_password:
        return {'error': 'SMTP не настроен'}
    
    try:
        msg = MIMEMultipart('mixed')
        msg['From'] = f"{smtp_from_name} <{smtp_user}>"
        msg['To'] = to_emails[0] if to_emails else ''
        
        if len(to_emails) > 1:
            msg['Cc'] = ', '.join(to_emails[1:])
        
        msg['Subject'] = subject
        
        # HTML
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        # Excel вложение
        if order and items_data:
            try:
                import pandas as pd
                from io import BytesIO
                
                # Создаём DataFrame
                df_data = []
                for item in items_data:
                    df_data.append({
                        'Артикул': item.get('article', ''),
                        'Размер': item.get('size', ''),
                        'Штрихкод': item.get('barcode', ''),
                        'Количество': item.get('quantity', 0)
                    })
                
                if df_data:
                    df = pd.DataFrame(df_data)
                    
                    # Сохраняем в BytesIO
                    excel_buffer = BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='Заказ', index=False)
                    
                    excel_buffer.seek(0)
                    excel_data = excel_buffer.read()
                    
                    # Прикрепляем
                    attachment = MIMEApplication(excel_data)
                    attachment.add_header(
                        'Content-Disposition', 
                        'attachment', 
                        filename=f'Заказ_{order.order_number.replace("/", "_")}.xlsx'
                    )
                    msg.attach(attachment)
            except Exception as excel_err:
                print(f"Ошибка Excel: {excel_err}")
        
        # Отправка
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
            server.starttls()
        
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        
        return {'success': True}
    except Exception as e:
        return {'error': str(e)}
