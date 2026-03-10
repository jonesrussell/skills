---
name: myme-weather
description: Use when modifying crates/myme-weather/ in MyMe. Covers weather API, platform-native geolocation (WinRT/D-Bus), caching.
---
# Weather Specialist

## Scope
Package: `crates/myme-weather/` (1111 lines)
Key files:
- `src/provider.rs` — WeatherProvider using Open-Meteo API
- `src/location.rs` — Platform-native geolocation (WinRT on Windows, GeoClue2/D-Bus on Linux)
- `src/cache.rs` — JSON file-based cache with staleness tracking
- `src/types.rs` — WeatherData, Location, WeatherCondition, DayForecast
- `src/geocode.rs` — Nominatim reverse geocoding (lat/lon → city name)

## Key Interfaces

**WeatherProvider**:
```rust
impl WeatherProvider {
    pub fn new(unit: TemperatureUnit) -> Result<Self, WeatherError>;  // 30s timeout
    pub fn set_unit(&mut self, unit: TemperatureUnit);
    pub async fn fetch(&self, location: &Location) -> Result<WeatherData, WeatherError>;
}
```

**Location** (platform-native):
```rust
pub async fn get_current_location() -> Result<Location, LocationError>;
pub async fn is_available() -> bool;
// Windows: windows::Devices::Geolocation::Geolocator (WinRT)
// Linux: org.freedesktop.GeoClue2 via zbus (D-Bus)
```

**WeatherCache** (JSON file):
```rust
impl WeatherCache {
    pub fn new(cache_dir: &Path) -> Self;
    pub fn get(&self) -> Option<&CachedWeather>;
    pub fn is_stale(&self) -> bool;    // > refresh_minutes from config
    pub fn is_expired(&self) -> bool;  // > 2 hours hard limit
    pub fn set(&mut self, data: WeatherData);
    pub fn save(&self) -> Result<()>;  // Writes JSON to disk
    pub fn load(&mut self) -> Result<()>;
}
```

**Types**:
```rust
pub struct WeatherData { pub current: CurrentWeather, pub daily: Vec<DayForecast>, pub location: Location }
pub struct CurrentWeather { pub temperature: f64, pub feels_like: f64, pub condition: WeatherCondition, pub humidity: u8, pub wind_speed: f64 }
pub struct DayForecast { pub date: NaiveDate, pub high: f64, pub low: f64, pub condition: WeatherCondition, pub precipitation_chance: u8 }
pub enum WeatherCondition { Clear, PartlyCloudy, Cloudy, Fog, Drizzle, Rain, Snow, Thunderstorm, ... }
```

## Architecture

Data flow: `get_current_location()` → `WeatherProvider::fetch(location)` → Open-Meteo API → parse WMO weather codes → `WeatherData`. Cache: check staleness → serve cached if fresh, fetch if stale.

Open-Meteo API is free, no API key needed. Nominatim reverse geocoding also free (OSM).

WMO weather code mapping: integer codes (0-99) → `WeatherCondition` enum. See `types.rs` for full mapping table.

## Common Mistakes
- **Platform compilation**: `location.rs` uses `#[cfg(target_os)]` — code changes must compile on both Windows (WinRT) and Linux (zbus/D-Bus)
- **GeoClue2 lifecycle**: Must call `client.Start()` before reading location AND `client.Stop()` after — forgetting Stop leaks D-Bus connections
- **Cache file race**: Multiple reads/writes to cache JSON can race — use `parking_lot::Mutex` around cache operations
- **Temperature unit**: `TemperatureUnit::Auto` resolves based on locale — test both Celsius and Fahrenheit paths
- **Nominatim rate limit**: 1 request/second — cache reverse geocode results aggressively

## Testing Patterns
- Provider: mock HTTP responses matching Open-Meteo JSON format
- Cache: `tempfile::tempdir()` for cache directory, test stale/expired/fresh states
- Location: platform tests only run on CI with appropriate OS
- Weather codes: test WMO code → condition mapping for all ranges

## Related Specs
- `docs/specs/weather.md` — Full type definitions, API response format, WMO code table, geolocation details
