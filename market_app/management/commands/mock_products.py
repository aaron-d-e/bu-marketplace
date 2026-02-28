from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from market_app.models import Product
import random

PRODUCTS = [
    # Textbooks
    {"title": "Calculus: Early Transcendentals (Stewart)", "description": "8th edition, minor highlighting in chapters 1-3. Great condition.", "price": 45.00, "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&h=280&fit=crop&auto=format"},
    {"title": "Organic Chemistry (Clayden)", "description": "Used one semester, no writing. Includes access code (unused).", "price": 60.00, "image_url": "https://images.unsplash.com/photo-1481627834876-b7833e8f5882?w=400&h=280&fit=crop&auto=format"},
    {"title": "Principles of Economics (Mankiw, 9th ed.)", "description": "Some pencil notes, all erasable. Perfect for EC101.", "price": 40.00, "image_url": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=400&h=280&fit=crop&auto=format"},
    {"title": "Introduction to Algorithms – CLRS", "description": "3rd edition hardcover. A few sticky notes inside, otherwise pristine.", "price": 70.00, "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=280&fit=crop&auto=format"},
    {"title": "Campbell Biology (12th Edition)", "description": "Highlighted throughout but all key diagrams intact.", "price": 55.00, "image_url": "https://images.unsplash.com/photo-1530026186672-2cd00ffc50fe?w=400&h=280&fit=crop&auto=format"},
    # Electronics
    {"title": "MacBook Pro 14\" M1 Pro (2021)", "description": "256GB SSD, 16GB RAM. Charger included. Minor scuff on bottom. Battery health 91%.", "price": 950.00, "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&h=280&fit=crop&auto=format"},
    {"title": "AirPods Pro 2nd Gen", "description": "Purchased Dec 2023. Both tips and case included. Works perfectly.", "price": 175.00, "image_url": "https://images.unsplash.com/photo-1610438235354-a6ae5528385c?w=400&h=280&fit=crop&auto=format"},
    {"title": "Dell 27\" IPS Monitor (S2722D)", "description": "1440p, 75Hz. Selling because I got an ultrawide. HDMI cable included.", "price": 160.00, "image_url": "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=400&h=280&fit=crop&auto=format"},
    {"title": "iPad Air 5th Gen + Apple Pencil", "description": "Space Gray, 64GB WiFi. No scratches, always in case. Great for notes.", "price": 480.00, "image_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&h=280&fit=crop&auto=format"},
    {"title": "Logitech MX Master 3 Mouse", "description": "Barely used, bought for internship. USB-C charging cable included.", "price": 55.00, "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400&h=280&fit=crop&auto=format"},
    # Dorm / Furniture
    {"title": "Mini Fridge – 3.2 cu ft", "description": "Galanz brand. Works perfectly, quiet motor. Selling at end of lease.", "price": 85.00, "image_url": "https://images.unsplash.com/photo-1584568694244-14fbdf83bd30?w=400&h=280&fit=crop&auto=format"},
    {"title": "IKEA MALM Desk (white)", "description": "4 years old but solid. Minor scuff on top corner. Must pick up in Allston.", "price": 60.00, "image_url": "https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=400&h=280&fit=crop&auto=format"},
    {"title": "Dorm Rug – Grey 5×7", "description": "From West Elm. Clean, no stains. Rolled up and ready to go.", "price": 35.00, "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=280&fit=crop&auto=format"},
    {"title": "Adjustable Desk Lamp", "description": "USB-C charging port built in, 3 brightness levels. Great for studying.", "price": 20.00, "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400&h=280&fit=crop&auto=format"},
    # Clothing / Gear
    {"title": "Baylor Bears Hoodie – Men's L", "description": "Champion brand, worn twice. Dark green. Excellent condition.", "price": 30.00, "image_url": "https://images.unsplash.com/photo-1620799140188-3b2a02fd9a77?w=400&h=280&fit=crop&auto=format"},
    {"title": "North Face ThermoBall Jacket – Men's M", "description": "Black, very warm. No rips or stains. Selling because I moved to California.", "price": 110.00, "image_url": "https://images.unsplash.com/photo-1544441893-675973e31535?w=400&h=280&fit=crop&auto=format"},
    # Sports / Recreation
    {"title": "Trek FX2 Road Bike (2022)", "description": "Barely ridden, one tune-up done. Helmet and lock included. Size M frame.", "price": 480.00, "image_url": "https://images.unsplash.com/photo-1571068316344-75bc8b5a3a49?w=400&h=280&fit=crop&auto=format"},
    {"title": "Wilson Clash 100 Tennis Racket", "description": "Used one season. Includes cover bag and 2 extra grips.", "price": 75.00, "image_url": "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=400&h=280&fit=crop&auto=format"},
    # Gaming / Entertainment
    {"title": "PlayStation 5 Disc Edition + 2 Controllers", "description": "Comes with Spider-Man 2 and God of War Ragnarok. All cables included.", "price": 430.00, "image_url": "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=400&h=280&fit=crop&auto=format"},
    {"title": "Nintendo Switch OLED (White)", "description": "Dock, two Joy-Cons, and carrying case included. No dead pixels.", "price": 260.00, "image_url": "https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=400&h=280&fit=crop&auto=format"},
    # Kitchen / Misc
    {"title": "Keurig K-Mini Coffee Maker", "description": "Used all of freshman year. Descaled and cleaned. Perfect for dorms.", "price": 30.00, "image_url": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&h=280&fit=crop&auto=format"},
    {"title": "T Commuter Rail Monthly Pass (April)", "description": "Transferable if purchased before April 1. Zone 1A, covers BU area.", "price": 90.00, "image_url": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=400&h=280&fit=crop&auto=format"},
]


class Command(BaseCommand):
    help = "Creates mock products for demo purposes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            default=len(PRODUCTS),
            help="Number of products to create (max %d)" % len(PRODUCTS),
            type=int,
        )
        parser.add_argument(
            "--user",
            default=None,
            help="Username to assign products to (defaults to first superuser or first user)",
        )

    def handle(self, *args, **options):
        count = min(options["count"], len(PRODUCTS))

        if options["user"]:
            try:
                user = User.objects.get(username=options["user"])
            except User.DoesNotExist:
                self.stderr.write(self.style.ERROR(f'User "{options["user"]}" not found.'))
                return
        else:
            user = User.objects.filter(is_superuser=True).first() or User.objects.first()
            if not user:
                self.stderr.write(self.style.ERROR("No users found. Create a user first with: python manage.py create_user"))
                return

        products_to_create = PRODUCTS[:count]
        created = 0
        for data in products_to_create:
            sold = random.random() < 0.2  # ~20% marked as sold for realism
            Product.objects.create(
                user=user,
                title=data["title"],
                description=data["description"],
                price=data["price"],
                image_url=data["image_url"],
                sold=sold,
            )
            created += 1
            self.stdout.write(f"  Created: {data['title']}")

        self.stdout.write(self.style.SUCCESS(f"\nDone — {created} products created for user '{user.username}'."))
