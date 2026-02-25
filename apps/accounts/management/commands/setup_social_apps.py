from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Setup default Site and Social Apps (Google/GitHub) for development'

    def handle(self, *args, **options):
        self.stdout.write("Setting up Social Apps...")

        # 1. Setup Site
        site_id = getattr(settings, 'SITE_ID', 1)
        domain = '127.0.0.1:8000'
        name = 'Antigravity Dev'

        # Ensure Site ID exists or update it
        if Site.objects.filter(id=site_id).exists():
            site = Site.objects.get(id=site_id)
            site.domain = domain
            site.name = name
            site.save()
            self.stdout.write(self.style.SUCCESS(f'Updated Site ID {site_id} to {domain}'))
        else:
            site = Site.objects.create(id=site_id, domain=domain, name=name)
            self.stdout.write(self.style.SUCCESS(f'Created Site ID {site_id} to {domain}'))

        # 2. Setup Social Apps
        # Use env vars if available, else dummy values
        providers = [
            {
                'provider': 'google', 
                'name': 'Google', 
                'client_id': os.environ.get('GOOGLE_CLIENT_ID', 'dummy-google-client-id'), 
                'secret': os.environ.get('GOOGLE_CLIENT_SECRET', 'dummy-google-secret')
            },
            {
                'provider': 'github', 
                'name': 'GitHub', 
                'client_id': os.environ.get('GITHUB_CLIENT_ID', 'dummy-github-client-id'), 
                'secret': os.environ.get('GITHUB_CLIENT_SECRET', 'dummy-github-secret')
            },
        ]

        for p in providers:
            app, created = SocialApp.objects.update_or_create(
                provider=p['provider'],
                defaults={
                    'name': p['name'],
                    'client_id': p['client_id'],
                    'secret': p['secret'],
                }
            )
            # Link the app to the current site
            app.sites.add(site)
            
            status = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f'{status} SocialApp: {p["name"]}'))

        self.stdout.write(self.style.SUCCESS('Choose Site ID 1 and Social Providers are ready!'))
