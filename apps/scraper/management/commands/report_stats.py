from django.core.management.base import BaseCommand
from apps.scraper.services.metrics import AlertMetricsManager, get_failed_analysis

class Command(BaseCommand):
    help = 'Generates a Professional "Mentor-Ready" Alert Performance Report.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Generating Audit Report...")
        
        metrics = AlertMetricsManager.generate_30_day_report()
        failures = get_failed_analysis()
        
        # Professional ASCII Table
        self.stdout.write(self.style.SUCCESS("\n" + "="*50))
        self.stdout.write(self.style.SUCCESS(f"  SMTP HEALTH REPORT: {metrics['period']}"))
        self.stdout.write(self.style.SUCCESS("="*50))
        self.stdout.write(f" Total Alerts Triggered  : {metrics['total_alerts']}")
        self.stdout.write(f" Successful Deliveries   : {metrics['successful_deliveries']}")
        self.stdout.write(f" Failed Deliveries       : {metrics['failed_deliveries']}")
        self.stdout.write(f" Suppressed (Spam Check) : {metrics['suppressed_alerts']}")
        self.stdout.write("-" * 50)
        self.stdout.write(self.style.HTTP_INFO(f" SUCCESS RATE            : {metrics['success_rate']}%"))
        self.stdout.write("="*50 + "\n")
        
        if failures:
            self.stdout.write(self.style.ERROR("TOP FAILURE CAUSES (Root Cause Analysis):"))
            for error, count in failures:
                self.stdout.write(f" - [{count}x] {error}...")
            self.stdout.write("\n")
        else:
             self.stdout.write(self.style.SUCCESS("No Failures Detected. System Healthy.\n"))
