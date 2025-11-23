import threading
from datetime import datetime, timedelta


class StatisticsManager:
    """
    Singleton para gestionar estadísticas en tiempo real del sitio
    Implementa el patrón Singleton para asegurar una única instancia
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(StatisticsManager, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._init_stats()

    def _init_stats(self):
        """Inicializar las estadísticas"""
        self.visit_count = 0
        self.active_sessions = {}
        self.daily_visits = {}
        self.page_views = {}

        # Inicializar contadores para el día actual
        today = datetime.now().date()
        self.daily_visits[today] = 0

    def register_visit(self, session_id, ip_address, user_agent, page=None):
        """Registrar una visita al sitio"""
        with self._lock:
            self.visit_count += 1

            # Registrar visita diaria
            today = datetime.now().date()
            if today not in self.daily_visits:
                self.daily_visits[today] = 0
            self.daily_visits[today] += 1

            # Registrar sesión activa
            self.active_sessions[session_id] = {
                'ip_address': ip_address,
                'user_agent': user_agent,
                'last_activity': datetime.now(),
                'page': page
            }

            # Registrar vista de página
            if page:
                if page not in self.page_views:
                    self.page_views[page] = 0
                self.page_views[page] += 1

    def remove_session(self, session_id):
        """Remover una sesión activa"""
        with self._lock:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]

    def cleanup_old_sessions(self, hours=1):
        """Limpiar sesiones antiguas (más de X horas)"""
        with self._lock:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            expired_sessions = [
                session_id for session_id, session_data in self.active_sessions.items()
                if session_data['last_activity'] < cutoff_time
            ]

            for session_id in expired_sessions:
                del self.active_sessions[session_id]

            return len(expired_sessions)

    def get_visit_count(self):
        """Obtener contador total de visitas"""
        return self.visit_count

    def get_active_users_count(self):
        """Obtener número de usuarios activos"""
        self.cleanup_old_sessions()
        return len(self.active_sessions)

    def get_daily_visits(self, days=7):
        """Obtener visitas de los últimos N días"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)

        daily_data = []
        current_date = start_date

        while current_date <= end_date:
            count = self.daily_visits.get(current_date, 0)
            daily_data.append({
                'date': current_date.isoformat(),
                'visits': count
            })
            current_date += timedelta(days=1)

        return daily_data

    def get_popular_pages(self, limit=10):
        """Obtener páginas más populares"""
        sorted_pages = sorted(
            self.page_views.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        return [
            {'page': page, 'views': views}
            for page, views in sorted_pages
        ]

    def get_stats(self):
        """Obtener todas las estadísticas"""
        self.cleanup_old_sessions()

        return {
            'total_visits': self.visit_count,
            'active_users': len(self.active_sessions),
            'daily_visits_7d': self.get_daily_visits(7),
            'popular_pages': self.get_popular_pages(5),
            'active_sessions': len(self.active_sessions)
        }


# Instancia global del Singleton
stats_manager = StatisticsManager()