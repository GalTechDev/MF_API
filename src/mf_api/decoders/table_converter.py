import os
import csv
import json
import re
from pathlib import Path

def generate_eccodes_tables(input_dir: str, output_base: str):
    """
    Generate eccodes element.table and sequence.def for each version found in the CSVs.
    """
    input_path = Path(input_dir)
    
    # Identify available versions by parsing localtabb_85_x.csv
    versions = set()
    for csv_file in input_path.glob("localtabb_85_*.csv"):
        m = re.search(r'localtabb_85_(\d+)\.csv', csv_file.name)
        if m:
            versions.add(int(m.group(1)))
            
    for version in sorted(versions):
        out_dir = Path(output_base) / "bufr" / "tables" / "0" / "local" / str(version) / "85" / "0"
        out_dir.mkdir(parents=True, exist_ok=True)
        
        # Write element.table
        tabb_file = input_path / f"localtabb_85_{version}.csv"
        if tabb_file.exists():
            with open(tabb_file, 'r', encoding='latin-1') as f_in, open(out_dir / "element.table", 'w', encoding='utf-8') as f_out:
                reader = csv.reader(f_in, delimiter=';')
                for row in reader:
                    if len(row) >= 8:
                        f_val, x_val, y_val, name, unit, scale, ref, width = row[:8]
                        if not f_val.strip() and not x_val.strip(): continue
                        try:
                            code = f"{int(f_val):01d}{int(x_val):02d}{int(y_val):03d}"
                            unit_str = unit.strip()
                            type_str = "Numeric"
                            if "Code table" in unit_str or "Flag table" in unit_str or "CODE TABLE" in unit_str.upper():
                                type_str = "Code table"
                            short_name = name.strip().replace(' ', '')
                            # Code|shortName|type|Name|Unit|Scale|Reference|Width|type|0|2
                            f_out.write(f"{code}|{short_name}|long|{name.strip()}|{unit_str}|{scale.strip()}|{ref.strip()}|{width.strip()}|{type_str}|0|2\n")
                        except ValueError:
                            pass
                            
        # Write sequence.def
        tabd_file = input_path / f"localtabd_85_{version}.csv"
        if tabd_file.exists():
            with open(tabd_file, 'r', encoding='latin-1') as f_in, open(out_dir / "sequence.def", 'w', encoding='utf-8') as f_out:
                reader = csv.reader(f_in, delimiter=';')
                current_seq = None
                members = []
                
                def write_seq():
                    if current_seq and members:
                        m_str = ", ".join(members)
                        f_out.write(f'"{current_seq}" = [ {m_str} ]\n')
                
                for row in reader:
                    if len(row) >= 6:
                        f_val, x_val, y_val = row[:3]
                        mf, mx, my = row[3:6]
                        mf = mf.strip()
                        if not mf: continue
                        
                        try:
                            member_code = f"{int(mf)}{int(mx.strip()):02d}{int(my.strip()):03d}"
                        except Exception:
                            continue
                            
                        if f_val.strip() and x_val.strip() and y_val.strip():
                            write_seq()
                            try:
                                current_seq = f"{int(f_val.strip())}{int(x_val.strip()):02d}{int(y_val.strip()):03d}"
                                members = [member_code]
                            except ValueError:
                                continue
                        elif current_seq:
                            members.append(member_code)
                write_seq()

if __name__ == "__main__":
    input_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "docs", "tables_extracted", "tables")
    base_dir = os.path.join(os.path.dirname(__file__), "eccodes_defs")
    generate_eccodes_tables(input_dir, base_dir)
    print("Tables eccodes générées avec succès!")
