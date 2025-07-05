#!/usr/bin/env python3
"""
Test the web interface by checking browser console
"""

import webbrowser
import time

print("🔧 Testing web interface...")
print("Open your browser to: http://localhost:5000")
print()
print("In the browser developer console (F12), check for:")
print("1. JavaScript errors")
print("2. Network requests to /api/status")
print("3. Try running this in the console:")
print()
print("   fetch('/api/status').then(r => r.json()).then(console.log)")
print()
print("This will show if the API is being called correctly.")

# Also let's create a simple debug page
html_debug = '''<!DOCTYPE html>
<html>
<head>
    <title>Gate Status Debug</title>
</head>
<body>
    <h1>Gate Status Debug</h1>
    <div id="raw-data"></div>
    <div id="position-test"></div>

    <script>
    async function testAPI() {
        try {
            console.log('Fetching status...');
            const response = await fetch('/api/status');
            const data = await response.json();

            console.log('Raw data:', data);
            document.getElementById('raw-data').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';

            // Test position update
            document.getElementById('position-test').innerHTML = 'Position: ' + data.position + '%';

        } catch (error) {
            console.error('Error:', error);
            document.getElementById('raw-data').innerHTML = 'Error: ' + error.message;
        }
    }

    // Test immediately
    testAPI();

    // Test every 2 seconds
    setInterval(testAPI, 2000);
    </script>
</body>
</html>'''

with open('debug.html', 'w') as f:
    f.write(html_debug)

print("Created debug.html - open this in your browser to test the API")
print("http://localhost:5000/../debug.html")
