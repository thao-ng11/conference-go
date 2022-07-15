import json
import pika
import django
import os
import sys
from django.core.mail import send_mail
import time
from pika.exceptions import AMQPConnectionError


sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "presentation_mailer.settings")
django.setup()

        # ALL OF YOUR CODE THAT HANDLES READING FROM THE
        # QUEUES AND SENDING EMAILS
def process_approval(ch, method, properties, body):

    presentation = json.loads(body)
    name = presentation['presenter_name']
    title = presentation['title']
    send_mail(
        'Presentation Approved',
        f"{name}, we're happy to tell you that your presentation {title} has been accepted",
        'admin@conference.go',
        [presentation['presenter_email']],
        fail_silently=False,
    )

def process_rejection(ch, method, properties, body):
    
    presentation = json.loads(body)
    name = presentation['presenter_name']
    title = presentation['title']
    send_mail(
        'Presentation Rejected',
        f"{name}, we're sorry to tell you that your presentation {title} has been rejected",
        'admin@conference.go',
        [presentation['presenter_email']],
        fail_silently=False,
            )

while True:
    try:

        parameters = pika.ConnectionParameters(host='rabbitmq')
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()



        channel.queue_declare(queue='presentation_approvals')
        channel.basic_consume(
            queue='presentation_approvals',
            on_message_callback=process_approval,
            auto_ack=True,
        )

        channel.queue_declare(queue='presentation_rejections')
        channel.basic_consume(
            queue='presentation_rejections',
            on_message_callback=process_rejection,
            auto_ack=True,
        )
        channel.start_consuming()

    except AMQPConnectionError:
            print("Could not connect to RabbitMQ")
            time.sleep(2.0)