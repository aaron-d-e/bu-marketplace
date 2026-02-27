from django.core.management.base import BaseCommand

def Command(BaseCommand):
    help="Creates mock products for testing"

    parser.add_argument(
        "--count",
        default=10,
        help="Number of products to create (creates a batch of 10 my default)",
        type=int,
    )
