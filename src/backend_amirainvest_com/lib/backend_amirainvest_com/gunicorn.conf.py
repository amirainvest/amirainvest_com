wsgi_app = "backend_amirainvest_com.api.app:app"
timeout = 300
graceful_timeout = 330
workers = 4
worker_class = "backend_amirainvest_com.main.ProductionUvicornWorker"
bind = "0.0.0.0:5000"
