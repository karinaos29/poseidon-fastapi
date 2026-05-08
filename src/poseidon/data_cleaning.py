import pandas as pd

class DataCleaner:
    
    @staticmethod
    def validate_report(readings: dict[str, float]) -> tuple[bool, list[str]]:
        """Shallow validation for incoming real-time telemetry."""
        errors = []
        for key in ["speed_knots", "draft_m", "heading_deg", "fuel_rate_lph"]:
            if key not in readings:
                errors.append(f"Missing key: {key}")
            elif readings[key] < 0 and key != "heading_deg":
                errors.append(f"{key} cannot be negative")
                
        if "speed_knots" in readings and readings["speed_knots"] > 50:
            errors.append("speed_knots exceeds realistic bounds (>50)")
            
        return len(errors) == 0, errors

    @staticmethod
    def clean_historical_batch(df: pd.DataFrame) -> pd.DataFrame:
        """Vectorized cleaning of the full historical frame."""
        df = df.dropna(subset=["vessel_id", "timestamp"]).copy()

        valid_mask = (
            (df["speed_knots"] >= 0) & 
            (df["speed_knots"] <= 50) & 
            (df["draft_m"] >= 0) & 
            (df["fuel_rate_lph"] >= 0)
        )
        df = df.loc[valid_mask].copy()

        df["heading_deg"] = (df["heading_deg"].astype("float64") % 360).astype("float32[pyarrow]")
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

        return df

    @staticmethod
    def parse_wkt_column(series: pd.Series) -> pd.DataFrame:
        """
        Flavour 2: Batch WKT parsing using modern pandas string extraction.
        Returns a DataFrame with 'lon' and 'lat' columns.
        """
        wkt_pattern = r"POINT\s*\(\s*(?P<lon>-?\d+\.?\d*)\s+(?P<lat>-?\d+\.?\d*)\s*\)"
        
        coords = series.str.extract(wkt_pattern).astype("float32[pyarrow]")
        return coords

    @staticmethod
    def categorise_by_speed(df: pd.DataFrame, thresholds: dict[str, float]) -> pd.DataFrame:
        """Adds a categorised 'risk_band' column based on speed thresholds."""
        bins = [
            -1.0,  
            thresholds["speed_safe"],
            thresholds["speed_moderate"],
            thresholds["speed_danger"],
            float("inf")
        ]
        labels = ["Safe", "Moderate", "Unsafe", "Danger"]
        
        return df.assign(
            risk_band=lambda d: pd.cut(d["speed_knots"], bins=bins, labels=labels)
        )

    @staticmethod
    def distribution_by_flag(
        df: pd.DataFrame, 
        thresholds: dict[str, float], 
        year: int, 
        month: int
    ) -> pd.DataFrame:
        """Aggregates data for the 100% stacked bar chart endpoint."""
        mask = (df["timestamp"].dt.year == year) & (df["timestamp"].dt.month == month)
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            return pd.DataFrame()

        categorised_df = DataCleaner.categorise_by_speed(filtered_df, thresholds)

        summary = (
            categorised_df
            .groupby(["flag_state", "risk_band"], observed=False)
            .agg(reports=("vessel_id", "size"))
            .reset_index()
        )
        return summary