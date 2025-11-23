# Importar todas las utilidades
from .singleton import stats_manager, StatisticsManager
from .pdf_generator import PDFGenerator, ParnetPDF
from .email_sender import email_sender, EmailSender

__all__ = [
    'stats_manager',
    'StatisticsManager',
    'PDFGenerator',
    'ParnetPDF',
    'email_sender',
    'EmailSender'
]