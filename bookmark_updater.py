"""
Power BI PBIP Comprehensive Updater
===================================================
Updates Year and Month filters in BOTH page.json and bookmark.json files.
Ensures the default report load state matches the updated bookmarks.
python bookmark_updater.py "C:\Path\To\YourReportFolder" --year 2024 --month March
python bookmark_updater.py "C:\Path\To\YourReportFolder" --bookmark "Canada" --year 2014 --month January

"""

import json
import argparse
import shutil
from pathlib import Path


def update_filter_list(filter_list, new_year, new_month):
    """
    Core logic to update Year and Month DAX literals in any filter array.
    """
    updates = []
    for filter_item in filter_list:
        expr = filter_item.get('expression', {})
        
        if 'HierarchyLevel' in expr:
            level = expr['HierarchyLevel'].get('Level', '')
            
            if level == 'Year':
                old_value = filter_item['filter']['Where'][0]['Condition']['In']['Values'][0][0]['Literal']['Value']
                new_value = f"{new_year}L" # Strict DAX Literal for Year
                
                filter_item['filter']['Where'][0]['Condition']['In']['Values'][0][0]['Literal']['Value'] = new_value
                
                if 'cachedDisplayNames' in filter_item and len(filter_item['cachedDisplayNames']) > 0:
                    filter_item['cachedDisplayNames'][0]['id']['scopeId']['Comparison']['Right']['Literal']['Value'] = new_value
                    filter_item['cachedDisplayNames'][0]['displayName'] = str(new_year)
                
                updates.append(f"Year: {old_value} -> {new_value}")
                
            elif level == 'Month':
                old_value = filter_item['filter']['Where'][0]['Condition']['In']['Values'][0][0]['Literal']['Value']
                new_value = f"'{new_month}'" # Strict DAX Literal for Month
                
                filter_item['filter']['Where'][0]['Condition']['In']['Values'][0][0]['Literal']['Value'] = new_value
                
                if 'cachedDisplayNames' in filter_item and len(filter_item['cachedDisplayNames']) > 0:
                    filter_item['cachedDisplayNames'][0]['id']['scopeId']['Comparison']['Right']['Literal']['Value'] = new_value
                    filter_item['cachedDisplayNames'][0]['displayName'] = new_month
                
                updates.append(f"Month: {old_value} -> {new_value}")
                
    return updates


def process_pbip(input_path, output_path, year, month):
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise ValueError(f"Input path does not exist: {input_path}")

    # Locate the .Report folder
    report_folder = None
    for item in input_path.rglob("*.Report"):
        if item.is_dir():
            report_folder = item
            break
            
    if not report_folder:
        if (input_path / "definition").exists():
            report_folder = input_path
        else:
            raise ValueError(f"Could not find Report folder in {input_path}")

    print(f"\n{'='*70}")
    print(f"PBIP PAGE & BOOKMARK UPDATER")
    print(f"{'='*70}")

    # Clone the directory to preserve original files
    output_path.mkdir(parents=True, exist_ok=True)
    for item in input_path.iterdir():
        dst = output_path / item.name
        if item.is_dir():
            shutil.copytree(item, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dst)

    output_report_folder = output_path / report_folder.name
    processed_count = 0

    # 1. UPDATE DEFAULT PAGE STATES (page.json)
    print("\n📄 Updating Report Pages (Default View)...")
    pages_dir = output_report_folder / "definition" / "pages"
    if pages_dir.exists():
        for page_dir in pages_dir.iterdir():
            if page_dir.is_dir():
                page_file = page_dir / "page.json"
                if page_file.exists():
                    with open(page_file, 'r', encoding='utf-8') as f:
                        page_data = json.load(f)
                    
                    if 'filters' in page_data:
                        changes = update_filter_list(page_data['filters'], year, month)
                        if changes:
                            with open(page_file, 'w', encoding='utf-8') as f:
                                json.dump(page_data, f, indent=2, ensure_ascii=False)
                            print(f"  ✓ {page_data.get('displayName', page_dir.name)} updated.")
                            processed_count += 1

    # 2. UPDATE BOOKMARKS (*.bookmark.json)
    print("\n🔖 Updating Bookmarks...")
    bookmarks = []
    bookmarks_dir = output_report_folder / "definition" / "bookmarks"
    
    # Collect all bookmark files
    if bookmarks_dir.exists():
        for b_file in bookmarks_dir.glob("*.bookmark.json"):
            bookmarks.append(b_file)
    else:
        for b_file in output_report_folder.glob("**/*.bookmark.json"):
            bookmarks.append(b_file)

    for bookmark_file in bookmarks:
        with open(bookmark_file, 'r', encoding='utf-8') as f:
            bookmark_data = json.load(f)

        section_id = bookmark_data['explorationState']['activeSection']
        filters = bookmark_data['explorationState']['sections'][section_id]['filters']['byExpr']
        
        changes = update_filter_list(filters, year, month)
        
        if changes:
            with open(bookmark_file, 'w', encoding='utf-8') as f:
                json.dump(bookmark_data, f, indent=2, ensure_ascii=False)
            print(f"  ✓ {bookmark_data.get('displayName', bookmark_file.name)} updated.")
            processed_count += 1

    print(f"\n{'='*70}")
    print(f"✅ COMPLETED! Modified {processed_count} files total.")
    print(f"📦 Output location: {output_path}")
    print(f"🚀 Open this updated PBIP in Power BI Desktop.")


def main():
    parser = argparse.ArgumentParser(description='Update Year and Month filters in PBIP pages and bookmarks')
    parser.add_argument('input', help='Input PBIP root folder')
    parser.add_argument('-o', '--output', help='Output folder')
    parser.add_argument('--year', type=int, default=2014, help='Target year (default: 2014)')
    parser.add_argument('--month', default='January', help='Target month (default: January)')

    args = parser.parse_args()

    output_path = Path(args.output) if args.output else Path(args.input).parent / f"{Path(args.input).name}_Updated"
    process_pbip(args.input, output_path, args.year, args.month)


if __name__ == '__main__':
    main()
