import re
from django.core.management.base import BaseCommand
from fleet.models import fleet

def normalize_fleet_number(fleet_number):
    """
    Normalize fleet_number for sorting:
    Strip whitespace, pad numeric parts with leading zeros to fixed length (e.g. 10 digits),
    convert to lowercase.
    """
    def pad_num(m):
        return m.group().zfill(10)
    return re.sub(r'\d+', pad_num, (fleet_number or '').strip().lower())

class Command(BaseCommand):
    help = 'Trim and normalize fleet_number, then fill fleet_number_sort for all existing fleet records'

    def handle(self, *args, **options):
        qs = fleet.objects.all()
        total = qs.count()
        self.stdout.write(f'Starting to update fleet_number_sort for {total} fleet records...')

        batch_size = 100
        updated = 0

        for start in range(0, total, batch_size):
            batch = qs[start:start+batch_size]
            for vehicle in batch:
                normalized = normalize_fleet_number(vehicle.fleet_number)
                if vehicle.fleet_number_sort != normalized:
                    vehicle.fleet_number_sort = normalized
                    vehicle.save(update_fields=['fleet_number_sort'])
                    updated += 1
            self.stdout.write(f'Processed {min(start+batch_size, total)} / {total}')

        self.stdout.write(self.style.SUCCESS(f'Updated fleet_number_sort for {updated} records.'))
