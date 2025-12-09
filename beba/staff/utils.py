import uuid
import datetime

def generate_staff_id(prefix="STF"):
    """
    Generate a unique staff ID.
    Format: STF-YYYYMMDD-XXXX
    - prefix: identifier for staff (default "STF")
    - YYYYMMDD: current date
    - XXXX: random hex string
    """
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    random_str = uuid.uuid4().hex[:4].upper()  # 4-char random code
    staff_id = f"{prefix}-{date_str}-{random_str}"
    return staff_id