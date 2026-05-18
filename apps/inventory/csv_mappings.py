"""
CSV Column Mappings for Different Inventory Categories
Maps CSV columns to InventoryAsset model fields and metadata
"""

# PC Inventory Mapping
PC_COLUMN_MAPPING = {
    "CPU Serial No.": "serial_number",
    "Purchase Date": "purchase_date",
    "Device Type": "category_indicator",  # Should be 'pc'
    "Accessories": ("metadata", "accessories"),
    "CPU Serial No.": ("metadata", "cpu_serial"),
    "Monitor Serial No.": ("metadata", "monitor_serial"),
    "Allocated To": "assigned_person_name",
    "Allocation Date": "assigned_date",
    "Allocated By": "assigned_by",
    "Delivery Mail": "delivery_mail_status",  # Maps to remarks or status
    "Acknwoldegment Status": ("metadata", "acknowledgment_status"),  # Note: Typo in CSV
}

# Laptop Inventory Mapping
LAPTOP_COLUMN_MAPPING = {
    "SN": "serial_number",
    "Allocated To": "assigned_person_name",
    "Device Type": "category_indicator",  # Should be 'laptop'
    "Allocation Date": "assigned_date",
    "CPU": ("metadata", "cpu"),
    "RAM": ("metadata", "ram"),
    "Storage": ("metadata", "storage"),
    "GPU": ("metadata", "gpu"),
    "OS": ("metadata", "os"),
    "Color": ("metadata", "color"),
    "Product Name": "asset_name",
    "SN": ("metadata", "sn"),
    "SN.MO": ("metadata", "sn_mo"),
    "(1S)MTM.SN": ("metadata", "mtm_sn"),
    "WMAC": ("metadata", "wmac"),
    "Model for India:": ("metadata", "model_india"),
    "Quantity": "quantity",
    "Laptop computer system": ("metadata", "laptop_system"),
    "Battery": ("metadata", "battery"),
    "Manual": ("metadata", "manual"),
    "Power Cord": ("metadata", "power_cord"),
    "Adapter": ("metadata", "adapter"),
    "Delivery Mail": "delivery_mail_status",
    "Acknwoldegment Status": ("metadata", "acknowledgment_status"),
}

# Headphone Inventory Mapping
HEADPHONE_COLUMN_MAPPING = {
    "Device Serial No.": "serial_number",
    "Purchase Date": "purchase_date",
    "Quantity": "quantity",
    "Device Type": "category_indicator",  # Should be 'headphone'
    "Device Configuration": ("metadata", "configuration"),
    "Device Serial No.": ("metadata", "device_serial"),
    "Brand": ("metadata", "brand"),
    "Model": ("metadata", "model"),
    "Accessories": ("metadata", "accessories"),
    "Assigned Date": "assigned_date",
    "Assigned Person": "assigned_person_name",
    "Profile": ("metadata", "profile"),
    "Assigned By": "assigned_by",
    "Condition (At Assignment)": "condition",
    "Assigned Mail Status": "delivery_mail_status",
    "Acknowledgment Status": ("metadata", "acknowledgment_status"),
    "Remark": "remarks",
}

# Connector Inventory Mapping
CONNECTOR_COLUMN_MAPPING = {
    "Device Serial No.": "serial_number",
    "Purchase Date": "purchase_date",
    "Quantity": "quantity",
    "Device Type": "category_indicator",  # Should be 'connector'
    "Device Configuration": ("metadata", "configuration"),
    "Device Serial No.": ("metadata", "device_serial"),
    "Brand": ("metadata", "brand"),
    "Model": ("metadata", "model"),
    "Accessories": ("metadata", "accessories"),
    "Assigned Date": "assigned_date",
    "Assigned Person": "assigned_person_name",
    "Profile": ("metadata", "profile"),
    "Assigned By": "assigned_by",
    "Condition (At Assignment)": "condition",
    "Assigned Mail Status": "delivery_mail_status",
    "Acknowledgment Status": ("metadata", "acknowledgment_status"),
    "Remark": "remarks",
}

# Mobile Inventory Mapping
MOBILE_COLUMN_MAPPING = {
    "Serial Number": "serial_number",
    "Assigned To": "assigned_person_name",
    "Device Name": "asset_name",
    "RAM": ("metadata", "ram"),
    "ROM": ("metadata", "rom"),
    "Model Number": ("metadata", "model"),
    "Serial Number": ("metadata", "device_serial"),
    "Adapter": ("metadata", "adapter"),
    "Wire": ("metadata", "wire"),
    "Phone Cover": ("metadata", "phone_cover"),
    "SIM Card": ("metadata", "sim_card"),
    "Number-1": ("metadata", "phone_number_1"),
    "Number-2": ("metadata", "phone_number_2"),
    "Delivery Mail": "delivery_mail_status",
    "Acknwoldegment Status": ("metadata", "acknowledgment_status"),
}

# Category Mapping (for file name detection)
CATEGORY_MAPPING = {
    "laptop": "laptop",
    "pc": "pc",
    "headphone": "headphone",
    "connector": "connector",
    "mobile": "mobile",
}

# Master mapping registry
COLUMN_MAPPINGS = {
    "pc": PC_COLUMN_MAPPING,
    "laptop": LAPTOP_COLUMN_MAPPING,
    "headphone": HEADPHONE_COLUMN_MAPPING,
    "connector": CONNECTOR_COLUMN_MAPPING,
    "mobile": MOBILE_COLUMN_MAPPING,
}


def get_mapping_for_category(category):
    """Get column mapping for a specific category"""
    return COLUMN_MAPPINGS.get(category.lower(), {})


def detect_category_from_filename(filename):
    """Detect category from CSV filename"""
    filename_lower = filename.lower()
    
    for category_key in CATEGORY_MAPPING.keys():
        if category_key in filename_lower:
            return category_key
    
    return None


def detect_category_from_columns(columns):
    """Detect category by matching CSV columns against known patterns"""
    columns_set = set(col.strip() for col in columns)
    
    # Check for unique identifier columns
    if "CPU Serial No." in columns_set and "Monitor Serial No." in columns_set:
        return "pc"
    
    if "Allocation No." in columns_set and "WMAC" in columns_set:
        return "laptop"
    
    if "Number-1" in columns_set and "Number-2" in columns_set:
        return "mobile"
    
    if "Assigned Mail Status" in columns_set and "Assigned Person" in columns_set:
        # Could be headphone or connector, check for more clues
        if "Model" in columns_set:
            return "headphone"  # or connector, but default to headphone
    
    return None
