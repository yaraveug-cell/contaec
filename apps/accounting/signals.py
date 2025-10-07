from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import JournalEntryLine

@receiver(post_save, sender=JournalEntryLine)
def update_journal_entry_totals_on_save(sender, instance, **kwargs):
    """Recalcular totales cuando se guarda una línea"""
    if instance.journal_entry_id:
        instance.journal_entry.calculate_totals()
        instance.journal_entry.save(update_fields=['total_debit', 'total_credit'])

@receiver(post_delete, sender=JournalEntryLine)
def update_journal_entry_totals_on_delete(sender, instance, **kwargs):
    """Recalcular totales cuando se elimina una línea"""
    if instance.journal_entry_id:
        instance.journal_entry.calculate_totals()
        instance.journal_entry.save(update_fields=['total_debit', 'total_credit'])