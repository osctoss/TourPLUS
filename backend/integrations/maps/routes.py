import math
from typing import Tuple, Optional


class RouteEngine:
    """
    Route and transit estimator.
    Computes geographic transit distance and estimated duration using Haversine calculation,
    with an extensible provider architecture for future Google Maps API integration.
    """

    EARTH_RADIUS_KM = 6371.0

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculates great-circle distance between two points on the Earth surface in km.
        """
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2.0) ** 2 +
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return RouteEngine.EARTH_RADIUS_KM * c

    @staticmethod
    def estimate_route(
        lat1: Optional[float],
        lon1: Optional[float],
        lat2: Optional[float],
        lon2: Optional[float]
    ) -> Tuple[float, int]:
        """
        Returns (distance_km, estimated_duration_minutes)
        """
        if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
            return 25.0, 45  # Standard default assumption if coordinates omitted

        dist_km = RouteEngine.haversine_distance(lat1, lon1, lat2, lon2)

        # Urban & highway mixed transit speed heuristic
        if dist_km <= 30.0:
            avg_speed_kmh = 30.0  # Dense urban traffic
        elif dist_km <= 150.0:
            avg_speed_kmh = 50.0  # Regional transit
        else:
            avg_speed_kmh = 70.0  # Intercity highway

        duration_hours = dist_km / avg_speed_kmh
        duration_minutes = max(15, int(round(duration_hours * 60)))

        return round(dist_km, 1), duration_minutes
