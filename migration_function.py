#!/usr/bin/env python3
"""
FoxPro Migration Script to be executed via bench
This script will be called by bench execute
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# These imports will work when called via bench execute
try:
    from dbfread import DBF
    import pandas as pd
except ImportError:
    print("Please install required packages: pip install dbfread pandas")
    sys.exit(1)


def migrate_data():
    """Main migration function"""
    import frappe

    # Configuration
    LEGACY_DATA_DIR = "/workspace/development/Zevar_URMS/Zevar_URMS/JCSWIN 1(1)/JCSWIN/"
    MIGRATION_LOG_FILE = f"/workspace/migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    MIGRATION_STATS_FILE = "/workspace/migration_stats.json"
    SQL_DUMP_FILE = "/workspace/migrated_data.sql"
    COMPRESSED_FILE = "/workspace/migrated_data.tar.gz"

    stats = {
        'total_processed': 0,
        'successful': 0,
        'failed': 0,
        'skipped': 0,
        'by_table': {},
        'start_time': datetime.now().isoformat(),
        'end_time': None
    }

    def clean_value(value, field_type='string'):
        """Clean and convert DBF values"""
        if pd.isna(value) or value is None:
            return None

        if field_type == 'string':
            return str(value).strip() if value else None
        elif field_type == 'int':
            try:
                return int(float(value))
            except (ValueError, TypeError):
                return 0
        elif field_type == 'float':
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0.0
        else:
            return value

    def read_dbf_file(filename):
        """Read a DBF file and return DataFrame"""
        dbf_path = os.path.join(LEGACY_DATA_DIR, filename)

        # Try different case combinations
        if not os.path.exists(dbf_path):
            alt_paths = [
                os.path.join(LEGACY_DATA_DIR, filename.lower()),
                os.path.join(LEGACY_DATA_DIR, filename.upper()),
                os.path.join(LEGACY_DATA_DIR, filename.replace('.DBF', '.dbf')),
                os.path.join(LEGACY_DATA_DIR, filename.replace('.dbf', '.DBF'))
            ]
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    dbf_path = alt_path
                    break

        if not os.path.exists(dbf_path):
            return None

        try:
            print(f"Reading DBF file: {filename}")
            table = DBF(dbf_path, load=True, encoding='cp1252', ignore_missing_memofile=True)
            df = pd.DataFrame(iter(table))
            print(f"✅ Successfully read {len(df)} records from {filename}")
            return df
        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")
            return None

    print("Starting FoxPro Migration")
    print("="*80)

    # Test connection
    supplier_count = frappe.db.count('tabSupplier')
    print(f"Current supplier count: {supplier_count}")

    # === MIGRATE SUPPLIERS ===
    print("\n" + "="*80)
    print("MIGRATING SUPPLIERS")
    print("="*80)

    supplier_df = read_dbf_file("supplier.dbf")
    if supplier_df is not None:
        supplier_stats = {'total': 0, 'success': 0, 'failed': 0, 'skipped': 0}
        print(f"Found {len(supplier_df)} supplier records")

        for index, row in supplier_df.iterrows():
            try:
                supplier_stats['total'] += 1

                # Get supplier name from FULLNAME field
                supplier_name = clean_value(row.get('FULLNAME'), 'string')
                if not supplier_name:
                    supplier_stats['skipped'] += 1
                    continue

                # Check if supplier exists
                if frappe.db.exists('Supplier', {'supplier_name': supplier_name}):
                    if index < 10:
                        print(f"Skipping duplicate supplier: {supplier_name}")
                    supplier_stats['skipped'] += 1
                    continue

                # Create supplier
                doc = frappe.new_doc('Supplier')
                doc.supplier_name = supplier_name
                doc.supplier_type = 'Company'
                doc.insert()
                supplier_stats['success'] += 1

                if (index + 1) % 50 == 0:
                    print(f"Processed {index + 1}/{len(supplier_df)} suppliers...")

            except Exception as e:
                print(f"❌ Error creating supplier {index}: {e}")
                supplier_stats['failed'] += 1

        stats['by_table']['Supplier'] = supplier_stats
        print(f"✅ Suppliers migration completed: {supplier_stats['success']} successful")

    # === MIGRATE ITEMS ===
    print("\n" + "="*80)
    print("MIGRATING ITEMS")
    print("="*80)

    item_df = read_dbf_file("inventor.dbf")
    if item_df is not None:
        item_stats = {'total': 0, 'success': 0, 'failed': 0, 'skipped': 0}
        print(f"Found {len(item_df)} item records")

        for index, row in item_df.iterrows():
            try:
                item_stats['total'] += 1

                # Get SKU from ABR field
                sku = clean_value(row.get('ABR'), 'string')
                if not sku:
                    item_stats['skipped'] += 1
                    continue

                # Build item name
                item_name = clean_value(row.get('DESCRIPT'), 'string') or sku

                # Check if item exists
                if frappe.db.exists('Item', {'item_code': sku}):
                    if index < 10:
                        print(f"Skipping duplicate item: {sku}")
                    item_stats['skipped'] += 1
                    continue

                # Get other values
                category = clean_value(row.get('CATEGORY'), 'string') or "All Item Groups"
                description = clean_value(row.get('DESC2'), 'string') or item_name
                cost = clean_value(row.get('COST'), 'float') or 0.0

                # Create item
                doc = frappe.new_doc('Item')
                doc.item_code = sku
                doc.item_name = item_name
                doc.description = description
                doc.item_group = category
                doc.stock_uom = 'Nos'
                doc.is_stock_item = 1
                doc.is_purchase_item = 1
                doc.is_sales_item = 1
                doc.valuation_rate = cost
                doc.insert()
                item_stats['success'] += 1

                if (index + 1) % 100 == 0:
                    print(f"Processed {index + 1}/{len(item_df)} items...")

            except Exception as e:
                print(f"❌ Error creating item {index}: {e}")
                item_stats['failed'] += 1

        stats['by_table']['Item'] = item_stats
        print(f"✅ Items migration completed: {item_stats['success']} successful")

    # Commit changes
    frappe.db.commit()
    print("✅ Database changes committed")

    # Calculate totals
    for table_stats in stats['by_table'].values():
        stats['total_processed'] += table_stats.get('total', 0)
        stats['successful'] += table_stats.get('success', 0)
        stats['failed'] += table_stats.get('failed', 0)
        stats['skipped'] += table_stats.get('skipped', 0)

    # Save stats
    stats['end_time'] = datetime.now().isoformat()
    with open(MIGRATION_STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2, default=str)

    # Print summary
    print("\n" + "="*80)
    print("MIGRATION SUMMARY")
    print("="*80)
    print(f"Total records processed: {stats['total_processed']}")
    print(f"Successfully migrated: {stats['successful']}")
    print(f"Failed: {stats['failed']}")
    print(f"Skipped (duplicates): {stats['skipped']}")

    print("\nBreakdown by Table:")
    for table, table_stats in stats['by_table'].items():
        print(f"  {table}:")
        print(f"    Total: {table_stats.get('total', 0)}")
        print(f"    Success: {table_stats.get('success', 0)}")
        print(f"    Failed: {table_stats.get('failed', 0)}")

    print("="*80)
    print(f"\n✅ Migration completed!")
    print(f"Statistics saved to: {MIGRATION_STATS_FILE}")

    return stats


if __name__ == "__main__":
    migrate_data()
