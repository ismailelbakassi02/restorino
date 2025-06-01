// Initialize map variables
let map;
let marker;
let mapInitialized = false;

// Function to initialize the map
function initMap() {
    // Default to Agadir center if no coordinates provided
    const defaultLocation = { lat: 30.4278, lng: -9.5981 };
    
    // Create map with default options
    map = new google.maps.Map(document.getElementById('map-preview'), {
        zoom: 14,
        center: defaultLocation,
        mapTypeControl: true,
        streetViewControl: false,
        fullscreenControl: true
    });
    
    // Create a marker that can be repositioned
    marker = new google.maps.Marker({
        position: defaultLocation,
        map: map,
        draggable: true,
        animation: google.maps.Animation.DROP
    });
    
    // When marker is dragged, update the form fields
    google.maps.event.addListener(marker, 'dragend', function() {
        const position = marker.getPosition();
        document.getElementById('latitude').value = position.lat();
        document.getElementById('longitude').value = position.lng();
    });
    
    mapInitialized = true;
    checkCoordinates();
}

// Function to update map when coordinates change
function updateMap(lat, lng) {
    if (!mapInitialized) return;
    
    const position = new google.maps.LatLng(lat, lng);
    marker.setPosition(position);
    map.setCenter(position);
    
    // Show the map and hide placeholder
    document.getElementById('map-preview').style.display = 'block';
    document.getElementById('map-placeholder').style.display = 'none';
}

// Function to check if coordinates are valid
function checkCoordinates() {
    const latField = document.getElementById('latitude');
    const lngField = document.getElementById('longitude');
    
    if (latField.value && lngField.value) {
        const lat = parseFloat(latField.value);
        const lng = parseFloat(lngField.value);
        
        if (!isNaN(lat) && !isNaN(lng) && lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
            updateMap(lat, lng);
            return;
        }
    }
    
    // If coordinates are invalid or empty, hide map and show placeholder
    document.getElementById('map-preview').style.display = 'none';
    document.getElementById('map-placeholder').style.display = 'block';
}

// Set up event listeners when document is loaded
document.addEventListener('DOMContentLoaded', function() {
    const latField = document.getElementById('latitude');
    const lngField = document.getElementById('longitude');
    
    // Add event listeners to coordinate fields
    if (latField && lngField) {
        latField.addEventListener('input', checkCoordinates);
        lngField.addEventListener('input', checkCoordinates);
    }
});
