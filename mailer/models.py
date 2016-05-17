from datetime import datetime

from django.db import models
from django.core.files.uploadedfile import InMemoryUploadedFile

from mailer.enums import PRIORITY_MAPPING, PRIORITIES, RESULT_CODES

class MessageManager(models.Manager):
    def ready(self):
        return self.filter(ready_to_send=True)

    def high_priority(self):
        return self.ready().filter(priority=PRIORITY_MAPPING['high'])

    def medium_priority(self):
        return self.ready().filter(priority=PRIORITY_MAPPING['medium'])

    def low_priority(self):
        return self.ready().filter(priority=PRIORITY_MAPPING['low'])

    def non_deferred(self):
        return self.ready().exclude(priority=PRIORITY_MAPPING['deferred'])

    def deferred(self):
        return self.ready().filter(priority=PRIORITY_MAPPING['deferred'])

    def retry_deferred(self, new_priority=PRIORITY_MAPPING['medium']):
        count = 0
        for message in self.deferred():
            if message.retry(new_priority):
                count += 1
        return count

class Message(models.Model):
    objects = MessageManager()

    to_address = models.CharField(max_length=50)
    from_address = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    message_body = models.TextField()
    when_added = models.DateTimeField(default=datetime.now)
    priority = models.CharField(max_length=1, choices=PRIORITIES, default=PRIORITY_MAPPING['medium'])
    html_body = models.TextField(blank=True)
    ready_to_send = models.BooleanField(default=True, blank=True)

    def defer(self):
        self.priority = PRIORITY_MAPPING['deferred']
        self.save()

    def retry(self, new_priority=PRIORITY_MAPPING['medium']):
        if self.priority == PRIORITY_MAPPING['deferred']:
            self.priority = new_priority
            self.save()
            return True
        else:
            return False

class AttachmentManager(models.Manager):
    def from_content(self, message, filename, content, mimetype=None):
        from cStringIO import StringIO

        mimetype = mimetype or 'application/octet-stream'

        attachment = self.create(message=message, mimetype=mimetype, filename=filename)

        buffer = StringIO()
        buffer.write(content)
        buffer.seek(2, 0)
        buffersize = buffer.tell()
        buffer.seek(0, 0)

        uploaded_file = InMemoryUploadedFile(buffer, 'attachment_file', filename, mimetype, buffersize, charset=None)
        attachment.attachment_file.save(filename, uploaded_file)

        buffer.close()

        attachment.save()

        return attachment

class Attachment(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    attachment_file = models.FileField(u'attachment file', upload_to='attachments/', blank=True)
    filename = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=255, blank=True)

    objects = AttachmentManager()

    def __unicode__(self):
        return self.attachment_file.name

class DontSendEntryManager(models.Manager):
    def has_address(self, address):
        """
        is the given address on the don't send list?
        """
        if self.filter(to_address=address).exists():
            return True
        else:
            return False

class DontSendEntry(models.Model):
    objects = DontSendEntryManager()

    to_address = models.CharField(max_length=50)
    when_added = models.DateTimeField()

    class Meta:
        verbose_name = 'don\'t send entry'
        verbose_name_plural = 'don\'t send entries'

class MessageLogManager(models.Manager):
    def log(self, message, result_code, log_message = ''):
        """
        create a log entry for an attempt to send the given message and
        record the given result and (optionally) a log message
        """

        attachments_info = u'\n'.join(u'%s: %s' % (attachment.filename, unicode(attachment)) for attachment in message.attachment_set.all())
        message_body = u'%s\n\nAttachments:\n%s' % (message.message_body, attachments_info) if attachments_info else message.message_body

        message_log = self.create(
            to_address = message.to_address,
            from_address = message.from_address,
            subject = message.subject,
            message_body = message_body,
            when_added = message.when_added,
            priority = message.priority,
            html_body = message.html_body,
            result = result_code,
            log_message = log_message,
        )
        message_log.save()

class MessageLog(models.Model):
    objects = MessageLogManager()

    to_address = models.CharField(max_length=50, db_index=True)
    from_address = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    message_body = models.TextField()
    when_added = models.DateTimeField()
    priority = models.CharField(max_length=1, choices=PRIORITIES)
    html_body = models.TextField(blank=True)

    when_attempted = models.DateTimeField(default=datetime.now)
    result = models.CharField(max_length=1, choices=RESULT_CODES)
    log_message = models.TextField()
