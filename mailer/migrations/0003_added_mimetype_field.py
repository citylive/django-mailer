# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Attachment.mimetype'
        db.add_column('mailer_attachment', 'mimetype', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Attachment.mimetype'
        db.delete_column('mailer_attachment', 'mimetype')


    models = {
        'mailer.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'attachment_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mailer.Message']"}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'mailer.dontsendentry': {
            'Meta': {'object_name': 'DontSendEntry'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_address': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'when_added': ('django.db.models.fields.DateTimeField', [], {})
        },
        'mailer.message': {
            'Meta': {'object_name': 'Message'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_data': ('django.db.models.fields.TextField', [], {}),
            'priority': ('django.db.models.fields.CharField', [], {'default': "'2'", 'max_length': '1'}),
            'when_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'mailer.messagelog': {
            'Meta': {'object_name': 'MessageLog'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log_message': ('django.db.models.fields.TextField', [], {}),
            'message_data': ('django.db.models.fields.TextField', [], {}),
            'priority': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'when_added': ('django.db.models.fields.DateTimeField', [], {}),
            'when_attempted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        }
    }

    complete_apps = ['mailer']
