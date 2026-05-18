"""
CSV Import Service for Inventory Assets
Handles parsing, validation, and bulk creation of inventory from CSV files
"""

import csv
import logging
from datetime import datetime
from typing import Dict, Optional

from django.utils.dateparse import parse_date

from .csv_mappings import (
    COLUMN_MAPPINGS,
    detect_category_from_columns,
    detect_category_from_filename,
)
from .models import InventoryAsset

logger = logging.getLogger(__name__)


class CSVImportError(Exception):
    """Base exception for CSV import errors"""

    pass


class CSVImportService:
    """Service to import inventory data from CSV files"""

    def __init__(self, category: Optional[str] = None):
        self.category = category
        self.mapping = None

        self.created_count = 0
        self.skipped_count = 0
        self.error_count = 0
        self.errors = []

    def import_from_file(
        self,
        file_path: str,
        detect_category: bool = True,
    ) -> Dict:

        try:
            with open(
                file_path,
                "r",
                encoding="utf-8-sig",
            ) as f:

                csv_reader = csv.DictReader(f)

                if not csv_reader.fieldnames:
                    raise CSVImportError("CSV file is empty")

                # ---------------------------------
                # DETECT CATEGORY
                # ---------------------------------

                if not self.category and detect_category:

                    self.category = detect_category_from_filename(file_path)

                    if not self.category:
                        self.category = detect_category_from_columns(
                            csv_reader.fieldnames
                        )

                if not self.category:
                    raise CSVImportError(
                        f"Could not detect category. "
                        f"Columns: {csv_reader.fieldnames}"
                    )

                # ---------------------------------
                # GET MAPPING
                # ---------------------------------

                self.mapping = COLUMN_MAPPINGS.get(self.category)

                if not self.mapping:
                    raise CSVImportError(f"Unknown category: " f"{self.category}")

                # ---------------------------------
                # IMPORT ROWS
                # ---------------------------------

                for row_num, row in enumerate(
                    csv_reader,
                    start=2,
                ):

                    try:
                        self._import_row(
                            row,
                            row_num,
                        )

                    except Exception as e:

                        self.error_count += 1

                        error_msg = f"Row {row_num}: " f"{str(e)}"

                        logger.warning(error_msg)

                        self.errors.append(error_msg)

            return self._get_results()

        except Exception as e:

            logger.error(f"CSV import error: {str(e)}")

            raise CSVImportError(f"Failed to import CSV: {str(e)}")

    def _import_row(
        self,
        row: Dict,
        row_num: int,
    ) -> None:
        """
        Import single row
        """

        parsed_data = self._parse_row(
            row,
            row_num,
        )

        if not parsed_data.get("serial_number"):

            raise CSVImportError("Serial number is required")

        serial_number = parsed_data["serial_number"]

        # ---------------------------------
        # DUPLICATE CHECK
        # ---------------------------------

        if InventoryAsset.objects.filter(serial_number=serial_number).exists():

            print("\nDUPLICATE FOUND:")
            print(f"Category: {self.category}")
            print(f"Row: {row_num}")
            print(f"Serial: {serial_number}")
            print(f"CSV Row: {row}")

            self.skipped_count += 1

            logger.info(
                f"Row {row_num}: "
                f"Duplicate serial number "
                f"{serial_number}, skipping"
            )

            return

        # ---------------------------------
        # CREATE ASSET
        # ---------------------------------

        asset = InventoryAsset.objects.create(**parsed_data)

        self.created_count += 1

        logger.info(f"Row {row_num}: " f"Created asset {asset.id}")

    def _parse_row(
        self,
        row: Dict,
        row_num: int = 0,
    ) -> Dict:
        """
        Parse CSV row into model fields
        """

        data = {
            "category": self.category,
            "metadata": {},
        }

        # ---------------------------------
        # PROCESS COLUMNS
        # ---------------------------------

        for (
            csv_column,
            mapping_target,
        ) in self.mapping.items():

            if csv_column not in row:
                continue

            value = row[csv_column]

            if not value or not str(value).strip():
                continue

            value = str(value).strip()

            # ---------------------------------
            # METADATA MAPPING
            # ---------------------------------

            if isinstance(
                mapping_target,
                tuple,
            ):

                (
                    target_location,
                    field_name,
                ) = mapping_target

                if target_location == "metadata":

                    data["metadata"][field_name] = value

                continue

            field_name = mapping_target

            # ---------------------------------
            # FIELD MAPPINGS
            # ---------------------------------

            if field_name == "serial_number":

                data["serial_number"] = value

            elif field_name == "asset_name":

                data["asset_name"] = value

            elif field_name == "assigned_person_name":

                data["assigned_person_name"] = value

            elif field_name == "assigned_email":

                if "@" in value:

                    data["assigned_email"] = value

            elif field_name == "assigned_date":

                parsed_date = self._parse_date(value)

                if parsed_date:

                    data["assigned_date"] = parsed_date

            elif field_name == "purchase_date":

                parsed_date = self._parse_date(value)

                if parsed_date:

                    data["purchase_date"] = parsed_date

            elif field_name == "assigned_by":

                data["assigned_by"] = value

            elif field_name == "condition":

                data["condition"] = self._normalize_condition(value)

            elif field_name == "quantity":

                try:
                    data["quantity"] = int(value)

                except Exception:
                    data["quantity"] = 1

            elif field_name == "remarks":

                data["remarks"] = value

            elif field_name == "delivery_mail_status":

                data["metadata"]["delivery_mail_status"] = value

        # ---------------------------------
        # FALLBACK SERIAL NUMBER
        # ---------------------------------

        if not data.get("serial_number"):

            fallback_fields = []

            if self.category == "pc":

                fallback_fields = [
                    row.get("CPU Serial No."),
                    row.get("Monitor Serial No."),
                    row.get("S No."),
                ]

            elif self.category == "laptop":

                fallback_fields = [
                    row.get("SN"),
                    row.get("SN.MO"),
                    row.get("(1S)MTM.SN"),
                    row.get("Allocation No."),
                ]

            elif self.category == "mobile":

                fallback_fields = [
                    row.get("Serial Number"),
                    row.get("Model Number"),
                    row.get("Allocation Serial No."),
                ]

            elif self.category in [
                "headphone",
                "connector",
            ]:

                fallback_fields = [
                    row.get("Device Serial No."),
                    row.get("Allocation Serial No."),
                ]

            for item in fallback_fields:

                if item and str(item).strip():

                    data["serial_number"] = str(item).strip()

                    break

        # ---------------------------------
        # MAKE SERIAL UNIQUE
        # ---------------------------------

        if data.get("serial_number"):

            serial = str(data["serial_number"]).strip()

            assigned_person = str(
                data.get(
                    "assigned_person_name",
                    "",
                )
            ).strip()

            invalid_values = [
                "",
                "not assigned",
                "not available",
                "n/a",
                "na",
                "none",
            ]

            serial_lower = serial.lower()

            assigned_lower = assigned_person.lower()

            # ---------------------------------
            # AVAILABLE DEVICES
            # ---------------------------------

            if serial_lower in invalid_values or assigned_lower in invalid_values:

                row_id = (
                    row.get("Device Serial No.")
                    or row.get("CPU Serial No.")
                    or row.get("Monitor Serial No.")
                    or row.get("SN")
                    or row.get("Serial Number")
                    or row.get("S No.")
                    or row.get("Allocation No.")
                    or row.get("Allocation Serial No.")
                    or row_num
                )

                row_id = str(row_id).strip().replace(" ", "_")

                data["serial_number"] = f"{self.category}" f"_available_" f"{row_id}"

                # Device available for request

                data["assigned_person_name"] = ""

                data["pending_claim"] = False

                data["claimed"] = False

                data["metadata"]["availability"] = "available"

            else:

                clean_name = (
                    assigned_person.replace(" ", "_")
                    .replace(".", "")
                    .replace("/", "_")
                    .lower()
                    .strip()
                )

                data["serial_number"] = f"{serial}_{clean_name}"

                data["pending_claim"] = True

                data["claimed"] = False

                # ---------------------------------
                # PROFILE STATUS
                # ---------------------------------

                if assigned_lower == "not defined":

                    data["metadata"]["profile_status"] = "profile_not_defined"

                elif assigned_lower == "not available":

                    data["metadata"]["profile_status"] = "profile_not_available"

        # ---------------------------------
        # DEFAULT ASSET NAME
        # ---------------------------------

        if not data.get("asset_name"):

            data["asset_name"] = (
                f"{self.category.upper()} - " f"{data.get('serial_number', 'N/A')}"
            )

        return data

    def _parse_date(
        self,
        date_str,
    ):

        if not date_str:
            return None

        date_str = str(date_str).strip()

        formats = [
            "%d-%m-%Y",
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%d.%m.%Y",
            "%B %d, %Y",
            "%b %d, %Y",
        ]

        for fmt in formats:

            try:

                return datetime.strptime(
                    date_str,
                    fmt,
                ).date()

            except ValueError:
                continue

        parsed = parse_date(date_str)

        if parsed:
            return parsed

        return None

    def _normalize_condition(
        self,
        value: str,
    ) -> str:

        value_lower = value.lower()

        condition_map = {
            "new": "new",
            "excellent": "excellent",
            "good": "good",
            "fair": "fair",
            "poor": "poor",
            "used": "good",
            "acceptable": "good",
        }

        for (
            key,
            normalized,
        ) in condition_map.items():

            if key in value_lower:
                return normalized

        return "good"

    def _get_results(self) -> Dict:

        return {
            "created": self.created_count,
            "skipped": self.skipped_count,
            "errors": self.error_count,
            "total": (self.created_count + self.skipped_count + self.error_count),
            "error_details": self.errors,
        }
