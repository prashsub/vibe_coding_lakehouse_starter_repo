"""
Data generation utility for Bronze layer testing.

This script provides standard functions for generating synthetic data with Faker,
including dimension and fact data generation with configurable corruption.
"""

from faker import Faker
import random
import sys
from typing import Dict, List, Optional

# Try to import Databricks widgets, fall back if not available
try:
    import dbutils
    DATABRICKS_AVAILABLE = True
except ImportError:
    DATABRICKS_AVAILABLE = False


def get_parameters():
    """
    Get parameters from notebook widgets or command line.
    
    Returns:
        Tuple of (catalog, schema, num_records, corruption_rate)
    """
    try:
        if DATABRICKS_AVAILABLE:
            # Try Databricks widgets first (notebook mode)
            catalog = dbutils.widgets.get("catalog")
            schema = dbutils.widgets.get("schema")
            num_records = int(dbutils.widgets.get("num_records"))
            corruption_rate = float(dbutils.widgets.get("corruption_rate"))
        else:
            raise AttributeError("dbutils not available")
    except:
        # Fall back to command line arguments or defaults
        catalog = "default_catalog"
        schema = "default_schema"
        num_records = 1000
        corruption_rate = 0.05  # 5% corruption by default
        
        for arg in sys.argv[1:]:
            if arg.startswith("--catalog="):
                catalog = arg.split("=")[1]
            elif arg.startswith("--schema="):
                schema = arg.split("=")[1]
            elif arg.startswith("--num_records="):
                num_records = int(arg.split("=")[1])
            elif arg.startswith("--corruption_rate="):
                corruption_rate = float(arg.split("=")[1])
    
    return catalog, schema, num_records, corruption_rate


def generate_dimension_data(
    entity_type: str,
    num_records: int,
    corruption_rate: float = 0.0,
    locale: str = 'en_US'
) -> List[Dict]:
    """
    Generate dimension data with realistic patterns.
    
    Args:
        entity_type: Type of dimension (e.g., 'customer', 'product', 'store')
        num_records: Number of records to generate
        corruption_rate: Percentage of records to intentionally corrupt (0.0 to 1.0)
        locale: Faker locale (default: 'en_US')
        
    Returns:
        List of dimension dictionaries
    """
    fake = Faker(locale)
    records = []
    
    print(f"\nGenerating {num_records} {entity_type} records (corruption rate: {corruption_rate*100}%)")
    
    for i in range(num_records):
        # Generate valid data first
        record = _generate_valid_dimension_record(fake, entity_type, i + 1)
        
        # Apply corruption if selected
        if random.random() < corruption_rate:
            record = _apply_dimension_corruption(record, entity_type)
        
        records.append(record)
    
    return records


def generate_fact_data(
    dimension_keys: Dict[str, List],
    num_records: int,
    corruption_rate: float = 0.0,
    locale: str = 'en_US'
) -> List[Dict]:
    """
    Generate fact data with referential integrity.
    
    Args:
        dimension_keys: Dictionary containing dimension keys for referential integrity
                        (e.g., {'customer_id': [1,2,3], 'product_id': [1,2,3]})
        num_records: Number of records to generate
        corruption_rate: Percentage of records to intentionally corrupt (0.0 to 1.0)
        locale: Faker locale (default: 'en_US')
        
    Returns:
        List of fact dictionaries
    """
    fake = Faker(locale)
    records = []
    
    print(f"\nGenerating {num_records} fact records (corruption rate: {corruption_rate*100}%)")
    
    for i in range(num_records):
        # Generate valid data first
        record = _generate_valid_fact_record(fake, dimension_keys, i + 1)
        
        # Apply corruption if selected
        if random.random() < corruption_rate:
            record = _apply_fact_corruption(record, dimension_keys)
        
        records.append(record)
    
    return records


