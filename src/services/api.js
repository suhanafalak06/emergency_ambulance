// Simple mock implementations so the UI works without a backend.

function haversineKm([lat1, lon1], [lat2, lon2]) {
  const toRad = (d) => (d * Math.PI) / 180;
  const R = 6371; // km
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
    Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

export async function optimizeRoute(emergencyData) {
  // Simulate latency
  await new Promise(r => setTimeout(r, 800));

  const { ambulance_location, emergency_location, hospital_location, traffic_factor } = emergencyData;

  // Simple 3-point route
  const optimized_route = [ambulance_location, emergency_location, hospital_location];

  const distance1 = haversineKm(ambulance_location, emergency_location);
  const distance2 = haversineKm(emergency_location, hospital_location);
  const distance = distance1 + distance2;

  // Basic ETA (assume 40km/h baseline, modified by traffic)
  const eta_hours = distance / (40 / traffic_factor);
  const eta_minutes = eta_hours * 60;

  const improvement_percent = 15 + Math.random() * 10; // pretend optimization gain 15–25%

  const traffic_conditions = [
    {
      start_point: ambulance_location,
      end_point: emergency_location,
      traffic_factor,
    },
    {
      start_point: emergency_location,
      end_point: hospital_location,
      traffic_factor: Math.max(1.0, traffic_factor - 0.1),
    }
  ];

  return {
    optimized_route,
    distance,
    eta_minutes,
    improvement_percent,
    traffic_conditions,
  };
}

export async function getTrafficStatus(/* lat, lng */) {
  // Simulate changing traffic
  await new Promise(r => setTimeout(r, 200));
  const random = 1 + Math.random() * 1.2; // 1.0–2.2
  return { traffic_factor: parseFloat(random.toFixed(2)) };
}