def _generate_valid_dimension_record(fake: Faker, entity_type: str, entity_id: int) -> Dict:
    """Generate a valid dimension record."""
    if entity_type == 'customer':
        return {
            'customer_id': entity_id,
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'phone': fake.phone_number(),
            'address': fake.address(),
            'city': fake.city(),
            'state': fake.state_abbr(),
            'zipcode': fake.zipcode(),
            'created_date': fake.date_between(start_date='-2y', end_date='today')
        }
    elif entity_type == 'product':
        return {
            'product_id': entity_id,
            'product_name': fake.catch_phrase(),
            'category': random.choice(['electronics', 'clothing', 'home', 'sports', 'books']),
            'price': round(random.uniform(10.0, 1000.0), 2),
            'sku': fake.ean13(),
            'created_date': fake.date_between(start_date='-1y', end_date='today')
        }
    else:
        raise ValueError(f"Unknown entity_type: {entity_type}")


def _generate_valid_fact_record(fake: Faker, dimension_keys: Dict[str, List], record_id: int) -> Dict:
    """Generate a valid fact record with referential integrity."""
    customer_ids = dimension_keys.get('customer_id', [])
    product_ids = dimension_keys.get('product_id', [])
    
    quantity = random.randint(1, 10)
    unit_price = round(random.uniform(10.0, 500.0), 2)
    
    return {
        'order_id': record_id,
        'customer_id': random.choice(customer_ids) if customer_ids else None,
        'product_id': random.choice(product_ids) if product_ids else None,
        'order_date': fake.date_between(start_date='-1y', end_date='today'),
        'quantity': quantity,
        'unit_price': unit_price,
        'total_amount': quantity * unit_price,
        'channel': random.choice(['web', 'mobile', 'store', 'phone']),
        'payment_method': random.choice(['credit_card', 'debit_card', 'cash', 'paypal']),
        'order_status': random.choice(['pending', 'processing', 'shipped', 'delivered'])
    }


def _apply_dimension_corruption(record: Dict, entity_type: str) -> Dict:
    """Apply corruption to dimension record."""
    corruption_type = random.choice([
        'null_required',
        'invalid_email',
        'too_short',
        'empty_string'
    ])
    
    if entity_type == 'customer':
        if corruption_type == 'null_required':
            # Will fail: valid_email (expects NOT NULL)
            record['email'] = None
        elif corruption_type == 'invalid_email':
            # Will fail: valid_email (expects valid email format)
            record['email'] = "not-an-email"
        elif corruption_type == 'too_short':
            # Will fail: valid_first_name (expects min length 2)
            record['first_name'] = "A"
        elif corruption_type == 'empty_string':
            # Will fail: valid_last_name (expects non-empty string)
            record['last_name'] = ""
    
    return record


def _apply_fact_corruption(record: Dict, dimension_keys: Dict[str, List]) -> Dict:
    """Apply corruption to fact record."""
    corruption_type = random.choice([
        'invalid_fk',
        'null_fk',
        'negative_value',
        'future_date'
    ])
    
    if corruption_type == 'invalid_fk':
        # Will fail: valid_customer_id (expects customer_id in dim_customer)
        record['customer_id'] = 999999
    elif corruption_type == 'null_fk':
        # Will fail: valid_product_id (expects NOT NULL)
        record['product_id'] = None
    elif corruption_type == 'negative_value':
        # Will fail: valid_quantity (expects quantity >= 0)
        record['quantity'] = -1
        record['total_amount'] = record['quantity'] * record['unit_price']
    elif corruption_type == 'future_date':
        # Will fail: valid_order_date (expects order_date <= current_date)
        fake = Faker()
        record['order_date'] = fake.future_date()
    
    return record


def apply_corruption(record: Dict, corruption_rate: float) -> Dict:
    """
    Apply corruption to a record based on corruption rate.
    
    Args:
        record: Record dictionary
        corruption_rate: Corruption rate (0.0 to 1.0)
        
    Returns:
        Corrupted record dictionary
    """
    if random.random() < corruption_rate:
        # Apply random corruption
        corruption_type = random.choice([
            'null_required',
            'invalid_format',
            'out_of_range',
            'business_logic_violation'
        ])
        
        # Apply corruption based on type
        # Implementation depends on specific record structure
        pass
    
    return record
